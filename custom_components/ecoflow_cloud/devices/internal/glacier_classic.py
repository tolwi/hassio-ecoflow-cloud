from __future__ import annotations

import logging
import time
from typing import Any, cast, override

from google.protobuf.json_format import MessageToDict
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.button import ButtonEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.entity import EntityCategory

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.api.message import Message, PrivateAPIMessageProtocol
from custom_components.ecoflow_cloud.binary_sensor import MiscBinarySensorEntity
from custom_components.ecoflow_cloud.devices import BaseInternalDevice, const
from custom_components.ecoflow_cloud.devices.internal.proto import (
    ef_glacier_classic_pb2 as glacier_classic_pb2,
)
from custom_components.ecoflow_cloud.entities import BaseSensorEntity
from custom_components.ecoflow_cloud.number import MaxBatteryLevelEntity, MinBatteryLevelEntity, SetTempEntity
from custom_components.ecoflow_cloud.select import DictSelectEntity
from custom_components.ecoflow_cloud.sensor import (
    AmpSensorEntity,
    CapacitySensorEntity,
    CyclesSensorEntity,
    FanSensorEntity,
    InWattsSensorEntity,
    LevelSensorEntity,
    MilliVoltSensorEntity,
    MiscSensorEntity,
    OutWattsSensorEntity,
    QuotaStatusSensorEntity,
    RemainSensorEntity,
    TempSensorEntity,
    VoltSensorEntity,
)
from custom_components.ecoflow_cloud.switch import EnabledEntity, InvertedBeeperEntity

_LOGGER = logging.getLogger(__name__)

BATTERY_PROTECTION_OPTIONS = {
    "Off": 0,
    "Low": 3,
    "Medium": 2,
    "High": 1,
}

DEVICE_STANDBY_OPTIONS = {
    "30 min": 1800,
    "1 hr": 3600,
    "2 hr": 7200,
    "4 hr": 14400,
    "12 hr": 43200,
    "24 hr": 86400,
    "Never": 0,
}

CONFIG_WRITE_FIELDS: dict[str, tuple[str, str]] = {
    "enBeep": ("en_beep", "int"),
    "devStandbyTime": ("dev_standby_time", "int"),
    "cmsMaxChgSoc": ("cms_max_chg_soc", "int"),
    "cmsMinDsgSoc": ("cms_min_dsg_soc", "int"),
    "standby": ("standby", "int"),
    "setPointLeft": ("set_point_left", "float"),
    "setPointRight": ("set_point_right", "float"),
    "childLock": ("child_lock", "int"),
    "simpleMode": ("simple_mode", "int"),
    "batProtect": ("bat_protect", "int"),
    "coolingMode": ("cooling_mode", "int"),
    "tempAlert": ("temp_alert", "int"),
}

PACKET_TYPES: dict[tuple[int, int], tuple[str, type[Any]]] = {
    (32, 2): ("CMSHeartBeatReport", glacier_classic_pb2.GlacierClassicCMSHeartBeatReport),
    (32, 50): ("BMSHeartBeatReport", glacier_classic_pb2.GlacierClassicBMSHeartBeatReport),
    (254, 21): ("DisplayPropertyUpload", glacier_classic_pb2.GlacierClassicDisplayPropertyUpload),
    (254, 22): ("RuntimePropertyUpload", glacier_classic_pb2.GlacierClassicRuntimePropertyUpload),
    (254, 18): ("ConfigWriteAck", glacier_classic_pb2.GlacierClassicDisplayPropertyUpload),
    (254, 17): ("SetCommand", glacier_classic_pb2.GlacierClassicSetCommand),
}


def _normalize_temp_unit(raw_value: Any) -> str | None:
    if raw_value is None:
        return None
    text = str(raw_value).strip().lower()
    if text in {"2", "f", "fahrenheit"}:
        return "fahrenheit"
    if text in {"0", "1", "c", "celsius", "false", "true"}:
        return "celsius"
    return None


class GlacierClassicDebugSensorEntity(MiscSensorEntity):
    """Debug sensor that exposes decoded packet details as attributes."""

    def __init__(self, client: EcoflowApiClient, device: BaseInternalDevice):
        super().__init__(client, device, "debug.packet_ts", "Protobuf Debug", enabled=False)

    @property
    def extra_state_attributes(self):
        attrs = dict(super().extra_state_attributes or {})
        params = self._device.data.params
        for key, value in params.items():
            if key.startswith("debug."):
                attrs[key.removeprefix("debug.")] = value
        return attrs


class GlacierClassicChargingStateSensorEntity(BaseSensorEntity):
    """Sensor for battery charging state."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:battery-charging"

    def _updated(self, data: dict[str, Any]):
        in_watts = float(data.get("bms_bmsStatus.inWatts", 0) or 0)
        out_watts = float(data.get("bms_bmsStatus.outWatts", 0) or 0)
        raw_state = data.get("bms_emsStatus.chgState", 0)
        if in_watts >= 3:
            state = "charging"
        elif out_watts >= 3:
            state = "discharging"
        else:
            fallback = {0: "idle", 1: "idle", 2: "idle", 3: "idle", 4: "error"}
            state = fallback.get(int(raw_state), str(raw_state))
        if self._attr_native_value != state:
            self._attr_native_value = state
            self.schedule_update_ha_state()


class GlacierClassicTemperatureSensorEntity(TempSensorEntity):
    """Temperature sensor that tracks the device-reported unit."""

    def _is_fahrenheit(self) -> bool:
        return _normalize_temp_unit(self._device.data.params.get("pd.tmpUnit")) == "fahrenheit"

    def _current_unit(self) -> UnitOfTemperature:
        if self._is_fahrenheit():
            return UnitOfTemperature.FAHRENHEIT
        return UnitOfTemperature.CELSIUS

    @property
    def native_unit_of_measurement(self) -> UnitOfTemperature | None:
        return self._current_unit()

    def _update_value(self, val: Any) -> bool:
        self._attr_native_unit_of_measurement = self._current_unit()
        return super()._update_value(round(float(val), 1))

    def _updated(self, data: dict[str, Any]):
        previous_unit = self._attr_native_unit_of_measurement
        self._attr_native_unit_of_measurement = self._current_unit()
        super()._updated(data)
        if previous_unit != self._attr_native_unit_of_measurement:
            self.schedule_update_ha_state()


class GlacierClassicSetTempEntity(SetTempEntity):
    """Setpoint entity that tracks the device-reported unit."""

    def _current_unit(self) -> UnitOfTemperature:
        if _normalize_temp_unit(self._device.data.params.get("pd.tmpUnit")) == "fahrenheit":
            return UnitOfTemperature.FAHRENHEIT
        return UnitOfTemperature.CELSIUS

    @property
    def native_unit_of_measurement(self) -> UnitOfTemperature | None:
        return self._current_unit()

    def _update_value(self, val: Any) -> bool:
        self._attr_native_unit_of_measurement = self._current_unit()
        return super()._update_value(val)

    def _updated(self, data: dict[str, Any]):
        previous_unit = self._attr_native_unit_of_measurement
        self._attr_native_unit_of_measurement = self._current_unit()
        super()._updated(data)
        if previous_unit != self._attr_native_unit_of_measurement:
            self.schedule_update_ha_state()


class GlacierClassicTemperatureUnitSensorEntity(MiscSensorEntity):
    """Sensor that exposes the human-readable temperature unit."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def _update_value(self, val: Any) -> bool:
        normalized = _normalize_temp_unit(val)
        if normalized == "fahrenheit":
            label = "Fahrenheit"
        elif normalized == "celsius":
            label = "Celsius"
        else:
            label = f"Unknown ({val})"
        return super()._update_value(label)


class InvertedMiscBinarySensorEntity(MiscBinarySensorEntity):
    """Binary sensor entity with inverted device semantics."""

    def _update_value(self, val: Any) -> bool:
        self._attr_is_on = not bool(val)
        return True


class GlacierClassicPrimaryTemperatureSensorEntity(GlacierClassicTemperatureSensorEntity):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._attr_entity_category = cast(Any, None)


class GlacierClassicControlSetTempEntity(GlacierClassicSetTempEntity):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._attr_entity_category = cast(Any, None)


class GlacierClassicCommandMessage(PrivateAPIMessageProtocol):
    """Message wrapper for Glacier Classic protobuf commands."""

    def __init__(
        self,
        payload: glacier_classic_pb2.GlacierClassicSetCommand,
        packet: glacier_classic_pb2.GlacierClassicSendHeaderMsg,
    ) -> None:
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


def _create_glacier_classic_proto_command(field_name: str, value: int | float, device_sn: str):
    """Create a protobuf command for Glacier Classic."""

    proto_field_name, value_kind = CONFIG_WRITE_FIELDS[field_name]
    payload = glacier_classic_pb2.GlacierClassicSetCommand()
    try:
        if value_kind == "float":
            setattr(payload, proto_field_name, float(value))
        else:
            setattr(payload, proto_field_name, int(value))
    except AttributeError:
        _LOGGER.error("Unknown Glacier Classic set field: %s", field_name)
        return None
    pdata = payload.SerializeToString()

    packet = glacier_classic_pb2.GlacierClassicSendHeaderMsg()
    message = packet.msg.add()
    message.pdata = pdata
    message.src = 32
    message.dest = 66
    message.d_src = 1
    message.d_dest = 1
    message.check_type = 3
    message.cmd_func = 254
    message.cmd_id = 17
    message.data_len = len(pdata)
    message.need_ack = 1
    message.seq = Message.gen_seq()
    message.version = 19
    message.payload_ver = 1
    setattr(message, "from", "Android")
    message.device_sn = device_sn
    return GlacierClassicCommandMessage(payload, packet)


class GlacierClassic(BaseInternalDevice):
    """EcoFlow Glacier Classic device implementation using protobuf decoding."""

    @override
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            LevelSensorEntity(client, self, "bms_bmsStatus.soc", const.MAIN_BATTERY_LEVEL)
            .attr("bms_bmsStatus.socPrecise", "Battery SOC Precise", 0)
            .attr("bms_bmsStatus.soh", const.SOH, 0)
            .attr("bms_emsStatus.maxChargeSoc", "Battery Max Charge SOC", 0)
            .attr("bms_emsStatus.minDischargeSoc", "Battery Min Discharge SOC", 0),
            CapacitySensorEntity(client, self, "bms_bmsStatus.designCap", const.MAIN_DESIGN_CAPACITY, False),
            CapacitySensorEntity(client, self, "bms_bmsStatus.fullCap", const.MAIN_FULL_CAPACITY, False),
            CapacitySensorEntity(client, self, "bms_bmsStatus.remainCap", const.MAIN_REMAIN_CAPACITY, False),
            LevelSensorEntity(client, self, "bms_emsStatus.f32LcdSoc", const.COMBINED_BATTERY_LEVEL),
            GlacierClassicChargingStateSensorEntity(
                client, self, "bms_emsStatus.chgState", const.BATTERY_CHARGING_STATE
            ),
            FanSensorEntity(client, self, "bms_emsStatus.fanLvl", "Fan Level"),
            InWattsSensorEntity(client, self, "bms_bmsStatus.inWatts", const.TOTAL_IN_POWER),
            OutWattsSensorEntity(client, self, "bms_bmsStatus.outWatts", const.TOTAL_OUT_POWER),
            RemainSensorEntity(client, self, "bms_emsStatus.chgRemain", const.CHARGE_REMAINING_TIME),
            RemainSensorEntity(client, self, "bms_emsStatus.dsgRemain", const.DISCHARGE_REMAINING_TIME),
            RemainSensorEntity(client, self, "bms_bmsStatus.remainTime", "Battery Remaining Time", False),
            CyclesSensorEntity(client, self, "bms_bmsStatus.cycles", const.CYCLES),
            GlacierClassicTemperatureSensorEntity(client, self, "bms_bmsStatus.tmp", const.BATTERY_TEMP)
            .attr("bms_bmsStatus.minCellTmp", const.ATTR_MIN_CELL_TEMP, 0)
            .attr("bms_bmsStatus.maxCellTmp", const.ATTR_MAX_CELL_TEMP, 0),
            GlacierClassicTemperatureSensorEntity(
                client, self, "bms_bmsStatus.minMosTmp", "Min MOS Temperature", False
            ),
            GlacierClassicTemperatureSensorEntity(
                client, self, "bms_bmsStatus.maxMosTmp", "Max MOS Temperature", False
            ),
            GlacierClassicPrimaryTemperatureSensorEntity(client, self, "pd.tmpL", "Left Temperature", False),
            GlacierClassicPrimaryTemperatureSensorEntity(client, self, "pd.tmpR", "Right Temperature", False),
            GlacierClassicPrimaryTemperatureSensorEntity(
                client, self, "pd.tmpM", "Combined Temperature", False
            ),
            GlacierClassicTemperatureSensorEntity(
                client, self, "pd.batTemp", "Battery Pack Temperature", False
            ),
            VoltSensorEntity(client, self, "pd.inputVolts", "Input Voltage", False),
            VoltSensorEntity(client, self, "bms_bmsStatus.vol", const.BATTERY_VOLT, False)
            .attr("bms_bmsStatus.minCellVol", const.ATTR_MIN_CELL_VOLT, 0)
            .attr("bms_bmsStatus.maxCellVol", const.ATTR_MAX_CELL_VOLT, 0),
            MilliVoltSensorEntity(client, self, "bms_bmsStatus.minCellVol", const.MIN_CELL_VOLT, False),
            MilliVoltSensorEntity(client, self, "bms_bmsStatus.maxCellVol", const.MAX_CELL_VOLT, False),
            AmpSensorEntity(client, self, "bms_bmsStatus.amp", "Battery Current", False),
            AmpSensorEntity(client, self, "bms_bmsStatus.tagChgAmp", "Target Charge Current", False),
            LevelSensorEntity(client, self, "bms_bmsStatus.actSoc", "Actual Battery SOC", False),
            LevelSensorEntity(client, self, "bms_bmsStatus.diffSoc", "Battery SOC Delta", False),
            LevelSensorEntity(client, self, "bms_bmsStatus.targetSoc", "Target Battery SOC", False),
            MiscSensorEntity(client, self, "pd.blTime", "Screen Off Time", False),
            MiscSensorEntity(client, self, "pd.devStandbyTime", "Device Standby Time", False),
            MiscSensorEntity(
                client,
                self,
                "runtime.runtime_property_full_upload_period",
                "Runtime Full Upload Period",
                False,
            ),
            MiscSensorEntity(
                client,
                self,
                "runtime.runtime_property_incremental_upload_period",
                "Runtime Incremental Upload Period",
                False,
            ),
            MiscSensorEntity(
                client,
                self,
                "runtime.display_property_full_upload_period",
                "Display Full Upload Period",
                False,
            ),
            MiscSensorEntity(
                client,
                self,
                "runtime.display_property_incremental_upload_period",
                "Display Incremental Upload Period",
                False,
            ),
            MiscSensorEntity(client, self, "diag.bmsFault", "BMS Fault Code", False),
            MiscSensorEntity(client, self, "diag.bmsErrorCode", "BMS Error Code", False),
            MiscSensorEntity(client, self, "diag.pdErrorCode", "PD Error Code", False),
            MiscSensorEntity(client, self, "diag.allErrorCode", "All Error Code", False),
            MiscSensorEntity(client, self, "diag.allBmsFault", "All BMS Fault", False),
            MiscSensorEntity(client, self, "diag.bqSysStatReg", "BQ System Status Register", False),
            MiscSensorEntity(client, self, "diag.bmsSn", "BMS Serial", False),
            MiscSensorEntity(client, self, "diag.bmsMainSn", "Main BMS Serial", False),
            MiscSensorEntity(client, self, "diag.hwVer", "BMS Hardware Version", False),
            MiscSensorEntity(client, self, "diag.bmsWarningState", "BMS Warning State", False),
            MiscSensorEntity(client, self, "diag.openBmsIdx", "Open BMS Index", False),
            MiscSensorEntity(client, self, "diag.maxAvailableNum", "Max Available Modules", False),
            GlacierClassicTemperatureUnitSensorEntity(client, self, "pd.tmpUnit", "Temperature Unit", False),
            MiscSensorEntity(client, self, "pd.tmpUnit", "Temperature Unit Raw", False),
            QuotaStatusSensorEntity(client, self),
            GlacierClassicDebugSensorEntity(client, self),
        ]

    @override
    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        device = self
        return [
            GlacierClassicControlSetTempEntity(
                client,
                self,
                "pd.tmpLSet",
                "Left Set Temperature",
                -20,
                20,
                lambda value: _create_glacier_classic_proto_command(
                    "setPointLeft", int(value), device.device_data.sn
                ),
            ),
            GlacierClassicControlSetTempEntity(
                client,
                self,
                "pd.tmpRSet",
                "Right Set Temperature",
                -20,
                20,
                lambda value: _create_glacier_classic_proto_command(
                    "setPointRight", int(value), device.device_data.sn
                ),
            ),
            MaxBatteryLevelEntity(
                client,
                self,
                "bms_emsStatus.maxChargeSoc",
                const.MAX_CHARGE_LEVEL,
                50,
                100,
                lambda value: _create_glacier_classic_proto_command(
                    "cmsMaxChgSoc", int(value), device.device_data.sn
                ),
            ),
            MinBatteryLevelEntity(
                client,
                self,
                "bms_emsStatus.minDischargeSoc",
                const.MIN_DISCHARGE_LEVEL,
                0,
                50,
                lambda value: _create_glacier_classic_proto_command(
                    "cmsMinDsgSoc", int(value), device.device_data.sn
                ),
            ),
        ]

    @override
    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        device = self
        return [
            InvertedBeeperEntity(
                client,
                self,
                "pd.beepEn",
                const.BEEPER,
                lambda value: _create_glacier_classic_proto_command(
                    "enBeep", value, device.device_data.sn
                ),
            ),
            EnabledEntity(
                client,
                self,
                "pd.coolMode",
                "Eco Mode",
                lambda value: _create_glacier_classic_proto_command(
                    "coolingMode", value, device.device_data.sn
                ),
            ),
            EnabledEntity(
                client,
                self,
                "pd.childLock",
                "Child Lock",
                lambda value: _create_glacier_classic_proto_command(
                    "childLock", value, device.device_data.sn
                ),
            ),
            EnabledEntity(
                client,
                self,
                "pd.simpleMode",
                "Simple Mode",
                lambda value: _create_glacier_classic_proto_command(
                    "simpleMode", value, device.device_data.sn
                ),
            ),
            EnabledEntity(
                client,
                self,
                "pd.tempAlert",
                "Temperature Alert",
                lambda value: _create_glacier_classic_proto_command(
                    "tempAlert", value, device.device_data.sn
                ),
            ).with_category(EntityCategory.CONFIG),
        ]

    @override
    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        device = self
        return [
            DictSelectEntity(
                client,
                self,
                "pd.powerPbLevel",
                "Battery Protection",
                BATTERY_PROTECTION_OPTIONS,
                lambda value: _create_glacier_classic_proto_command(
                    "batProtect", value, device.device_data.sn
                ),
            ),
            DictSelectEntity(
                client,
                self,
                "pd.devStandbyTime",
                "Device Standby Time",
                DEVICE_STANDBY_OPTIONS,
                lambda value: _create_glacier_classic_proto_command(
                    "devStandbyTime", value, device.device_data.sn
                ),
            ),
        ]

    @override
    def binary_sensors(self, client: EcoflowApiClient) -> list[BinarySensorEntity]:
        return [
            InvertedMiscBinarySensorEntity(client, self, "pd.flagTwoZone", "Dual Zone Mode"),
            MiscBinarySensorEntity(client, self, "pd.lidStatus", "Lid Status").with_device_class("door"),
            MiscBinarySensorEntity(client, self, "pd.pvFlag", "External Supply Connected").with_device_class("plug"),
        ]

    @override
    def buttons(self, client: EcoflowApiClient) -> list[ButtonEntity]:
        return []

    def _decode_header_message(self, raw_data: bytes) -> dict[str, Any] | None:
        """Decode HeaderMessage and extract header info."""
        try:
            header_msg = glacier_classic_pb2.GlacierClassicSendHeaderMsg()
            header_msg.ParseFromString(raw_data)
            if not header_msg.msg:
                return None

            header = header_msg.msg[0]
            return {
                "src": getattr(header, "src", 0),
                "dest": getattr(header, "dest", 0),
                "dSrc": getattr(header, "d_src", 0),
                "dDest": getattr(header, "d_dest", 0),
                "encType": getattr(header, "enc_type", 0),
                "checkType": getattr(header, "check_type", 0),
                "cmdFunc": getattr(header, "cmd_func", 0),
                "cmdId": getattr(header, "cmd_id", 0),
                "dataLen": getattr(header, "data_len", 0),
                "needAck": getattr(header, "need_ack", 0),
                "seq": getattr(header, "seq", 0),
                "productId": getattr(header, "product_id", 0),
                "version": getattr(header, "version", 0),
                "payloadVer": getattr(header, "payload_ver", 0),
                "header_obj": header,
                "header_msg": header_msg,
            }
        except Exception as e:
            _LOGGER.debug("[GlacierClassic] Failed to parse header message: %s", e)
            return None

    def _build_header_info(self, header_obj: Any) -> dict[str, Any]:
        """Build a header metadata dictionary for a single message frame."""

        return {
            "src": getattr(header_obj, "src", 0),
            "dest": getattr(header_obj, "dest", 0),
            "dSrc": getattr(header_obj, "d_src", 0),
            "dDest": getattr(header_obj, "d_dest", 0),
            "encType": getattr(header_obj, "enc_type", 0),
            "checkType": getattr(header_obj, "check_type", 0),
            "cmdFunc": getattr(header_obj, "cmd_func", 0),
            "cmdId": getattr(header_obj, "cmd_id", 0),
            "dataLen": getattr(header_obj, "data_len", 0),
            "needAck": getattr(header_obj, "need_ack", 0),
            "seq": getattr(header_obj, "seq", 0),
            "productId": getattr(header_obj, "product_id", 0),
            "version": getattr(header_obj, "version", 0),
            "payloadVer": getattr(header_obj, "payload_ver", 0),
            "header_obj": header_obj,
        }

    def _extract_payload_data(self, header_obj: Any) -> bytes | None:
        """Extract payload bytes from header."""
        try:
            pdata = getattr(header_obj, "pdata", b"")
            return bytes(pdata) if pdata else None
        except Exception as e:
            _LOGGER.debug("[GlacierClassic] Failed to extract payload data: %s", e)
            return None

    def _perform_xor_decode(self, pdata: bytes, header_info: dict[str, Any]) -> bytes:
        """Perform XOR decoding if required by header info."""
        enc_type = header_info.get("encType", 0)
        src = header_info.get("src", 0)
        seq = header_info.get("seq", 0)
        if enc_type == 1 and src != 32:
            return self._xor_decode_pdata(pdata, seq)
        return pdata

    def _xor_decode_pdata(self, pdata: bytes, seq: int) -> bytes:
        if not pdata:
            return b""
        decoded_payload = bytearray()
        for byte_val in pdata:
            decoded_payload.append((byte_val ^ seq) & 0xFF)
        return bytes(decoded_payload)

    def _protobuf_to_dict(self, protobuf_obj: Any) -> dict[str, Any]:
        return MessageToDict(protobuf_obj, preserving_proto_field_name=True)

    def _get_packet_type(self, header_info: dict[str, Any]) -> tuple[str, type[Any] | None]:
        """Look up the protobuf type for a packet header."""

        cmd_func = header_info.get("cmdFunc", 0)
        cmd_id = header_info.get("cmdId", 0)
        return PACKET_TYPES.get((cmd_func, cmd_id), ("Unknown", None))

    def _decode_message_by_type(self, pdata: bytes, header_info: dict[str, Any]) -> dict[str, Any]:
        """Decode protobuf message based on cmdFunc/cmdId."""

        cmd_func = header_info.get("cmdFunc", 0)
        cmd_id = header_info.get("cmdId", 0)
        packet_name, packet_type = self._get_packet_type(header_info)
        if packet_type is None:
            return {}
        try:
            payload = packet_type()
            payload.ParseFromString(pdata)
            return self._protobuf_to_dict(payload)
        except Exception:
            _LOGGER.debug(
                "[GlacierClassic] Failed to parse packet cmd_func=%s cmd_id=%s",
                cmd_func,
                cmd_id,
                exc_info=True,
            )
            return {}

    def _map_packet_data(self, packet_name: str, packet_data: dict[str, Any]) -> dict[str, Any]:
        """Map a decoded protobuf packet into the legacy entity key space."""

        if packet_name == "BMSHeartBeatReport":
            return self._map_bms(packet_data)
        if packet_name == "CMSHeartBeatReport":
            return self._map_cms(packet_data)
        if packet_name in {"DisplayPropertyUpload", "ConfigWriteAck"}:
            return self._map_display(packet_data)
        if packet_name == "RuntimePropertyUpload":
            return self._map_runtime(packet_data)
        return {}

    def _create_debug_payload(
        self,
        raw_data: bytes,
        packet_ts: int,
        decoded_packets: list[dict[str, Any]],
        error: str | None = None,
    ) -> dict[str, Any]:
        """Create the flattened debug payload stored in params."""

        debug_data: dict[str, Any] = {
            "packet_ts": packet_ts,
            "raw_hex": raw_data.hex(),
        }
        if error is not None:
            debug_data["error"] = error
        else:
            debug_data["message_count"] = len(decoded_packets)
            debug_data["messages"] = str(decoded_packets)

        return self._flatten_dict({"debug": debug_data})

    @override
    def _prepare_data(self, raw_data: bytes) -> dict[str, Any]:
        """Prepare Glacier Classic data by decoding protobuf and flattening fields."""
        packet_ts = int(time.time())
        flat_dict: dict[str, Any] = {}
        decoded_packets: list[dict[str, Any]] = []
        try:
            header_info = self._decode_header_message(raw_data)
            if not header_info:
                return super()._prepare_data(raw_data)

            header_msg = header_info["header_msg"]
            for header in header_msg.msg:
                current_header_info = self._build_header_info(header)
                pdata = self._extract_payload_data(header)
                if not pdata:
                    continue

                decoded_pdata = self._perform_xor_decode(pdata, current_header_info)
                packet_name, _ = self._get_packet_type(current_header_info)
                packet_data = self._decode_message_by_type(decoded_pdata, current_header_info)

                cmd_func = int(current_header_info["cmdFunc"] or 0)
                cmd_id = int(current_header_info["cmdId"] or 0)
                header_dict = self._protobuf_to_dict(header)
                header_dict.pop("pdata", None)
                decoded_packets.append(
                    {
                        "cmd_func": cmd_func,
                        "cmd_id": cmd_id,
                        "name": packet_name,
                        "header": header_dict,
                        "data": packet_data,
                        "raw_hex": decoded_pdata.hex(),
                    }
                )
                flat_dict.update(self._map_packet_data(packet_name, packet_data))

            flat_dict.update(self._create_debug_payload(raw_data, packet_ts, decoded_packets))
        except Exception:
            _LOGGER.warning("[GlacierClassic] Data processing failed", exc_info=True)
            flat_dict.update(self._create_debug_payload(raw_data, packet_ts, decoded_packets, "decode_failed"))
        return {"params": flat_dict, "all_fields": {"packets": decoded_packets}}

    def _map_bms(self, payload: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {"bms_bmsStatus": {}}
        bms = result["bms_bmsStatus"]
        if "soc" in payload:
            bms["soc"] = int(payload["soc"])
        if "f32_show_soc" in payload:
            bms["socPrecise"] = round(float(payload["f32_show_soc"]), 2)
        elif "soc" in payload:
            bms["socPrecise"] = float(payload["soc"])
        if "design_cap" in payload:
            bms["designCap"] = int(payload["design_cap"])
        if "remain_cap" in payload:
            bms["remainCap"] = int(payload["remain_cap"])
        if "full_cap" in payload:
            bms["fullCap"] = int(payload["full_cap"])
        if "cycles" in payload:
            bms["cycles"] = int(payload["cycles"])
        if "soh" in payload:
            bms["soh"] = int(payload["soh"])
        if "vol" in payload:
            bms["vol"] = round(int(payload["vol"]) / 1000, 3)
        if "amp" in payload:
            bms["amp"] = round(int(payload["amp"]) / 1000, 3)
        if "min_cell_vol" in payload:
            bms["minCellVol"] = int(payload["min_cell_vol"])
        if "max_cell_vol" in payload:
            bms["maxCellVol"] = int(payload["max_cell_vol"])
        if "temp" in payload:
            bms["tmp"] = int(payload["temp"])
        if "min_cell_temp" in payload:
            bms["minCellTmp"] = int(payload["min_cell_temp"])
        if "max_cell_temp" in payload:
            bms["maxCellTmp"] = int(payload["max_cell_temp"])
        if "min_mos_temp" in payload:
            bms["minMosTmp"] = int(payload["min_mos_temp"])
        if "max_mos_temp" in payload:
            bms["maxMosTmp"] = int(payload["max_mos_temp"])
        if "input_watts" in payload:
            bms["inWatts"] = int(payload["input_watts"])
        if "output_watts" in payload:
            bms["outWatts"] = int(payload["output_watts"])
        if "remain_time" in payload:
            bms["remainTime"] = int(payload["remain_time"])
        if "tag_chg_amp" in payload:
            bms["tagChgAmp"] = round(int(payload["tag_chg_amp"]) / 1000, 3)
        if "act_soc" in payload:
            bms["actSoc"] = round(float(payload["act_soc"]), 2)
        if "diff_soc" in payload:
            bms["diffSoc"] = round(float(payload["diff_soc"]), 2)
        if "target_soc" in payload:
            bms["targetSoc"] = round(float(payload["target_soc"]), 2)
        if "bms_fault" in payload:
            result.setdefault("diag", {})["bmsFault"] = int(payload["bms_fault"])
        if "err_code" in payload:
            result.setdefault("diag", {})["bmsErrorCode"] = int(payload["err_code"])
        if "all_err_code" in payload:
            result.setdefault("diag", {})["allErrorCode"] = int(payload["all_err_code"])
        if "all_bms_fault" in payload:
            result.setdefault("diag", {})["allBmsFault"] = int(payload["all_bms_fault"])
        if "bq_sys_stat_reg" in payload:
            result.setdefault("diag", {})["bqSysStatReg"] = int(payload["bq_sys_stat_reg"])
        if "bms_sn" in payload:
            result.setdefault("diag", {})["bmsSn"] = payload["bms_sn"]
        if "pack_sn" in payload:
            result.setdefault("diag", {})["packSn"] = payload["pack_sn"]
        if "hw_ver" in payload:
            result.setdefault("diag", {})["hwVer"] = payload["hw_ver"]
        return self._flatten_dict(result)

    def _map_cms(self, payload: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {"bms_emsStatus": {}}
        v1p0 = payload.get("v1p0", {})
        if not isinstance(v1p0, dict):
            return {}
        ems = result["bms_emsStatus"]
        if "chg_state" in v1p0:
            ems["chgState"] = int(v1p0["chg_state"])
        if "fan_level" in v1p0:
            ems["fanLvl"] = int(v1p0["fan_level"])
        if "max_charge_soc" in v1p0:
            ems["maxChargeSoc"] = int(v1p0["max_charge_soc"])
        if "min_dsg_soc" in v1p0:
            ems["minDischargeSoc"] = int(v1p0["min_dsg_soc"])
        if "chg_remain_time" in v1p0:
            ems["chgRemain"] = int(v1p0["chg_remain_time"])
        if "dsg_remain_time" in v1p0:
            ems["dsgRemain"] = int(v1p0["dsg_remain_time"])
        if "lcd_show_soc" in v1p0:
            ems["lcdSoc"] = int(v1p0["lcd_show_soc"])
        if "f32_lcd_show_soc" in v1p0:
            ems["f32LcdSoc"] = round(float(v1p0["f32_lcd_show_soc"]), 2)
        if "chg_cmd" in v1p0:
            ems["chgCmd"] = int(v1p0["chg_cmd"])
        if "dsg_cmd" in v1p0:
            ems["dsgCmd"] = int(v1p0["dsg_cmd"])
        if "bms_warning_state" in v1p0:
            result.setdefault("diag", {})["bmsWarningState"] = int(v1p0["bms_warning_state"])
        if "open_bms_idx" in v1p0:
            result.setdefault("diag", {})["openBmsIdx"] = int(v1p0["open_bms_idx"])
        if "max_available_num" in v1p0:
            result.setdefault("diag", {})["maxAvailableNum"] = int(v1p0["max_available_num"])
        return self._flatten_dict(result)

    def _map_display(self, payload: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {"pd": {}, "bms_emsStatus": {}, "bms_bmsStatus": {}}
        pd = result["pd"]
        ems = result["bms_emsStatus"]
        bms = result["bms_bmsStatus"]
        if "en_beep" in payload:
            pd["beepEn"] = int(payload["en_beep"])
        if "screen_off_time" in payload:
            pd["blTime"] = int(payload["screen_off_time"])
        if "dev_standby_time" in payload:
            pd["devStandbyTime"] = int(payload["dev_standby_time"])
        if "set_point_left" in payload:
            pd["tmpLSet"] = round(float(payload["set_point_left"]), 1)
            pd.setdefault("tmpMSet", pd["tmpLSet"])
        if "set_point_right" in payload:
            pd["tmpRSet"] = round(float(payload["set_point_right"]), 1)
        if "temp_monitor_left" in payload:
            pd["tmpL"] = round(float(payload["temp_monitor_left"]), 1)
            pd.setdefault("tmpM", pd["tmpL"])
        if "temp_monitor_right" in payload:
            pd["tmpR"] = round(float(payload["temp_monitor_right"]), 1)
        if "bat_protect" in payload:
            pd["powerPbLevel"] = int(payload["bat_protect"])
        if "cooling_mode" in payload:
            pd["coolMode"] = int(payload["cooling_mode"])
        if "temp_unit" in payload:
            pd["tmpUnit"] = int(payload["temp_unit"])
        if "child_lock" in payload:
            pd["childLock"] = int(payload["child_lock"])
        if "simple_mode" in payload:
            pd["simpleMode"] = int(payload["simple_mode"])
        if "temp_alert" in payload:
            pd["tempAlert"] = int(payload["temp_alert"])
        if "zone_status" in payload:
            pd["flagTwoZone"] = int(payload["zone_status"])
        if "lid_status" in payload:
            pd["lidStatus"] = int(payload["lid_status"])
        if "input_volt777" in payload:
            pd["inputVolts"] = round(float(payload["input_volt777"]), 2)
        if "bat_temp102" in payload:
            pd["batTemp"] = int(payload["bat_temp102"])
        if "plug_in_info_pv_flag" in payload:
            pd["pvFlag"] = int(payload["plug_in_info_pv_flag"])
        if "plug_in_info_pv_type" in payload:
            pd["pvType"] = int(payload["plug_in_info_pv_type"])
        if "plug_in_info_dcp_in_flag" in payload:
            pd["dcpInFlag"] = int(payload["plug_in_info_dcp_in_flag"])
        if "pd_err_code" in payload:
            result.setdefault("diag", {})["pdErrorCode"] = int(payload["pd_err_code"])
        if "bms_err_code" in payload:
            result.setdefault("diag", {})["bmsErrorCode"] = int(payload["bms_err_code"])
        if "bms_main_sn" in payload:
            result.setdefault("diag", {})["bmsMainSn"] = payload["bms_main_sn"]
        if "cms_batt_soc" in payload:
            ems["f32LcdSoc"] = round(float(payload["cms_batt_soc"]), 2)
        if "cms_max_chg_soc" in payload:
            ems["maxChargeSoc"] = int(payload["cms_max_chg_soc"])
        if "cms_min_dsg_soc" in payload:
            ems["minDischargeSoc"] = int(payload["cms_min_dsg_soc"])
        if "cms_chg_rem_time" in payload:
            ems["chgRemain"] = int(payload["cms_chg_rem_time"])
        if "cms_dsg_rem_time" in payload:
            ems["dsgRemain"] = int(payload["cms_dsg_rem_time"])
        if "cms_chg_dsg_state" in payload:
            ems["chgState"] = int(payload["cms_chg_dsg_state"])
        if "pow_in_sum_w" in payload:
            bms["inWatts"] = round(float(payload["pow_in_sum_w"]))
        if "pow_out_sum_w" in payload:
            bms["outWatts"] = round(float(payload["pow_out_sum_w"]))
        if "cms_batt_design_cap" in payload:
            bms["designCap"] = int(payload["cms_batt_design_cap"])
        flattened = self._flatten_dict(result)
        return {key: value for key, value in flattened.items() if value != {}}

    def _map_runtime(self, payload: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {"pd": {}, "runtime": {}}
        if "plug_in_info_ac_in_vol" in payload:
            ac_in_volts = round(float(payload["plug_in_info_ac_in_vol"]), 2)
            result["pd"]["acInVolts"] = ac_in_volts
            result["pd"]["inputVolts"] = ac_in_volts
        for key, value in payload.items():
            if key != "plug_in_info_ac_in_vol":
                result["runtime"][key] = value
        return self._flatten_dict(result)

    def _flatten_dict(self, data: dict[str, Any], parent_key: str = "", sep: str = ".") -> dict[str, Any]:
        items: list[tuple[str, Any]] = []
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, dict):
                items.extend(self._flatten_dict(value, new_key, sep=sep).items())
            else:
                items.append((new_key, value))
        return dict(items)
