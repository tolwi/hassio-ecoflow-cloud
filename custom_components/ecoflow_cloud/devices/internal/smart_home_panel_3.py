import asyncio
import logging
import struct
import time
from typing import TYPE_CHECKING, Any, Self, override

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.binary_sensor import MiscBinarySensorEntity
from custom_components.ecoflow_cloud.devices import const
from custom_components.ecoflow_cloud.devices.internal.delta_pro_3 import DeltaPro3
from custom_components.ecoflow_cloud.devices.public.delta3_max_plus import Delta3ChargingStateSensorEntity
from custom_components.ecoflow_cloud.sensor import (
    AmpSensorEntity,
    BatteryLimitSensorEntity,
    InAmpSensorEntity,
    InVoltSensorEntity,
    InWattsSensorEntity,
    LevelSensorEntity,
    MiscSensorEntity,
    QuotaStatusSensorEntity,
    VoltSensorEntity,
    WattsSensorEntity,
)

_LOGGER = logging.getLogger(__name__)

# DisplayPropertyUpload (cmdFunc 254 / cmdId 21) per-circuit array: fields
# 1015.., one submessage per circuit {1: volt, 2: watt (signed), 3: amp}.
# These fields are absent from the DP3 proto (dropped on ParseFromString),
# so they are recovered with a second raw pass over the payload.
# The circuit count, name-field blocks and array base are class attributes on
# SmartHomePanel3 (below) so wider variants (e.g. Ocean Pro, 40 circuits) can
# extend this device by overriding them rather than duplicating the decoders.
# Aggregate flow and grid per-leg fields (float, wiretype 5).
F_GRID_PWR = 515
F_LOAD_PWR = 516
F_GRID_L1_PWR, F_GRID_L2_PWR = 962, 963
F_L1_VOL, F_L2_VOL = 956, 957
F_GRID_L1_AMP, F_GRID_L2_AMP = 958, 959
# Panel state, sent only in the 120 s full frames. Names and meanings follow
# the SHP3 schema in rabits/ha-ef-ble (dev_apl_comm), which agrees with
# 1RadMan/ecoflow-cloud-dpu-extra. 619, 461, 270, 467 and 282 travel in one
# frame, 752, 806, 1244 and 1245 in another; 282 also comes in the 2 s frames
# when it changes.
F_GRID_STA = 619  # grid_connection_sta: 1 grid in, 2 offline, 3 feeding
F_GRID_ENERGIZED = 752
F_BACKUP_RESERVE = 461  # %
F_MAX_CHG_SOC = 270  # cms_max_chg_soc, %: the app's charge limit
F_NICE_TO_HAVE_SOC = 806  # mid_priority_discharge_low, %: Nice to Have circuits shed below it
F_STORM_GUARD = 467  # storm_pattern_enable
F_CHG_DSG_STATE = 282  # cms_chg_dsg_state: 0 idle, 1 discharging, 2 charging
F_CHARGE_LIMIT = 1244  # W
F_PANEL_MODE = 1245  # submessage of mode flags, see PANEL_MODES
# Operating-mode flag sub-fields of 1245; none set means Backup. Sub-field 4
# (EPS) is a separate flag that combines with any of them.
PANEL_MODES = {1: "self_powered", 2: "scheduled", 3: "tou", 5: "mix_scheduled", 6: "intelligent"}
PANEL_MODE_EPS = 4
GRID_STA_ON = {1: True, 2: False, 3: True}
# 2.5 full-frame periods: one lost frame is tolerated, a dead stream is not.
PANEL_STATE_STALE_S = 300

# Protobuf wire types (as tagged by _parse_fields).
WIRE_VARINT = 0
WIRE_F64 = 1
WIRE_LEN = 2
WIRE_F32 = 5

# proto3 omits a scalar field whose value is 0, and the coordinator merges
# each frame's params cumulatively — so a key that is simply not written
# keeps its previous (stale) value. For bimodal fields that feed energy
# integration (per-circuit watts, grid import) an omitted value means 0,
# not "unchanged", and must be written explicitly; anything sampled sparsely
# must instead be skipped when absent. _decode_flows / _decode_circuits
# apply this distinction per field.

FieldMap = dict[int, list[tuple[int, Any]]]


def _read_varint(b: bytes, i: int) -> tuple[int, int]:
    r = s = 0
    while True:
        x = b[i]
        i += 1
        r |= (x & 0x7F) << s
        s += 7
        if not x & 0x80:
            return r, i


def _parse_fields(b: bytes) -> FieldMap:
    """Minimal protobuf reader: {field_no: [(wire_type, value), ...]}."""
    i, n = 0, len(b)
    out: FieldMap = {}
    while i < n:
        try:
            tag, i = _read_varint(b, i)
            fn, wt = tag >> 3, tag & 7
            v: Any
            if wt == WIRE_VARINT:
                v, i = _read_varint(b, i)
            elif wt == WIRE_LEN:
                ln, i = _read_varint(b, i)
                v, i = b[i : i + ln], i + ln
            elif wt == WIRE_F32:
                v, i = struct.unpack("<f", b[i : i + 4])[0], i + 4
            elif wt == WIRE_F64:
                v, i = struct.unpack("<d", b[i : i + 8])[0], i + 8
            else:
                break
        except (IndexError, struct.error):
            break
        out.setdefault(fn, []).append((wt, v))
    return out


def _first(fields: FieldMap, no: int, wire_type: int) -> Any | None:
    """First value of a field, or None if absent or of another wire type."""
    vals = fields.get(no)
    return vals[0][1] if vals and vals[0][0] == wire_type else None


if TYPE_CHECKING:
    from custom_components.ecoflow_cloud.entities import BaseSensorEntity, EcoFlowDictEntity

    _CircuitNamedBase = BaseSensorEntity
    _PanelStateBase = EcoFlowDictEntity
else:
    _CircuitNamedBase = object
    _PanelStateBase = object


class _CircuitNamed(_CircuitNamedBase):
    """Mixin: name a per-circuit entity from the device-provided circuit label.

    The SHP3 streams circuit labels (`ch_N_name`) over the first ~minute,
    after the entities are built. The name is derived live from coordinator
    params (single source of truth, so an app-side rename is picked up too),
    falling back to the original "Circuit N …" title until the label arrives.
    """

    def for_circuit(self, n: int, suffix: str) -> Self:
        self._circuit_no = n
        self._circuit_suffix = suffix
        return self

    def _circuit_name(self) -> str:
        data = getattr(self._device, "data", None)
        params = data.params if data is not None else {}
        label = params.get(f"ch_{self._circuit_no}_name")
        if not label:
            return self._attr_name
        partner = params.get(f"ch_{self._circuit_no}_partner")
        if partner:
            # Primary leg carries the combined 240V load; the secondary reads 0.
            label += " (240V L2)" if partner < self._circuit_no else " (240V)"
        return f"{label} {self._circuit_suffix}"

    @property
    def name(self) -> str:
        return self._circuit_name()

    def title(self) -> str:
        return self._circuit_name()

    def _updated(self, data: dict[str, Any]) -> None:
        super()._updated(data)  # type: ignore[misc]
        # The base class only writes state when the value changes, so a
        # circuit holding a steady value (idle at 0 W, a flat 10 A) would keep
        # its old name forever. Write whenever the name itself changes: the
        # label first streaming in, or an app-side rename later on.
        name = self._circuit_name()
        if name != getattr(self, "_written_name", None):
            self._written_name = name
            if getattr(self, "hass", None) is not None:
                self.schedule_update_ha_state()


class NamedCircuitWatts(_CircuitNamed, WattsSensorEntity):
    pass


class NamedCircuitVolt(_CircuitNamed, VoltSensorEntity):
    pass


class NamedCircuitAmp(_CircuitNamed, AmpSensorEntity):
    pass


class _PanelState(_PanelStateBase):
    """Mixin: unavailable once the panel-state value is PANEL_STATE_STALE_S old.

    These values arrive only in the 120 s full frames and hold in between, so
    without this a lost frame stream would show the last value indefinitely.
    """

    @property
    def available(self) -> bool:
        seen = getattr(self._device, "panel_state_seen", {}).get(self.mqtt_key)
        fresh = seen is not None and time.monotonic() - seen < PANEL_STATE_STALE_S
        return super().available and fresh

    def _handle_coordinator_update(self) -> None:
        super()._handle_coordinator_update()  # type: ignore[misc]
        # The base class writes state only on a new value; going stale is not one.
        available = self.available
        if available != getattr(self, "_written_available", None):
            self._written_available = available
            self.schedule_update_ha_state()


class PanelStateBinarySensorEntity(_PanelState, MiscBinarySensorEntity):
    pass


class PanelLimitSensorEntity(_PanelState, BatteryLimitSensorEntity):
    pass


class PanelChargingStateSensorEntity(_PanelState, Delta3ChargingStateSensorEntity):  # type: ignore[misc]
    pass


class GridStatusBinarySensorEntity(_PanelState, MiscBinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.POWER

    def _update_value(self, val: Any) -> bool:
        # 0 (no valid status) and unknown codes read as unknown, not "off".
        self._attr_is_on = GRID_STA_ON.get(val)
        return True


class ChargeLimitSensorEntity(_PanelState, MiscSensorEntity):  # type: ignore[misc]
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT


class PanelModeSensorEntity(_PanelState, MiscSensorEntity):  # type: ignore[misc]
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["backup", *PANEL_MODES.values()]


class SmartHomePanel3(DeltaPro3):
    """EcoFlow Smart Home Panel 3 (private / app API).

    The SHP3 speaks the Delta Pro 3 protobuf dialect (same header, same
    cmdFunc/cmdId routing, DisplayPropertyUpload = 254/21), so the DP3 decode
    pipeline is inherited unchanged. The SHP-specific data — a 32-circuit
    load array plus aggregate flow powers — lives in fields the DP3 proto
    doesn't declare, so it is recovered with a second raw pass per frame.
    Read-only: no control entities until actuation is deliberately in scope.

    Circuit geometry is expressed as class attributes so wider panels (e.g.
    Ocean Pro, 40 circuits) can subclass and override without touching the
    decoders.
    """

    # SHP3 has 32 monitored load circuits.
    CIRCUITS = 32
    # Circuit metadata submessages (sub-field 5 = the app's circuit label,
    # sub-field 2 = split-phase link) in two field blocks, in the same order as
    # the power array: circuit N (1-based) -> NAME_FIELDS[N - 1].
    NAME_FIELDS = list(range(794, 806)) + list(range(920, 940))
    # Per-circuit array base field in DisplayPropertyUpload (254/21).
    CIRCUIT_FIELD_BASE = 1015

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Circuit metadata (label, 240V partner), keyed by circuit number.
        self._meta: dict[int, dict[str, Any]] = {}
        # Last-seen grid/load pair, carried across frames that omit the group.
        self._flows: dict[str, float] = {}
        # Panel-state key -> monotonic time it was last decoded (see _PanelState).
        self.panel_state_seen: dict[str, float] = {}

    @override
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        out: list[SensorEntity] = [
            # Battery SoC — DP3 field 262 (cms_batt_soc), decodes via the parent.
            LevelSensorEntity(client, self, "cms_batt_soc", const.COMBINED_BATTERY_LEVEL),
            # The three headline flows, with integrated energy (kWh,
            # total_increasing) for the HA Energy dashboard.
            WattsSensorEntity(client, self, "shp_load_pwr", "Home Load Power")
            .with_icon("mdi:home-lightning-bolt")
            .with_energy(),
            InWattsSensorEntity(client, self, "shp_grid_pwr", "Grid Power").with_energy(),
            # "Storage" = EcoFlow's term for the non-grid source (battery, and
            # any generator on the connection box), which is what load - grid
            # measures.
            WattsSensorEntity(client, self, "shp_batt_pwr", "Storage Output Power").with_icon("mdi:home-battery"),
            QuotaStatusSensorEntity(client, self),
            # Grid-side per-leg detail — disabled by default, diagnostic.
            InWattsSensorEntity(client, self, "shp_grid_l1_pwr", "Grid L1 Power", False, diagnostic=True),
            InWattsSensorEntity(client, self, "shp_grid_l2_pwr", "Grid L2 Power", False, diagnostic=True),
            InVoltSensorEntity(client, self, "shp_l1_vol", "Grid L1 Voltage", False, diagnostic=True),
            InVoltSensorEntity(client, self, "shp_l2_vol", "Grid L2 Voltage", False, diagnostic=True),
            InAmpSensorEntity(client, self, "shp_grid_l1_amp", "Grid L1 Current", False, diagnostic=True),
            InAmpSensorEntity(client, self, "shp_grid_l2_amp", "Grid L2 Current", False, diagnostic=True),
            # Panel settings, read-only. Updated every 120 s (full frame).
            PanelLimitSensorEntity(client, self, "shp_backup_reserve", "Backup Reserve"),
            PanelLimitSensorEntity(client, self, "shp_max_chg_soc", "Charge Limit"),
            PanelLimitSensorEntity(
                client, self, "shp_nice_to_have_soc", "Nice to Have Threshold", False, diagnostic=True
            ),
            PanelChargingStateSensorEntity(client, self, "shp_chg_dsg_state", const.BATTERY_CHARGING_STATE),
            PanelModeSensorEntity(client, self, "shp_panel_mode", "Operating Mode", diagnostic=False),
            ChargeLimitSensorEntity(client, self, "shp_charge_limit", "Charge Power Limit", False),
        ]
        # Per-circuit sensors: power enabled with an integrated-energy
        # companion (kWh) for the Energy dashboard; volt/amp disabled by
        # default. Titles use the device-provided circuit label once it has
        # been seen (persisted across restarts), falling back to "Circuit N".
        data = getattr(self, "data", None)
        params = data.params if data is not None else {}

        def circuit_label(n: int) -> str:
            return params.get(f"ch_{n}_name") or f"Circuit {n}"

        for n in range(1, self.CIRCUITS + 1):
            label = circuit_label(n)
            out.append(
                NamedCircuitWatts(client, self, f"ch_{n}_pwr", f"{label} Power").for_circuit(n, "Power").with_energy()
            )
            out.append(
                NamedCircuitVolt(client, self, f"ch_{n}_vol", f"{label} Voltage", False, diagnostic=True).for_circuit(
                    n, "Voltage"
                )
            )
            out.append(
                NamedCircuitAmp(client, self, f"ch_{n}_amp", f"{label} Current", False, diagnostic=True).for_circuit(
                    n, "Current"
                )
            )
        return out

    @override
    def binary_sensors(self, client: EcoflowApiClient) -> list[BinarySensorEntity]:
        return [
            GridStatusBinarySensorEntity(client, self, "shp_grid_sta", "Grid"),
            PanelStateBinarySensorEntity(client, self, "shp_grid_energized", "Grid Energized").with_device_class(
                "power"
            ),
            PanelStateBinarySensorEntity(client, self, "shp_eps_mode", "EPS Mode", False, diagnostic=True),
            PanelStateBinarySensorEntity(client, self, "shp_storm_guard", "Storm Guard", False, diagnostic=True),
        ]

    @override
    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return []

    @override
    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return []

    @override
    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return []

    def configure(self, hass: HomeAssistant) -> None:
        super().configure(hass)
        self._hass = hass
        self._store: Store[dict] = Store(hass, 1, f"ecoflow_cloud.{self.device_info.sn}.circuit_names")

    async def async_restore_state(self) -> None:
        # Load persisted circuit labels before entities are built, so names
        # are correct immediately after a restart/reload instead of showing
        # "Circuit N" until the panel re-streams its metadata.
        data = await self._store.async_load()
        if data:
            self._meta = {int(n): m for n, m in data.items()}
            self._publish_meta(self.data.params)

    def _publish_meta(self, result: dict[str, Any]) -> None:
        for n, m in self._meta.items():
            if "name" in m:
                result[f"ch_{n}_name"] = m["name"]
            if "partner" in m:
                result[f"ch_{n}_partner"] = m["partner"]

    def _save_meta(self) -> None:
        # Decode runs on the MQTT client thread; hop to the event loop to
        # write the Store.
        asyncio.run_coroutine_threadsafe(
            self._store.async_save({str(n): m for n, m in self._meta.items()}),
            self._hass.loop,
        )

    @override
    def _decode_message_by_type(self, pdata: bytes, header_info: dict[str, Any]) -> dict[str, Any]:
        result = super()._decode_message_by_type(pdata, header_info)
        # Only DisplayPropertyUpload (254/21) carries the SHP-specific fields.
        if header_info.get("cmdFunc") == 254 and header_info.get("cmdId") == 21:
            try:
                fields = _parse_fields(pdata)
                self._decode_flows(fields, result)
                self._decode_panel_state(fields, result)
                self._decode_circuits(fields, result)
                self._decode_metadata(fields, result)
                self._combine_split_phase(result)
            except Exception as e:  # reverse-engineered payload; never break the DP3 decode
                _LOGGER.debug("SHP3 field parse skipped: %s", e)
        return result

    def _decode_flows(self, fields: FieldMap, result: dict[str, Any]) -> None:
        """Aggregate flows: home load, grid import, computed battery power."""
        # Grid import and home load travel as one group, carried only by full
        # frames. Home load is realistically never 0, so its presence marks
        # such a frame — and within it an absent grid means 0 import
        # (islanded), not "unchanged" (zero-omission, see module note).
        load = _first(fields, F_LOAD_PWR, WIRE_F32)
        if load is not None:
            result["shp_load_pwr"] = round(load, 2)
            grid = _first(fields, F_GRID_PWR, WIRE_F32) or 0.0
            result["shp_grid_pwr"] = round(grid, 2)

        # Per-leg grid detail is sampled sparsely — here absent genuinely
        # means "not reported this frame", so skip rather than zero.
        for key, no in (
            ("shp_grid_l1_pwr", F_GRID_L1_PWR),
            ("shp_grid_l2_pwr", F_GRID_L2_PWR),
            ("shp_l1_vol", F_L1_VOL),
            ("shp_l2_vol", F_L2_VOL),
            ("shp_grid_l1_amp", F_GRID_L1_AMP),
            ("shp_grid_l2_amp", F_GRID_L2_AMP),
        ):
            v = _first(fields, no, WIRE_F32)
            if v is not None:
                result[key] = round(v, 2)

        # Battery contribution = load - grid, signed (positive = battery
        # supplying the load, negative = charging through the panel). The
        # last-seen pair is cached so frames without the group still compute.
        for k in ("shp_grid_pwr", "shp_load_pwr"):
            if k in result:
                self._flows[k] = result[k]
        if len(self._flows) == 2:
            result["shp_batt_pwr"] = round(self._flows["shp_load_pwr"] - self._flows["shp_grid_pwr"], 2)

    def _decode_panel_state(self, fields: FieldMap, result: dict[str, Any]) -> None:
        """Grid status, panel settings, charge state, operating mode."""
        # These have no reliable marker for their frame, so absent means "not
        # in this frame" and the last value holds. The full frame sends them
        # even when 0 (467 and 282 arrive as explicit zeros).
        now = time.monotonic()
        for key, no in (
            ("shp_grid_sta", F_GRID_STA),
            ("shp_backup_reserve", F_BACKUP_RESERVE),
            ("shp_max_chg_soc", F_MAX_CHG_SOC),
            ("shp_nice_to_have_soc", F_NICE_TO_HAVE_SOC),
            ("shp_storm_guard", F_STORM_GUARD),
            ("shp_chg_dsg_state", F_CHG_DSG_STATE),
        ):
            v = _first(fields, no, WIRE_VARINT)
            if v is not None:
                result[key] = v
                self.panel_state_seen[key] = now

        # The mode submessage carries the operating mode. In the full frame an
        # absent 752/1244 means 0: grid de-energized, no charge limit
        # (zero-omission, see module note). A mode change arrives as a frame
        # with 1245 alone, where absent 752/1244 hold. The full frame is
        # recognised by any of its other fields being present, so it is only
        # missed when all three are 0 at once.
        mode = _first(fields, F_PANEL_MODE, WIRE_LEN)
        if mode is None:
            return
        flags = _parse_fields(mode)
        result["shp_panel_mode"] = next(
            (name for no, name in PANEL_MODES.items() if _first(flags, no, WIRE_VARINT)), "backup"
        )
        result["shp_eps_mode"] = bool(_first(flags, PANEL_MODE_EPS, WIRE_VARINT))
        seen = ["shp_panel_mode", "shp_eps_mode"]
        full_frame = any(no in fields for no in (F_GRID_ENERGIZED, F_NICE_TO_HAVE_SOC, F_CHARGE_LIMIT))
        energized = _first(fields, F_GRID_ENERGIZED, WIRE_VARINT)
        if energized is not None or full_frame:
            result["shp_grid_energized"] = bool(energized)
            seen.append("shp_grid_energized")
        limit = _first(fields, F_CHARGE_LIMIT, WIRE_VARINT)
        if limit is not None or full_frame:
            result["shp_charge_limit"] = limit or 0
            seen.append("shp_charge_limit")
        for key in seen:
            self.panel_state_seen[key] = now

    def _decode_circuits(self, fields: FieldMap, result: dict[str, Any]) -> None:
        """Per-circuit volt / watt / amp from the 32-entry array."""
        for i in range(self.CIRCUITS):
            entry = _first(fields, self.CIRCUIT_FIELD_BASE + i, WIRE_LEN)
            if entry is None:
                continue
            sub = _parse_fields(entry)
            n = i + 1
            vol = _first(sub, 1, WIRE_F32)
            watt = _first(sub, 2, WIRE_F32)
            amp = _first(sub, 3, WIRE_F32)
            # An entry is present for every circuit, so an absent sub-field
            # means 0 (zero-omission, see module note) — write it explicitly.
            result[f"ch_{n}_vol"] = round(vol, 2) if vol is not None else 0.0
            # EcoFlow signs branch consumption negative; negate to read
            # positive and clamp noise so integrated energy stays monotonic.
            result[f"ch_{n}_pwr"] = max(round(-watt, 2), 0.0) if watt is not None else 0.0
            result[f"ch_{n}_amp"] = round(amp, 2) if amp is not None else 0.0

    def _decode_metadata(self, fields: FieldMap, result: dict[str, Any]) -> None:
        """Circuit labels + 240V partner links (rotate in over several frames)."""
        before = {n: dict(m) for n, m in self._meta.items()}
        for n, field_no in enumerate(self.NAME_FIELDS, 1):
            entry = _first(fields, field_no, WIRE_LEN)
            if entry is None:
                continue
            meta = _parse_fields(entry)
            label = _first(meta, 5, WIRE_LEN)
            if label:
                try:
                    self._meta.setdefault(n, {})["name"] = label.decode("utf-8").strip().strip("\x00")
                except UnicodeDecodeError:
                    pass
            link = _first(meta, 2, WIRE_LEN)
            if link is not None:
                partner = _first(_parse_fields(link), 2, WIRE_VARINT)
                if partner is not None:
                    self._meta.setdefault(n, {})["partner"] = partner
        # Persist labels across restart/reload, but only when they change.
        if self._meta != before:
            self._save_meta()
        self._publish_meta(result)

    def _combine_split_phase(self, result: dict[str, Any]) -> None:
        """Fold each 240V pair onto its primary (lower-numbered) leg.

        The appliance then reads once — energy isn't double-counted — and
        the secondary leg reads 0.
        """
        for n, m in self._meta.items():
            p = m.get("partner")
            if p and n < p and f"ch_{n}_pwr" in result and f"ch_{p}_pwr" in result:
                result[f"ch_{n}_pwr"] = round(result[f"ch_{n}_pwr"] + result[f"ch_{p}_pwr"], 2)
                result[f"ch_{p}_pwr"] = 0.0
