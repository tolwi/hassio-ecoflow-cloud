import logging
from typing import Any, override

from homeassistant.components.sensor import SensorEntity

from custom_components.ecoflow_cloud.api import EcoflowApiClient
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
    SolarPowerSensorEntity,
    WattsSensorEntity,
)

_LOGGER = logging.getLogger(__name__)

# Ocean Pro drives an OCEAN Smart Panel with 40 monitored load circuits — the
# SHP3 layout widened by 8. The per-circuit array (DisplayPropertyUpload
# 254/21, fields 1015..1054, one submessage {1: volt, 2: watt, 3: amp}), the
# aggregate flows and the SoC (DP3 field 262 -> cms_batt_soc) are all inherited
# from SmartHomePanel3 unchanged.
OCEAN_PRO_CIRCUITS = 40

# Circuit label / split-phase metadata blocks. SHP3 carries 32 labels across
# fields 794..805 + 920..939. The fields the extra 8 Ocean Pro labels arrive on
# are not yet confirmed from a live capture; the second block is extended by 8
# (920..947) as a working assumption. Unconfirmed labels simply fall back to
# "Circuit N", so a wrong guess here is cosmetic, never a decode failure.
# TODO(capture): confirm the name-field block for circuits 33..40.
OCEAN_PRO_NAME_FIELDS = list(range(794, 806)) + list(range(920, 948))

# Inverter PV strings pv1..pv8 -> DisplayPropertyUpload fields 1476..1483, F32
# watts at the top level of the 254/21 payload. These leaf numbers recur inside
# unrelated nested submessages, so a value outside a sane PV range is that reuse
# leaking through and is rejected (this is the pv6 ~1e23 decode fix).
PV_FIELD_BASE = 1476
PV_STRINGS = 8
PV_MAX_W = 5_500  # per-string MPPT ceiling; anything above is field-reuse noise

# Battery power is NOT in the 254/21 stream. It is reported per pack in separate
# cmdFunc=32 / cmdId=177 frames: field 44 = bp_power (W, signed: positive =
# charging, negative = discharging; confirmed 2026-08-14 vs SoC direction,
# n=760), field 5 = pack slot index. Power adds across packs, so track the last
# value per slot and sum. (SHP3's inherited shp_batt_pwr = load - grid remains
# as the derived cross-check.)
BATTERY_PACK_CMD = (32, 177)  # (cmdFunc, cmdId)
F_BATT_SLOT = 5
F_BATT_PWR = 44


def _first_num(fields: FieldMap, no: int) -> float | None:
    """First numeric value of a field regardless of wire type (varint or float).

    The pack-frame scalars are plain numbers whose wire type isn't pinned from
    captures, so accept any of varint / f32 / f64 rather than guess one.
    """
    for wt in (WIRE_F32, WIRE_VARINT, WIRE_F64):
        v = _first(fields, no, wt)
        if v is not None:
            return float(v)
    return None


class OceanPro(SmartHomePanel3):
    """EcoFlow Ocean Pro (OCEAN Smart Panel + OCEAN Pro inverter, private / app API).

    Ocean Pro speaks the same DP3 / SHP3 protobuf dialect as the Smart Home
    Panel 3 (DisplayPropertyUpload = cmdFunc 254 / cmdId 21), so the SHP3 decode
    pipeline — flows, the per-circuit array, circuit-label metadata, split-phase
    folding, SoC — is inherited wholesale. Ocean Pro adds the solar/inverter
    side SHP3 has no notion of: PV strings pv1..pv8 and real (pack-reported)
    battery power.

    Read-only: sensors only, no control entities.
    """

    CIRCUITS = OCEAN_PRO_CIRCUITS
    NAME_FIELDS = OCEAN_PRO_NAME_FIELDS

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Last-seen battery power per pack slot, summed into total battery power.
        self._pack_pwr: dict[int, float] = {}

    @override
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        # SHP3's set already covers the 40 circuits (via CIRCUITS above), the
        # grid/load flows, derived storage power and SoC.
        out = super().sensors(client)
        # PV strings: per-string production power with integrated energy (kWh,
        # total_increasing) for the HA Energy dashboard.
        for i in range(1, PV_STRINGS + 1):
            out.append(
                SolarPowerSensorEntity(client, self, f"pv{i}_pwr", f"PV{i} Power").with_energy()
            )
        # Battery power straight from the packs (signed: + charge / - discharge),
        # alongside SHP3's derived shp_batt_pwr.
        out.append(
            WattsSensorEntity(client, self, "ocean_batt_pwr", "Battery Power").with_icon("mdi:home-battery")
        )
        return out

    @override
    def _decode_message_by_type(self, pdata: bytes, header_info: dict[str, Any]) -> dict[str, Any]:
        result = super()._decode_message_by_type(pdata, header_info)
        cmd = (header_info.get("cmdFunc"), header_info.get("cmdId"))
        try:
            if cmd == (254, 21):
                self._decode_pv(_parse_fields(pdata), result)
            elif cmd == BATTERY_PACK_CMD:
                self._decode_battery(_parse_fields(pdata), result)
        except Exception as e:  # reverse-engineered payload; never break the base decode
            _LOGGER.debug("Ocean Pro field parse skipped: %s", e)
        return result

    def _decode_pv(self, fields: FieldMap, result: dict[str, Any]) -> None:
        """Per-string PV production power (pv1..pv8), inverter fields 1476..1483."""
        for i in range(PV_STRINGS):
            v = _first(fields, PV_FIELD_BASE + i, WIRE_F32)
            # Reject field-number reuse from nested submessages (out-of-range).
            if v is not None and 0 <= v <= PV_MAX_W:
                result[f"pv{i + 1}_pwr"] = round(v, 2)

    def _decode_battery(self, fields: FieldMap, result: dict[str, Any]) -> None:
        """Pack-reported battery power, summed across slots (cmdFunc 32 / cmdId 177)."""
        pwr = _first_num(fields, F_BATT_PWR)
        if pwr is None:
            return
        slot = _first_num(fields, F_BATT_SLOT)
        self._pack_pwr[int(slot) if slot is not None else 0] = round(pwr, 2)
        result["ocean_batt_pwr"] = round(sum(self._pack_pwr.values()), 2)
