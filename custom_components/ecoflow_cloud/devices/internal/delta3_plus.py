"""EcoFlow DELTA 3 Plus device implementation.

Self-contained: this module does not import or subclass the DELTA 3 device, its
protobuf schema or its constants. Everything protocol-specific (messages, command
builders, decoding, entity lists) lives in this module, delta3_plus_const and
ef_delta3_plus.proto, so changes to other devices can never affect the DELTA 3 Plus.

Covers the station telemetry and controls, two Solar/Car inputs, a second USB-C
output, a single DELTA 3 Smart Extra Battery (BMS routed by pack number) and a
writable Storm Guard switch.
"""

import base64
import logging
import math
import time
from typing import Any, override

from google.protobuf.json_format import MessageToDict
from google.protobuf.message import DecodeError
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import RestoreSensor, SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import EntityCategory

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.api.message import Message, PrivateAPIMessageProtocol
from custom_components.ecoflow_cloud.devices import BaseInternalDevice
from custom_components.ecoflow_cloud.devices.data_holder import PreparedData
from custom_components.ecoflow_cloud.devices.internal import delta3_plus_const as plus_const
from custom_components.ecoflow_cloud.devices.internal.proto import (
    ef_delta3_plus_pb2 as plus_pb2,
)
from custom_components.ecoflow_cloud.entities import BaseSensorEntity
from custom_components.ecoflow_cloud.number import (
    BatteryBackupLevel,
    ChargingPowerEntity,
    MaxBatteryLevelEntity,
    MinBatteryLevelEntity,
)
from custom_components.ecoflow_cloud.select import (
    DictSelectEntity,
    TimeoutDictSelectEntity,
)
from custom_components.ecoflow_cloud.sensor import (
    CapacitySensorEntity,
    CyclesSensorEntity,
    InMilliampSensorEntity,
    InVoltSensorEntity,
    InWattsSensorEntity,
    LevelSensorEntity,
    MilliVoltSensorEntity,
    MiscSensorEntity,
    OutVoltSensorEntity,
    OutWattsSensorEntity,
    QuotaStatusSensorEntity,
    RemainSensorEntity,
    StateOfHealthSensorEntity,
    TempSensorEntity,
    VoltSensorEntity,
)
from custom_components.ecoflow_cloud.switch import (
    BeeperEntity,
    BypassBanScalarSwitch,
    EnabledEntity,
)

_LOGGER = logging.getLogger(__name__)

# Main battery State of Health comes only from BMS soh (field 15, cmdFunc 32 /
# cmdId 50, num missing or 0). Display field 243 is never used.
MAIN_SOH_KEY = "bms_batt_soh"

# Verified routing (physical capture): the station battery and the single
# DELTA 3 Smart Extra Battery both send the BMS report with cmdFunc 32 /
# cmdId 50 and differ by the pack number `num` (0 = station, 1 = extra).
_BMS_CMD_FUNC = 32
_BMS_CMD_ID = 50
_EXTRA_BATTERY_NUM = 1
_EXTRA_BATTERY_D_SRC = 2
_EXTRA_BATTERY_PRODUCT_DETAIL = 7

EXTRA_BATTERY_PREFIX = "extra_battery_"
# Presence of this key means an Extra Battery packet was received in this session.
EXTRA_BATTERY_SEEN_KEY = f"{EXTRA_BATTERY_PREFIX}num"

# Allow-list: serial numbers and per-cell arrays are deliberately not stored.
_EXTRA_BATTERY_FIELDS = (
    "f32_show_soc",
    "input_watts",
    "output_watts",
    "chg_dsg_state",
    "remain_cap",
    "full_cap",
    "design_cap",
    "soh",
    "cycles",
    "temp",
    "min_cell_temp",
    "max_cell_temp",
    "min_cell_vol",
    "max_cell_vol",
    "sys_ver",
)

_BMS_HEARTBEAT_COMMANDS: set[tuple[int, int]] = {
    (3, 1),
    (3, 2),
    (3, 30),
    (3, 50),
    (32, 1),
    (32, 3),
    (32, 50),
    (32, 51),
    (32, 52),
    (254, 24),
    (254, 25),
    (254, 26),
    (254, 27),
    (254, 28),
    (254, 29),
    (254, 30),
}


class Delta3PlusCommandMessage(PrivateAPIMessageProtocol):
    """Message wrapper for DELTA 3 Plus protobuf commands."""

    def __init__(
        self,
        payload: plus_pb2.Delta3PlusSetCommand,
        packet: plus_pb2.Delta3PlusSendHeaderMsg,
    ):
        self._packet = packet
        self._payload = payload

    @override
    def to_mqtt_payload(self):
        return self._packet.SerializeToString()

    @override
    def to_dict(self) -> dict:
        payload_dict = MessageToDict(self._payload, preserving_proto_field_name=True)
        result = MessageToDict(self._packet, preserving_proto_field_name=True)
        result["msg"][0]["pdata"] = {type(self._payload).__name__: payload_dict}
        result["msg"][0].pop("seq", None)
        return {type(self._packet).__name__: result}


def _build_set_packet(
    payload: plus_pb2.Delta3PlusSetCommand,
    pdata: bytes,
    device_sn: str,
    data_len: int | None = None,
) -> Delta3PlusCommandMessage:
    """Wrap serialized set-command bytes in the verified cmdFunc 254 / cmdId 17 header."""
    packet = plus_pb2.Delta3PlusSendHeaderMsg()
    message = packet.msg.add()
    message.src = 32
    message.dest = 2
    message.d_src = 1
    message.d_dest = 1
    message.cmd_func = 254
    message.cmd_id = 17
    message.need_ack = 1
    message.seq = Message.gen_seq()
    message.product_id = 1
    message.version = 19
    message.payload_ver = 1
    message.device_sn = device_sn
    message.data_len = data_len if data_len is not None else len(pdata)
    message.pdata = pdata
    return Delta3PlusCommandMessage(payload, packet)


def _create_proto_command(
    field_name: str, value: int, device_sn: str, data_len: int | None = None
) -> Delta3PlusCommandMessage:
    """Create a single-scalar-field set command."""
    payload = plus_pb2.Delta3PlusSetCommand()
    try:
        setattr(payload, field_name, int(value))
    except AttributeError as e:
        raise ValueError(f"Unknown DELTA 3 Plus set field: {field_name}") from e
    return _build_set_packet(payload, payload.SerializeToString(), device_sn, data_len)


def _encode_varint(v: int) -> bytes:
    out = bytearray()
    while True:
        byte = v & 0x7F
        v >>= 7
        if v:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            break
    return bytes(out)


def _create_ac_charging_power_command(value: int, device_sn: str) -> Delta3PlusCommandMessage:
    """Create the AC charging power command.

    The firmware ignores a command carrying only field 54
    (plug_in_info_ac_in_chg_pow_max); the app always sends it together with the
    undeclared companion field 125 = 0, so pdata is built manually:
    ``b0 03 <value_varint> e8 07 00``.
    """
    pdata = bytes([0xB0, 0x03]) + _encode_varint(int(value)) + bytes([0xE8, 0x07, 0x00])
    return _build_set_packet(plus_pb2.Delta3PlusSetCommand(), pdata, device_sn)


def _create_get_quota_command() -> Delta3PlusCommandMessage:
    """Build the protobuf 'get all' request that fetches the full device snapshot."""
    packet = plus_pb2.Delta3PlusSendHeaderMsg()
    header = packet.msg.add()
    header.src = 32
    header.dest = 32
    header.seq = Message.gen_seq()
    # ``from`` is a Python reserved word, so it is set via setattr.
    setattr(header, "from", "HomeAssistant")
    return Delta3PlusCommandMessage(plus_pb2.Delta3PlusSetCommand(), packet)


def _create_energy_backup_command(
    energy_backup_en: int | None, energy_backup_start_soc: int, device_sn: str
) -> Delta3PlusCommandMessage:
    payload = plus_pb2.Delta3PlusSetCommand()
    payload.cfg_energy_backup.energy_backup_start_soc = int(energy_backup_start_soc)
    if energy_backup_en is not None:
        payload.cfg_energy_backup.energy_backup_en = int(energy_backup_en)
    message = _build_set_packet(payload, payload.SerializeToString(), device_sn)
    message._packet.msg[0].seq = int(time.time() * 1000) % 2147483647
    return message


def _create_energy_strategy_command(mode: int, device_sn: str) -> Delta3PlusCommandMessage:
    """Select the energy strategy: 0 standard, 1 self-powered, 2 scheduled, 3 TOU.

    The three flags are mutually exclusive, so all are written on every change.
    """
    payload = plus_pb2.Delta3PlusSetCommand()
    payload.energy_strategy_operate_mode.operate_self_powered_open = 1 if mode == 1 else 0
    payload.energy_strategy_operate_mode.operate_scheduled_open = 1 if mode == 2 else 0
    payload.energy_strategy_operate_mode.operate_tou_mode_open = 1 if mode == 3 else 0
    message = _build_set_packet(payload, payload.SerializeToString(), device_sn)
    message._packet.msg[0].seq = int(time.time() * 1000) % 2147483647
    return message


def _create_storm_guard_command(enabled: bool, device_sn: str) -> Delta3PlusCommandMessage:
    """Build the verified Storm Guard command (cmdFunc 254 / cmdId 17, field 93).

    ON encodes storm_pattern_enable = true; OFF sends cfg_storm_pattern as an
    empty nested message (false is the proto3 default). Field 93 is always present.
    """
    payload = plus_pb2.Delta3PlusSetCommand()
    payload.cfg_storm_pattern.SetInParent()
    if enabled:
        payload.cfg_storm_pattern.storm_pattern_enable = True
    return _build_set_packet(payload, payload.SerializeToString(), device_sn)


def _derive_energy_strategy_mode(result: dict[str, Any]) -> None:
    """Collapse the nested energy strategy flags into one scalar key."""
    strategy = result.get("energy_strategy_operate_mode")
    if not isinstance(strategy, dict):
        return
    if strategy.get("operate_tou_mode_open") == 1:
        result["energy_strategy_mode"] = 3
    elif strategy.get("operate_scheduled_open") == 1:
        result["energy_strategy_mode"] = 2
    elif strategy.get("operate_self_powered_open") == 1:
        result["energy_strategy_mode"] = 1
    else:
        result["energy_strategy_mode"] = 0


class Delta3PlusChargingStateSensorEntity(BaseSensorEntity):
    """Battery charging state (0 idle, 1 discharging, 2 charging)."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:battery-charging"

    def _update_value(self, val: Any) -> bool:
        if val == 0:
            return super()._update_value("idle")
        elif val == 1:
            return super()._update_value("discharging")
        elif val == 2:
            return super()._update_value("charging")
        else:
            return False


class Delta3PlusOutWattsAbsSensorEntity(OutWattsSensorEntity):
    """Output power sensor that uses the absolute value."""

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(abs(int(val)))


class _RestoreLastValueMixin(RestoreSensor):
    """Restore the last valid native value of a slow-changing diagnostic sensor.

    Only the entity's native value is restored; device data, the Extra Battery
    "seen" marker and availability are untouched, and any fresh telemetry goes
    through the normal update path and replaces the restored value.
    """

    _restore_min: float = 0
    _restore_max: float | None = None
    _restore_integer = True

    def _is_restorable(self, value: Any, unit: str | None) -> bool:
        if isinstance(value, bool) or not isinstance(value, int | float):
            return False
        if self._restore_integer and not isinstance(value, int):
            return False
        if not math.isfinite(value) or value < self._restore_min:
            return False
        if self._restore_max is not None and value > self._restore_max:
            return False
        current_unit = self.native_unit_of_measurement
        return unit is None or current_unit is None or unit == current_unit

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if self._attr_native_value is not None:
            return
        last = await self.async_get_last_sensor_data()
        if last is not None and self._is_restorable(last.native_value, last.native_unit_of_measurement):
            self._attr_native_value = last.native_value  # type: ignore[assignment]


class _RestoredMainHealth(_RestoreLastValueMixin, StateOfHealthSensorEntity):
    _restore_max = 100
    _restore_integer = False


class _RestoredMainCycles(_RestoreLastValueMixin, CyclesSensorEntity):
    pass


class _RestoredMainCapacity(_RestoreLastValueMixin, CapacitySensorEntity):
    pass


class _ExtraBatteryEntity(BaseSensorEntity):
    """Unavailable until an Extra Battery BMS packet has been received."""

    @property
    def available(self) -> bool:
        return super().available and EXTRA_BATTERY_SEEN_KEY in self._device.data.params


class _ExtraBatteryLevel(_ExtraBatteryEntity, LevelSensorEntity):
    pass


class _TotalInWatts(InWattsSensorEntity):
    """Total input power; its energy sensor is a primary measurement, not a diagnostic."""

    @override
    def energy_sensor(self):
        energy = super().energy_sensor()
        if energy is not None:
            energy._attr_entity_category = None
        return energy


class _TotalOutWatts(OutWattsSensorEntity):
    """Total output power; its energy sensor is a primary measurement, not a diagnostic."""

    @override
    def energy_sensor(self):
        energy = super().energy_sensor()
        if energy is not None:
            energy._attr_entity_category = None
        return energy


class _ExtraBatteryInWatts(_ExtraBatteryEntity, InWattsSensorEntity):
    pass


class _ExtraBatteryOutWatts(_ExtraBatteryEntity, OutWattsSensorEntity):
    pass


class _ExtraBatteryCapacity(_ExtraBatteryEntity, CapacitySensorEntity):
    pass


class _ExtraBatteryHealth(_ExtraBatteryEntity, StateOfHealthSensorEntity):
    pass


class _ExtraBatteryCycles(_ExtraBatteryEntity, CyclesSensorEntity):
    pass


class _ExtraBatteryTemp(_ExtraBatteryEntity, TempSensorEntity):
    pass


class _ExtraBatteryCellVolt(_ExtraBatteryEntity, MilliVoltSensorEntity):
    pass


class _ExtraBatteryMisc(_ExtraBatteryEntity, MiscSensorEntity):  # type: ignore[misc]
    pass


class _RestoredExtraBatteryHealth(_RestoreLastValueMixin, _ExtraBatteryHealth):
    _restore_max = 100
    _restore_integer = False


class _RestoredExtraBatteryCycles(_RestoreLastValueMixin, _ExtraBatteryCycles):
    pass


class _RestoredExtraBatteryCapacity(_RestoreLastValueMixin, _ExtraBatteryCapacity):
    pass


class _RestoredExtraBatteryFirmware(_RestoreLastValueMixin, _ExtraBatteryMisc):  # type: ignore[misc]
    pass


class Delta3Plus(BaseInternalDevice):
    """EcoFlow DELTA 3 Plus (dual Solar/Car input) using protobuf decoding."""

    @staticmethod
    def default_charging_power_step() -> int:
        return 50

    @override
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        c = plus_const
        return [
            LevelSensorEntity(client, self, "bms_batt_soc", c.MAIN_BATTERY_LEVEL)
            .attr("bms_design_cap", c.ATTR_DESIGN_CAPACITY, 0)
            .attr("bms_full_cap", c.ATTR_FULL_CAPACITY, 0)
            .attr("bms_remain_cap", c.ATTR_REMAIN_CAPACITY, 0),
            _RestoredMainCapacity(client, self, "bms_design_cap", c.MAIN_DESIGN_CAPACITY, False, diagnostic=True),
            _RestoredMainCapacity(client, self, "bms_full_cap", c.MAIN_FULL_CAPACITY, False, diagnostic=True),
            CapacitySensorEntity(client, self, "bms_remain_cap", c.MAIN_REMAIN_CAPACITY, False, diagnostic=True),
            _RestoredMainHealth(client, self, MAIN_SOH_KEY, c.SOH, diagnostic=True),
            LevelSensorEntity(client, self, "cms_batt_soc", c.COMBINED_BATTERY_LEVEL),
            Delta3PlusChargingStateSensorEntity(client, self, "bms_chg_dsg_state", c.BATTERY_CHARGING_STATE),
            _TotalInWatts(client, self, "pow_in_sum_w", c.TOTAL_IN_POWER).with_energy(),
            _TotalOutWatts(client, self, "pow_out_sum_w", c.TOTAL_OUT_POWER).with_energy(),
            # Each input port supports solar and car charging. The pv -> input 1 and
            # pv2 -> input 2 mapping was validated on a physical device. The device
            # reports no usable solar energy value, so no energy entity is created.
            InWattsSensorEntity(client, self, "pow_get_pv", c.SOLAR_CAR_INPUT_1_POWER),
            InVoltSensorEntity(client, self, "plug_in_info_pv_vol", c.SOLAR_CAR_INPUT_1_VOLTAGE),
            InMilliampSensorEntity(client, self, "plug_in_info_pv_amp", c.SOLAR_CAR_INPUT_1_CURRENT),
            TempSensorEntity(client, self, "temp_pv", c.SOLAR_CAR_INPUT_1_TEMP),
            InWattsSensorEntity(client, self, "pow_get_pv2", c.SOLAR_CAR_INPUT_2_POWER),
            InVoltSensorEntity(client, self, "plug_in_info_pv2_vol", c.SOLAR_CAR_INPUT_2_VOLTAGE),
            InMilliampSensorEntity(client, self, "plug_in_info_pv2_amp", c.SOLAR_CAR_INPUT_2_CURRENT),
            TempSensorEntity(client, self, "temp_pv2", c.SOLAR_CAR_INPUT_2_TEMP),
            InWattsSensorEntity(client, self, "pow_get_ac_in", c.AC_IN_POWER),
            Delta3PlusOutWattsAbsSensorEntity(client, self, "pow_get_ac_out", c.AC_OUT_POWER),
            InVoltSensorEntity(client, self, "plug_in_info_ac_in_vol", c.AC_IN_VOLT),
            OutVoltSensorEntity(client, self, "plug_in_info_ac_out_vol", c.AC_OUT_VOLT),
            OutWattsSensorEntity(client, self, "pow_get_12v", c.DC_OUT_POWER),
            Delta3PlusOutWattsAbsSensorEntity(client, self, "pow_get_typec1", c.TYPEC_1_OUT_POWER),
            # pow_get_typec2 (Display 12); port-to-socket mapping awaits physical testing.
            Delta3PlusOutWattsAbsSensorEntity(client, self, "pow_get_typec2", c.TYPEC_2_OUT_POWER),
            Delta3PlusOutWattsAbsSensorEntity(client, self, "pow_get_qcusb1", c.USB_QC_1_OUT_POWER),
            Delta3PlusOutWattsAbsSensorEntity(client, self, "pow_get_qcusb2", c.USB_QC_2_OUT_POWER),
            RemainSensorEntity(client, self, "bms_chg_rem_time", c.CHARGE_REMAINING_TIME),
            RemainSensorEntity(client, self, "bms_dsg_rem_time", c.DISCHARGE_REMAINING_TIME),
            RemainSensorEntity(client, self, "cms_chg_rem_time", c.REMAINING_TIME),
            TempSensorEntity(client, self, "temp_pcs_dc", c.PCS_DC_TEMP),
            TempSensorEntity(client, self, "temp_pcs_ac", c.PCS_AC_TEMP),
            TempSensorEntity(client, self, "bms_min_cell_temp", c.BATTERY_TEMP).attr(
                "bms_max_cell_temp", c.MAX_CELL_TEMP, 0
            ),
            TempSensorEntity(client, self, "bms_max_cell_temp", c.MAX_CELL_TEMP, False),
            VoltSensorEntity(client, self, "bms_batt_vol", c.BATTERY_VOLT, False, diagnostic=True)
            .attr("bms_min_cell_vol", c.MIN_CELL_VOLT, 0)
            .attr("bms_max_cell_vol", c.MAX_CELL_VOLT, 0),
            MilliVoltSensorEntity(client, self, "bms_min_cell_vol", c.MIN_CELL_VOLT, False, diagnostic=True),
            MilliVoltSensorEntity(client, self, "bms_max_cell_vol", c.MAX_CELL_VOLT, False, diagnostic=True),
            _RestoredMainCycles(client, self, "cycles", c.CYCLES),
            QuotaStatusSensorEntity(client, self),
            *self._extra_battery_sensors(client),
        ]

    def _extra_battery_sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        p = EXTRA_BATTERY_PREFIX
        c = plus_const
        return [
            _ExtraBatteryLevel(client, self, f"{p}f32_show_soc", c.EXTRA_BATTERY_LEVEL),
            _ExtraBatteryInWatts(client, self, f"{p}input_watts", c.EXTRA_BATTERY_IN_POWER),
            _ExtraBatteryOutWatts(client, self, f"{p}output_watts", c.EXTRA_BATTERY_OUT_POWER),
            # chg_dsg_state (heartbeat field 47) has no verified enum, so it stays raw.
            _ExtraBatteryMisc(client, self, f"{p}chg_dsg_state", c.EXTRA_BATTERY_CHARGING_STATE_RAW, False),
            _ExtraBatteryCapacity(client, self, f"{p}remain_cap", c.EXTRA_BATTERY_REMAIN_CAPACITY, diagnostic=True),
            _RestoredExtraBatteryCapacity(client, self, f"{p}full_cap", c.EXTRA_BATTERY_FULL_CAPACITY, diagnostic=True),
            _RestoredExtraBatteryCapacity(
                client, self, f"{p}design_cap", c.EXTRA_BATTERY_DESIGN_CAPACITY, diagnostic=True
            ),
            _RestoredExtraBatteryHealth(client, self, f"{p}soh", c.EXTRA_BATTERY_SOH, diagnostic=True),
            _RestoredExtraBatteryCycles(client, self, f"{p}cycles", c.EXTRA_BATTERY_CYCLES),
            _ExtraBatteryTemp(client, self, f"{p}temp", c.EXTRA_BATTERY_TEMP),
            _ExtraBatteryTemp(client, self, f"{p}min_cell_temp", c.EXTRA_BATTERY_MIN_CELL_TEMP),
            _ExtraBatteryTemp(client, self, f"{p}max_cell_temp", c.EXTRA_BATTERY_MAX_CELL_TEMP),
            _ExtraBatteryCellVolt(client, self, f"{p}min_cell_vol", c.EXTRA_BATTERY_MIN_CELL_VOLT, diagnostic=True),
            _ExtraBatteryCellVolt(client, self, f"{p}max_cell_vol", c.EXTRA_BATTERY_MAX_CELL_VOLT, diagnostic=True),
            # sys_ver is exposed as the raw number; its version encoding is not verified.
            _RestoredExtraBatteryFirmware(client, self, f"{p}sys_ver", c.EXTRA_BATTERY_FIRMWARE_VERSION),
        ]

    @override
    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        device = self
        c = plus_const
        return [
            MaxBatteryLevelEntity(
                client,
                self,
                "cms_max_chg_soc",
                c.MAX_CHARGE_LEVEL,
                50,
                100,
                lambda value: _create_proto_command("cms_max_chg_soc", int(value), device.device_data.sn),
            ),
            MinBatteryLevelEntity(
                client,
                self,
                "cms_min_dsg_soc",
                c.MIN_DISCHARGE_LEVEL,
                0,
                30,
                lambda value: _create_proto_command("cms_min_dsg_soc", int(value), device.device_data.sn),
            ),
            ChargingPowerEntity(
                client,
                self,
                "plug_in_info_ac_in_chg_pow_max",
                c.AC_CHARGING_POWER,
                100,
                1500,
                lambda value: _create_ac_charging_power_command(int(value), device.device_data.sn),
            ),
            BatteryBackupLevel(
                client,
                self,
                "energy_backup_start_soc",
                c.BACKUP_RESERVE_LEVEL,
                5,
                100,
                "cms_min_dsg_soc",
                "cms_max_chg_soc",
                5,
                lambda value: _create_energy_backup_command(1, int(value), device.device_data.sn),
            ),
            BatteryBackupLevel(
                client,
                self,
                "backup_reverse_soc",
                c.BACKUP_RESERVE_SOC,
                5,
                100,
                "cms_min_dsg_soc",
                "cms_max_chg_soc",
                5,
                lambda value: _create_proto_command("backup_reverse_soc", int(value), device.device_data.sn),
            ),
        ]

    @override
    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        device = self
        c = plus_const
        return [
            BeeperEntity(
                client,
                self,
                "en_beep",
                c.BEEPER,
                lambda value: _create_proto_command("en_beep", 1 if value else 0, device.device_data.sn, data_len=2),
                # en_beep is 1 = beeper enabled, unlike the legacy quiet-mode keys.
                enableValue=1,
                disableValue=0,
            ),
            EnabledEntity(
                client,
                self,
                "cfg_ac_out_open",
                c.AC_ENABLED,
                lambda value, params=None: _create_proto_command(
                    "cfg_ac_out_open", 1 if value else 0, device.device_data.sn
                ),
            ),
            EnabledEntity(
                client,
                self,
                "xboost_en",
                c.XBOOST_ENABLED,
                lambda value, params=None: _create_proto_command("xboost_en", 1 if value else 0, device.device_data.sn),
            ),
            EnabledEntity(
                client,
                self,
                "cfg_dc12v_out_open",
                c.DC_ENABLED,
                lambda value, params=None: _create_proto_command(
                    "cfg_dc12v_out_open", 1 if value else 0, device.device_data.sn
                ),
            ),
            EnabledEntity(
                client,
                self,
                "cfg_usb_open",
                c.USB_ENABLED,
                lambda value, params=None: _create_proto_command(
                    "cfg_usb_open", 1 if value else 0, device.device_data.sn
                ),
            ),
            EnabledEntity(
                client,
                self,
                "output_power_off_memory",
                c.AC_ALWAYS_ENABLED,
                lambda value, params=None: _create_proto_command(
                    "output_power_off_memory", 1 if value else 0, device.device_data.sn
                ),
            ),
            EnabledEntity(
                client,
                self,
                "energy_backup_en",
                c.BP_ENABLED,
                lambda value, params=None: _create_energy_backup_command(
                    1 if value else None,
                    params.get("energy_backup_start_soc", 5) if params else 5,
                    device.device_data.sn,
                ),
            ),
            BypassBanScalarSwitch(
                client,
                self,
                "ban_bypass_en",
                c.GRID_BYPASS,
                lambda value, params=None: _create_proto_command("ban_bypass_en", int(value), device.device_data.sn),
                enableValue=1,
                disableValue=0,
            ),
            # The state comes from the incoming storm_pattern_enable (field 467) updates.
            EnabledEntity(
                client,
                self,
                "storm_pattern_enable",
                c.STORM_GUARD,
                lambda value: _create_storm_guard_command(bool(value), device.device_data.sn),
            ),
        ]

    @override
    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        device = self
        c = plus_const
        return [
            DictSelectEntity(
                client,
                self,
                "plug_in_info_pv_dc_amp_max",
                c.DC_CHARGE_CURRENT,
                c.DC_CHARGE_CURRENT_OPTIONS,
                lambda value: _create_proto_command("plug_in_info_pv_dc_amp_max", int(value), device.device_data.sn),
            ),
            DictSelectEntity(
                client,
                self,
                "energy_strategy_mode",
                c.ENERGY_STRATEGY,
                c.ENERGY_STRATEGY_OPTIONS,
                lambda value: _create_energy_strategy_command(int(value), device.device_data.sn),
            ),
            DictSelectEntity(
                client,
                self,
                "plug_in_info_ac_in_chg_mode",
                c.AC_CHARGE_MODE,
                c.AC_CHARGE_MODE_OPTIONS,
                # Custom (0) applies the wattage from the AC Charging Power entity
                # (field 54); Auto (1) lets the firmware choose; Silent (2) caps it.
                lambda value: _create_proto_command("plug_in_info_ac_in_chg_mode", int(value), device.device_data.sn),
            ),
            TimeoutDictSelectEntity(
                client,
                self,
                "screen_off_time",
                c.SCREEN_TIMEOUT,
                c.SCREEN_TIMEOUT_OPTIONS,
                lambda value: _create_proto_command("screen_off_time", int(value), device.device_data.sn),
            ),
            TimeoutDictSelectEntity(
                client,
                self,
                "dev_standby_time",
                c.UNIT_TIMEOUT,
                c.UNIT_TIMEOUT_OPTIONS,
                lambda value: _create_proto_command("dev_standby_time", int(value), device.device_data.sn),
            ),
            TimeoutDictSelectEntity(
                client,
                self,
                "ac_standby_time",
                c.AC_TIMEOUT,
                c.AC_TIMEOUT_OPTIONS,
                lambda value: _create_proto_command("ac_standby_time", int(value), device.device_data.sn),
            ),
            TimeoutDictSelectEntity(
                client,
                self,
                "dc_standby_time",
                c.DC_TIMEOUT,
                c.DC_TIMEOUT_OPTIONS,
                lambda value: _create_proto_command("dc_standby_time", int(value), device.device_data.sn),
            ),
        ]

    @override
    def get_quota_message(self) -> Delta3PlusCommandMessage:
        """Return the protobuf 'get all' request used by quota_all()."""
        return _create_get_quota_command()

    @override
    def _prepare_data(self, raw_data: bytes) -> dict[str, Any]:
        """Decode protobuf and flatten fields."""
        flat_dict: dict[str, Any] | None = None
        decoded_data: dict[str, Any] | None = None
        try:
            header_info = self._decode_header_message(raw_data)
            if not header_info:
                return super()._prepare_data(raw_data)

            pdata = self._extract_payload_data(header_info.get("header_obj"))
            if not pdata:
                return {}

            decoded_pdata = self._perform_xor_decode(pdata, header_info)
            decoded_data = self._decode_message_by_type(decoded_pdata, header_info)
            if not decoded_data:
                return {}

            flat_dict = self._flatten_dict(decoded_data)
        except Exception as e:
            _LOGGER.debug("[Delta3Plus] Data processing failed: %s", e)
            return {}

        return {
            "params": flat_dict or {},
            "all_fields": decoded_data or {},
        }

    @staticmethod
    def _b64_or_raw(raw_data: bytes) -> bytes:
        try:
            return base64.b64decode(raw_data, validate=True)
        except Exception as e:
            # Most payloads are raw protobuf, not base64; silent fall-through.
            _LOGGER.debug("[Delta3Plus] b64decode failed: %s", e)
            return raw_data

    @override
    def _prepare_data_get_reply_topic(self, raw_data: bytes) -> PreparedData:
        """Decode a multi-header ``thing/property/get_reply`` full-state snapshot."""
        try:
            raw_data = self._b64_or_raw(raw_data)
            header_msg = plus_pb2.Delta3PlusMessage()
            header_msg.ParseFromString(raw_data)
        except Exception as e:
            _LOGGER.debug("[Delta3Plus] get_reply parse failed: %s", e)
            return PreparedData(None, None, {"proto": raw_data.hex()})

        merged: dict[str, Any] = {}
        for header in header_msg.header:
            try:
                header_info = {
                    "src": header.src,
                    "dSrc": header.d_src,
                    "encType": header.enc_type,
                    "seq": header.seq,
                    "cmdFunc": header.cmd_func,
                    "cmdId": header.cmd_id,
                }
                if not header.pdata:
                    continue
                decoded_pdata = self._perform_xor_decode(header.pdata, header_info)
                decoded = self._decode_message_by_type(decoded_pdata, header_info)
                if decoded:
                    merged.update(decoded)
            except Exception as e:
                _LOGGER.debug("[Delta3Plus] get_reply header decode failed: %s", e)
                continue

        if not merged:
            return PreparedData(None, None, {"proto": raw_data.hex()})

        flat = self._flatten_dict(merged)
        return PreparedData(None, {"params": flat, "all_fields": merged}, {"proto": raw_data.hex()})

    @override
    def _prepare_data_set_reply_topic(self, raw_data: bytes) -> PreparedData:
        """Parse a set reply; acknowledgements carry ``config_ok``."""
        try:
            raw_data = self._b64_or_raw(raw_data)
            header_msg = plus_pb2.Delta3PlusSendHeaderMsg()
            header_msg.ParseFromString(raw_data)

            if header_msg.msg:
                header = header_msg.msg[0]
                pdata = header.pdata
                if pdata:
                    try:
                        if header.enc_type == 1 and header.src != 32:
                            pdata = self._xor_decode_pdata(pdata, header.seq)
                        reply_msg = plus_pb2.Delta3PlusSetReply()
                        reply_msg.ParseFromString(pdata)
                        result = self._protobuf_to_dict(reply_msg)
                        return PreparedData(None, {"params": self._flatten_dict(result)}, {"proto": raw_data.hex()})
                    except Exception as e:
                        _LOGGER.debug("Failed to parse as Delta3PlusSetReply: %s", e)
        except Exception as e:
            _LOGGER.debug("Protobuf parse failed for set_reply: %s", e)

        return PreparedData(None, None, {"proto": raw_data.hex()})

    def _decode_header_message(self, raw_data: bytes) -> dict[str, Any] | None:
        """Decode the message envelope and extract the first header."""
        try:
            raw_data = self._b64_or_raw(raw_data)
            try:
                header_msg = plus_pb2.Delta3PlusMessage()
                header_msg.ParseFromString(raw_data)
            except Exception as e:
                _LOGGER.debug("[Delta3Plus] Failed to parse header message: %s", e)
                return None

            if not header_msg.header:
                return None

            header = header_msg.header[0]
            return {
                "src": header.src,
                "dest": header.dest,
                "dSrc": header.d_src,
                "dDest": header.d_dest,
                "encType": header.enc_type,
                "checkType": header.check_type,
                "cmdFunc": header.cmd_func,
                "cmdId": header.cmd_id,
                "dataLen": header.data_len,
                "needAck": header.need_ack,
                "seq": header.seq,
                "productId": header.product_id,
                "version": header.version,
                "payloadVer": header.payload_ver,
                "header_obj": header,
            }
        except Exception as e:
            _LOGGER.debug("[Delta3Plus] Failed to decode header message: %s", e)
            return None

    @staticmethod
    def _extract_payload_data(header_obj: Any) -> bytes | None:
        pdata = getattr(header_obj, "pdata", b"")
        return pdata if pdata else None

    def _perform_xor_decode(self, pdata: bytes, header_info: dict[str, Any]) -> bytes:
        if header_info.get("encType", 0) == 1 and header_info.get("src", 0) != 32:
            return self._xor_decode_pdata(pdata, header_info.get("seq", 0))
        return pdata

    @staticmethod
    def _xor_decode_pdata(pdata: bytes, seq: int) -> bytes:
        return bytes((b ^ seq) & 0xFF for b in pdata) if pdata else b""

    def _decode_message_by_type(self, pdata: bytes, header_info: dict[str, Any]) -> dict[str, Any]:
        """Decode a payload by cmdFunc/cmdId.

        - 254/21 display upload, 254/22 runtime upload
        - 254/17 set command, 254/18 set reply
        - 32/2 CMS heartbeat, BMS heartbeats (32/50 routed by pack number)
        """
        cmd_func = header_info.get("cmdFunc", 0)
        cmd_id = header_info.get("cmdId", 0)

        try:
            if cmd_func == 254 and cmd_id == 21:
                display = plus_pb2.Delta3PlusDisplayPropertyUpload()
                display.ParseFromString(pdata)
                result = self._protobuf_to_dict(display)
                # Display field 243 is never sent by the device; main State of Health
                # comes only from BMS soh (field 15), so never map 243 to bms_batt_soh.
                result.pop("bms_batt_soh", None)
                # The firmware never sends cfg_ac_out_open, cfg_dc12v_out_open or
                # cfg_usb_open in telemetry; flow_info_* == 14 iff the output is
                # enabled and == 4 iff disabled (verified by MQTT sniffing).
                # Other values are transient and ignored.
                dc_flow = result.get("flow_info_12v")
                if dc_flow == 14:
                    result["cfg_dc12v_out_open"] = 1
                elif dc_flow == 4:
                    result["cfg_dc12v_out_open"] = 0

                ac_flow = result.get("flow_info_ac_out")
                if ac_flow == 14:
                    result["cfg_ac_out_open"] = 1
                elif ac_flow == 4:
                    result["cfg_ac_out_open"] = 0

                usb_keys = ("flow_info_qcusb1", "flow_info_qcusb2", "flow_info_typec1", "flow_info_typec2")
                usb_values = [result.get(k) for k in usb_keys if k in result]
                if usb_values:
                    if any(v == 14 for v in usb_values):
                        result["cfg_usb_open"] = 1
                    elif all(v == 4 for v in usb_values):
                        result["cfg_usb_open"] = 0

                _derive_energy_strategy_mode(result)
                return result

            if cmd_func == 254 and cmd_id == 22:
                runtime = plus_pb2.Delta3PlusRuntimePropertyUpload()
                runtime.ParseFromString(pdata)
                return self._protobuf_to_dict(runtime)

            if cmd_func == 254 and cmd_id == 17:
                try:
                    set_command = plus_pb2.Delta3PlusSetCommand()
                    set_command.ParseFromString(pdata)
                    result = self._protobuf_to_dict(set_command)
                    _derive_energy_strategy_mode(result)
                    return result
                except Exception as e:
                    _LOGGER.debug("Failed to decode as Delta3PlusSetCommand: %s", e)
                    return {}

            if cmd_func == 254 and cmd_id == 18:
                try:
                    set_reply = plus_pb2.Delta3PlusSetReply()
                    set_reply.ParseFromString(pdata)
                    result = self._protobuf_to_dict(set_reply)
                    if not result.get("config_ok", False):
                        return {}
                    _derive_energy_strategy_mode(result)
                    return result
                except Exception as e:
                    _LOGGER.debug("Failed to decode as Delta3PlusSetReply: %s", e)
                    return {}

            if cmd_func == 32 and cmd_id == 2:
                try:
                    cms = plus_pb2.Delta3PlusCmsHeartBeatReport()
                    cms.ParseFromString(pdata)
                    return self._protobuf_to_dict(cms)
                except Exception as e:
                    _LOGGER.debug("Failed to decode as Delta3PlusCmsHeartBeatReport: %s", e)
                    return {}

            if (cmd_func, cmd_id) in _BMS_HEARTBEAT_COMMANDS:
                if cmd_func == _BMS_CMD_FUNC and cmd_id == _BMS_CMD_ID:
                    routed = self._decode_bms_by_pack(pdata, header_info)
                    if routed is not None:
                        return routed
                try:
                    bms = plus_pb2.Delta3PlusBmsPropertyUpload()
                    bms.ParseFromString(pdata)
                    bms_result = self._protobuf_to_dict(bms)
                    if cmd_func == _BMS_CMD_FUNC and cmd_id == _BMS_CMD_ID and bms.HasField("soh"):
                        bms_result[MAIN_SOH_KEY] = bms.soh
                    return bms_result
                except Exception as e:
                    _LOGGER.debug("Failed to decode BMS report (cmdFunc=%s, cmdId=%s): %s", cmd_func, cmd_id, e)
                    return {}

            # Unknown message type: accept it only if it looks like a BMS report.
            try:
                bms = plus_pb2.Delta3PlusBmsPropertyUpload()
                bms.ParseFromString(pdata)
                result = self._protobuf_to_dict(bms)
                if "cycles" in result or "accu_chg_energy" in result or "accu_dsg_energy" in result:
                    return result
            except Exception as e:
                _LOGGER.debug("Failed to decode as fallback BMS report: %s", e)

            return {}
        except Exception as e:
            _LOGGER.debug("Message decode error for cmdFunc=%s, cmdId=%s: %s", cmd_func, cmd_id, e)
            return {}

    def _decode_bms_by_pack(self, pdata: bytes, header_info: dict[str, Any]) -> dict[str, Any] | None:
        """Route a cmdFunc 32 / cmdId 50 BMS report by pack number.

        Returns None when the packet follows the main-battery path (pack 0, or no
        pack number present). Pack 1 is stored under the ``extra_battery_`` prefix
        only. Any other pack number is dropped so it can not overwrite either battery.
        """
        msg = plus_pb2.Delta3PlusBmsPropertyUpload()
        try:
            msg.ParseFromString(pdata)
        except DecodeError:
            return None
        if not msg.HasField("num") or msg.num == 0:
            return None
        if msg.num != _EXTRA_BATTERY_NUM:
            _LOGGER.debug("Ignoring BMS heartbeat for unsupported pack number %s", msg.num)
            return {}
        d_src = header_info.get("dSrc")
        if (d_src and d_src != _EXTRA_BATTERY_D_SRC) or (
            msg.HasField("product_detail") and msg.product_detail != _EXTRA_BATTERY_PRODUCT_DETAIL
        ):
            _LOGGER.debug(
                "Extra Battery packet differs from verified metadata (d_src=%s, product_detail=%s)",
                d_src,
                msg.product_detail if msg.HasField("product_detail") else None,
            )
        data: dict[str, Any] = {EXTRA_BATTERY_SEEN_KEY: msg.num}
        for name in _EXTRA_BATTERY_FIELDS:
            if msg.HasField(name):
                data[f"{EXTRA_BATTERY_PREFIX}{name}"] = getattr(msg, name)
        return data

    def _flatten_dict(self, d: dict, parent_key: str = "", sep: str = "_") -> dict:
        """Flatten nested dict with underscore separator."""
        items: list[tuple[str, Any]] = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    @staticmethod
    def _protobuf_to_dict(protobuf_obj: Any) -> dict[str, Any]:
        return MessageToDict(protobuf_obj, preserving_proto_field_name=True)
