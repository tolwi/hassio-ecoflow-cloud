import logging
import struct
import time
from collections.abc import Sequence
from typing import Any, override

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

WIRE_VARINT = 0
WIRE_64BIT = 1
WIRE_LENGTH = 2
WIRE_32BIT = 5

BATTERY_PROTECTION_OPTIONS = {
    "Low": 0,
    "Medium": 1,
    "High": 2,
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


def _normalize_temp_unit(raw_value: Any) -> str | None:
    if raw_value is None:
        return None

    text = str(raw_value).strip().lower()
    if text in {"2", "f", "fahrenheit"}:
        return "fahrenheit"
    if text in {"0", "1", "c", "celsius", "false", "true"}:
        return "celsius"
    return None

HEADER_SPEC = {
    1: ("pdata", "bytes"),
    2: ("src", "int32"),
    3: ("dest", "int32"),
    4: ("d_src", "int32"),
    5: ("d_dest", "int32"),
    6: ("enc_type", "int32"),
    7: ("check_type", "int32"),
    8: ("cmd_func", "int32"),
    9: ("cmd_id", "int32"),
    10: ("data_len", "int32"),
    11: ("need_ack", "int32"),
    12: ("is_ack", "int32"),
    14: ("seq", "int32"),
    15: ("product_id", "int32"),
    16: ("version", "int32"),
    17: ("payload_ver", "int32"),
    18: ("time_snap", "int32"),
    19: ("is_rw_cmd", "int32"),
    20: ("is_queue", "int32"),
    21: ("ack_type", "int32"),
    22: ("code", "string"),
    23: ("from", "string"),
    24: ("module_sn", "string"),
    25: ("device_sn", "string"),
}

TOP_LEVEL_SPEC = {
    1: ("msg", ("message", HEADER_SPEC), True),
}

BMS_HEARTBEAT_SPEC = {
    1: ("num", "uint32"),
    3: ("cell_id", "uint32"),
    4: ("err_code", "uint32"),
    5: ("sys_ver", "uint32"),
    6: ("soc", "uint32"),
    7: ("vol", "uint32"),
    8: ("amp", "int32"),
    9: ("temp", "int32"),
    10: ("open_bms_flag", "uint32"),
    11: ("design_cap", "uint32"),
    12: ("remain_cap", "uint32"),
    13: ("full_cap", "uint32"),
    14: ("cycles", "uint32"),
    15: ("soh", "uint32"),
    16: ("max_cell_vol", "uint32"),
    17: ("min_cell_vol", "uint32"),
    18: ("max_cell_temp", "int32"),
    19: ("min_cell_temp", "int32"),
    20: ("max_mos_temp", "int32"),
    21: ("min_mos_temp", "int32"),
    22: ("bms_fault", "uint32"),
    23: ("bq_sys_stat_reg", "uint32"),
    24: ("tag_chg_amp", "uint32"),
    25: ("f32_show_soc", "float"),
    26: ("input_watts", "uint32"),
    27: ("output_watts", "uint32"),
    28: ("remain_time", "uint32"),
    29: ("mos_state", "uint32"),
    30: ("balance_state", "uint32"),
    31: ("max_vol_diff", "uint32"),
    32: ("cell_series_num", "uint32"),
    33: ("cell_vol", "uint32", True),
    35: ("cell_temp", "int32", True),
    36: ("hw_ver", "string"),
    39: ("bms_sn", "string"),
    42: ("act_soc", "float"),
    43: ("diff_soc", "float"),
    44: ("target_soc", "float"),
    48: ("all_err_code", "uint32"),
    49: ("all_bms_fault", "uint32"),
    81: ("pack_sn", "string"),
    82: ("water_in_flag", "uint32"),
}

CMS_V1P0_SPEC = {
    1: ("chg_state", "uint32"),
    2: ("chg_cmd", "uint32"),
    3: ("dsg_cmd", "uint32"),
    5: ("chg_amp", "uint32"),
    6: ("fan_level", "uint32"),
    7: ("max_charge_soc", "uint32"),
    8: ("bms_model", "uint32"),
    9: ("lcd_show_soc", "uint32"),
    10: ("open_ups_flag", "uint32"),
    11: ("bms_warning_state", "uint32"),
    12: ("chg_remain_time", "uint32"),
    13: ("dsg_remain_time", "uint32"),
    14: ("ems_is_normal_flag", "uint32"),
    15: ("f32_lcd_show_soc", "float"),
    16: ("bms_is_connt", "uint32", True),
    17: ("max_available_num", "uint32"),
    18: ("open_bms_idx", "uint32"),
    19: ("para_vol_min", "uint32"),
    20: ("para_vol_max", "uint32"),
    21: ("min_dsg_soc", "uint32"),
    22: ("min_open_oil_eb_soc", "uint32"),
    23: ("max_close_oil_eb_soc", "uint32"),
}

CMS_V1P3_SPEC = {
    1: ("chg_disable_cond", "uint32"),
    2: ("dsg_disable_cond", "uint32"),
    3: ("chg_line_plug_in_flag", "uint32"),
    4: ("sys_chg_dsg_state", "uint32"),
    5: ("ems_heartbeat_ver", "uint32"),
}

CMS_HEARTBEAT_SPEC = {
    1: ("v1p0", ("message", CMS_V1P0_SPEC)),
    2: ("v1p3", ("message", CMS_V1P3_SPEC)),
}

DISPLAY_PROPERTY_SPEC = {
    1: ("errcode", "uint32"),
    2: ("sys_status", "uint32"),
    3: ("pow_in_sum_w", "float"),
    4: ("pow_out_sum_w", "float"),
    17: ("dev_standby_time", "uint32"),
    18: ("screen_off_time", "uint32"),
    102: ("bat_temp102", "uint32"),
    140: ("bms_err_code", "uint32"),
    195: ("en_beep", "uint32"),
    213: ("pd_err_code", "uint32"),
    262: ("cms_batt_soc", "float"),
    268: ("cms_dsg_rem_time", "uint32"),
    269: ("cms_chg_rem_time", "uint32"),
    270: ("cms_max_chg_soc", "uint32"),
    271: ("cms_min_dsg_soc", "uint32"),
    282: ("cms_chg_dsg_state", "uint32"),
    288: ("cms_batt_design_cap", "uint32"),
    362: ("plug_in_info_pv_flag", "uint32"),
    363: ("plug_in_info_pv_type", "uint32"),
    392: ("bms_main_sn", "string"),
    426: ("plug_in_info_dcp_in_flag", "uint32"),
    512: ("temp_unit", "uint32"),
    736: ("set_point_left", "float"),
    737: ("set_point_right", "float"),
    738: ("child_lock", "uint32"),
    739: ("simple_mode", "uint32"),
    740: ("bat_protect", "uint32"),
    741: ("cooling_mode", "uint32"),
    742: ("temp_monitor_left", "float"),
    743: ("temp_monitor_right", "float"),
    744: ("lid_status", "uint32"),
    745: ("zone_status", "uint32"),
    748: ("temp_alert", "uint32"),
    777: ("input_volt777", "float"),
}

RUNTIME_PROPERTY_SPEC = {
    68: ("plug_in_info_ac_in_vol", "float"),
    293: ("display_property_full_upload_period", "int32"),
    294: ("display_property_incremental_upload_period", "int32"),
    295: ("runtime_property_full_upload_period", "int32"),
    296: ("runtime_property_incremental_upload_period", "int32"),
}

CONFIG_WRITE_FIELDS: dict[str, tuple[int, str]] = {
    "enBeep": (9, "int32"),
    "devStandbyTime": (13, "int32"),
    "cmsMaxChgSoc": (33, "int32"),
    "cmsMinDsgSoc": (34, "int32"),
    "standby": (172, "int32"),
    "setPointLeft": (226, "float"),
    "setPointRight": (227, "float"),
    "childLock": (228, "uint32"),
    "simpleMode": (229, "uint32"),
    "batProtect": (230, "uint32"),
    "coolingMode": (231, "uint32"),
    "tempAlert": (234, "uint32"),
}

PACKET_SPECS: dict[tuple[int, int], tuple[str, dict[int, Any]]] = {
    (32, 2): ("CMSHeartBeatReport", CMS_HEARTBEAT_SPEC),
    (32, 50): ("BMSHeartBeatReport", BMS_HEARTBEAT_SPEC),
    (254, 21): ("DisplayPropertyUpload", DISPLAY_PROPERTY_SPEC),
    (254, 22): ("RuntimePropertyUpload", RUNTIME_PROPERTY_SPEC),
    (254, 18): ("ConfigWriteAck", DISPLAY_PROPERTY_SPEC),
}


class GlacierClassicDebugSensorEntity(MiscSensorEntity):
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
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:battery-charging"

    def _updated(self, data: dict[str, Any]):
        in_watts = float(data.get("bms_bmsStatus.inWatts", 0) or 0)
        out_watts = float(data.get("bms_bmsStatus.outWatts", 0) or 0)
        raw_state = data.get("bms_emsStatus.chgState", 0)

        # The Classic's raw charge-state looks like a charger mode/status code,
        # not a direct charging/discharging enum, so prefer real power flow.
        if in_watts >= 3:
            state = "charging"
        elif out_watts >= 3:
            state = "discharging"
        else:
            fallback = {
                0: "idle",
                1: "idle",
                2: "idle",
                3: "idle",
                4: "error",
            }
            state = fallback.get(int(raw_state), str(raw_state))

        if self._attr_native_value != state:
            self._attr_native_value = state
            self.schedule_update_ha_state()


class GlacierClassicTemperatureSensorEntity(TempSensorEntity):
    def _is_fahrenheit(self) -> bool:
        return _normalize_temp_unit(self._device.data.params.get("pd.tmpUnit")) == "fahrenheit"

    def _current_unit(self) -> str:
        if self._is_fahrenheit():
            return UnitOfTemperature.FAHRENHEIT
        return UnitOfTemperature.CELSIUS

    @property
    def native_unit_of_measurement(self) -> str | None:
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
    def _current_unit(self) -> str:
        if _normalize_temp_unit(self._device.data.params.get("pd.tmpUnit")) == "fahrenheit":
            return UnitOfTemperature.FAHRENHEIT
        return UnitOfTemperature.CELSIUS

    @property
    def native_unit_of_measurement(self) -> str | None:
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


class GlacierClassicPowerSourceSensorEntity(MiscSensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:power-plug"

    def _updated(self, data: dict[str, Any]):
        ac_input_voltage = float(
            data.get("pd.acInVolts", data.get("runtime.plug_in_info_ac_in_vol", 0)) or 0
        )
        input_voltage = float(data.get("pd.inputVolts", 0) or 0)
        pv_flag = int(data.get("pd.pvFlag", 0) or 0)
        pv_type = int(data.get("pd.pvType", 0) or 0)
        dcp_flag = int(data.get("pd.dcpInFlag", 0) or 0)

        if pv_flag:
            value = "solar" if pv_type == 0 else f"solar_{pv_type}"
        elif ac_input_voltage > 0:
            value = "ac"
        elif dcp_flag:
            value = "dc"
        elif input_voltage > 0:
            value = "dc"
        else:
            value = "none"

        if self._attr_native_value != value:
            self._attr_native_value = value
            self.schedule_update_ha_state()


class InvertedMiscBinarySensorEntity(MiscBinarySensorEntity):
    def _update_value(self, val: Any) -> bool:
        self._attr_is_on = not bool(val)
        return True


class GlacierClassicPrimaryTemperatureSensorEntity(GlacierClassicTemperatureSensorEntity):
    _attr_entity_category = None


class GlacierClassicControlSetTempEntity(GlacierClassicSetTempEntity):
    _attr_entity_category = None


class GlacierClassicCommandMessage(PrivateAPIMessageProtocol):
    def __init__(self, packet: bytes, fields: dict[str, Any]) -> None:
        self._packet = packet
        self._fields = fields

    @override
    def to_mqtt_payload(self):
        return self._packet

    @override
    def to_dict(self) -> dict:
        return {
            "GlacierClassicConfigWrite": {
                "fields": self._fields,
                "packet_hex": self._packet.hex(),
            }
        }


def _read_varint(data: bytes, offset: int) -> tuple[int, int]:
    result = 0
    shift = 0
    while True:
        if offset >= len(data):
            raise ValueError("Unexpected end of data while reading varint")
        byte = data[offset]
        offset += 1
        result |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return result, offset
        shift += 7
        if shift >= 64:
            raise ValueError("Varint too long")


def _decode_signed(value: int) -> int:
    if value >= 1 << 63:
        return value - (1 << 64)
    return value


def _encode_varint(value: int) -> bytes:
    if value < 0:
        value &= (1 << 64) - 1
    encoded = bytearray()
    while True:
        to_write = value & 0x7F
        value >>= 7
        if value:
            encoded.append(to_write | 0x80)
        else:
            encoded.append(to_write)
            return bytes(encoded)


def _encode_key(field_number: int, wire_type: int) -> bytes:
    return _encode_varint((field_number << 3) | wire_type)


def _encode_field(field_number: int, kind: str, value: Any) -> bytes:
    if kind in {"uint32", "int32"}:
        return _encode_key(field_number, WIRE_VARINT) + _encode_varint(int(value))
    if kind == "float":
        return _encode_key(field_number, WIRE_32BIT) + struct.pack("<f", float(value))
    if kind == "string":
        raw = str(value).encode("utf-8")
        return _encode_key(field_number, WIRE_LENGTH) + _encode_varint(len(raw)) + raw
    raise ValueError(f"Unsupported config field kind: {kind}")


def _decode_message(data: bytes, spec: dict[int, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    offset = 0
    while offset < len(data):
        key, offset = _read_varint(data, offset)
        field_number = key >> 3
        wire_type = key & 0x07

        field_spec = spec.get(field_number)
        if field_spec is None:
            name = f"field_{field_number}"
            kind = None
            repeated = False
        else:
            name = field_spec[0]
            kind = field_spec[1]
            repeated = len(field_spec) > 2 and bool(field_spec[2])

        if wire_type == WIRE_VARINT:
            raw_value, offset = _read_varint(data, offset)
            if kind == "int32":
                value = _decode_signed(raw_value)
            elif kind == "bool":
                value = bool(raw_value)
            else:
                value = raw_value
        elif wire_type == WIRE_32BIT:
            raw = data[offset : offset + 4]
            offset += 4
            if kind == "float":
                value = struct.unpack("<f", raw)[0]
            else:
                value = int.from_bytes(raw, "little")
        elif wire_type == WIRE_64BIT:
            raw = data[offset : offset + 8]
            offset += 8
            value = raw.hex()
        elif wire_type == WIRE_LENGTH:
            length, offset = _read_varint(data, offset)
            raw = data[offset : offset + length]
            offset += length
            if isinstance(kind, tuple) and kind[0] == "message":
                value = _decode_message(raw, kind[1])
            elif kind == "string":
                value = raw.decode("utf-8", errors="ignore")
            elif kind == "bytes" or kind is None:
                value = raw
            else:
                value = raw.hex()
        else:
            raise ValueError(f"Unsupported protobuf wire type {wire_type}")

        if repeated:
            result.setdefault(name, []).append(value)
        else:
            result[name] = value

    return result


def _decode_header_messages(raw_data: bytes) -> list[dict[str, Any]]:
    decoded = _decode_message(raw_data, TOP_LEVEL_SPEC)
    messages = decoded.get("msg", [])
    if not isinstance(messages, list):
        return []

    for message in messages:
        pdata = message.get("pdata")
        if isinstance(pdata, bytes) and int(message.get("enc_type", 0) or 0) == 1 and int(message.get("src", 0) or 0) != 32:
            xor_byte = int(message.get("seq", 0) or 0) & 0xFF
            message["pdata"] = bytes(byte ^ xor_byte for byte in pdata)
    return messages


def _create_glacier_classic_command(field_name: str, value: int | float, device_sn: str):
    field_number, kind = CONFIG_WRITE_FIELDS[field_name]
    payload = _encode_field(field_number, kind, value)

    packet = bytearray()
    packet.extend(_encode_key(1, WIRE_LENGTH))

    header = bytearray()
    header.extend(_encode_key(1, WIRE_LENGTH))
    header.extend(_encode_varint(len(payload)))
    header.extend(payload)
    header.extend(_encode_field(2, "int32", 32))
    header.extend(_encode_field(3, "int32", 66))
    header.extend(_encode_field(4, "int32", 1))
    header.extend(_encode_field(5, "int32", 1))
    header.extend(_encode_field(7, "int32", 3))
    header.extend(_encode_field(8, "int32", 254))
    header.extend(_encode_field(9, "int32", 17))
    header.extend(_encode_field(10, "int32", len(payload)))
    header.extend(_encode_field(11, "int32", 1))
    header.extend(_encode_field(14, "int32", Message.gen_seq()))
    header.extend(_encode_field(16, "int32", 19))
    header.extend(_encode_field(17, "int32", 1))
    header.extend(_encode_field(23, "string", "Android"))
    header.extend(_encode_field(25, "string", device_sn))

    packet.extend(_encode_varint(len(header)))
    packet.extend(header)
    return GlacierClassicCommandMessage(bytes(packet), {field_name: value})


class GlacierClassic(BaseInternalDevice):
    @override
    def sensors(self, client: EcoflowApiClient) -> Sequence[SensorEntity]:
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
            GlacierClassicChargingStateSensorEntity(client, self, "bms_emsStatus.chgState", const.BATTERY_CHARGING_STATE),
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
            GlacierClassicTemperatureSensorEntity(client, self, "bms_bmsStatus.minMosTmp", "Min MOS Temperature", False),
            GlacierClassicTemperatureSensorEntity(client, self, "bms_bmsStatus.maxMosTmp", "Max MOS Temperature", False),
            GlacierClassicPrimaryTemperatureSensorEntity(client, self, "pd.tmpL", "Left Temperature", False),
            GlacierClassicPrimaryTemperatureSensorEntity(client, self, "pd.tmpR", "Right Temperature", False),
            GlacierClassicPrimaryTemperatureSensorEntity(client, self, "pd.tmpM", "Combined Temperature", False),
            GlacierClassicTemperatureSensorEntity(client, self, "pd.batTemp", "Battery Pack Temperature", False),
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
            MiscSensorEntity(client, self, "runtime.runtime_property_full_upload_period", "Runtime Full Upload Period", False),
            MiscSensorEntity(
                client, self, "runtime.runtime_property_incremental_upload_period", "Runtime Incremental Upload Period", False
            ),
            MiscSensorEntity(client, self, "runtime.display_property_full_upload_period", "Display Full Upload Period", False),
            MiscSensorEntity(
                client, self, "runtime.display_property_incremental_upload_period", "Display Incremental Upload Period", False
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
            GlacierClassicPowerSourceSensorEntity(client, self, "pd.powerSource", "Power Source", False),
            QuotaStatusSensorEntity(client, self),
            GlacierClassicDebugSensorEntity(client, self),
        ]

    @override
    def numbers(self, client: EcoflowApiClient) -> Sequence[NumberEntity]:
        return [
            GlacierClassicControlSetTempEntity(
                client,
                self,
                "pd.tmpLSet",
                "Left Set Temperature",
                -20,
                20,
                lambda value: _create_glacier_classic_command("setPointLeft", int(value), self.device_data.sn),
            ),
            GlacierClassicControlSetTempEntity(
                client,
                self,
                "pd.tmpRSet",
                "Right Set Temperature",
                -20,
                20,
                lambda value: _create_glacier_classic_command("setPointRight", int(value), self.device_data.sn),
            ),
            MaxBatteryLevelEntity(
                client,
                self,
                "bms_emsStatus.maxChargeSoc",
                const.MAX_CHARGE_LEVEL,
                50,
                100,
                lambda value: _create_glacier_classic_command("cmsMaxChgSoc", int(value), self.device_data.sn),
            ),
            MinBatteryLevelEntity(
                client,
                self,
                "bms_emsStatus.minDischargeSoc",
                const.MIN_DISCHARGE_LEVEL,
                0,
                50,
                lambda value: _create_glacier_classic_command("cmsMinDsgSoc", int(value), self.device_data.sn),
            ),
        ]

    @override
    def switches(self, client: EcoflowApiClient) -> Sequence[SwitchEntity]:
        return [
            InvertedBeeperEntity(
                client,
                self,
                "pd.beepEn",
                const.BEEPER,
                lambda value: _create_glacier_classic_command("enBeep", value, self.device_data.sn),
            ),
            EnabledEntity(
                client,
                self,
                "pd.coolMode",
                "Eco Mode",
                lambda value: _create_glacier_classic_command("coolingMode", value, self.device_data.sn),
            ),
            EnabledEntity(
                client,
                self,
                "pd.childLock",
                "Child Lock",
                lambda value: _create_glacier_classic_command("childLock", value, self.device_data.sn),
            ),
            EnabledEntity(
                client,
                self,
                "pd.simpleMode",
                "Simple Mode",
                lambda value: _create_glacier_classic_command("simpleMode", value, self.device_data.sn),
            ),
            EnabledEntity(
                client,
                self,
                "pd.tempAlert",
                "Temperature Alert",
                lambda value: _create_glacier_classic_command("tempAlert", value, self.device_data.sn),
            ).with_category(EntityCategory.CONFIG),
        ]

    @override
    def selects(self, client: EcoflowApiClient) -> Sequence[SelectEntity]:
        return [
            DictSelectEntity(
                client,
                self,
                "pd.powerPbLevel",
                "Battery Protection",
                BATTERY_PROTECTION_OPTIONS,
                lambda value: _create_glacier_classic_command("batProtect", value, self.device_data.sn),
            ),
            DictSelectEntity(
                client,
                self,
                "pd.devStandbyTime",
                "Device Standby Time",
                DEVICE_STANDBY_OPTIONS,
                lambda value: _create_glacier_classic_command("devStandbyTime", value, self.device_data.sn),
            ),
        ]

    @override
    def binary_sensors(self, client: EcoflowApiClient) -> Sequence[BinarySensorEntity]:
        return [
            InvertedMiscBinarySensorEntity(client, self, "pd.flagTwoZone", "Dual Zone Mode"),
            MiscBinarySensorEntity(client, self, "pd.lidStatus", "Lid Status").with_device_class("door"),
        ]

    @override
    def buttons(self, client: EcoflowApiClient) -> Sequence[ButtonEntity]:
        return []

    @override
    def _prepare_data(self, raw_data: bytes) -> dict[str, Any]:
        packet_ts = int(time.time())
        params: dict[str, Any] = {}
        decoded_packets: list[dict[str, Any]] = []

        try:
            for header in _decode_header_messages(raw_data):
                cmd_func = int(header.get("cmd_func", 0) or 0)
                cmd_id = int(header.get("cmd_id", 0) or 0)
                pdata = header.get("pdata")
                if not isinstance(pdata, bytes):
                    continue

                packet_name, packet_spec = PACKET_SPECS.get((cmd_func, cmd_id), ("Unknown", {}))
                packet_data = _decode_message(pdata, packet_spec) if packet_spec else {}
                decoded_packets.append(
                    {
                        "cmd_func": cmd_func,
                        "cmd_id": cmd_id,
                        "name": packet_name,
                        "header": {k: v for k, v in header.items() if k != "pdata"},
                        "data": packet_data,
                        "raw_hex": pdata.hex(),
                    }
                )

                if packet_name == "BMSHeartBeatReport":
                    params.update(self._map_bms(packet_data))
                elif packet_name == "CMSHeartBeatReport":
                    params.update(self._map_cms(packet_data))
                elif packet_name in {"DisplayPropertyUpload", "ConfigWriteAck"}:
                    params.update(self._map_display(packet_data))
                elif packet_name == "RuntimePropertyUpload":
                    params.update(self._map_runtime(packet_data))

            params.update(
                self._flatten_dict(
                    {
                        "debug": {
                            "packet_ts": packet_ts,
                            "raw_hex": raw_data.hex(),
                            "message_count": len(decoded_packets),
                            "messages": str(decoded_packets),
                        }
                    }
                )
            )
        except Exception:
            _LOGGER.warning("[GlacierClassic] Data processing failed", exc_info=True)
            params.update(
                self._flatten_dict(
                    {
                        "debug": {
                            "packet_ts": packet_ts,
                            "raw_hex": raw_data.hex(),
                            "error": "decode_failed",
                        }
                    }
                )
            )

        return {
            "params": params,
            "all_fields": {"packets": decoded_packets},
        }

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
        result: dict[str, Any] = {
            "pd": {},
            "bms_emsStatus": {},
            "bms_bmsStatus": {},
        }

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
