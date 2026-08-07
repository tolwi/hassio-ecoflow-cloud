import asyncio
import logging
import struct
from typing import TYPE_CHECKING, Any, Self, override

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import const
from custom_components.ecoflow_cloud.devices.internal.delta_pro_3 import DeltaPro3
from custom_components.ecoflow_cloud.sensor import (
    AmpSensorEntity,
    InAmpSensorEntity,
    InVoltSensorEntity,
    InWattsSensorEntity,
    LevelSensorEntity,
    QuotaStatusSensorEntity,
    VoltSensorEntity,
    WattsSensorEntity,
)

_LOGGER = logging.getLogger(__name__)

# SHP3 has 32 monitored load circuits.
CIRCUITS = 32
# Circuit metadata submessages (sub-field 5 = the app's circuit label,
# sub-field 2 = split-phase link) in two field blocks, in the same order as
# the power array: circuit N (1-based) -> NAME_FIELDS[N - 1].
NAME_FIELDS = list(range(794, 806)) + list(range(920, 940))
# DisplayPropertyUpload (cmdFunc 254 / cmdId 21) per-circuit array: fields
# 1015..1046, one submessage per circuit {1: volt, 2: watt (signed), 3: amp}.
# These fields are absent from the DP3 proto (dropped on ParseFromString),
# so they are recovered with a second raw pass over the payload.
CIRCUIT_FIELD_BASE = 1015
# Aggregate flow and grid per-leg fields (float, wiretype 5).
F_GRID_PWR = 515
F_LOAD_PWR = 516
F_GRID_L1_PWR, F_GRID_L2_PWR = 962, 963
F_L1_VOL, F_L2_VOL = 956, 957
F_GRID_L1_AMP, F_GRID_L2_AMP = 958, 959

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
    from custom_components.ecoflow_cloud.entities import BaseSensorEntity

    _CircuitNamedBase = BaseSensorEntity
else:
    _CircuitNamedBase = object


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
        # Force one state write when the label first streams in, so idle
        # circuits (no value change) pick up their name immediately.
        if not getattr(self, "_labelled", False) and data.get(f"ch_{self._circuit_no}_name"):
            self._labelled = True
            if getattr(self, "hass", None) is not None:
                self.schedule_update_ha_state()


class NamedCircuitWatts(_CircuitNamed, WattsSensorEntity):
    pass


class NamedCircuitVolt(_CircuitNamed, VoltSensorEntity):
    pass


class NamedCircuitAmp(_CircuitNamed, AmpSensorEntity):
    pass


class SmartHomePanel3(DeltaPro3):
    """EcoFlow Smart Home Panel 3 (private / app API).

    The SHP3 speaks the Delta Pro 3 protobuf dialect (same header, same
    cmdFunc/cmdId routing, DisplayPropertyUpload = 254/21), so the DP3 decode
    pipeline is inherited unchanged. The SHP-specific data — a 32-circuit
    load array plus aggregate flow powers — lives in fields the DP3 proto
    doesn't declare, so it is recovered with a second raw pass per frame.
    Read-only: no control entities until actuation is deliberately in scope.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Circuit metadata (label, 240V partner), keyed by circuit number.
        self._meta: dict[int, dict[str, Any]] = {}
        # Last-seen grid/load pair, carried across frames that omit the group.
        self._flows: dict[str, float] = {}

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
        ]
        # Per-circuit sensors: power enabled with an integrated-energy
        # companion (kWh) for the Energy dashboard; volt/amp disabled by
        # default. Titles use the device-provided circuit label once it has
        # been seen (persisted across restarts), falling back to "Circuit N".
        data = getattr(self, "data", None)
        params = data.params if data is not None else {}

        def circuit_label(n: int) -> str:
            return params.get(f"ch_{n}_name") or f"Circuit {n}"

        for n in range(1, CIRCUITS + 1):
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

    def _decode_circuits(self, fields: FieldMap, result: dict[str, Any]) -> None:
        """Per-circuit volt / watt / amp from the 32-entry array."""
        for i in range(CIRCUITS):
            entry = _first(fields, CIRCUIT_FIELD_BASE + i, WIRE_LEN)
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
        for n, field_no in enumerate(NAME_FIELDS, 1):
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
