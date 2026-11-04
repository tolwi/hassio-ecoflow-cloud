import logging
from collections.abc import Mapping
from typing import Any, ClassVar, override

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import Platform
from homeassistant.helpers import entity_registry as er

from custom_components.ecoflow_cloud import ECOFLOW_DOMAIN
from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.api.message import PrivateAPIMessageProtocol
from custom_components.ecoflow_cloud.devices import const
from custom_components.ecoflow_cloud.devices.internal.smart_home_panel_3 import (
    F_GRID_L1_AMP,
    F_GRID_L1_PWR,
    F_GRID_L2_AMP,
    F_GRID_L2_PWR,
    F_GRID_PWR,
    F_L1_VOL,
    F_L2_VOL,
    WIRE_F32,
    WIRE_LEN,
    WIRE_VARINT,
    FieldMap,
    SmartHomePanel3,
    _CircuitNamed,
    _first,
    _parse_fields,
)
from custom_components.ecoflow_cloud.entities import BaseSensorEntity
from custom_components.ecoflow_cloud.number import (
    ChargingPowerEntity,
    MaxBatteryLevelEntity,
    MinBatteryLevelEntity,
)
from custom_components.ecoflow_cloud.select import DictSelectEntity
from custom_components.ecoflow_cloud.sensor import (
    BatteryLimitSensorEntity,
    InWattsSensorEntity,
    OutWattsSensorEntity,
    RemainSensorEntity,
    VoltSensorEntity,
    WattsSensorEntity,
)
from custom_components.ecoflow_cloud.switch import EnabledEntity

_LOGGER = logging.getLogger(__name__)

# 8 monitored circuits (the gateway has 6 physical circuits; 7 and 8 are
# present in the protocol array, meaning not yet known) - the SHP3 layout narrowed.
SMART_GATEWAY_CIRCUITS = 8
# Physical breaker circuits exposed for circuit state (1..6).
SMART_GATEWAY_PHYSICAL_CIRCUITS = 6
# Circuit metadata submessages, in the same order as the power array
# (circuit N -> NAME_FIELDS[N - 1]). The first block of the SHP3 layout
# (fields 794..801) covers all 8 gateway circuits.
SMART_GATEWAY_NAME_FIELDS = list(range(794, 794 + SMART_GATEWAY_CIRCUITS))

# Any contiguous circuit pair (1&2, 2&3, 3&4, 4&5, 5&6) can be combined for
# split-phase 240V load power (detected from the app-reported partner metadata
# and reported on the lower-numbered circuit), whereas only circuits 5 & 6 can
# be combined and used for solar input.
SOLAR_CIRCUITS = (5, 6)
CIRCUIT_SUFFIXES = ("pwr", "vol", "amp", "state")
SOLAR_CIRCUIT_KEYS = {f"ch_{n}_{s}" for n in SOLAR_CIRCUITS for s in CIRCUIT_SUFFIXES}

# Aggregate flow and status fields in DisplayPropertyUpload (254/21), confirmed
# across grid, solar-export, battery-discharge, and settings captures:
#   461  (varint, %) = backup reserve SoC level (low discharge limit)
#   467  (varint)    = Storm Guard enable (0 = Off, 1 = On)
#   515  (float,  W) = grid power (+ import / - export)
#   516  (float,  W) = monitored branch circuits load
#   517  (float,  W) = solar power (circuits 5/6)
#   518  (float,  W) = storage / battery power (- discharging / + charging)
#   538  (varint, %) = self-powered reserve SoC level (fallback for 461)
#   540  (varint, %) = target charge SoC level
#   619  (varint)    = power source state (1 = Grid, 2 = Battery)
#   792  (varint, W) = generator charge power limit
#   900  (varint)    = legacy operating mode summary (1 = Self-Powered, 2 = Scheduled, 3 = AI)
#   1063 (float,  V) = backup panel L1 voltage
#   1064 (float,  V) = backup panel L2 voltage
#   1244 (varint, W) = max battery charge power limit
#   1245 (submsg)    = operating mode & EPS mode ({1: self_powered, 2: scheduled, 4: eps_mode, 5: custom, 6: ai})
#   1544 (varint, W) = total home load at the main-panel connection
F_BACKUP_RESERVE_SOC = 461
F_STORM_GUARD = 467
F_HOME_LOAD = 1544
F_SOLAR_PWR = 517
F_BATT_PWR = 518
F_BACKUP_RESERVE_SOC_ALT = 538
F_TARGET_SOC = 540
F_GEN_CHG_PWR_MAX = 792
F_OPERATE_MODE_SUMMARY = 900
F_PANEL_L1_VOL = 1063
F_PANEL_L2_VOL = 1064
F_MAX_CHG_PWR = 1244
F_OPERATE_MODE_INFO = 1245

# SetCommand (cmdFunc=254, cmdId=17, dest=11) field numbers:
CMD_MAX_CHG_SOC = 33
CMD_STORM_GUARD = 93
CMD_GEN_CHG_PWR_MAX = 101
CMD_BACKUP_RESERVE_SOC = 102
CMD_FORCE_CHARGE = 536
CMD_MAX_CHG_PWR = 542
CMD_OPERATE_MODE = 544
CMD_AI_MODE_SUB = 546

# Operating mode options (sub-field of Display field 1245 / SetCommand field 544).
GATEWAY_OPERATING_MODE_OPTIONS: dict[str, int] = {
    "Self-Powered": 1,
    "Scheduled Tasks": 2,
    "Custom": 5,
    "AI Mode": 6,
}

# Sensor keys that were promoted to Select/Switch/Number controls and should be
# cleaned up from the Sensor platform registry if present from earlier builds.
_MIGRATED_SENSOR_KEYS: set[str] = {
    "shp_operating_mode",
    "shp_storm_guard",
    "shp_backup_reserve_soc",
    "cms_max_chg_soc",
    "cms_min_dsg_soc",
    "shp_max_chg_pwr",
    "shp_gen_chg_pwr",
}

_GATEWAY_SEQ = 100


def _next_gateway_seq() -> int:
    global _GATEWAY_SEQ
    _GATEWAY_SEQ = 100 if _GATEWAY_SEQ >= 999999 else _GATEWAY_SEQ + 1
    return _GATEWAY_SEQ


def _encode_varint(v: int) -> bytes:
    out = bytearray()
    v &= 0xFFFFFFFFFFFFFFFF
    while True:
        b = v & 0x7F
        v >>= 7
        if v:
            out.append(b | 0x80)
        else:
            out.append(b)
            break
    return bytes(out)


def _encode_varint_field(field_no: int, val: int) -> bytes:
    return _encode_varint((field_no << 3) | WIRE_VARINT) + _encode_varint(val)


def _encode_len_field(field_no: int, payload: bytes) -> bytes:
    return _encode_varint((field_no << 3) | WIRE_LEN) + _encode_varint(len(payload)) + payload


def _build_gateway_header_bytes(item: bytes, seq: int, device_sn: str) -> bytes:
    """Build a DP3Header byte string matching the EcoFlow App SET command format."""
    sn_bytes = device_sn.encode("utf-8")
    out = bytearray()
    out += _encode_len_field(1, item)          # pdata
    out += _encode_varint_field(2, 32)         # src = APP (32)
    out += _encode_varint_field(3, 11)         # dest = Smart Gateway (11)
    out += _encode_varint_field(4, 1)          # d_src = 1
    out += _encode_varint_field(5, 1)          # d_dest = 1
    out += _encode_varint_field(7, 3)          # check_type = 3
    out += _encode_varint_field(8, 254)        # cmd_func = 254
    out += _encode_varint_field(9, 17)         # cmd_id = 17
    out += _encode_varint_field(10, len(item)) # data_len
    out += _encode_varint_field(11, 1)         # need_ack = 1
    out += _encode_varint_field(14, seq)       # seq
    out += _encode_varint_field(16, 4)         # version = 4
    out += _encode_varint_field(17, 1)         # payload_ver = 1
    out += _encode_len_field(23, b"ios")       # from = "ios"
    out += _encode_len_field(25, sn_bytes)     # device_sn
    out += _encode_len_field(26, sn_bytes)     # gateway target sn
    out += _encode_len_field(27, sn_bytes)     # gateway session sn
    return bytes(out)


class SmartGatewayCommandMessage(PrivateAPIMessageProtocol):
    """Protobuf SET command wrapper for the Smart Gateway (cmdFunc=254, cmdId=17, dest=11)."""

    def __init__(self, pdata: bytes, desc: dict[str, Any], device_sn: str) -> None:
        self._pdata = pdata
        self._desc = desc
        seq = _next_gateway_seq()
        hdr_bytes = _build_gateway_header_bytes(pdata, seq, device_sn)
        self._raw_payload = _encode_len_field(1, hdr_bytes)

    @override
    def to_mqtt_payload(self) -> bytes:
        return self._raw_payload

    @override
    def to_dict(self) -> dict[str, Any]:
        return {
            "cmdFunc": 254,
            "cmdId": 17,
            "dest": 11,
            "payload": self._desc,
            "raw_hex": self._pdata.hex(),
        }


def _create_gateway_varint_command(field_no: int, value: int, device_sn: str) -> SmartGatewayCommandMessage:
    """Create a SET command setting a single top-level varint field."""
    ival = int(value)
    pdata = _encode_varint_field(field_no, ival)
    return SmartGatewayCommandMessage(pdata, {str(field_no): ival}, device_sn)


def _create_gateway_storm_guard_command(enabled: bool, device_sn: str) -> SmartGatewayCommandMessage:
    """Create a SET command (field 93) to enable or disable Storm Guard."""
    sub = _encode_varint_field(1, 1) if enabled else b""
    pdata = _encode_len_field(CMD_STORM_GUARD, sub)
    desc: dict[str, Any] = {str(CMD_STORM_GUARD): {"1": 1} if enabled else {}}
    return SmartGatewayCommandMessage(pdata, desc, device_sn)


def _create_gateway_operate_mode_bytes(mode: int, eps_enabled: int) -> tuple[bytes, dict[str, Any]]:
    sub = bytearray()
    if mode in (1, 2):
        sub += _encode_varint_field(mode, 1)
        sub += _encode_varint_field(4, 1 if eps_enabled else 0)
    elif mode == 5:
        sub += _encode_varint_field(4, 1 if eps_enabled else 0)
        sub += _encode_varint_field(5, 1)
    elif mode == 6:
        sub += _encode_varint_field(4, 1 if eps_enabled else 0)
        sub += _encode_varint_field(6, 1)
    else:
        sub += _encode_varint_field(4, 1 if eps_enabled else 0)

    pdata = _encode_len_field(CMD_OPERATE_MODE, bytes(sub))
    desc: dict[str, Any] = {str(CMD_OPERATE_MODE): {"4": 1 if eps_enabled else 0}}
    if mode in (1, 2, 5, 6):
        desc[str(CMD_OPERATE_MODE)][str(mode)] = 1
    if mode == 6:
        sub_546 = _encode_varint_field(1, 1) + _encode_varint_field(2, 1)
        pdata += _encode_len_field(CMD_AI_MODE_SUB, sub_546)
        desc[str(CMD_AI_MODE_SUB)] = {"1": 1, "2": 1}
    return pdata, desc


def _create_gateway_operate_mode_command(
    mode: int,
    eps_enabled: int,
    device_sn: str,
    client: EcoflowApiClient | None = None,
    stop_force_charge: bool = False,
) -> SmartGatewayCommandMessage:
    """Create a SET command (field 544 / 546) for Smart Gateway Operating Mode and EPS Mode."""
    if stop_force_charge and client is not None and device_sn in client.devices:
        sub_536 = _encode_varint_field(2, 2)
        pdata_536 = _encode_len_field(CMD_FORCE_CHARGE, sub_536)
        cmd_536 = SmartGatewayCommandMessage(pdata_536, {str(CMD_FORCE_CHARGE): {"2": 2}}, device_sn)
        client.mqtt_client.publish(client.devices[device_sn].device_info.set_topic, cmd_536.to_mqtt_payload())
    pdata, desc = _create_gateway_operate_mode_bytes(mode, eps_enabled)
    return SmartGatewayCommandMessage(pdata, desc, device_sn)


def _create_gateway_force_charge_command(
    client: EcoflowApiClient,
    enabled: bool,
    mode: int,
    eps_enabled: int,
    device_sn: str,
) -> SmartGatewayCommandMessage:
    """Send field 536 and return field 544 as two separate single-header MQTT packets."""
    if enabled:
        sub_536 = _encode_varint_field(1, 1) + _encode_varint_field(2, 1)
        pdata_536 = _encode_len_field(CMD_FORCE_CHARGE, sub_536)
        desc_536: dict[str, Any] = {str(CMD_FORCE_CHARGE): {"1": 1, "2": 1}}
        pdata_544, desc_544 = _create_gateway_operate_mode_bytes(0, eps_enabled)
    else:
        sub_536 = _encode_varint_field(2, 2)
        pdata_536 = _encode_len_field(CMD_FORCE_CHARGE, sub_536)
        desc_536 = {str(CMD_FORCE_CHARGE): {"2": 2}}
        pdata_544, desc_544 = _create_gateway_operate_mode_bytes(mode if mode in (1, 2, 5, 6) else 2, eps_enabled)
    cmd_536 = SmartGatewayCommandMessage(pdata_536, desc_536, device_sn)
    if device_sn in client.devices:
        client.mqtt_client.publish(client.devices[device_sn].device_info.set_topic, cmd_536.to_mqtt_payload())
    return SmartGatewayCommandMessage(pdata_544, desc_544, device_sn)


class _GatewayChargingStateSensorEntity(BaseSensorEntity):
    """Translates cms_chg_dsg_state (0=Idle, 1=Discharging, 2=Charging) to text."""

    _LABELS: ClassVar[dict[int, str]] = {
        0: "Idle",
        1: "Discharging",
        2: "Charging",
    }
    _attr_icon = "mdi:battery-charging"

    def _update_value(self, val: Any) -> bool:
        try:
            label = self._LABELS.get(int(val), f"Unknown ({val})")
        except (TypeError, ValueError):
            label = str(val)
        return super()._update_value(label)


class _GatewayBooleanStateSensorEntity(BaseSensorEntity):
    """Translates a 0/1 varint flag into Off/On."""

    def _update_value(self, val: Any) -> bool:
        try:
            label = "On" if int(val) == 1 else "Off"
        except (TypeError, ValueError):
            label = str(val)
        return super()._update_value(label)


class _GatewayRemainSensorEntity(RemainSensorEntity):
    """Remaining charge/discharge duration sensor allowing multi-day home backup runtimes."""

    @override
    def _update_value(self, val: Any) -> Any:
        ival = int(val)
        # EcoFlow home storage uses >= 14399 (10 days) as the idle/infinite sentinel;
        # valid runtimes on a large battery bank regularly exceed 5000 minutes.
        if ival < 0 or ival >= 14399:
            ival = 0
        return super(RemainSensorEntity, self)._update_value(ival)


class _GatewayTaskSensorEntity(BaseSensorEntity):
    """Formats the active scheduled time-task from DisplayPropertyUpload field 126."""

    _TASK_LABELS: ClassVar[dict[str, str]] = {
        "TIME_TASK_TYPE_AC_CHG": "AC Charging",
        "TIME_TASK_TYPE_AC_DSG": "AC Discharging",
        "TIME_TASK_TYPE_DC_CHG": "DC / Solar Charging",
        "TIME_TASK_TYPE_DC2_CHG": "DC2 Charging",
        "TIME_TASK_TYPE_DC_DSG": "DC Discharging",
        "TIME_TASK_TYPE_OIL_ON": "Generator On",
        "TIME_TASK_TYPE_OIL_OFF": "Generator Off",
        "TIME_TASK_TYPE_USB_CHG": "USB Charging",
        "TIME_TASK_TYPE_USB_DSG": "USB Discharging",
    }
    _attr_icon = "mdi:calendar-clock"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        attrs = dict(super().extra_state_attributes or {})
        params = self._device.data.params
        for suffix in ("is_enable", "is_cfg", "task_index", "type", "val", "conflict_flag"):
            k = f"current_time_task_v2_item_{suffix}"
            if k in params:
                attrs[suffix] = params[k]
        return attrs

    def _update_value(self, val: Any) -> bool:
        params = self._device.data.params
        enabled = params.get("current_time_task_v2_item_is_enable")
        raw = str(val)
        label = self._TASK_LABELS.get(raw, raw)
        if enabled is False:
            label = f"Inactive ({label})"
        return super()._update_value(label)


class NamedCircuitState(_CircuitNamed, BaseSensorEntity):
    """Per-circuit source/breaker state with breaker amperage rating attribute."""

    _attr_icon = "mdi:electric-switch"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        attrs = dict(super().extra_state_attributes or {})
        params = self._device.data.params
        max_amp = params.get(f"ch_{self._circuit_no}_max_amp")
        if max_amp is not None:
            attrs["breaker_rating_a"] = max_amp
        raw_state = params.get(f"ch_{self._circuit_no}_raw_state")
        if raw_state is not None:
            attrs["raw_state"] = raw_state
        return attrs


class SmartGateway(SmartHomePanel3):
    """EcoFlow Smart Gateway (200A, HR65, private / app API).

    Identical to the Smart Home Panel 3 but with 8 circuits instead of 32; the
    per-circuit array, circuit labels / 240V pairing, grid/load flows and SoC
    are all inherited unchanged (only the circuit geometry is overridden).
    * Any contiguous pair (1&2, 2&3, 3&4, 4&5, 5&6) combined for 240V
      split-phase power is reported as 1 circuit sensor on the primary
      (lower-numbered) channel, omitting the secondary channel.
    * When circuits 5 & 6 are configured for solar in the integration options,
      they are reported as a single `Solar Power` (`shp_solar_pwr`) sensor
      instead of individual circuit 5 and 6 sensors.
    """

    CIRCUITS = SMART_GATEWAY_CIRCUITS
    NAME_FIELDS = SMART_GATEWAY_NAME_FIELDS

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._solar_enabled: bool = bool(getattr(self.device_data.options, "solar_enabled", False))
        self._grid: float = 0.0
        self._solar: float = 0.0
        self._batt: float = 0.0
        self._home: float = 0.0
        self._seen_flows: set[str] = set()

    def _omitted_circuits(self) -> set[int]:
        """Circuits omitted from individual reporting.

        * Secondary leg of any contiguous 240V split-phase pair (1&2, 2&3,
          3&4, 4&5, 5&6), where the primary (lower-numbered) circuit carries
          the combined 240V load.
        * Both circuits 5 and 6 when solar is enabled (reported as a single
          `shp_solar_pwr` sensor instead).
        """
        omitted: set[int] = set()
        for n, m in self._meta.items():
            partner = m.get("partner")
            if partner and partner < n:
                omitted.add(n)
        if self._solar_enabled:
            omitted.update(SOLAR_CIRCUITS)
        return omitted

    def _remove_stale_entities(self, stale_keys: set[str]) -> None:
        if getattr(self, "_hass", None) is None:
            return
        try:
            ent_reg = er.async_get(self._hass)
            sn = self.device_data.sn
            for key in stale_keys:
                base_uid = f"ecoflow-{sn}-{key.replace('_', '-')}"
                for uid in (base_uid, f"{base_uid}_energy"):
                    entity_id = ent_reg.async_get_entity_id(Platform.SENSOR, ECOFLOW_DOMAIN, uid)
                    if entity_id is not None:
                        ent_reg.async_remove(entity_id)
        except Exception as e:
            _LOGGER.debug("Entity cleanup skipped: %s", e)

    @override
    def charging_power_step(self) -> int:
        return 500

    @override
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        out = super().sensors(client)
        omitted = self._omitted_circuits()
        omitted_keys = {f"ch_{n}_{s}" for n in omitted for s in CIRCUIT_SUFFIXES} | {
            "shp_backup_reserve",
            "shp_max_chg_soc",
            "shp_nice_to_have_soc",
            "shp_chg_dsg_state",
            "shp_panel_mode",
            "shp_charge_limit",
        }
        out = [s for s in out if getattr(s, "mqtt_key", None) not in omitted_keys]
        if self._solar_enabled:
            out.append(
                WattsSensorEntity(client, self, "shp_solar_pwr", "Solar Power")
                .with_icon("mdi:solar-power")
                .with_energy()
            )
        # Energy dashboard directional flows (Grid Import/Export & Battery Charge/Discharge),
        # battery status, remaining time, target SoC, active scheduled task, and diagnostic voltages.
        out.extend(
            [
                InWattsSensorEntity(client, self, "shp_grid_in_pwr", "Grid Import Power").with_energy(),
                OutWattsSensorEntity(client, self, "shp_grid_out_pwr", "Grid Export Power").with_energy(),
                InWattsSensorEntity(client, self, "shp_batt_chg_pwr", "Battery Charge Power")
                .with_icon("mdi:battery-arrow-up")
                .with_energy(),
                OutWattsSensorEntity(client, self, "shp_batt_dsg_pwr", "Battery Discharge Power")
                .with_icon("mdi:battery-arrow-down")
                .with_energy(),
                _GatewayChargingStateSensorEntity(client, self, "cms_chg_dsg_state", const.BATTERY_CHARGING_STATE),
                _GatewayRemainSensorEntity(client, self, "cms_dsg_rem_time", const.DISCHARGE_REMAINING_TIME),
                _GatewayRemainSensorEntity(client, self, "cms_chg_rem_time", const.CHARGE_REMAINING_TIME),
                BatteryLimitSensorEntity(client, self, "shp_target_soc", "Target Charge Level"),
                _GatewayTaskSensorEntity(client, self, "current_time_task_v2_item_task_type", "Active Scheduled Task"),
                VoltSensorEntity(client, self, "shp_panel_l1_vol", "Panel L1 Voltage", False, diagnostic=True),
                VoltSensorEntity(client, self, "shp_panel_l2_vol", "Panel L2 Voltage", False, diagnostic=True),
            ]
        )
        # Per-circuit state for physical circuits 1..6 (excluding omitted 240V secondary / solar legs).
        data = getattr(self, "data", None)
        params = data.params if data is not None else {}
        for n in range(1, SMART_GATEWAY_PHYSICAL_CIRCUITS + 1):
            if n in omitted:
                continue
            label = params.get(f"ch_{n}_name") or f"Circuit {n}"
            out.append(
                NamedCircuitState(client, self, f"ch_{n}_state", f"{label} Breaker State").for_circuit(
                    n, "Breaker State"
                )
            )
        return out

    @override
    def binary_sensors(self, client: EcoflowApiClient) -> list[BinarySensorEntity]:
        return []

    @override
    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        device = self
        return [
            MinBatteryLevelEntity(
                client,
                self,
                "shp_backup_reserve_soc",
                const.BACKUP_RESERVE_LEVEL,
                10,
                50,
                lambda value: _create_gateway_varint_command(CMD_BACKUP_RESERVE_SOC, value, device.device_data.sn),
            ),
            MaxBatteryLevelEntity(
                client,
                self,
                "cms_max_chg_soc",
                const.MAX_CHARGE_LEVEL,
                50,
                100,
                lambda value: _create_gateway_varint_command(CMD_MAX_CHG_SOC, value, device.device_data.sn),
            ),
            ChargingPowerEntity(
                client,
                self,
                "shp_max_chg_pwr",
                "Max Charge Rate",
                500,
                10000,
                lambda value: _create_gateway_varint_command(CMD_MAX_CHG_PWR, value, device.device_data.sn),
            ).with_icon("mdi:flash"),
            ChargingPowerEntity(
                client,
                self,
                "shp_gen_chg_pwr",
                "Generator Charge Rate",
                500,
                10000,
                lambda value: _create_gateway_varint_command(CMD_GEN_CHG_PWR_MAX, value, device.device_data.sn),
            ).with_icon("mdi:engine"),
        ]

    @override
    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        device = self
        return [
            DictSelectEntity(
                client,
                self,
                "shp_operating_mode",
                "Operating Mode",
                GATEWAY_OPERATING_MODE_OPTIONS,
                lambda value: _create_gateway_operate_mode_command(
                    int(value),
                    int(device.data.params.get("shp_eps_mode", 1)),
                    device.device_data.sn,
                    client=client,
                    stop_force_charge=bool(device.data.params.get("shp_force_charge", 0)),
                ),
            ),
        ]

    @override
    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        device = self
        return [
            EnabledEntity(
                client,
                self,
                "shp_eps_mode",
                "EPS Mode",
                lambda value, params=None: _create_gateway_operate_mode_command(
                    0
                    if device.data.params.get("shp_force_charge", 0)
                    else int(device.data.params.get("shp_operating_mode", 2)),
                    1 if value else 0,
                    device.device_data.sn,
                ),
                enableValue=1,
                disableValue=0,
            ).with_icon("mdi:shield-flash"),
            EnabledEntity(
                client,
                self,
                "shp_storm_guard",
                "Storm Guard",
                lambda value, params=None: _create_gateway_storm_guard_command(
                    bool(value),
                    device.device_data.sn,
                ),
                enableValue=1,
                disableValue=0,
            ).with_icon("mdi:weather-lightning-rainy"),
            EnabledEntity(
                client,
                self,
                "shp_force_charge",
                "Emergency Charge",
                lambda value, params=None: _create_gateway_force_charge_command(
                    client,
                    bool(value),
                    int(device.data.params.get("shp_operating_mode", 2)),
                    int(device.data.params.get("shp_eps_mode", 1)),
                    device.device_data.sn,
                ),
                enableValue=1,
                disableValue=0,
            ).with_icon("mdi:battery-charging-high"),
        ]

    @override
    async def async_restore_state(self) -> None:
        await super().async_restore_state()
        stale_keys = {f"ch_{n}_{s}" for n in self._omitted_circuits() for s in CIRCUIT_SUFFIXES}
        if not self._solar_enabled:
            stale_keys.add("shp_solar_pwr")
        for key in stale_keys:
            self.data.params.pop(key, None)
        self._remove_stale_entities(stale_keys | _MIGRATED_SENSOR_KEYS)

    @override
    def _decode_flows(self, fields: FieldMap, result: dict[str, Any]) -> None:
        """Aggregate flows and gateway-level status fields.

        The gateway reports all headline flows directly in DisplayPropertyUpload
        using proto2 optional presence (explicitly sending 0.0 when a flow returns
        to zero, and omitting unchanged fields in 2s incremental frames):
          * 515  (float,  W) = grid power (+ import / - export)
          * 517  (float,  W) = solar power (circuits 5/6)
          * 518  (float,  W) = storage / battery power (- discharging / + charging)
          * 1544 (varint, W) = total home load at the main-panel connection
        """
        grid = _first(fields, F_GRID_PWR, WIRE_F32)
        solar = _first(fields, F_SOLAR_PWR, WIRE_F32) if self._solar_enabled else None
        batt = _first(fields, F_BATT_PWR, WIRE_F32)
        home = _first(fields, F_HOME_LOAD, WIRE_VARINT)
        is_full_frame = F_BACKUP_RESERVE_SOC in fields and F_L1_VOL in fields and F_HOME_LOAD in fields

        if grid is not None:
            self._grid = float(grid)
            self._seen_flows.add("grid")
        elif is_full_frame:
            self._grid = 0.0
            self._seen_flows.add("grid")

        if self._solar_enabled:
            if solar is not None:
                self._solar = max(0.0, float(solar))
                self._seen_flows.add("solar")
            elif is_full_frame:
                self._solar = 0.0
                self._seen_flows.add("solar")

        if batt is not None:
            self._batt = -float(batt)
            self._seen_flows.add("batt")
        elif result.get("cms_chg_dsg_state") == 0 or is_full_frame:
            self._batt = 0.0
            self._seen_flows.add("batt")

        if home is not None:
            self._home = float(home)
            self._seen_flows.add("home")
        elif (grid is not None or solar is not None or batt is not None) and "grid" in self._seen_flows:
            self._home = max(0.0, self._grid + self._solar + self._batt)
            self._seen_flows.add("home")

        if "grid" in self._seen_flows:
            result["shp_grid_pwr"] = round(self._grid, 2)
            result["shp_grid_in_pwr"] = round(max(0.0, self._grid), 2)
            result["shp_grid_out_pwr"] = round(max(0.0, -self._grid), 2)
        if "batt" in self._seen_flows:
            result["shp_batt_pwr"] = round(self._batt, 2)
            result["shp_batt_chg_pwr"] = round(max(0.0, -self._batt), 2)
            result["shp_batt_dsg_pwr"] = round(max(0.0, self._batt), 2)
        if "home" in self._seen_flows:
            result["shp_load_pwr"] = round(self._home, 2)
        if self._solar_enabled and "solar" in self._seen_flows:
            result["shp_solar_pwr"] = round(self._solar, 2)

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

        # Gateway status & configuration fields in DisplayPropertyUpload.
        reserve_soc = _first(fields, F_BACKUP_RESERVE_SOC, WIRE_VARINT)
        if reserve_soc is None and "shp_backup_reserve_soc" not in self.data.params:
            reserve_soc = _first(fields, F_BACKUP_RESERVE_SOC_ALT, WIRE_VARINT)
        if reserve_soc is not None:
            result["shp_backup_reserve_soc"] = int(reserve_soc)

        for key, no in (
            ("shp_target_soc", F_TARGET_SOC),
            ("shp_max_chg_pwr", F_MAX_CHG_PWR),
            ("shp_gen_chg_pwr", F_GEN_CHG_PWR_MAX),
            ("shp_storm_guard", F_STORM_GUARD),
        ):
            v = _first(fields, no, WIRE_VARINT)
            if v is not None:
                result[key] = int(v)

        # Operating mode & EPS mode submessage (field 1245) + summary mode (field 900).
        summary_mode = _first(fields, F_OPERATE_MODE_SUMMARY, WIRE_VARINT)
        if summary_mode is not None:
            self.__dict__["_last_mode_summary"] = int(summary_mode)
        last_summary = self.__dict__.get("_last_mode_summary")

        op_raw = _first(fields, F_OPERATE_MODE_INFO, WIRE_LEN)
        if op_raw is not None:
            op_sub = _parse_fields(op_raw)
            eps = _first(op_sub, 4, WIRE_VARINT)
            result["shp_eps_mode"] = 1 if eps == 1 else 0
            found_mode = None
            for mode_id in (1, 2, 5, 6):
                if _first(op_sub, mode_id, WIRE_VARINT) == 1:
                    found_mode = mode_id
                    break
            if found_mode is not None:
                result["shp_operating_mode"] = found_mode
                result["shp_force_charge"] = 0
            elif last_summary == 3:
                result["shp_operating_mode"] = 6
                result["shp_force_charge"] = 0
            else:
                result["shp_force_charge"] = 1
        elif "shp_operating_mode" not in self.data.params and summary_mode is not None:
            if summary_mode in (1, 2):
                result["shp_operating_mode"] = int(summary_mode)
            elif summary_mode == 3:
                result["shp_operating_mode"] = 6

        for key, no in (
            ("shp_panel_l1_vol", F_PANEL_L1_VOL),
            ("shp_panel_l2_vol", F_PANEL_L2_VOL),
        ):
            v = _first(fields, no, WIRE_F32)
            if v is not None:
                result[key] = round(v, 2)

    @override
    def _decode_panel_state(self, fields: FieldMap, result: dict[str, Any]) -> None:
        """SmartGateway handles panel state, mode, EPS, and SoC limits in _decode_flows."""

    @override
    def _decode_circuits(self, fields: FieldMap, result: dict[str, Any]) -> None:
        super()._decode_circuits(fields, result)
        if self._solar_enabled:
            for key in SOLAR_CIRCUIT_KEYS:
                result.pop(key, None)

    @override
    def _decode_metadata(self, fields: FieldMap, result: dict[str, Any]) -> None:
        before_omitted = self._omitted_circuits()
        super()._decode_metadata(fields, result)
        after_omitted = self._omitted_circuits()
        omitted = after_omitted
        # Decode per-circuit state (sub-field 1: 2=Battery/Inverter, 1=Grid, 0=Off) and
        # max amp rating (sub-field 3, float) from metadata fields 794..801.
        for n, field_no in enumerate(self.NAME_FIELDS, 1):
            if n > SMART_GATEWAY_PHYSICAL_CIRCUITS or n in omitted:
                continue
            entry = _first(fields, field_no, WIRE_LEN)
            if entry is None:
                continue
            meta = _parse_fields(entry)
            raw_state = _first(meta, 1, WIRE_VARINT)
            if raw_state is not None:
                result[f"ch_{n}_raw_state"] = int(raw_state)
                if raw_state == 2:
                    result[f"ch_{n}_state"] = "On (Battery)"
                elif raw_state == 1:
                    result[f"ch_{n}_state"] = "On (Grid)"
                else:
                    result[f"ch_{n}_state"] = "Off"
            max_amp = _first(meta, 3, WIRE_F32)
            if max_amp is not None:
                result[f"ch_{n}_max_amp"] = round(max_amp, 1)

        if after_omitted != before_omitted and getattr(self, "_hass", None) is not None:
            newly_omitted = after_omitted - before_omitted
            if newly_omitted:
                stale_keys = {f"ch_{n}_{s}" for n in newly_omitted for s in CIRCUIT_SUFFIXES}
                self._hass.loop.call_soon_threadsafe(self._remove_stale_entities, stale_keys)

    @override
    def _combine_split_phase(self, result: dict[str, Any]) -> None:
        super()._combine_split_phase(result)
        for n, m in self._meta.items():
            p = m.get("partner")
            if p and n < p:
                if f"ch_{n}_vol" in result and f"ch_{p}_vol" in result:
                    result[f"ch_{n}_vol"] = round(result[f"ch_{n}_vol"] + result[f"ch_{p}_vol"], 2)
                for s in CIRCUIT_SUFFIXES:
                    result.pop(f"ch_{p}_{s}", None)
