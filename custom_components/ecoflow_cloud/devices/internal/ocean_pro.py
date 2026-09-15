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
import struct
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
    AmpSensorEntity,
    CentivoltSensorEntity,
    FrequencySensorEntity,
    MiscSensorEntity,
    QuotaStatusSensorEntity,
    SolarPowerSensorEntity,
    VoltSensorEntity,
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

# Total solar power, 254/21 field 517 — the inverter's OWN sum of the MPPT strings.
# On the HR51 stream this equals sum(pv1..8) to <0.5% (verified from live captures), so it
# is a faithful mirror of the string sum, not an independent measurement. Mirrored here for
# field-for-field parity with the mini collector (which stores it as `solar_total`).
F_SOLAR_TOTAL = 517
SOLAR_TOTAL_MAX = PV_MAX_W * PV_STRINGS  # 8-string ceiling; above = field-reuse noise

# Per-leg PCS AC telemetry on the SAME 254/21 stream (fields 1463..1468). A/B phase
# assignment is provisional (per the meter-validated fieldmap). Voltage/current are
# positive; per-leg power is signed and follows F_PCS_TOTAL (negative = production/export).
# These leaf numbers recur inside unrelated nested submessages, so out-of-range values
# are that reuse leaking through and are rejected (same guard idea as PV).
PCS_LEG_FIELDS: dict[str, int] = {
    "pcsA_voltage": 1463,
    "pcsA_current": 1464,
    "pcsB_voltage": 1465,
    "pcsB_current": 1466,
    "pcsA_power": 1467,
    "pcsB_power": 1468,
}
PCS_V_MAX = 300.0  # split-phase leg is ~120-125 V; anything above is field-reuse noise
PCS_A_MAX = 300.0  # per-leg current is well under 100 A; guard generously
PCS_P_MAX = 20_000.0  # per-leg magnitude ceiling; abs above this is reuse noise

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

# --- Work mode + battery pack: decoded the mini collector's PROVEN way ------
# Work mode (254/21, decoded on OceanPanel/HR61) and the per-pack scalars (cmdFunc=32/
# cmdId=177, decoded on OceanProInverter/HR51) are read by flattening the WHOLE frame and
# matching the EXACT nested path ``1.1.<field>`` — the same rule the utility-meter-validated
# collector uses — NOT a shallow top-level match on the leaf number. These field numbers are
# small (slot=5, mode=1470) and recur inside unrelated nested submessages, so a top-level-first
# match grabbed the wrong occurrence: it collapsed all packs to one slot (reporting 1 pack, not
# 4). Work mode ALSO must come from the right DEVICE: field 1470 reads a stale self_use (0) on
# the HR51 inverter stream but the real mode (e.g. backup) on the HR61 panel stream — confirmed
# from live captures — so it is decoded on OceanPanel, not here.
# Voltage (field 45) is a real measurement (10 mV/count -> V = /100, ~398 V, matching the
# EF-BP-10 datasheet's 400 V / 380-550 V rating); pack count is a real count. Per-pack
# current (field 43) has an unsettled scale, so it is surfaced RAW (no amp unit), and
# field 44 is the impossible-value field the module note above rejects (battery power is
# derived from PV+PCS instead). The pack stream sends ONE pack per frame, tagged by slot,
# so bank figures accumulate per slot: voltage AVERAGES, current SUMS, packs = slot count.
BATTERY_PACK_CMD = (32, 177)
P_CMDFUNC, P_CMDID = "1.8", "1.9"  # header cmdFunc / cmdId in the flattened frame
P_WORK_MODE = "1.1.1470"  # 254/21: EMS operating mode code
P_BP_SLOT = "1.1.5"  # 32/177: pack slot index
P_BP_VOLTAGE = "1.1.45"  # 32/177: pack voltage, 10 mV/count -> V = /100
P_BP_CURRENT = "1.1.43"  # 32/177: pack current, RAW (scale unsettled)
BP_V_RAW_MIN, BP_V_RAW_MAX = 30_000.0, 60_000.0  # 300-600 V at /100; guard bad frames

# US app work-mode names (field 1470), confirmed via live Self-powered <-> Backup toggles.
WORK_MODE_CODES: dict[int, str] = {
    0: "self_use",  # Self-powered
    1: "time_of_use",
    2: "backup",  # Emergency Backup
    3: "debug",
    4: "ac_makeup",
    5: "drm",
    6: "remote_schedule",
    7: "standby",
    8: "soc_calibration",
    9: "intelligent",  # Intelligent (app)
}

# --- Status frame (254/22): grid metering, DC-bus, fault register ------------
# These ride cmdFunc=254 cmdId=22 (the status frame), NOT the 254/21 telemetry burst that
# _decode_message_by_type consumes via _parse_fields. So they are read from the SAME raw
# frame using the collector's proven full-path flatten (path 1.1.<field>), matched on
# cmdFunc==254 (mirrors the mini collector, which harvests on any cmdFunc=254 frame). The
# range guards reject field-number reuse leaking from nested submessages.
STATUS_CMDFUNC = 254
# key -> (field, min, max). Grid-side metering (per split-phase leg) + DC-bus voltage.
STATUS_GUARDED_FIELDS: dict[str, tuple[int, float, float]] = {
    "grid_freq": (641, 55.0, 65.0),
    "grid_voltage_l1": (643, 100.0, 300.0),
    "grid_voltage_l2": (644, 100.0, 300.0),
    "grid_current_l1": (645, 0.0, 300.0),
    "grid_current_l2": (646, 0.0, 300.0),
    "dc_bus_voltage": (1502, 300.0, 500.0),
    "dc_bus_voltage2": (1503, 300.0, 500.0),
}
# Fault/status register, 8 slots (fields 1512..1519). Baseline 0,0,0,0,0,2,0,2 — a bank of
# per-subsystem err/warn codes (the EU PowerOcean JSON carries the same shape as parallel
# bpErrCode/pcsAcErrCode/mppt*FaultCode fields). No public dictionary maps the code numbers,
# so a nonzero needs EcoFlow to decode. Varints; surfaced as-is (no guard) so a change shows.
FAULT_FIELD_BASE = 1512
FAULT_SLOTS = 8
# Candidate-unknown fields: live-varying but unidentified, collected raw for later ID (they
# feed an "unknown fields" dashboard). The two devices carry different sets on their streams.
INVERTER_UNKNOWN_FIELDS: tuple[int, ...] = (22, 50, 518, 1469, 1472, 1557, 1560, 1682)
PANEL_UNKNOWN_FIELDS: tuple[int, ...] = (
    518, 962, 963, 964, 965, 966, 967, 1227, 1462, 1485, 1486,
)


def _flat_num(flat: dict[str, Any], field: int) -> int | float | None:
    """Read a numeric leaf at the exact nested path 1.1.<field>, or None."""
    v = flat.get(f"1.1.{field}")
    return v if isinstance(v, (int, float)) else None


def _store_raw(params: dict[str, Any], key: str, v: int | float) -> None:
    """Store a numeric field as int when it is one, else a 2-dp float."""
    params[key] = int(v) if isinstance(v, int) else round(float(v), 2)


class OceanPanel(SmartHomePanel3):
    """OCEAN Smart Panel (HR61…, private / app API). Read-only.

    Identical to the Smart Home Panel 3 but with 40 circuits instead of 32; the
    per-circuit array, circuit labels, grid/load flows and SoC are all inherited
    unchanged (only the circuit geometry is overridden).

    Also carries the authoritative EMS work mode (254/21 field 1470): on the panel
    stream it reads the real mode (e.g. backup), whereas the same field on the
    inverter (HR51) stream is a stale default (self_use) — confirmed from live
    captures — so work mode is decoded HERE, not on OceanProInverter.
    """

    CIRCUITS = OCEAN_PANEL_CIRCUITS
    NAME_FIELDS = OCEAN_PANEL_NAME_FIELDS

    @override
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        # EMS operating mode (254/21 field 1470), mapped to the app's mode names.
        # Enabled (diagnostic) — collect-all rule, local patch, not upstreamed to tolwi yet;
        # if/when upstreamed, flip to enabled=False to match tolwi convention.
        return super().sensors(client) + [
            MiscSensorEntity(client, self, "ocean_work_mode", "Work Mode", diagnostic=True).with_icon("mdi:home-lightning-bolt"),
        ] + [
            # Candidate-unknown fields on the panel stream, collected raw for identification.
            MiscSensorEntity(client, self, f"ef_unknown_{f}", f"Unknown 254/{f}", diagnostic=True)
            for f in PANEL_UNKNOWN_FIELDS
        ]

    @override
    def _prepare_data(self, raw_data: bytes) -> dict[str, Any]:
        """Augment the base panel decode with the authoritative EMS work mode.

        Field 1470 is a small number that collides in nested submessages, so it is read
        from the SAME raw frame using the collector's proven full-path flatten (``1.1.1470``),
        not a shallow top-level match — the same rule OceanProInverter uses for its scalars.
        """
        result = super()._prepare_data(raw_data)
        try:
            flat = _pb_flatten(list(_pb_parse(raw_data)))
            if (flat.get(P_CMDFUNC), flat.get(P_CMDID)) == (254, 21):
                v = flat.get(P_WORK_MODE)
                if isinstance(v, (int, float)):
                    # HA reads entity values from result["params"][mqtt_key]; materialise it.
                    result.setdefault("params", {})["ocean_work_mode"] = WORK_MODE_CODES.get(
                        int(v), f"unknown_{int(v)}"
                    )
            # Candidate-unknown fields ride the 254 status frames (any cmdId); collect raw.
            if flat.get(P_CMDFUNC) == STATUS_CMDFUNC:
                params = result.setdefault("params", {})
                for field in PANEL_UNKNOWN_FIELDS:
                    v = _flat_num(flat, field)
                    if v is not None:
                        _store_raw(params, f"ef_unknown_{field}", v)
        except Exception as e:  # reverse-engineered payload; never break the base decode
            _LOGGER.debug("Ocean Panel work-mode decode skipped: %s", e)
        return result


class OceanProInverter(DeltaPro3):
    """OCEAN Pro inverter (HR51…, private / app API). Read-only.

    Shares the Delta Pro 3 254/21 decode pipeline (and its battery SoC), and
    adds the solar/battery side unique to Ocean Pro: PV strings pv1..pv8, the
    inverter AC output, and pack-reported battery power.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Per-slot latest pack readings, keyed by slot index. Each 32/177 frame carries
        # one pack; the bank rollup reads across all slots seen so far.
        self._bp_slots: dict[int, dict[str, float]] = {}

    @override
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        out: list[SensorEntity] = [
            # Inverter AC output; sign follows production (negative = export).
            WattsSensorEntity(client, self, "ocean_pcs_pwr", "Inverter Output Power").with_icon("mdi:sine-wave"),
            # Total solar (254/21 field 517) — the inverter's own sum of the MPPT strings.
            # No energy integration: the per-string PV sensors already feed the Energy dashboard,
            # so integrating this too would double-count. Mirror for parity with the mini.
            SolarPowerSensorEntity(client, self, "ocean_solar_total", "Total Solar").with_icon("mdi:solar-power"),
            # Work mode is NOT read here: field 1470 on the inverter stream is a stale default
            # (self_use). The authoritative EMS mode lives on the HR61 panel stream and is
            # decoded on OceanPanel instead. See that class + the module note.
            # Battery pack bank telemetry (32/177 stream). Voltage is a real measurement;
            # if/when upstreamed, flip these three to enabled=False to match tolwi convention.
            # pack count is a real count; current is raw (scale unsettled — see module note).
            CentivoltSensorEntity(client, self, "bp_voltage_raw", "Battery Pack Voltage", diagnostic=True).with_icon("mdi:home-battery"),
            MiscSensorEntity(client, self, "bp_packs", "Battery Packs Online", diagnostic=True).with_icon("mdi:battery-sync"),
            MiscSensorEntity(client, self, "bp_current_raw", "Battery Pack Current (raw)", diagnostic=True).with_icon("mdi:current-dc"),
            # Battery power, derived from PV + PCS on the 254/21 stream (signed:
            # + charge / - discharge). See the module note on why field 44 is not used.
            WattsSensorEntity(client, self, "ocean_batt_pwr", "Battery Power").with_icon("mdi:home-battery"),
            # Per-leg AC (PCS phase A/B): voltage, current and active power. Same 254/21
            # stream as PV/PCS-total; not exposed by upstream — the split-phase grid
            # voltage HA otherwise lacks entirely.
            VoltSensorEntity(client, self, "pcsA_voltage", "PCS Phase A Voltage").with_icon("mdi:sine-wave"),
            AmpSensorEntity(client, self, "pcsA_current", "PCS Phase A Current"),
            WattsSensorEntity(client, self, "pcsA_power", "PCS Phase A Power").with_icon("mdi:sine-wave"),
            VoltSensorEntity(client, self, "pcsB_voltage", "PCS Phase B Voltage").with_icon("mdi:sine-wave"),
            AmpSensorEntity(client, self, "pcsB_current", "PCS Phase B Current"),
            WattsSensorEntity(client, self, "pcsB_power", "PCS Phase B Power").with_icon("mdi:sine-wave"),
            QuotaStatusSensorEntity(client, self),
        ]
        # Grid-side metering (254/22 status frame): frequency + per-leg voltage/current.
        # Distinct from the PCS/inverter-output legs above — this is the grid connection.
        out += [
            FrequencySensorEntity(client, self, "grid_freq", "Grid Frequency"),
            VoltSensorEntity(client, self, "grid_voltage_l1", "Grid Voltage L1").with_icon("mdi:sine-wave"),
            VoltSensorEntity(client, self, "grid_voltage_l2", "Grid Voltage L2").with_icon("mdi:sine-wave"),
            AmpSensorEntity(client, self, "grid_current_l1", "Grid Current L1"),
            AmpSensorEntity(client, self, "grid_current_l2", "Grid Current L2"),
            # DC-bus (DC-link) voltage — diagnostic; boosted ~5 V above battery terminal.
            VoltSensorEntity(client, self, "dc_bus_voltage", "DC Bus Voltage", diagnostic=True).with_icon("mdi:current-dc"),
            VoltSensorEntity(client, self, "dc_bus_voltage2", "DC Bus Voltage 2", diagnostic=True).with_icon("mdi:current-dc"),
        ]
        # Fault/status register — 8 per-subsystem err/warn slots. No public code dictionary
        # exists, so a nonzero value needs EcoFlow to decode. Diagnostic.
        out += [
            MiscSensorEntity(client, self, f"fault_{FAULT_FIELD_BASE + i}", f"Fault Reg {i}", diagnostic=True).with_icon("mdi:alert-circle-outline")
            for i in range(FAULT_SLOTS)
        ]
        # Candidate-unknown fields on the inverter stream, collected raw for identification.
        out += [
            MiscSensorEntity(client, self, f"ef_unknown_{f}", f"Unknown 254/{f}", diagnostic=True)
            for f in INVERTER_UNKNOWN_FIELDS
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
    def _prepare_data(self, raw_data: bytes) -> dict[str, Any]:
        """Augment the base decode with battery-pack bank telemetry.

        The per-pack scalars live at nested paths that a shallow top-level parse mis-reads
        (small field numbers collide), so they are read here from the SAME raw frame the base
        pipeline consumes, using the collector's proven full-path flatten (``1.1.<field>``).
        Everything else — PV, PCS, total solar, derived battery power — is decoded in
        ``_decode_message_by_type`` on the base's extracted pdata as before. (Work mode is
        decoded on OceanPanel/HR61, where field 1470 is authoritative.)
        """
        result = super()._prepare_data(raw_data)
        try:
            flat = _pb_flatten(list(_pb_parse(raw_data)))
            # Work mode is decoded on OceanPanel (HR61), where field 1470 is authoritative;
            # this inverter stream carries only the per-pack bank telemetry.
            if (flat.get(P_CMDFUNC), flat.get(P_CMDID)) == BATTERY_PACK_CMD:
                # HA reads entity values from result["params"][mqtt_key]; a pack-only frame
                # makes the base return {}, so materialise "params" before writing into it.
                self._decode_battery_pack(flat, result.setdefault("params", {}))
            # Grid metering, DC-bus and the fault register ride the 254 status frame(s),
            # not the 254/21 telemetry burst; read them here from the same flattened frame.
            if flat.get(P_CMDFUNC) == STATUS_CMDFUNC:
                self._decode_status_fields(flat, result.setdefault("params", {}))
        except Exception as e:  # reverse-engineered payload; never break the base decode
            _LOGGER.debug("Ocean Pro raw-frame decode skipped: %s", e)
        return result

    def _decode_status_fields(self, flat: dict[str, Any], params: dict[str, Any]) -> None:
        """Grid metering + DC-bus + fault register from a 254 status frame (path 1.1.<field>).

        Grid/DC-bus values are range-guarded to reject field-number reuse from nested
        submessages; the fault register and candidate-unknown fields are surfaced raw so a
        change is always visible.
        """
        for key, (field, lo, hi) in STATUS_GUARDED_FIELDS.items():
            v = _flat_num(flat, field)
            if v is not None and lo <= v <= hi:
                params[key] = round(float(v), 2)
        for i in range(FAULT_SLOTS):
            v = _flat_num(flat, FAULT_FIELD_BASE + i)
            if v is not None:
                params[f"fault_{FAULT_FIELD_BASE + i}"] = int(v)
        for field in INVERTER_UNKNOWN_FIELDS:
            v = _flat_num(flat, field)
            if v is not None:
                _store_raw(params, f"ef_unknown_{field}", v)

    @override
    def _decode_message_by_type(self, pdata: bytes, header_info: dict[str, Any]) -> dict[str, Any]:
        result = super()._decode_message_by_type(pdata, header_info)
        cmd = (header_info.get("cmdFunc"), header_info.get("cmdId"))
        try:
            if cmd == (254, 21):
                fields = _parse_fields(pdata)
                self._decode_pv(fields, result)
                self._decode_pcs(fields, result)
                self._decode_solar_total(fields, result)
                self._decode_pcs_legs(fields, result)
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

    def _decode_solar_total(self, fields: FieldMap, result: dict[str, Any]) -> None:
        """Total solar power (field 517) — the inverter's own sum of the MPPT strings.

        Range-guarded like PV to reject field-number reuse from nested submessages.
        """
        v = _first(fields, F_SOLAR_TOTAL, WIRE_F32)
        if v is not None and 0 <= v <= SOLAR_TOTAL_MAX:
            result["ocean_solar_total"] = round(v, 2)

    def _decode_pcs_legs(self, fields: FieldMap, result: dict[str, Any]) -> None:
        """Per-leg PCS AC voltage/current/power (fields 1463..1468).

        Same 254/21 stream and F32 wire type as PV/PCS-total. Voltage and current are
        positive; per-leg power is signed (negative = production/export). Range guards
        reject the same field-number reuse from nested submessages that PV guards against.
        """
        for key, fnum in PCS_LEG_FIELDS.items():
            v = _first(fields, fnum, WIRE_F32)
            if v is None:
                continue
            if key.endswith("_voltage") and not (0 <= v <= PCS_V_MAX):
                continue
            if key.endswith("_current") and not (0 <= v <= PCS_A_MAX):
                continue
            if key.endswith("_power") and abs(v) > PCS_P_MAX:
                continue
            result[key] = round(v, 2)

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

    def _decode_battery_pack(self, flat: dict[str, Any], params: dict[str, Any]) -> None:
        """Bank rollup from the per-pack 32/177 stream (one pack per frame).

        Voltage averages across paralleled packs; current sums; pack count = distinct
        slots seen. Each frame carries a single pack (path 1.1.5 = slot), so the running
        per-slot state (self._bp_slots) is what the bank figures read across.
        """
        slot = flat.get(P_BP_SLOT)
        slot = int(slot) if isinstance(slot, (int, float)) else 0
        pack = self._bp_slots.setdefault(slot, {})

        volt = flat.get(P_BP_VOLTAGE)
        if isinstance(volt, (int, float)) and BP_V_RAW_MIN <= volt <= BP_V_RAW_MAX:
            pack["v"] = float(volt)  # raw counts; CentivoltSensor renders /100 = V
        amp = flat.get(P_BP_CURRENT)
        if isinstance(amp, (int, float)):
            pack["a"] = float(amp)  # raw; scale unsettled

        volts = [p["v"] for p in self._bp_slots.values() if "v" in p]
        if volts:
            params["bp_voltage_raw"] = round(sum(volts) / len(volts), 1)
        amps = [p["a"] for p in self._bp_slots.values() if "a" in p]
        if amps:
            params["bp_current_raw"] = round(sum(amps), 1)
        params["bp_packs"] = len(self._bp_slots)


# --- Protobuf full-path decoder, copied verbatim from the collector's protodump ---------
# Kept byte-for-byte identical to the utility-meter-validated mini collector so work mode
# and the pack scalars decode to the same values the collector records. Reads a frame into
# field-path -> value, recursing into submessages; F32/F64 surface as their float.
def _pb_read_varint(buf: bytes, pos: int) -> tuple[int, int]:
    result = shift = 0
    while pos < len(buf):
        byte = buf[pos]
        result |= (byte & 0x7F) << shift
        pos += 1
        if not byte & 0x80:
            return result, pos
        shift += 7
        if shift > 63:
            break
    raise ValueError("varint overrun")


def _pb_looks_like_message(buf: bytes) -> bool:
    try:
        return bool(list(_pb_parse(buf, depth=0, probe=True)))
    except (ValueError, IndexError, struct.error):
        return False


def _pb_parse(buf: bytes, depth: int = 0, probe: bool = False):
    """Yield (field, wire, value); recurse into submessages (mirrors protodump.parse)."""
    pos = 0
    while pos < len(buf):
        key, pos = _pb_read_varint(buf, pos)
        field, wire = key >> 3, key & 0x07
        if field == 0:
            raise ValueError("field 0")
        value: Any  # varint int | wire-1/5 dict | submessage list | bytes | str
        if wire == 0:
            value, pos = _pb_read_varint(buf, pos)
        elif wire == 1:
            if pos + 8 > len(buf):
                raise ValueError("truncated 64-bit")
            raw = buf[pos : pos + 8]
            value = {"u64": struct.unpack("<Q", raw)[0], "f64": struct.unpack("<d", raw)[0]}
            pos += 8
        elif wire == 2:
            length, pos = _pb_read_varint(buf, pos)
            if pos + length > len(buf):
                raise ValueError("truncated bytes")
            raw = buf[pos : pos + length]
            pos += length
            if probe:
                value = raw
            elif depth < 6 and length and _pb_looks_like_message(raw):
                value = list(_pb_parse(raw, depth + 1))
            else:
                try:
                    text = raw.decode("ascii")
                    value = text if text.isprintable() else raw.hex()
                except UnicodeDecodeError:
                    value = raw.hex()
        elif wire == 5:
            if pos + 4 > len(buf):
                raise ValueError("truncated 32-bit")
            raw = buf[pos : pos + 4]
            value = {"u32": struct.unpack("<I", raw)[0], "f32": round(struct.unpack("<f", raw)[0], 4)}
            pos += 4
        else:
            raise ValueError(f"bad wire type {wire}")
        yield field, wire, value


def _pb_flatten(items, prefix: str = "") -> dict[str, Any]:
    """field-path -> value (F32/F64 as their float). Mirrors protodump.flatten_paths."""
    out: dict[str, Any] = {}
    for field, _wire, value in items:
        path = f"{prefix}.{field}" if prefix else str(field)
        if isinstance(value, list):
            out.update(_pb_flatten(value, path))
        elif isinstance(value, dict):
            out[path] = value.get("f32", value.get("f64"))
        else:
            out[path] = value
    return out
