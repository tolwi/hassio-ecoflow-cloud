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

# Battery power is NOT read from per-pack field 44 (cmdFunc=32 / cmdId=177). That field
# decodes to physically impossible values while charging — ~122 kW per pack and ~15 kA of
# current, scaling with the pack count — so summing it per slot reported hundreds of kW.
# A plausibility clamp on field 44 only turned the garbage into a *frozen* sensor: with
# every charge frame rejected, Battery Power held its last discharge value for the entire
# charge. Instead derive it from the reliable 254/21 stream by the DC-bus power balance:
#
#     battery power (+ = charge) = sum(pv1..pv8) + PCS total
#
# with PCS in its native sign (negative = production/export). Verified against a night
# grid-charge (PV 0, PCS +20.7 kW -> +20.7 kW charge, matching grid 29.2 - home 8.6 kW)
# and idle (-> 0). This is DC-bus power, so it reads a few % high vs true pack terminal
# power (it ignores conversion loss) — an acceptable trade for a fresh, non-freezing value
# that tracks SoC through a charge instead of freezing on it.


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

    @override
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        out: list[SensorEntity] = [
            # Inverter AC output; sign follows production (negative = export).
            WattsSensorEntity(client, self, "ocean_pcs_pwr", "Inverter Output Power").with_icon("mdi:sine-wave"),
            # Battery power, derived from PV + PCS on the 254/21 stream (signed:
            # + charge / - discharge). See the module note on why field 44 is not used.
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
                self._derive_battery_power(result)
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

    def _derive_battery_power(self, result: dict[str, Any]) -> None:
        """Battery power from the DC-bus balance: sum(pv1..pv8) + PCS total.

        + = charging, - = discharging. Computed from this 254/21 frame's own PV and
        PCS values (not persisted), so it is correctly PV=0 at night — the PV fields
        are simply absent then — instead of holding a stale daytime sum. Requires PCS;
        if the frame carried no PCS reading, leave the previous value untouched.
        """
        pcs = result.get("ocean_pcs_pwr")
        if pcs is None:
            return
        solar_in = sum(
            result[f"pv{i}_pwr"]
            for i in range(1, PV_STRINGS + 1)
            if result.get(f"pv{i}_pwr")
        )
        result["ocean_batt_pwr"] = round(solar_in + pcs, 2)
