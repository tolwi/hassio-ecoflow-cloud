"""EcoFlow Ocean Pro (US) — read-only internal / app-API device profiles.

An Ocean Pro system is two physically separate devices, each publishing its own
`/app/device/property/<sn>` MQTT stream, so it is modelled here as two HA
devices (the user adds both serial numbers):

  * OceanPanel      — the OCEAN Smart Panel (HR61…). Its stream carries the
                      per-circuit array, circuit labels and grid/load flows.
                      This is exactly the Smart Home Panel 3 shape, widened
                      32 -> 40 circuits, so it subclasses SmartHomePanel3.
  * OceanProInverter — the OCEAN Pro inverter (HR51…). Its stream carries the
                      solar strings pv1..pv8, the inverter AC output (pcs_total)
                      and the battery packs. None of the circuit data lives
                      here, so it subclasses DeltaPro3 (the shared 254/21
                      decode) and adds only the solar/battery side.

Verified against ~4,992 field checks replayed from live captures vs a private,
utility-meter-validated collector (see the repo's fieldmap for the field map).
Both devices are read-only: sensors only, no control entities.
"""

import logging
from typing import Any, override

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices.internal.delta_pro_3 import DeltaPro3
from custom_components.ecoflow_cloud.devices.internal.smart_home_panel_3 import (
    WIRE_F32,
    WIRE_F64,
    WIRE_VARINT,
    FieldMap,
    SmartHomePanel3,
    _first,
    _parse_fields,
)
from custom_components.ecoflow_cloud.sensor import (
    QuotaStatusSensorEntity,
    SolarPowerSensorEntity,
    WattsSensorEntity,
)

_LOGGER = logging.getLogger(__name__)

# --- Panel (HR61) -----------------------------------------------------------
# 40 monitored load circuits — the SHP3 layout (fields 1015..1054) widened by 8.
OCEAN_PANEL_CIRCUITS = 40
# Circuit label / split-phase metadata blocks, positional (circuit N ->
# NAME_FIELDS[N-1]). Confirmed against a live panel config broadcast: circuits
# 1..12 -> fields 794..805, circuits 13..40 -> fields 920..947 (SHP3's 32-circuit
# 794..805 + 920..939, extended by 8). Self-calibrated from the panel's own
# "Circuit N" defaults and cross-checked against the app-set names.
OCEAN_PANEL_NAME_FIELDS = list(range(794, 806)) + list(range(920, 948))

# --- Inverter (HR51) --------------------------------------------------------
# PV strings pv1..pv8 -> DisplayPropertyUpload (254/21) fields 1476..1483, F32
# watts. These leaf numbers recur inside unrelated nested submessages, so a
# value outside a sane PV range is that reuse leaking through and is rejected.
PV_FIELD_BASE = 1476
PV_STRINGS = 8
PV_MAX_W = 5_500  # per-string MPPT ceiling; anything above is field-reuse noise

# Inverter AC output (PCS total active power), 254/21 field 53, signed
# (negative = production/export).
F_PCS_TOTAL = 53

# Battery power is reported per pack in separate cmdFunc=32 / cmdId=177 frames:
# field 44 = bp_power (W, signed: positive = charging, negative = discharging;
# confirmed vs SoC direction, n=760), field 5 = pack slot index. Power adds
# across packs, so track the last value per slot and sum.
BATTERY_PACK_CMD = (32, 177)  # (cmdFunc, cmdId)
F_BATT_SLOT = 5
F_BATT_PWR = 44
# field 44 usually carries a sane per-pack power (watts), but intermittently
# emits an implausible spike (tens to hundreds of kW for a single pack) that the
# per-slot sum then amplifies. Reject any read beyond a pack's realistic share of
# the inverter's rating (~24 kW / 4 packs, with generous headroom) as decode
# noise, and keep the slot's last good value — same guard used for PV strings.
BATT_PACK_MAX_W = 10_000


def _first_num(fields: FieldMap, no: int) -> float | None:
    """First numeric value of a field regardless of wire type (varint or float)."""
    for wt in (WIRE_F32, WIRE_VARINT, WIRE_F64):
        v = _first(fields, no, wt)
        if v is not None:
            return float(v)
    return None


class OceanPanel(SmartHomePanel3):
    """OCEAN Smart Panel (HR61…, private / app API). Read-only.

    Identical to the Smart Home Panel 3 but with 40 circuits instead of 32; the
    per-circuit array, circuit labels, grid/load flows and SoC are all inherited
    unchanged (only the circuit geometry is overridden).
    """

    CIRCUITS = OCEAN_PANEL_CIRCUITS
    NAME_FIELDS = OCEAN_PANEL_NAME_FIELDS


class OceanProInverter(DeltaPro3):
    """OCEAN Pro inverter (HR51…, private / app API). Read-only.

    Shares the Delta Pro 3 254/21 decode pipeline (and its battery SoC), and
    adds the solar/battery side unique to Ocean Pro: PV strings pv1..pv8, the
    inverter AC output, and pack-reported battery power.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Last-seen battery power per pack slot, summed into total battery power.
        self._pack_pwr: dict[int, float] = {}

    @override
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        out: list[SensorEntity] = [
            # Inverter AC output; sign follows production (negative = export).
            WattsSensorEntity(client, self, "ocean_pcs_pwr", "Inverter Output Power").with_icon("mdi:sine-wave"),
            # Pack-reported battery power (signed: + charge / - discharge).
            WattsSensorEntity(client, self, "ocean_batt_pwr", "Battery Power").with_icon("mdi:home-battery"),
            QuotaStatusSensorEntity(client, self),
        ]
        # PV strings: per-string production power with integrated energy (kWh,
        # total_increasing) for the HA Energy dashboard.
        for i in range(1, PV_STRINGS + 1):
            out.append(SolarPowerSensorEntity(client, self, f"pv{i}_pwr", f"PV{i} Power").with_energy())
        return out

    @override
    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return []

    @override
    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return []

    @override
    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return []

    @override
    def _decode_message_by_type(self, pdata: bytes, header_info: dict[str, Any]) -> dict[str, Any]:
        result = super()._decode_message_by_type(pdata, header_info)
        cmd = (header_info.get("cmdFunc"), header_info.get("cmdId"))
        try:
            if cmd == (254, 21):
                fields = _parse_fields(pdata)
                self._decode_pv(fields, result)
                self._decode_pcs(fields, result)
            elif cmd == BATTERY_PACK_CMD:
                self._decode_battery(_parse_fields(pdata), result)
        except Exception as e:  # reverse-engineered payload; never break the base decode
            _LOGGER.debug("Ocean Pro inverter field parse skipped: %s", e)
        return result

    def _decode_pv(self, fields: FieldMap, result: dict[str, Any]) -> None:
        """Per-string PV production power (pv1..pv8), inverter fields 1476..1483."""
        for i in range(PV_STRINGS):
            v = _first(fields, PV_FIELD_BASE + i, WIRE_F32)
            # Reject field-number reuse from nested submessages (out-of-range).
            if v is not None and 0 <= v <= PV_MAX_W:
                result[f"pv{i + 1}_pwr"] = round(v, 2)

    def _decode_pcs(self, fields: FieldMap, result: dict[str, Any]) -> None:
        """Inverter AC output (PCS total active power), field 53."""
        v = _first(fields, F_PCS_TOTAL, WIRE_F32)
        if v is not None:
            result["ocean_pcs_pwr"] = round(v, 2)

    def _decode_battery(self, fields: FieldMap, result: dict[str, Any]) -> None:
        """Pack-reported battery power, summed across slots (cmdFunc 32 / cmdId 177)."""
        pwr = _first_num(fields, F_BATT_PWR)
        # Missing, or an implausible spike (field-44 decode noise) — keep the
        # last good per-slot values rather than poisoning the sum.
        if pwr is None or abs(pwr) > BATT_PACK_MAX_W:
            return
        slot = _first_num(fields, F_BATT_SLOT)
        self._pack_pwr[int(slot) if slot is not None else 0] = round(pwr, 2)
        result["ocean_batt_pwr"] = round(sum(self._pack_pwr.values()), 2)
