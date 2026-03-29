# NOTE: Field names and command operateType strings are based on the best-known
# Smart Plug protocol mapping.  They should be verified against live diagnostic data
# once the device is running in HA with Diagnostic Mode enabled.
#
# - Sensor field keys (e.g. "switchSta", "temp") are the raw JSON param names
#   delivered by the private MQTT broker topic /app/device/property/{sn}.
# - Command operateType values may differ from the public API cmdCode names;
#   update them after capturing a set-message trace.

import logging
from typing import Any, override

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity

from google.protobuf.json_format import MessageToDict

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.api.message import Message, PrivateAPIMessageProtocol
from custom_components.ecoflow_cloud.devices import BaseInternalDevice, const
from custom_components.ecoflow_cloud.number import BrightnessLevelEntity, MaxWattsEntity
from custom_components.ecoflow_cloud.devices.internal.proto import AddressId
import custom_components.ecoflow_cloud.devices.internal.proto.smartplug_pb2 as pb2
from custom_components.ecoflow_cloud.sensor import (
    DeciwattsSensorEntity,
    QuotaStatusSensorEntity,
    TempSensorEntity,
    VoltSensorEntity,
    MilliampSensorEntity
)
from custom_components.ecoflow_cloud.switch import EnabledEntity

_LOGGER = logging.getLogger(__name__)


class SmartPlug(BaseInternalDevice):
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            TempSensorEntity(client, self, "temp", const.TEMPERATURE),
            VoltSensorEntity(client, self, "volt", const.VOLT),
            MilliampSensorEntity(client, self, "current", const.CURRENT).attr("maxCur", const.MAX_CURRENT, 0),
            DeciwattsSensorEntity(client, self, "watts", const.POWER),
            QuotaStatusSensorEntity(client, self),
        ]

    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return [
            BrightnessLevelEntity(
                client,
                self,
                "brightness",
                const.BRIGHTNESS,
                0,
                1023,
                lambda value: _create_set_brightness_message(value, self.device_info.sn),
            ),
            MaxWattsEntity(
                client,
                self,
                "maxWatts",
                const.MAX_POWER,
                0,
                2500,
                lambda value: _create_set_max_watts_message(value, self.device_info.sn),
            ),
        ]

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return [
            EnabledEntity(
                client,
                self,
                "switchSta",
                const.MODE_ON,
                lambda value: _create_change_switch_status_message(value, self.device_info.sn),
            ),
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return []

    def _prepare_data(self, raw_data: bytes) -> dict[str, Any]:
        try:
            _LOGGER.debug(f"Processing {len(raw_data)} bytes of raw data")
            params = self._parse_smartplug_packet(raw_data)
            return { "params": params }
        except Exception as e:
            _LOGGER.error(
                f"[SmartPlug] Data processing failed: {e}", exc_info=True)
            _LOGGER.debug(
                "[SmartPlug] Attempting JSON fallback after protobuf failure")
            try:
                return super()._prepare_data(raw_data)
            except Exception as e2:
                _LOGGER.error(f"[SmartPlug] JSON fallback also failed: {e2}")
                return {}

    def _parse_smartplug_packet(self, raw_data: bytes) -> dict[str, Any]:
        packet = pb2.SendSmartPlugHeaderMsg()
        try:
            packet.ParseFromString(raw_data)
        except Exception:
            return {}

        if not packet.msg:
            return {}

        result: dict[str, Any] = {}

        for msg in packet.msg:
            if msg.deviceSn and msg.deviceSn != self.device_info.sn:
                continue

            _LOGGER.debug(f"parsing MQTT package with cmdFunc={msg.cmdFunc}, cmdId={msg.cmdId}")

            if (msg.cmdFunc != pb2.CMD_FUNC_WN_SMART_PLUG):
                continue
            elif msg.cmdId == pb2.CMD_ID_DATA:
                result.update(_read_data(msg.pdata))
            elif msg.cmdId == pb2.CMD_ID_CHANGE_SWITCH_STATUS:
                result.update(_read_change_switch_status(msg.pdata))
            elif msg.cmdId == pb2.CMD_ID_SET_BRIGHTNESS:
                result.update(_read_set_brightness(msg.pdata))
            elif msg.cmdId == pb2.CMD_ID_SET_MAX_WATTS:
                result.update(_read_set_max_watts(msg.pdata))
            else:
                _LOGGER.info(f"Ignoring unknown MQTT package cmdFunc={msg.cmdFunc}, cmdId={msg.cmdId} for SmartPlug")

        _LOGGER.debug(f"result: {result}")
        return result

class SmartPlug3CommandMessage(PrivateAPIMessageProtocol):
    """Message wrapper for SmartPlug protobuf commands."""

    def __init__(
        self,
        payload: Message,
        packet: pb2.SendSmartPlugHeaderMsg,
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


def _create_send_header_message(cmd_id: int, device_sn: str, payload: Message):
    packet = pb2.SendSmartPlugHeaderMsg()
    msg = packet.msg.add()

    msg.pdata = payload.SerializeToString()
    msg.dataLen = len(msg.pdata)
    msg.src = AddressId.APP
    msg.dest = AddressId.MQTT
    msg.cmdFunc = pb2.CMD_FUNC_WN_SMART_PLUG
    msg.cmdId = cmd_id
    msg.needAck = 1
    msg.seq = Message.gen_seq()
    msg.deviceSn = device_sn

    return SmartPlug3CommandMessage(payload, packet)


def _create_change_switch_status_message(value: int, device_sn: str):

    payload = pb2.WnPlugSwitchMessage()
    if value:
        payload.switchSta = True

    return _create_send_header_message(pb2.CMD_ID_CHANGE_SWITCH_STATUS, device_sn, payload)


def _create_set_brightness_message(value: int, device_sn: str):
    payload = pb2.WnBrightnessPack()
    payload.brightness = value

    return _create_send_header_message(pb2.CMD_ID_SET_BRIGHTNESS, device_sn, payload)

def _create_set_max_watts_message(value: int, device_sn: str):
    payload = pb2.WnMaxWattsPack()
    payload.maxWatts = value

    return _create_send_header_message(pb2.CMD_ID_SET_MAX_WATTS, device_sn, payload)

def _read_data(pdata: bytes) -> dict[str, Any]:
    msg = pb2.WnPlugHeartbeatPack()
    msg.ParseFromString(pdata)

    _LOGGER.debug(f"WnPlugHeartbeatPack: {msg}")

    result = MessageToDict(msg, preserving_proto_field_name=True)

    return result
    
def _read_change_switch_status(pdata: bytes) -> dict[str, Any]:
    msg = pb2.WnPlugSwitchMessage()
    msg.ParseFromString(pdata)
    return {
        "switchSta": True if msg.switchSta else False,
    }

def _read_set_brightness(pdata: bytes) -> dict[str, Any]:
    msg = pb2.WnBrightnessPack()
    msg.ParseFromString(pdata)
    return {
        "brightness": msg.brightness,
    }

def _read_set_max_watts(pdata: bytes) -> dict[str, Any]:
    msg = pb2.WnMaxWattsPack()
    msg.ParseFromString(pdata)
    return {
        "maxWatts": msg.maxWatts,
    }