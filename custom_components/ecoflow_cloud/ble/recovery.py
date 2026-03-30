from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import struct
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING, Any

import ecdsa
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from bleak.exc import BleakError
from bleak_retry_connector import BleakNotFoundError, establish_connection
from google.protobuf import descriptor_pb2, descriptor_pool, message_factory
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
    async_last_service_info,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.util import dt

from .. import CONF_DEVICE_LIST, OPTS_BLE_WIFI_PASSWORD, OPTS_BLE_WIFI_SSID
from . import keydata

if TYPE_CHECKING:
    from ..api import EcoflowApiClient
    from ..device_data import DeviceData


_LOGGER = logging.getLogger(__name__)

_MANUFACTURER_ID = 0xB5B5
_DEFAULT_CAPABILITY_FLAGS = 0b0111000
_RIVER2_PACKET_VERSION = 2
_AUTH_HEADER_DST = 0x35
_PD_ADDR = 0x02
_PD_CMD_SET = 0x20
_PD_GET_WIFI_INFO_CMD_ID = 0xA1
_AP_FOLLOW_INFO_LIST_CMD_SET = 0x35
_AP_FOLLOW_INFO_LIST_CMD_ID = 0x26
_POST_PROVISION_OBSERVE_SEC = 15
_DHODM_RPC_SRC = "user_1"
_SUPPORTED_DEVICE_TYPES = {
    "RIVER_2",
    "RIVER_2_MAX",
    "RIVER_2_PRO",
    "RIVER 2",
    "RIVER 2 Max",
    "RIVER 2 Pro",
}
_MODULE_SOURCE_NAMES = {
    0x02: "pd",
    0x03: "bms_ems",
    0x04: "inv",
    0x05: "mppt",
}
_BT_PROTOCOL_UUIDS = {
    "rfcomm": {
        "notify": "00000003-0000-1000-8000-00805f9b34fb",
        "write": "00000002-0000-1000-8000-00805f9b34fb",
    },
    "nordic_uart": {
        "notify": "6e400003-b5a3-f393-e0a9-e50e24dcca9e",
        "write": "6e400002-b5a3-f393-e0a9-e50e24dcca9e",
    },
}

ATTR_BLE_RECOVERY_ACTIVE = "ble_recovery_active"
ATTR_BLE_RECOVERY_ATTEMPTS = "ble_recovery_attempts"
ATTR_BLE_RECOVERY_LAST_ATTEMPT = "ble_recovery_last_attempt"
ATTR_BLE_RECOVERY_LAST_RESULT = "ble_recovery_last_result"
ATTR_BLE_RECOVERY_LAST_ERROR = "ble_recovery_last_error"
ATTR_BLE_RECOVERY_STAGE = "ble_recovery_stage"
ATTR_BLE_RECOVERY_STRATEGY = "ble_recovery_strategy"
ATTR_BLE_RECOVERY_NETWORK_STATUS = "ble_recovery_network_status"
ATTR_BLE_RECOVERY_AUTH_STATUS = "ble_recovery_auth_status"
ATTR_BLE_RECOVERY_CLOUD_BIND = "ble_recovery_cloud_bind"

_WIFI_SSID_KEYS = {
    "modulewifissid",
    "wifissid",
}
_WIFI_CHANNEL_KEYS = {
    "modulewificonnectchannel",
    "modulewifichannel",
    "wificonnectchannel",
    "wifichannel",
}
_BLE_WIFI_CREDENTIALS_ISSUE_PREFIX = "ble_wifi_credentials_"


class BleRecoveryError(Exception):
    pass


class BleAuthError(BleRecoveryError):
    pass


class BlePacketError(BleRecoveryError):
    pass


def supports_ble_wifi_recovery_device_type(device_type: str) -> bool:
    return device_type in _SUPPORTED_DEVICE_TYPES


def _discovery_address(discovery: BluetoothServiceInfoBleak) -> str:
    return getattr(discovery, "address", "") or discovery.device.address


def _discovery_name(discovery: BluetoothServiceInfoBleak) -> str:
    return getattr(discovery, "name", "") or discovery.device.name or ""


def _discovery_rssi(discovery: BluetoothServiceInfoBleak) -> int:
    rssi = getattr(discovery.advertisement, "rssi", None)
    return rssi if isinstance(rssi, int) else -127


def _discovery_source(discovery: BluetoothServiceInfoBleak) -> str:
    source = getattr(discovery, "source", None)
    if isinstance(source, str) and source:
        return source

    details = getattr(discovery.device, "details", None)
    if isinstance(details, dict):
        detail_source = details.get("source")
        if isinstance(detail_source, str) and detail_source:
            return detail_source

        props = details.get("props")
        if isinstance(props, dict):
            adapter = props.get("Adapter")
            if isinstance(adapter, str) and adapter:
                return adapter

    return "unknown"


def get_ble_recovery_state_attributes(client: "EcoflowApiClient", sn: str) -> dict[str, Any]:
    manager = getattr(client, "ble_recovery_manager", None)
    if manager is None:
        return {}
    device = client.devices.get(sn)
    if device is None or not manager.supports_device(device.device_data):
        return {}
    return manager.state_attributes(sn)


def _crc8_ccitt(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0x07) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc


def _crc16_arc(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x01:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF


@dataclass(slots=True)
class Packet:
    src: int
    dst: int
    cmd_set: int
    cmd_id: int
    payload: bytes = b""
    dsrc: int = 1
    ddst: int = 1
    version: int = 3
    seq: bytes = b"\x00\x00\x00\x00"
    product_id: int = 0

    PREFIX = b"\xAA"

    def to_bytes(self) -> bytes:
        data = self.PREFIX
        data += struct.pack("<B", self.version) + struct.pack("<H", len(self.payload))
        data += struct.pack("<B", _crc8_ccitt(data))
        data += b"\x0D" + self.seq + b"\x00\x00"
        data += struct.pack("<B", self.src) + struct.pack("<B", self.dst)
        if self.version >= 0x03:
            data += struct.pack("<B", self.dsrc) + struct.pack("<B", self.ddst)
        data += struct.pack("<B", self.cmd_set) + struct.pack("<B", self.cmd_id)
        data += self.payload
        data += struct.pack("<H", _crc16_arc(data))
        return data

    @classmethod
    def from_bytes(cls, data: bytes, *, xor_payload: bool = False) -> "Packet":
        if not data.startswith(cls.PREFIX):
            raise BlePacketError(f"Incorrect packet prefix: {data.hex()}")

        version = data[1]
        if (version == 2 and len(data) < 18) or (version in (3, 4) and len(data) < 20):
            raise BlePacketError(f"Packet too short: {data.hex()}")

        payload_length = struct.unpack("<H", data[2:4])[0]
        if version in (2, 3, 4) and _crc16_arc(data[:-2]) != struct.unpack("<H", data[-2:])[0]:
            raise BlePacketError(f"Incorrect CRC16: {data.hex()}")
        if _crc8_ccitt(data[:4]) != data[4]:
            raise BlePacketError(f"Incorrect CRC8: {data.hex()}")

        seq = data[6:10]
        src = data[12]
        dst = data[13]
        dsrc = 0
        ddst = 0
        payload_start = 16 if version == 2 else 18
        if version == 2:
            cmd_set, cmd_id = data[14:payload_start]
        else:
            dsrc, ddst, cmd_set, cmd_id = data[14:payload_start]

        payload = b""
        if payload_length > 0:
            payload = data[payload_start : payload_start + payload_length]
            if xor_payload and seq[0] != 0:
                payload = bytes([value ^ seq[0] for value in payload])
            if version == 0x13 and payload.endswith(b"\xBB\xBB"):
                payload = payload[:-2]

        return cls(
            src=src,
            dst=dst,
            cmd_set=cmd_set,
            cmd_id=cmd_id,
            payload=payload,
            dsrc=dsrc,
            ddst=ddst,
            version=version,
            seq=seq,
        )


class EncPacket:
    PREFIX = b"\x5A\x5A"

    FRAME_TYPE_COMMAND = 0x00
    FRAME_TYPE_PROTOCOL = 0x01
    PAYLOAD_TYPE_VX_PROTOCOL = 0x00

    def __init__(
        self,
        frame_type: int,
        payload_type: int,
        payload: bytes,
        enc_key: bytes | None = None,
        iv: bytes | None = None,
    ) -> None:
        self._frame_type = frame_type
        self._payload_type = payload_type
        self._payload = payload
        self._enc_key = enc_key
        self._iv = iv

    def _encrypt_payload(self) -> bytes:
        if self._enc_key is None or self._iv is None:
            return self._payload
        cipher = AES.new(self._enc_key, AES.MODE_CBC, self._iv)
        return cipher.encrypt(pad(self._payload, AES.block_size))

    def to_bytes(self) -> bytes:
        payload = self._encrypt_payload()
        data = self.PREFIX + struct.pack("<B", (self._frame_type << 4) | self._payload_type) + b"\x01"
        data += struct.pack("<H", len(payload) + 2)
        data += payload
        data += struct.pack("<H", _crc16_arc(data))
        return data


class Type7Encryption:
    def __init__(self, session_key: bytes, iv: bytes) -> None:
        self.session_key = session_key
        self.iv = iv

    async def encrypt(self, plaintext: bytes) -> bytes:
        cipher = AES.new(self.session_key, AES.MODE_CBC, self.iv)
        return cipher.encrypt(pad(plaintext, AES.block_size))

    async def decrypt(self, ciphertext: bytes) -> bytes:
        aligned = len(ciphertext) - len(ciphertext) % AES.block_size
        if aligned == 0:
            return ciphertext
        cipher = AES.new(self.session_key, AES.MODE_CBC, self.iv)
        decrypted = cipher.decrypt(ciphertext[:aligned])
        try:
            return unpad(decrypted, AES.block_size)
        except ValueError:
            return decrypted


class Type1Encryption(Type7Encryption):
    async def encrypt(self, plaintext: bytes) -> bytes:
        padded_len = (len(plaintext) + 15) // 16 * 16
        padded = plaintext + b"\x00" * (padded_len - len(plaintext))
        cipher = AES.new(self.session_key, AES.MODE_CBC, self.iv)
        return cipher.encrypt(padded)

    async def decrypt(self, ciphertext: bytes) -> bytes:
        cipher = AES.new(self.session_key, AES.MODE_CBC, self.iv)
        return cipher.decrypt(ciphertext)


class SimplePacketAssembler:
    def __init__(self) -> None:
        self._buffer = b""

    @staticmethod
    def encode(payload: bytes) -> bytes:
        return EncPacket(
            EncPacket.FRAME_TYPE_COMMAND,
            EncPacket.PAYLOAD_TYPE_VX_PROTOCOL,
            payload,
        ).to_bytes()

    def parse(self, data: bytes) -> bytes | None:
        if self._buffer:
            data = self._buffer + data
            self._buffer = b""

        while data:
            start = data.find(EncPacket.PREFIX)
            if start < 0:
                raise BlePacketError(f"No simple packet prefix found in {data.hex()}")
            if start > 0:
                data = data[start:]

            if len(data) < 8:
                self._buffer = data
                return None

            header = data[0:6]
            data_end = 6 + struct.unpack("<H", header[4:6])[0]
            if data_end > len(data):
                next_prefix = data[2:].find(EncPacket.PREFIX)
                if next_prefix >= 0:
                    data = data[2 + next_prefix :]
                    continue
                self._buffer = data
                return None

            payload_data = data[6 : data_end - 2]
            payload_crc = data[data_end - 2 : data_end]
            if _crc16_arc(header + payload_data) != struct.unpack("<H", payload_crc)[0]:
                data = data[2:]
                continue

            return payload_data

        return None


class EncPacketAssembler:
    def __init__(self, encryption: Type7Encryption | Type1Encryption) -> None:
        self._buffer = b""
        self._encryption = encryption

    @property
    def write_with_response(self) -> bool:
        return True

    async def encode(self, packet: Packet) -> bytes:
        return EncPacket(
            EncPacket.FRAME_TYPE_PROTOCOL,
            EncPacket.PAYLOAD_TYPE_VX_PROTOCOL,
            packet.to_bytes(),
            self._encryption.session_key,
            self._encryption.iv,
        ).to_bytes()

    async def reassemble(self, data: bytes) -> list[bytes]:
        if self._buffer:
            data = self._buffer + data
            self._buffer = b""

        payloads: list[bytes] = []
        while data:
            start = data.find(EncPacket.PREFIX)
            if start < 0:
                break
            if start > 0:
                data = data[start:]

            if len(data) < 8:
                break

            header = data[0:6]
            payload_len = struct.unpack("<H", header[4:6])[0]
            if payload_len > 10_000:
                data = data[2:]
                continue

            data_end = 6 + payload_len
            if data_end > len(data):
                next_prefix = data[2:].find(EncPacket.PREFIX)
                if next_prefix >= 0:
                    data = data[2 + next_prefix :]
                    continue
                break

            payload_data = data[6 : data_end - 2]
            payload_crc = data[data_end - 2 : data_end]
            if _crc16_arc(header + payload_data) != struct.unpack("<H", payload_crc)[0]:
                data = data[2:]
                continue

            data = data[data_end:]
            payloads.append(await self._encryption.decrypt(payload_data))

        self._buffer = data
        return payloads


class RawHeaderAssembler:
    def __init__(self, encryption: Type1Encryption) -> None:
        self._buffer = b""
        self._encryption = encryption

    @property
    def write_with_response(self) -> bool:
        return False

    async def encode(self, packet: Packet) -> bytes:
        raw = packet.to_bytes()
        header = raw[:5]
        body = raw[5:]
        encrypted = await self._encryption.encrypt(body)
        return header + encrypted

    async def reassemble(self, data: bytes) -> list[bytes]:
        if self._buffer:
            data = self._buffer + data
            self._buffer = b""

        payloads: list[bytes] = []
        while data:
            start = data.find(Packet.PREFIX)
            if start < 0:
                break
            if start > 0:
                data = data[start:]

            if len(data) < 5:
                break

            if _crc8_ccitt(data[:4]) != data[4]:
                data = data[1:]
                continue

            payload_length = struct.unpack("<H", data[2:4])[0]
            version = data[1]
            inner_overhead = 15 if version >= 3 else 13
            inner_len = inner_overhead + payload_length
            encrypted_len = (inner_len + 15) // 16 * 16
            frame_len = 5 + encrypted_len
            if len(data) < frame_len:
                break

            header = data[:5]
            encrypted_body = data[5:frame_len]
            data = data[frame_len:]
            decrypted = await self._encryption.decrypt(encrypted_body)
            payloads.append(header + decrypted[:inner_len])

        self._buffer = data
        return payloads


def _serial_from_advertisement(advertisement: AdvertisementData) -> str | None:
    manufacturer_data = advertisement.manufacturer_data.get(_MANUFACTURER_ID)
    if manufacturer_data is None or len(manufacturer_data) < 17:
        return None
    serial_number = manufacturer_data[1:17].strip(b"\x00")
    if not serial_number:
        return None
    return serial_number.decode("ascii", errors="ignore")


def _encrypt_type_from_advertisement(advertisement: AdvertisementData) -> int:
    manufacturer_data = advertisement.manufacturer_data.get(_MANUFACTURER_ID)
    if manufacturer_data is None:
        return 7
    capability_flags = manufacturer_data[22] if len(manufacturer_data) > 22 else _DEFAULT_CAPABILITY_FLAGS
    return (capability_flags & 0b0111000) >> 3


def _parse_bssid(value: str | None) -> bytes | None:
    if value is None:
        return None
    normalized = value.strip().replace("-", ":")
    if not normalized:
        return None
    parts = normalized.split(":")
    if len(parts) != 6:
        raise ValueError(f"Invalid BSSID: {value}")
    return bytes(int(part, 16) for part in parts)


def _get_ecdh_type_size(curve_num: int) -> int:
    if curve_num == 1:
        return 52
    if curve_num == 2:
        return 56
    if curve_num in (3, 4):
        return 64
    return 40


@lru_cache(maxsize=1)
def _network_message_class():
    file_descriptor = descriptor_pb2.FileDescriptorProto()
    file_descriptor.name = "wn_synchronous.proto"
    file_descriptor.package = "wn"
    file_descriptor.syntax = "proto2"

    message = file_descriptor.message_type.add()
    message.name = "network_message"
    fields = [
        ("mesh_type", 1, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32),
        ("router_ssid", 2, descriptor_pb2.FieldDescriptorProto.TYPE_STRING),
        ("router_pwd", 3, descriptor_pb2.FieldDescriptorProto.TYPE_STRING),
        ("router_bssid", 4, descriptor_pb2.FieldDescriptorProto.TYPE_BYTES),
        ("mesh_id", 5, descriptor_pb2.FieldDescriptorProto.TYPE_BYTES),
        ("https_url", 6, descriptor_pb2.FieldDescriptorProto.TYPE_STRING),
        ("router_channel", 7, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32),
        ("mesh_enable", 8, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32),
        ("softap_pwd", 9, descriptor_pb2.FieldDescriptorProto.TYPE_STRING),
    ]
    for name, number, field_type in fields:
        field = message.field.add()
        field.name = name
        field.number = number
        field.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
        field.type = field_type

    pool = descriptor_pool.DescriptorPool()
    pool.Add(file_descriptor)
    descriptor = pool.FindMessageTypeByName("wn.network_message")
    return message_factory.GetMessageClass(descriptor)


@lru_cache(maxsize=1)
def _ap_follow_info_proto_classes() -> tuple[type[Any], type[Any], type[Any]]:
    file_descriptor = descriptor_pb2.FileDescriptorProto()
    file_descriptor.name = "iot_comm_ap_follow.proto"
    file_descriptor.package = "ecoflow.iot"
    file_descriptor.syntax = "proto2"

    ack_message = file_descriptor.message_type.add()
    ack_message.name = "ApFollowInfoAck"
    ack_fields = [
        ("follow_switch", 1, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32),
        ("pack_lost_rate", 2, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32),
        ("rssi", 3, descriptor_pb2.FieldDescriptorProto.TYPE_INT32),
        ("ip_addr", 4, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32),
        ("bssid", 5, descriptor_pb2.FieldDescriptorProto.TYPE_STRING),
        ("ssid", 6, descriptor_pb2.FieldDescriptorProto.TYPE_STRING),
        ("pwd", 7, descriptor_pb2.FieldDescriptorProto.TYPE_STRING),
        ("is_connect", 8, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32),
        ("is_enable", 9, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32),
        ("is_found", 10, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32),
        ("retry_cnt", 11, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32),
        ("channel", 12, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32),
        ("disconnect_reason", 13, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32),
        ("connect_timestamp", 14, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32),
    ]
    for name, number, field_type in ack_fields:
        field = ack_message.field.add()
        field.name = name
        field.number = number
        field.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
        field.type = field_type

    list_ack_message = file_descriptor.message_type.add()
    list_ack_message.name = "ApFollowInfoListAck"
    list_field = list_ack_message.field.add()
    list_field.name = "list"
    list_field.number = 1
    list_field.label = descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED
    list_field.type = descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE
    list_field.type_name = ".ecoflow.iot.ApFollowInfoAck"

    list_get_message = file_descriptor.message_type.add()
    list_get_message.name = "ApFollowInfoListGet"

    pool = descriptor_pool.DescriptorPool()
    pool.Add(file_descriptor)
    ack_descriptor = pool.FindMessageTypeByName("ecoflow.iot.ApFollowInfoAck")
    list_ack_descriptor = pool.FindMessageTypeByName("ecoflow.iot.ApFollowInfoListAck")
    list_get_descriptor = pool.FindMessageTypeByName("ecoflow.iot.ApFollowInfoListGet")
    return (
        message_factory.GetMessageClass(ack_descriptor),
        message_factory.GetMessageClass(list_ack_descriptor),
        message_factory.GetMessageClass(list_get_descriptor),
    )


@lru_cache(maxsize=1)
def _cfg_net_proto_classes() -> tuple[type[Any], type[Any]]:
    file_descriptor = descriptor_pb2.FileDescriptorProto()
    file_descriptor.name = "iot_config.proto"
    file_descriptor.package = "ecoflow.iot"
    file_descriptor.syntax = "proto2"

    share_message = file_descriptor.message_type.add()
    share_message.name = "ShareCfgNetInfo"
    share_fields = [
        ("wifi_ssid", 1, descriptor_pb2.FieldDescriptorProto.TYPE_STRING),
        ("wifi_password", 2, descriptor_pb2.FieldDescriptorProto.TYPE_STRING),
        ("https_url", 3, descriptor_pb2.FieldDescriptorProto.TYPE_STRING),
    ]
    for name, number, field_type in share_fields:
        field = share_message.field.add()
        field.name = name
        field.number = number
        field.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
        field.type = field_type

    cfg_list_message = file_descriptor.message_type.add()
    cfg_list_message.name = "CfgNetDeviceList"

    device_sn_field = cfg_list_message.field.add()
    device_sn_field.name = "device_sn"
    device_sn_field.number = 1
    device_sn_field.label = descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED
    device_sn_field.type = descriptor_pb2.FieldDescriptorProto.TYPE_STRING

    share_cfg_field = cfg_list_message.field.add()
    share_cfg_field.name = "share_cfg_net_info"
    share_cfg_field.number = 2
    share_cfg_field.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
    share_cfg_field.type = descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE
    share_cfg_field.type_name = ".ecoflow.iot.ShareCfgNetInfo"

    pool = descriptor_pool.DescriptorPool()
    pool.Add(file_descriptor)
    share_descriptor = pool.FindMessageTypeByName("ecoflow.iot.ShareCfgNetInfo")
    cfg_list_descriptor = pool.FindMessageTypeByName("ecoflow.iot.CfgNetDeviceList")
    return (
        message_factory.GetMessageClass(share_descriptor),
        message_factory.GetMessageClass(cfg_list_descriptor),
    )


def _build_ap_follow_info_list_get_payload() -> bytes:
    _, _, list_get_cls = _ap_follow_info_proto_classes()
    return list_get_cls().SerializeToString()


def _build_cfg_net_device_list_payload(
    *,
    device_sns: list[str],
    ssid: str,
    password: str,
    https_url: str | None = None,
) -> bytes:
    share_cls, cfg_list_cls = _cfg_net_proto_classes()

    share_message = share_cls()
    share_message.wifi_ssid = ssid
    share_message.wifi_password = password
    if https_url:
        share_message.https_url = https_url

    cfg_list_message = cfg_list_cls()
    cfg_list_message.device_sn.extend(device_sns)
    cfg_list_message.share_cfg_net_info.CopyFrom(share_message)
    return cfg_list_message.SerializeToString()


def _next_packet_seq() -> bytes:
    return struct.pack("<I", int(dt.utcnow().timestamp() * 1000) & 0xFFFFFFFF)


def _decode_ap_follow_info_list(payload: bytes) -> dict[str, Any] | None:
    if not payload:
        return None

    _, list_ack_cls, _ = _ap_follow_info_proto_classes()
    try:
        decoded = list_ack_cls.FromString(payload)
    except Exception:
        return None

    entries: list[dict[str, Any]] = []
    connected_entry: dict[str, Any] | None = None
    for entry in decoded.list:
        parsed = {
            "follow_switch": int(entry.follow_switch),
            "pack_lost_rate": int(entry.pack_lost_rate),
            "rssi": int(entry.rssi),
            "ip_addr": int(entry.ip_addr),
            "bssid": str(entry.bssid),
            "ssid": str(entry.ssid),
            "pwd": str(entry.pwd),
            "is_connect": int(entry.is_connect),
            "is_enable": int(entry.is_enable),
            "is_found": int(entry.is_found),
            "retry_cnt": int(entry.retry_cnt),
            "channel": int(entry.channel),
            "disconnect_reason": int(entry.disconnect_reason),
            "connect_timestamp": int(entry.connect_timestamp),
        }
        entries.append(parsed)
        if connected_entry is None and parsed["is_connect"] == 1:
            connected_entry = parsed

    return {
        "entry_count": len(entries),
        "connected_entry": connected_entry,
        "entries": entries,
        "raw": payload.hex(),
    }


def _build_network_message_payload(
    *,
    ssid: str | None,
    password: str | None,
    bssid: bytes | None,
    channel: int | None = None,
    https_url: str | None = None,
) -> bytes:
    message_cls = _network_message_class()
    message = message_cls()
    if ssid is not None:
        message.router_ssid = ssid
    if password is not None:
        message.router_pwd = password
    message.mesh_id = b""
    if https_url is not None:
        message.https_url = https_url
    message.mesh_enable = 0
    if bssid is not None:
        message.router_bssid = bssid
    if channel is not None and channel >= 0:
        message.router_channel = channel
    return message.SerializeToString()


def _recovery_https_url(client: "EcoflowApiClient") -> str:
    api_domain = str(getattr(client, "api_domain", "")).strip()
    if not api_domain:
        return ""
    return f"https://{api_domain}"


def _recovery_mqtt_server(client: "EcoflowApiClient") -> str:
    mqtt_info = getattr(client, "mqtt_info", None)
    if mqtt_info is None:
        return ""

    url = str(getattr(mqtt_info, "url", "")).strip()
    port = getattr(mqtt_info, "port", None)
    if not url:
        return ""

    if isinstance(port, int) and port > 0:
        return f"{url}:{port}"

    return url


def _build_dhodm_rpc_payload(
    *,
    request_id: int,
    method: str,
    params: Any,
    dst: str = "",
) -> bytes:
    payload = {
        "id": request_id,
        "src": _DHODM_RPC_SRC,
        "method": method,
        "params": params,
        "dst": dst,
        "result": None,
    }
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _decode_protobuf_fields(payload: bytes) -> dict[int, Any]:
    values: dict[int, Any] = {}
    index = 0
    payload_len = len(payload)

    def read_varint(start: int) -> tuple[int, int]:
        shift = 0
        value = 0
        pos = start
        while pos < payload_len:
            byte = payload[pos]
            value |= (byte & 0x7F) << shift
            pos += 1
            if byte < 0x80:
                return value, pos
            shift += 7
        raise ValueError("truncated_varint")

    while index < payload_len:
        key, index = read_varint(index)
        field_number = key >> 3
        wire_type = key & 0x07

        if field_number == 0:
            raise ValueError("invalid_field_number")

        if wire_type == 0:
            value, index = read_varint(index)
        elif wire_type == 2:
            size, index = read_varint(index)
            value_bytes = payload[index : index + size]
            if len(value_bytes) != size:
                raise ValueError("truncated_length_delimited")
            index += size
            try:
                decoded = value_bytes.decode("utf-8")
            except UnicodeDecodeError:
                value = value_bytes.hex()
            else:
                value = decoded if decoded.isprintable() else value_bytes.hex()
        elif wire_type == 5:
            value_bytes = payload[index : index + 4]
            if len(value_bytes) != 4:
                raise ValueError("truncated_fixed32")
            value = struct.unpack("<I", value_bytes)[0]
            index += 4
        elif wire_type == 1:
            value_bytes = payload[index : index + 8]
            if len(value_bytes) != 8:
                raise ValueError("truncated_fixed64")
            value = struct.unpack("<Q", value_bytes)[0]
            index += 8
        else:
            raise ValueError(f"unsupported_wire_type:{wire_type}")

        values[field_number] = value

    return values


def _decode_network_status_payload(payload: bytes) -> dict[str, Any] | None:
    if not payload:
        return None

    try:
        fields = _decode_protobuf_fields(payload)
    except ValueError:
        return None

    decoded = {
        "mesh_state": fields.get(1),
        "mesh_layer": fields.get(2),
        "parent_rssi": fields.get(3),
        "https_state": fields.get(4),
        "mqtt_state": fields.get(5),
        "ping_info": fields.get(6),
        "raw": payload.hex(),
    }
    if not any(value is not None for key, value in decoded.items() if key != "raw"):
        return None
    return decoded


def _auth_result_error(payload: bytes) -> str | None:
    if payload == b"\x00":
        return None
    errors = {
        b"\x01": "general_error",
        b"\x02": "ota_upgrade",
        b"\x03": "user_id_incorrect_length",
        b"\x04": "iot_status_error",
        b"\x05": "user_key_read_error",
        b"\x06": "incorrect_user_id",
        b"\x07": "maximum_devices_error",
    }
    return errors.get(payload, f"unknown_auth_error:{payload.hex()}")


def _decode_auth_status_payload(payload: bytes) -> dict[str, Any]:
    auth_type = payload[1] if len(payload) > 1 else 0
    key_status = payload[0] if payload else 0
    decoded = {
        "auth_type": auth_type,
        "key_status": key_status,
        "raw": payload.hex(),
    }
    if auth_type == 1:
        decoded["flow"] = "token"
    else:
        decoded["flow"] = "key"
    return decoded


def _decode_cstring_bytes(data: bytes) -> str:
    return data.split(b"\x00", 1)[0].decode("utf-8", errors="ignore")


def _decode_device_key_info_payload(payload: bytes) -> dict[str, Any]:
    if len(payload) < 134:
        return {
            "is_success": False,
            "raw": payload.hex(),
            "error": f"payload_too_short:{len(payload)}",
        }

    random_code = _decode_cstring_bytes(payload[1:65])
    sign_string = _decode_cstring_bytes(payload[65:129])
    ver = payload[129]
    timestamp_raw = struct.unpack("<I", payload[130:134])[0]
    return {
        "is_success": True,
        "random_code": random_code,
        "sign_string": sign_string,
        "timestamp": str(timestamp_raw),
        "timestamp_raw": timestamp_raw,
        "ver": ver,
        "raw": payload.hex(),
    }


def _normalize_wifi_channel(value: Any) -> int | None:
    if isinstance(value, bool):
        return None

    if isinstance(value, int):
        return value if value > 0 else None

    if isinstance(value, float) and value.is_integer():
        parsed = int(value)
        return parsed if parsed > 0 else None

    if isinstance(value, str):
        stripped = value.strip()
        if stripped.isdigit():
            parsed = int(stripped)
            return parsed if parsed > 0 else None

    return None


def _module_source_name(src: int) -> str:
    return _MODULE_SOURCE_NAMES.get(src, f"src_0x{src:02X}")


def _decode_module_blob_words(payload: bytes, *, preview_words: int = 12) -> dict[str, Any]:
    """Expose opaque module payloads as little-endian word slices for debugging."""
    if not payload:
        return {"raw": ""}

    whole_words = len(payload) // 4
    words_u32 = [
        int.from_bytes(payload[index : index + 4], "little", signed=False)
        for index in range(0, whole_words * 4, 4)
    ]
    words_i32 = [
        int.from_bytes(payload[index : index + 4], "little", signed=True)
        for index in range(0, whole_words * 4, 4)
    ]
    trailing = payload[whole_words * 4 :]

    return {
        "len": len(payload),
        "u32_head": words_u32[:preview_words],
        "i32_head": words_i32[:preview_words],
        "u32_tail": words_u32[-min(preview_words, len(words_u32)) :],
        "nonzero_u32": {
            f"w{index:02d}": value
            for index, value in enumerate(words_u32)
            if value != 0
        },
        "trailing_hex": trailing.hex(),
    }


def _decode_wifi_state_payload(payload: bytes) -> dict[str, Any] | None:
    """Decode EcoFlow WifiStateBean payload used by PD cmd_id 0x20."""
    if not payload:
        return None

    decoded: dict[str, Any] = {"raw": payload.hex()}
    if len(payload) >= 1:
        decoded["type"] = payload[0]
    if len(payload) >= 2:
        decoded["state"] = payload[1]
    if len(payload) >= 4:
        decoded["ping_min_raw"] = payload[2:4].hex()
        decoded["ping_min_le"] = int.from_bytes(payload[2:4], "little", signed=False)
        decoded["ping_min_be"] = int.from_bytes(payload[2:4], "big", signed=False)
    if len(payload) >= 6:
        decoded["ping_max_raw"] = payload[4:6].hex()
        decoded["ping_max_le"] = int.from_bytes(payload[4:6], "little", signed=False)
        decoded["ping_max_be"] = int.from_bytes(payload[4:6], "big", signed=False)
    if len(payload) >= 8:
        decoded["ping_avg_raw"] = payload[6:8].hex()
        decoded["ping_avg_le"] = int.from_bytes(payload[6:8], "little", signed=False)
        decoded["ping_avg_be"] = int.from_bytes(payload[6:8], "big", signed=False)
    return decoded


def _decode_wifi_state_prefix(payload: bytes) -> dict[str, Any] | None:
    """Expose the leading type/state bytes on opaque module status payloads."""
    if len(payload) < 2:
        return None

    state_type = payload[0]
    state_value = payload[1]
    return {
        "type": state_type,
        "state": state_value,
        "meaning": _classify_wifi_state(state_type, state_value),
        "raw_prefix": payload[:8].hex(),
    }


def _classify_wifi_state(state_type: int, state_value: int) -> str:
    """Classify WifiStateBean states observed in the official app."""
    if state_type == 3 and state_value == 0:
        return "network_config_success"
    if state_type == 0 and state_value == 0:
        return "idle_or_no_progress"
    if state_type == 0 and state_value == 1:
        return "in_progress_or_partial"
    if state_type == 0 and state_value == 2:
        return "transient_step_2"
    if state_type == 0 and state_value == 16:
        return "transient_step_16"
    return "unknown"


def _diff_module_blob_words(left: bytes, right: bytes) -> dict[str, Any]:
    """Summarize changed 32-bit words between two opaque payload snapshots."""
    word_count = min(len(left), len(right)) // 4
    changed_words: dict[str, dict[str, int]] = {}
    for index in range(word_count):
        left_word = int.from_bytes(left[index * 4 : index * 4 + 4], "little", signed=False)
        right_word = int.from_bytes(right[index * 4 : index * 4 + 4], "little", signed=False)
        if left_word != right_word:
            changed_words[f"w{index:02d}"] = {
                "left": left_word,
                "right": right_word,
            }

    return {
        "same_len": len(left) == len(right),
        "left_len": len(left),
        "right_len": len(right),
        "changed_word_count": len(changed_words),
        "changed_words": changed_words,
    }


@dataclass(slots=True)
class BleRecoveryState:
    in_progress: bool = False
    attempt_count: int = 0
    last_attempt: Any = None
    last_result: str | None = None
    last_error: str | None = None
    last_stage: str | None = None
    last_strategy: str | None = None
    last_network_status: dict[str, Any] | None = None
    last_auth_status: dict[str, Any] | None = None
    last_device_key_info: dict[str, Any] | None = None
    last_cloud_bind: dict[str, Any] | None = None
    learned_ssid: str | None = None
    learned_channel: int | None = None


class EcoflowBleProvisioner:
    def __init__(
        self,
        ble_device: BLEDevice,
        serial_number: str,
        user_id: str,
        *,
        encrypt_type: int,
        packet_version: int,
        timeout: int = 20,
    ) -> None:
        self._ble_device = ble_device
        self._serial_number = serial_number
        self._user_id = user_id
        self._encrypt_type = encrypt_type
        self._packet_version = packet_version
        self._timeout = timeout

        self._client: BleakClient | None = None
        self._notify_started = False
        self._notify_queue: asyncio.Queue[bytes] = asyncio.Queue()
        self._session_encryption: Type7Encryption | Type1Encryption | None = None

    async def connect(self) -> None:
        try:
            self._client = await establish_connection(
                BleakClient,
                self._ble_device,
                self._ble_device.name or self._serial_number,
                ble_device_callback=lambda: self._ble_device,
                max_attempts=3,
                timeout=self._timeout,
            )
        except (BleakError, BleakNotFoundError, TimeoutError) as err:
            raise BleRecoveryError(f"ble_connect_failed:{err}") from err

        backend = getattr(self._client, "_backend", None)
        if backend is not None and backend.__class__.__name__ == "BleakClientBlueZDBus":
            try:
                await backend._acquire_mtu()
            except Exception:  # noqa: BLE001
                _LOGGER.debug("Unable to acquire BLE MTU for %s", self._serial_number, exc_info=True)

    async def disconnect(self) -> None:
        if self._client is None:
            return
        try:
            if self._notify_started:
                try:
                    await self._client.stop_notify(self._notify_characteristic)
                except Exception:  # noqa: BLE001
                    _LOGGER.debug("Failed to stop notify for %s", self._serial_number, exc_info=True)
                self._notify_started = False
            if self._client.is_connected:
                await self._client.disconnect()
        except Exception:  # noqa: BLE001
            _LOGGER.debug("BLE disconnect failed for %s", self._serial_number, exc_info=True)
        finally:
            self._client = None

    @property
    def _write_characteristic(self):
        assert self._client is not None
        for uuids in _BT_PROTOCOL_UUIDS.values():
            characteristic = self._client.services.get_characteristic(uuids["write"])
            if characteristic is not None:
                return characteristic
        available = [
            f"{characteristic.uuid} {characteristic.description} {characteristic.properties}"
            for characteristic in self._client.services.characteristics.values()
        ]
        raise BleRecoveryError(f"unsupported_ble_write_protocol:{available}")

    @property
    def _notify_characteristic(self):
        assert self._client is not None
        for uuids in _BT_PROTOCOL_UUIDS.values():
            characteristic = self._client.services.get_characteristic(uuids["notify"])
            if characteristic is not None:
                return characteristic
        available = [
            f"{characteristic.uuid} {characteristic.description} {characteristic.properties}"
            for characteristic in self._client.services.characteristics.values()
        ]
        raise BleRecoveryError(f"unsupported_ble_notify_protocol:{available}")

    async def _ensure_notify(self) -> None:
        if self._notify_started:
            return
        assert self._client is not None

        def _handler(_: BleakGATTCharacteristic, data: bytearray) -> None:
            self._notify_queue.put_nowait(bytes(data))

        await self._client.start_notify(self._notify_characteristic, _handler)
        self._notify_started = True

    def _drain_notifications(self) -> None:
        while not self._notify_queue.empty():
            self._notify_queue.get_nowait()

    async def _write(self, payload: bytes, *, response: bool) -> None:
        assert self._client is not None
        await self._client.write_gatt_char(self._write_characteristic, bytearray(payload), response=response)

    async def _await_simple_payload(self, timeout: float) -> bytes:
        parser = SimplePacketAssembler()
        deadline = asyncio.get_running_loop().time() + timeout
        while True:
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                raise BleRecoveryError("simple_response_timeout")
            frame = await asyncio.wait_for(self._notify_queue.get(), timeout=remaining)
            try:
                payload = parser.parse(frame)
            except BlePacketError:
                continue
            if payload is not None:
                return payload

    async def _await_packets(
        self,
        timeout: float,
        *,
        predicate: Callable[[Packet], bool] | None = None,
    ) -> list[Packet]:
        if self._session_encryption is None:
            raise BleRecoveryError("session_not_initialized")

        assembler: EncPacketAssembler | RawHeaderAssembler
        if self._encrypt_type == 1:
            assembler = RawHeaderAssembler(self._session_encryption)  # type: ignore[arg-type]
        else:
            assembler = EncPacketAssembler(self._session_encryption)

        deadline = asyncio.get_running_loop().time() + timeout
        while True:
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                raise BleRecoveryError("packet_response_timeout")
            frame = await asyncio.wait_for(self._notify_queue.get(), timeout=remaining)
            packets: list[Packet] = []
            for raw_payload in await assembler.reassemble(frame):
                try:
                    packets.append(Packet.from_bytes(raw_payload))
                except BlePacketError:
                    continue
            if not packets:
                continue
            if predicate is None:
                return packets
            matched = [packet for packet in packets if predicate(packet)]
            if matched:
                return matched

    async def _await_dhodm_payloads(self, timeout: float) -> tuple[list[dict[str, Any]], bool]:
        if self._session_encryption is None:
            raise BleRecoveryError("session_not_initialized")

        assembler: EncPacketAssembler | RawHeaderAssembler
        if self._encrypt_type == 1:
            assembler = RawHeaderAssembler(self._session_encryption)  # type: ignore[arg-type]
        else:
            assembler = EncPacketAssembler(self._session_encryption)

        deadline = asyncio.get_running_loop().time() + timeout
        ignored_frames = 0
        seen_frames = 0
        raw_payloads_seen = 0
        sample_notes: list[str] = []
        saw_packet_activity = False
        while True:
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                summary = (
                    f"dhodm_response_timeout:"
                    f"frames={seen_frames},payloads={raw_payloads_seen},ignored={ignored_frames},samples={sample_notes[:5]}"
                )
                raise BleRecoveryError(summary)

            try:
                frame = await asyncio.wait_for(self._notify_queue.get(), timeout=remaining)
            except TimeoutError as err:
                summary = (
                    f"dhodm_response_timeout:"
                    f"frames={seen_frames},payloads={raw_payloads_seen},ignored={ignored_frames},samples={sample_notes[:5]}"
                )
                raise BleRecoveryError(summary) from err
            seen_frames += 1
            responses: list[dict[str, Any]] = []
            raw_payload_batch = await assembler.reassemble(frame)
            if not raw_payload_batch:
                sample_notes.append(f"no-payload len={len(frame)} hex={frame[:16].hex()}")
            for raw_payload in raw_payload_batch:
                raw_payloads_seen += 1
                try:
                    decoded = raw_payload.decode("utf-8")
                except UnicodeDecodeError:
                    ignored_frames += 1
                    if len(sample_notes) < 8:
                        try:
                            packet = Packet.from_bytes(raw_payload)
                            saw_packet_activity = True
                            decoded_network_status = None
                            if packet.cmd_set == 0x20:
                                decoded_network_status = _decode_network_status_payload(packet.payload)
                            sample_notes.append(
                                "packet "
                                f"src=0x{packet.src:02X} dst=0x{packet.dst:02X} "
                                f"cmd_set=0x{packet.cmd_set:02X} cmd_id=0x{packet.cmd_id:02X} "
                                f"seq={packet.seq.hex()} decoded={decoded_network_status}"
                            )
                        except Exception:  # noqa: BLE001
                            sample_notes.append(f"non-utf8 len={len(raw_payload)} hex={raw_payload[:24].hex()}")
                    continue
                try:
                    payload = json.loads(decoded)
                except json.JSONDecodeError:
                    ignored_frames += 1
                    if len(sample_notes) < 8:
                        sample_notes.append(f"non-json {decoded[:80]!r}")
                    continue
                if isinstance(payload, dict):
                    responses.append(payload)
                else:
                    ignored_frames += 1
                    if len(sample_notes) < 8:
                        sample_notes.append(f"non-dict-json {payload!r}")

            if responses:
                return responses, saw_packet_activity

            if saw_packet_activity:
                return [], True

    async def _send_simple_request(self, payload: bytes, *, timeout: float = 10) -> bytes:
        await self._ensure_notify()
        self._drain_notifications()
        await self._write(SimplePacketAssembler.encode(payload), response=True)
        return await self._await_simple_payload(timeout)

    async def _send_dhodm_rpc_request(self, payload: bytes, *, timeout: float = 5) -> tuple[list[dict[str, Any]], bool]:
        if self._session_encryption is None:
            raise BleRecoveryError("session_not_initialized")

        await self._ensure_notify()
        self._drain_notifications()
        encoded = EncPacket(
            EncPacket.FRAME_TYPE_PROTOCOL,
            0x02,
            payload,
            self._session_encryption.session_key,
            self._session_encryption.iv,
        ).to_bytes()
        await self._write(encoded, response=True)
        return await self._await_dhodm_payloads(timeout)

    def _packet_assembler(self) -> EncPacketAssembler | RawHeaderAssembler:
        if self._session_encryption is None:
            raise BleRecoveryError("session_not_initialized")
        if self._encrypt_type == 1:
            assert isinstance(self._session_encryption, Type1Encryption)
            return RawHeaderAssembler(self._session_encryption)
        return EncPacketAssembler(self._session_encryption)

    async def _send_packet_request(
        self,
        packet: Packet,
        *,
        timeout: float = 10,
        predicate: Callable[[Packet], bool] | None = None,
    ) -> list[Packet]:
        await self._ensure_notify()
        self._drain_notifications()
        assembler = self._packet_assembler()
        payload = await assembler.encode(packet)
        await self._write(payload, response=assembler.write_with_response)
        return await self._await_packets(timeout, predicate=predicate)

    async def _send_packet_no_reply(self, packet: Packet) -> None:
        await self._ensure_notify()
        self._drain_notifications()
        assembler = self._packet_assembler()
        payload = await assembler.encode(packet)
        await self._write(payload, response=assembler.write_with_response)

    async def _send_packet_no_reply_without_drain(self, packet: Packet) -> None:
        await self._ensure_notify()
        assembler = self._packet_assembler()
        payload = await assembler.encode(packet)
        await self._write(payload, response=assembler.write_with_response)

    async def _reply_packet(self, packet: Packet) -> None:
        reply = Packet(
            packet.dst,
            packet.src,
            packet.cmd_set,
            packet.cmd_id,
            packet.payload,
            dsrc=0x01,
            ddst=0x01,
            version=packet.version,
            seq=packet.seq,
            product_id=packet.product_id,
        )
        await self._send_packet_no_reply_without_drain(reply)

    @staticmethod
    def _should_reply_post_provision_packet(packet: Packet) -> bool:
        if packet.dst != 0x21:
            return False

        if packet.cmd_set == 0x20:
            return True

        if packet.src in {0x02, 0x03, 0x04, 0x05} and packet.cmd_set == 0x02:
            return True

        return packet.src == 0x06 and packet.cmd_set == 0xFE and packet.cmd_id == 0x10

    def _generate_session_key(self, seed: bytes, srand: bytes) -> bytes:
        position = seed[0] * 0x10 + ((seed[1] - 1) & 0xFF) * 0x100
        data = keydata.get8bytes(position)
        data += keydata.get8bytes(position + 8)
        data += srand[:16]
        return hashlib.md5(data).digest()

    async def _authenticate_type7(self) -> None:
        private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP160r1)
        public_key = private_key.get_verifying_key()
        response = await self._send_simple_request(b"\x01\x00" + public_key.to_string())
        if len(response) < 3:
            raise BleAuthError(f"invalid_public_key_response:{response.hex()}")

        curve_size = _get_ecdh_type_size(response[2])
        device_public_key = ecdsa.VerifyingKey.from_string(
            response[3 : 3 + curve_size],
            curve=ecdsa.SECP160r1,
        )
        shared_key = ecdsa.ECDH(ecdsa.SECP160r1, private_key, device_public_key).generate_sharedsecret_bytes()
        iv = hashlib.md5(shared_key).digest()
        temp_encryption = Type7Encryption(shared_key[:16], iv)

        key_info = await self._send_simple_request(b"\x02")
        if not key_info or key_info[0] != 0x02:
            raise BleAuthError(f"key_info_request_failed:{key_info.hex()}")

        decrypted = await temp_encryption.decrypt(key_info[1:])
        session_key = self._generate_session_key(decrypted[16:18], decrypted[:16])
        self._session_encryption = Type7Encryption(session_key, iv)

    async def _authenticate_type1(self) -> None:
        session_key = hashlib.md5(self._serial_number.encode()).digest()
        iv = hashlib.md5(self._serial_number[::-1].encode()).digest()
        self._session_encryption = Type1Encryption(session_key, iv)

    async def authenticate(self) -> dict[str, Any]:
        if self._encrypt_type == 1:
            await self._authenticate_type1()
        else:
            await self._authenticate_type7()

        auth_status_packet = Packet(
            0x21,
            _AUTH_HEADER_DST,
            0x35,
            0x89,
            b"",
            dsrc=0x01,
            ddst=0x01,
            version=self._packet_version,
        )
        auth_status_packets = await self._send_packet_request(
            auth_status_packet,
            timeout=10,
            predicate=lambda packet: packet.src == _AUTH_HEADER_DST
            and packet.cmd_set == 0x35
            and packet.cmd_id == 0x89,
        )
        auth_status = _decode_auth_status_payload(auth_status_packets[0].payload)
        _LOGGER.info(
            "BLE auth status for %s: auth_type=%s key_status=%s flow=%s raw=%s",
            self._serial_number,
            auth_status["auth_type"],
            auth_status["key_status"],
            auth_status["flow"],
            auth_status["raw"],
        )

        if auth_status["auth_type"] == 1:
            return auth_status

        md5_data = hashlib.md5((self._user_id + self._serial_number).encode("ascii")).digest()
        auth_payload = ("".join(f"{byte:02X}" for byte in md5_data)).encode("ascii")
        auth_packet = Packet(
            0x21,
            _AUTH_HEADER_DST,
            0x35,
            0x86,
            auth_payload,
            dsrc=0x01,
            ddst=0x01,
            version=self._packet_version,
        )
        auth_packets = await self._send_packet_request(
            auth_packet,
            timeout=10,
            predicate=lambda packet: packet.src == _AUTH_HEADER_DST
            and packet.cmd_set == 0x35
            and packet.cmd_id == 0x86,
        )
        auth_error = _auth_result_error(auth_packets[0].payload)
        if auth_error is not None:
            raise BleAuthError(auth_error)
        auth_status["key_auth_result"] = "ok"
        return auth_status

    async def query_device_key_info(self) -> dict[str, Any]:
        user_id_bytes = self._user_id.encode("utf-8")[:64]
        payload = bytes([0x01]) + user_id_bytes.ljust(64, b"\x00") + struct.pack(
            "<I", int(dt.utcnow().timestamp())
        )
        packet = Packet(
            0x20,
            _AUTH_HEADER_DST,
            0x35,
            0xA8,
            payload,
            dsrc=0x01,
            ddst=0x01,
            version=4,
            seq=_next_packet_seq(),
        )
        try:
            packets = await self._send_packet_request(
                packet,
                timeout=10,
                predicate=lambda response: response.cmd_set == 0x35 and response.cmd_id == 0xA8,
            )
        except (BleRecoveryError, TimeoutError):
            decoded = {
                "is_success": False,
                "error": "timeout",
            }
            _LOGGER.warning(
                "BLE device-key-info probe timed out for %s",
                self._serial_number,
            )
            return decoded
        decoded = _decode_device_key_info_payload(packets[0].payload)
        _LOGGER.info(
            "BLE device-key-info for %s: success=%s ver=%s timestamp=%s random_code_len=%s sign_string_len=%s raw=%s",
            self._serial_number,
            decoded.get("is_success"),
            decoded.get("ver"),
            decoded.get("timestamp"),
            len(decoded.get("random_code", "")),
            len(decoded.get("sign_string", "")),
            decoded.get("raw"),
        )
        return decoded

    async def provision_wifi(
        self,
        *,
        ssid: str,
        password: str,
        bssid: str | None = None,
        channel: int | None = None,
        https_url: str | None = None,
        ) -> dict[str, Any]:
        payload = _build_network_message_payload(
            ssid=ssid,
            password=password,
            bssid=_parse_bssid(bssid),
            channel=channel,
            https_url=https_url,
        )
        packet = Packet(
            0x21,
            _AUTH_HEADER_DST,
            0x35,
            0x0D,
            payload,
            dsrc=0x01,
            ddst=0x01,
            version=self._packet_version,
        )
        await self._send_packet_no_reply(packet)
        try:
            packets = await self._await_packets(timeout=5)
        except BleRecoveryError:
            _LOGGER.debug("No immediate BLE provision response for %s", self._serial_number)
            return await self._observe_post_provision_packets(timeout=_POST_PROVISION_OBSERVE_SEC)

        for response in packets:
            _LOGGER.debug(
                "BLE provision response for %s: src=0x%02X cmd_set=0x%02X cmd_id=0x%02X payload=%s",
                self._serial_number,
                response.src,
                response.cmd_set,
                response.cmd_id,
                response.payload.hex(),
            )

        return await self._observe_post_provision_packets(timeout=_POST_PROVISION_OBSERVE_SEC)

    async def provision_wifi_cfg_net(
        self,
        *,
        ssid: str,
        password: str,
        https_url: str | None = None,
    ) -> dict[str, Any]:
        payload = _build_cfg_net_device_list_payload(
            device_sns=[self._serial_number],
            ssid=ssid,
            password=password,
            https_url=https_url,
        )
        packet = Packet(
            0x20,
            _AUTH_HEADER_DST,
            0x35,
            0x2A,
            payload,
            dsrc=0x01,
            ddst=0x01,
            version=4,
            seq=_next_packet_seq(),
        )
        await self._send_packet_no_reply(packet)
        try:
            packets = await self._await_packets(timeout=5)
        except BleRecoveryError:
            _LOGGER.debug("No immediate BLE cfg-net response for %s", self._serial_number)
            return await self._observe_post_provision_packets(timeout=_POST_PROVISION_OBSERVE_SEC)

        for response in packets:
            wifi_state = None
            if response.cmd_set == 0x35 and response.cmd_id in {0x20, 0x35}:
                wifi_state = _decode_wifi_state_prefix(response.payload)
            _LOGGER.debug(
                "BLE cfg-net response for %s: src=0x%02X dst=0x%02X cmd_set=0x%02X cmd_id=0x%02X seq=%s payload=%s decoded=%s",
                self._serial_number,
                response.src,
                response.dst,
                response.cmd_set,
                response.cmd_id,
                response.seq.hex(),
                response.payload.hex(),
                wifi_state,
            )

        return await self._observe_post_provision_packets(timeout=_POST_PROVISION_OBSERVE_SEC)

    async def provision_device_url(self, *, https_url: str) -> None:
        if not https_url.strip():
            return

        payload = _build_network_message_payload(
            ssid=None,
            password=None,
            bssid=None,
            channel=None,
            https_url=https_url,
        )
        packet = Packet(
            0x21,
            _AUTH_HEADER_DST,
            0x35,
            0x0D,
            payload,
            dsrc=0x01,
            ddst=0x01,
            version=self._packet_version,
        )
        await self._send_packet_no_reply(packet)

        try:
            packets = await self._await_packets(timeout=2)
        except BleRecoveryError:
            _LOGGER.debug("No immediate BLE URL-preflight response for %s", self._serial_number)
            return

        for response in packets:
            decoded_network_status = None
            if response.cmd_set == 0x20:
                decoded_network_status = _decode_network_status_payload(response.payload)

            _LOGGER.debug(
                "BLE URL-preflight response for %s: src=0x%02X dst=0x%02X cmd_set=0x%02X cmd_id=0x%02X payload=%s decoded=%s",
                self._serial_number,
                response.src,
                response.dst,
                response.cmd_set,
                response.cmd_id,
                response.payload.hex(),
                decoded_network_status,
            )

    async def send_dhodm_rpc(
        self,
        *,
        method: str,
        params: dict[str, Any],
        request_id: int,
        timeout: float = 5,
        best_effort: bool = False,
    ) -> list[dict[str, Any]]:
        payload = _build_dhodm_rpc_payload(
            request_id=request_id,
            method=method,
            params=params,
        )
        try:
            responses, saw_packet_activity = await self._send_dhodm_rpc_request(payload, timeout=timeout)
        except BleRecoveryError as err:
            err_text = str(err)
            if not best_effort or not err_text.startswith("dhodm_response_timeout"):
                raise
            _LOGGER.warning(
                "BLE DHOdm request timed out for %s method=%s request_id=%s details=%s; continuing best-effort",
                self._serial_number,
                method,
                request_id,
                err_text,
            )
            return []
        if saw_packet_activity and not responses:
            _LOGGER.info(
                "BLE DHOdm command for %s method=%s request_id=%s saw packet activity without JSON reply",
                self._serial_number,
                method,
                request_id,
            )
        for response in responses:
            _LOGGER.debug(
                "BLE DHOdm response for %s method=%s request_id=%s payload=%s",
                self._serial_number,
                method,
                request_id,
                response,
            )
        return responses

    async def provision_mqtt_config(
        self,
        *,
        request_id: int,
        server: str,
        client_id: str,
        username: str,
        password: str,
        topic_prefix: str,
        ssl_ca: str,
    ) -> bool | None:
        responses = await self.send_dhodm_rpc(
            method="Mqtt.SetConfig",
            request_id=request_id,
            params={
                "config": {
                    "enable": True,
                    "server": server,
                    "client_id": client_id,
                    "user": username,
                    "pass": password,
                    "ssl_ca": ssl_ca,
                    "topic_prefix": topic_prefix,
                    "use_client_cert": False,
                }
            },
            best_effort=True,
        )
        return self._extract_restart_required(responses)

    async def configure_rpc_udp(self, *, request_id: int) -> bool | None:
        responses = await self.send_dhodm_rpc(
            method="Sys.SetConfig",
            request_id=request_id,
            params={"config": {"rpc_udp": {"listen_port": 7890}}},
            best_effort=True,
        )
        return self._extract_restart_required(responses)

    async def enable_ble_config(self, *, request_id: int) -> bool | None:
        responses = await self.send_dhodm_rpc(
            method="BLE.SetConfig",
            request_id=request_id,
            params={"config": {"enable": True}},
            timeout=2,
            best_effort=True,
        )
        return self._extract_restart_required(responses)

    async def reboot_device(self, *, request_id: int) -> bool | None:
        responses = await self.send_dhodm_rpc(
            method="Shelly.Reboot",
            request_id=request_id,
            params={},
            timeout=2,
            best_effort=True,
        )
        return self._extract_restart_required(responses)

    async def request_wifi_status(self, *, request_id: int) -> None:
        await self.send_dhodm_rpc(
            method="WiFi.GetStatus",
            request_id=request_id,
            params={},
            timeout=2,
            best_effort=True,
        )

    async def request_mqtt_status(self, *, request_id: int) -> None:
        await self.send_dhodm_rpc(
            method="Mqtt.GetStatus",
            request_id=request_id,
            params={},
            timeout=2,
            best_effort=True,
        )

    @staticmethod
    def _extract_restart_required(responses: list[dict[str, Any]]) -> bool | None:
        for response in responses:
            result = response.get("result")
            if isinstance(result, dict) and "restart_required" in result:
                restart_required = result.get("restart_required")
                if isinstance(restart_required, bool):
                    return restart_required
        return None

    async def query_connect_status(self) -> list[Packet]:
        packet = Packet(
            0x21,
            _AUTH_HEADER_DST,
            0x35,
            0xA2,
            b"",
            dsrc=0x01,
            ddst=0x01,
            version=self._packet_version,
        )

        try:
            packets = await self._send_packet_request(packet, timeout=2)
        except BleRecoveryError:
            _LOGGER.debug("No BLE connect-status response for %s", self._serial_number)
            return []

        for response in packets:
            decoded_network_status = None
            if response.cmd_set == 0x20:
                decoded_network_status = _decode_network_status_payload(response.payload)

            _LOGGER.debug(
                "BLE connect-status response for %s: src=0x%02X dst=0x%02X cmd_set=0x%02X cmd_id=0x%02X payload=%s decoded=%s",
                self._serial_number,
                response.src,
                response.dst,
                response.cmd_set,
                response.cmd_id,
                response.payload.hex(),
                decoded_network_status,
            )

        return packets

    async def query_pd_wifi_info(self) -> list[Packet]:
        packet = Packet(
            0x21,
            _PD_ADDR,
            _PD_CMD_SET,
            _PD_GET_WIFI_INFO_CMD_ID,
            b"",
            dsrc=0x01,
            ddst=0x01,
            version=self._packet_version,
        )

        try:
            packets = await self._send_packet_request(
                packet,
                timeout=3,
                predicate=lambda response: response.src == _PD_ADDR and response.cmd_set == _PD_CMD_SET,
            )
        except BleRecoveryError:
            _LOGGER.warning("No PD wifi-info response for %s", self._serial_number)
            return []

        for response in packets:
            _LOGGER.warning(
                "BLE PD wifi-info response for %s: src=0x%02X dst=0x%02X cmd_set=0x%02X cmd_id=0x%02X seq=%s payload=%s",
                self._serial_number,
                response.src,
                response.dst,
                response.cmd_set,
                response.cmd_id,
                response.seq.hex(),
                response.payload.hex(),
            )

        return packets

    async def query_ap_follow_info_list(self) -> list[Packet]:
        packet = Packet(
            0x21,
            _AUTH_HEADER_DST,
            _AP_FOLLOW_INFO_LIST_CMD_SET,
            _AP_FOLLOW_INFO_LIST_CMD_ID,
            _build_ap_follow_info_list_get_payload(),
            dsrc=0x01,
            ddst=0x01,
            version=self._packet_version,
        )

        await self._ensure_notify()
        self._drain_notifications()
        assembler = self._packet_assembler()
        payload = await assembler.encode(packet)
        await self._write(payload, response=assembler.write_with_response)

        packets: list[Packet] = []
        sample_packets: list[dict[str, Any]] = []
        deadline = asyncio.get_running_loop().time() + 3
        while True:
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                break
            try:
                batch = await self._await_packets(timeout=min(remaining, 1))
            except (BleRecoveryError, TimeoutError):
                break

            for response in batch:
                decoded = None
                if response.cmd_set == _AP_FOLLOW_INFO_LIST_CMD_SET:
                    decoded = _decode_ap_follow_info_list(response.payload)
                wifi_state = None
                wifi_state_prefix = None
                if response.cmd_set == _PD_CMD_SET and response.cmd_id == 0x20:
                    wifi_state = _decode_wifi_state_payload(response.payload)
                elif response.cmd_set == _PD_CMD_SET:
                    wifi_state_prefix = _decode_wifi_state_prefix(response.payload)
                if len(sample_packets) < 8:
                    sample_packets.append(
                        {
                            "src": f"0x{response.src:02X}",
                            "dst": f"0x{response.dst:02X}",
                            "cmd_set": f"0x{response.cmd_set:02X}",
                            "cmd_id": f"0x{response.cmd_id:02X}",
                            "seq": response.seq.hex(),
                            "decoded": decoded,
                            "wifi_state": wifi_state,
                            "wifi_state_prefix": wifi_state_prefix,
                            "payload": response.payload.hex(),
                        }
                    )
                if response.cmd_id == _AP_FOLLOW_INFO_LIST_CMD_ID or decoded is not None:
                    packets.append(response)

        if not packets:
            _LOGGER.warning(
                "No AP-follow wifi-info response for %s; samples=%s",
                self._serial_number,
                sample_packets,
            )
            return []

        for response in packets:
            _LOGGER.warning(
                "BLE AP-follow wifi-info response for %s: src=0x%02X dst=0x%02X cmd_set=0x%02X cmd_id=0x%02X seq=%s payload=%s decoded=%s",
                self._serial_number,
                response.src,
                response.dst,
                response.cmd_set,
                response.cmd_id,
                response.seq.hex(),
                response.payload.hex(),
                _decode_ap_follow_info_list(response.payload),
            )

        return packets

    async def _observe_post_provision_packets(self, timeout: float) -> dict[str, Any]:
        deadline = asyncio.get_running_loop().time() + timeout
        saw_packet = False
        network_status_by_source: dict[str, Any] = {}

        await self.query_connect_status()

        while True:
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                break

            try:
                packets = await self._await_packets(timeout=min(remaining, 5))
            except (BleRecoveryError, TimeoutError):
                break

            saw_packet = True
            for response in packets:
                decoded_network_status = None
                wifi_state = None
                wifi_state_prefix = None
                if response.cmd_set == 0x20:
                    decoded_network_status = _decode_network_status_payload(response.payload)
                    if decoded_network_status is not None:
                        network_status_by_source[f"0x{response.src:02X}"] = decoded_network_status
                    elif response.cmd_id == 0x20:
                        wifi_state = _decode_wifi_state_payload(response.payload)
                        if wifi_state is not None:
                            network_status_by_source[f"0x{response.src:02X}"] = {
                                "module": _module_source_name(response.src),
                                "cmd_id": response.cmd_id,
                                "seq": response.seq.hex(),
                                "wifi_state": wifi_state,
                                "raw": response.payload.hex(),
                            }
                    else:
                        wifi_state_prefix = _decode_wifi_state_prefix(response.payload)
                        network_status_by_source[f"0x{response.src:02X}"] = {
                            "module": _module_source_name(response.src),
                            "cmd_id": response.cmd_id,
                            "seq": response.seq.hex(),
                            "wifi_state_prefix": wifi_state_prefix,
                            "decoded_words": _decode_module_blob_words(response.payload),
                            "raw": response.payload.hex(),
                        }
                elif response.cmd_set == 0x35 and response.cmd_id in {0x20, 0x35}:
                    wifi_state_prefix = _decode_wifi_state_prefix(response.payload)
                    network_status_by_source[f"0x35:{response.cmd_id:02X}:0x{response.src:02X}"] = {
                        "module": _module_source_name(response.src),
                        "cmd_id": response.cmd_id,
                        "seq": response.seq.hex(),
                        "wifi_state_prefix": wifi_state_prefix,
                        "raw": response.payload.hex(),
                    }

                if response.cmd_set == 0x35 and response.cmd_id == 0xA2:
                    _LOGGER.info(
                        "BLE post-provision connect status for %s: src=0x%02X seq=%s payload=%s",
                        self._serial_number,
                        response.src,
                        response.seq.hex(),
                        response.payload.hex(),
                    )
                else:
                    _LOGGER.debug(
                        "BLE post-provision packet for %s: src=0x%02X dst=0x%02X cmd_set=0x%02X cmd_id=0x%02X seq=%s payload=%s decoded=%s",
                        self._serial_number,
                        response.src,
                        response.dst,
                        response.cmd_set,
                        response.cmd_id,
                        response.seq.hex(),
                        response.payload.hex(),
                        decoded_network_status
                        if decoded_network_status is not None
                        else wifi_state
                        if wifi_state is not None
                        else wifi_state_prefix,
                    )

                if self._should_reply_post_provision_packet(response):
                    _LOGGER.debug(
                        "BLE post-provision ack for %s: src=0x%02X dst=0x%02X cmd_set=0x%02X cmd_id=0x%02X seq=%s",
                        self._serial_number,
                        response.src,
                        response.dst,
                        response.cmd_set,
                        response.cmd_id,
                        response.seq.hex(),
                    )
                    await self._reply_packet(response)

        if not saw_packet:
            _LOGGER.debug("No BLE post-provision status packets for %s", self._serial_number)
        return network_status_by_source


class EcoflowBleRecoveryManager:
    def __init__(self, hass: HomeAssistant, client: "EcoflowApiClient", entry_id: str) -> None:
        self._hass = hass
        self._client = client
        self._entry_id = entry_id
        self._states: dict[str, BleRecoveryState] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._tasks: dict[str, asyncio.Task[bool]] = {}

    def supports_device(self, device_data: "DeviceData") -> bool:
        return supports_ble_wifi_recovery_device_type(device_data.device_type) and bool(
            str(getattr(self._client, "user_id", "")).strip()
        )

    def state_attributes(self, sn: str) -> dict[str, Any]:
        state = self._states.get(sn)
        if state is None:
            return {
                ATTR_BLE_RECOVERY_ACTIVE: False,
                ATTR_BLE_RECOVERY_ATTEMPTS: 0,
                ATTR_BLE_RECOVERY_LAST_ATTEMPT: None,
                ATTR_BLE_RECOVERY_LAST_RESULT: None,
                ATTR_BLE_RECOVERY_LAST_ERROR: None,
                ATTR_BLE_RECOVERY_STAGE: None,
                ATTR_BLE_RECOVERY_STRATEGY: None,
                ATTR_BLE_RECOVERY_NETWORK_STATUS: None,
                ATTR_BLE_RECOVERY_AUTH_STATUS: None,
                "ble_recovery_device_key_info": None,
                ATTR_BLE_RECOVERY_CLOUD_BIND: None,
            }
        return {
            ATTR_BLE_RECOVERY_ACTIVE: state.in_progress,
            ATTR_BLE_RECOVERY_ATTEMPTS: state.attempt_count,
            ATTR_BLE_RECOVERY_LAST_ATTEMPT: state.last_attempt,
            ATTR_BLE_RECOVERY_LAST_RESULT: state.last_result,
            ATTR_BLE_RECOVERY_LAST_ERROR: state.last_error,
            ATTR_BLE_RECOVERY_STAGE: state.last_stage,
            ATTR_BLE_RECOVERY_STRATEGY: state.last_strategy,
            ATTR_BLE_RECOVERY_NETWORK_STATUS: state.last_network_status,
            ATTR_BLE_RECOVERY_AUTH_STATUS: state.last_auth_status,
            "ble_recovery_device_key_info": state.last_device_key_info,
            ATTR_BLE_RECOVERY_CLOUD_BIND: state.last_cloud_bind,
        }

    async def async_shutdown(self) -> None:
        for task in list(self._tasks.values()):
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks.values(), return_exceptions=True)
        self._tasks.clear()

    def async_schedule_recovery(self, sn: str, *, reason: str) -> None:
        if sn in self._tasks and not self._tasks[sn].done():
            return

        task = self._hass.async_create_task(self.async_recover(sn, reason=reason))
        self._tasks[sn] = task

        def _cleanup(done_task: asyncio.Task[bool]) -> None:
            current = self._tasks.get(sn)
            if current is done_task:
                self._tasks.pop(sn, None)

        task.add_done_callback(_cleanup)

    async def async_recover(
        self,
        sn: str,
        *,
        reason: str = "manual",
        manual: bool = False,
        ssid: str | None = None,
        password: str | None = None,
        bssid: str | None = None,
        channel: int | None = None,
    ) -> bool:
        lock = self._locks.setdefault(sn, asyncio.Lock())
        if lock.locked():
            return False

        async with lock:
            return await self._async_recover_locked(
                sn,
                reason=reason,
                manual=manual,
                ssid=ssid,
                password=password,
                bssid=bssid,
                channel=channel,
            )

    def _state(self, sn: str) -> BleRecoveryState:
        return self._states.setdefault(sn, BleRecoveryState())

    def _device(self, sn: str):
        return self._client.devices.get(sn)

    @staticmethod
    def _issue_id(sn: str) -> str:
        return f"{_BLE_WIFI_CREDENTIALS_ISSUE_PREFIX}{sn}"

    @staticmethod
    def _normalize_wifi_key(key: str) -> str:
        return "".join(char for char in key.lower() if char.isalnum())

    def _extract_wifi_ssid(self, value: Any) -> str | None:
        if isinstance(value, dict):
            for key, item in value.items():
                if isinstance(item, str) and self._normalize_wifi_key(key) in _WIFI_SSID_KEYS:
                    ssid = item.strip()
                    if ssid:
                        return ssid
                nested = self._extract_wifi_ssid(item)
                if nested:
                    return nested
            return None

        if isinstance(value, list):
            for item in value:
                nested = self._extract_wifi_ssid(item)
                if nested:
                    return nested
        return None

    def _extract_wifi_channel(self, value: Any) -> int | None:
        if isinstance(value, dict):
            for key, item in value.items():
                if self._normalize_wifi_key(key) in _WIFI_CHANNEL_KEYS:
                    channel = _normalize_wifi_channel(item)
                    if channel is not None:
                        return channel
                nested = self._extract_wifi_channel(item)
                if nested is not None:
                    return nested
            return None

        if isinstance(value, list):
            for item in value:
                nested = self._extract_wifi_channel(item)
                if nested is not None:
                    return nested

        return None

    def note_online_device(self, sn: str) -> None:
        device = self._device(sn)
        if device is None or not bool(device.data.online):
            return

        ssid = self._extract_wifi_ssid(device.data.params)
        if not ssid:
            return

        state = self._state(sn)
        state.learned_ssid = ssid
        if not device.device_data.options.ble_wifi_ssid:
            device.device_data.options.ble_wifi_ssid = ssid

        channel = self._extract_wifi_channel(device.data.params)
        if channel is not None:
            state.learned_channel = channel
            if device.device_data.options.ble_wifi_channel is None:
                device.device_data.options.ble_wifi_channel = channel

    def _find_device_discovery(self, sn: str) -> BluetoothServiceInfoBleak | None:
        matches_by_address: dict[str, list[BluetoothServiceInfoBleak]] = {}
        for discovery in async_discovered_service_info(self._hass):
            if _serial_from_advertisement(discovery.advertisement) != sn:
                continue

            address = _discovery_address(discovery)
            matches_by_address.setdefault(address, []).append(discovery)

        if not matches_by_address:
            return None

        preferred_matches: list[BluetoothServiceInfoBleak] = []
        for address, candidates in matches_by_address.items():
            for candidate in candidates:
                _LOGGER.debug(
                    "BLE recovery candidate for %s via source=%s address=%s rssi=%s name=%s",
                    sn,
                    _discovery_source(candidate),
                    address,
                    _discovery_rssi(candidate),
                    _discovery_name(candidate),
                )

            preferred = async_last_service_info(self._hass, address, connectable=True)
            if preferred is not None and _serial_from_advertisement(preferred.advertisement) == sn:
                preferred_matches.append(preferred)
                continue

            preferred_matches.append(max(candidates, key=_discovery_rssi))

        selected = max(preferred_matches, key=_discovery_rssi)
        _LOGGER.debug(
            "BLE recovery selected source=%s address=%s rssi=%s name=%s for %s",
            _discovery_source(selected),
            _discovery_address(selected),
            _discovery_rssi(selected),
            _discovery_name(selected),
            sn,
        )
        return selected

    def _delete_credentials_issue(self, sn: str) -> None:
        ir.async_delete_issue(self._hass, "ecoflow_cloud", self._issue_id(sn))

    def _create_credentials_issue(self, sn: str, *, reason: str) -> None:
        device = self._device(sn)
        if device is None:
            return

        state = self._state(sn)
        suggested_ssid = device.device_data.options.ble_wifi_ssid or state.learned_ssid or ""
        ir.async_create_issue(
            self._hass,
            "ecoflow_cloud",
            self._issue_id(sn),
            is_fixable=True,
            is_persistent=True,
            severity=ir.IssueSeverity.ERROR,
            translation_key="ble_wifi_credentials",
            translation_placeholders={
                "device_name": device.device_data.name,
            },
            data={
                "entry_id": self._entry_id,
                "serial_number": sn,
                "reason": reason,
                "suggested_ssid": suggested_ssid,
            },
        )

    def _find_shared_wifi_password(self, sn: str, ssid: str) -> str | None:
        target_ssid = ssid.strip()
        if not target_ssid:
            return None

        for other_sn, other_device in self._client.devices.items():
            if other_sn == sn:
                continue

            other_options = other_device.device_data.options
            other_ssid = other_options.ble_wifi_ssid.strip()
            if not other_ssid:
                other_state = self._states.get(other_sn)
                other_ssid = (other_state.learned_ssid or "").strip() if other_state is not None else ""

            if other_ssid != target_ssid:
                continue

            shared_password = other_options.ble_wifi_password.strip()
            if shared_password:
                return shared_password

        return None

    def _persist_wifi_credentials(self, sn: str, *, ssid: str, password: str) -> None:
        device = self._device(sn)
        if device is None:
            return

        ssid = ssid.strip()
        password = password.strip()
        if not ssid or not password:
            return

        changed = False
        if device.device_data.options.ble_wifi_ssid != ssid:
            device.device_data.options.ble_wifi_ssid = ssid
            changed = True
        if device.device_data.options.ble_wifi_password != password:
            device.device_data.options.ble_wifi_password = password
            changed = True
        if not changed:
            return

        entry = self._hass.config_entries.async_get_entry(self._entry_id)
        if entry is None:
            return

        new_options = deepcopy(dict(entry.options))
        if sn not in new_options.get(CONF_DEVICE_LIST, {}):
            return

        new_options[CONF_DEVICE_LIST][sn][OPTS_BLE_WIFI_SSID] = ssid
        new_options[CONF_DEVICE_LIST][sn][OPTS_BLE_WIFI_PASSWORD] = password
        self._hass.config_entries.async_update_entry(entry, options=new_options)

    async def _wait_for_cloud_recovery(self, sn: str, timeout: int) -> bool:
        device = self._device(sn)
        if device is None:
            return False

        start_time = device.data.last_received_time()
        deadline = asyncio.get_running_loop().time() + timeout
        last_quota_request = 0.0

        while True:
            if device.data.last_received_time() > start_time and bool(device.data.online):
                return True

            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                return False

            if (
                getattr(self._client, "mqtt_client", None) is not None
                and self._client.mqtt_client.is_connected()
                and asyncio.get_running_loop().time() - last_quota_request >= 10
            ):
                await self._client.quota_all(sn)
                last_quota_request = asyncio.get_running_loop().time()

            await asyncio.sleep(min(5, remaining))

    async def _async_recover_locked(
        self,
        sn: str,
        *,
        reason: str,
        manual: bool,
        ssid: str | None,
        password: str | None,
        bssid: str | None,
        channel: int | None,
    ) -> bool:
        state = self._state(sn)
        device = self._device(sn)
        now = dt.utcnow()

        if device is None:
            state.last_attempt = now
            state.last_result = "device_missing"
            state.last_error = None
            return False

        options = device.device_data.options
        if not manual and state.last_attempt is not None:
            elapsed = (now - state.last_attempt).total_seconds()
            if elapsed < options.ble_recovery_cooldown_sec:
                state.last_result = "cooldown"
                state.last_error = None
                return False

        state.in_progress = True
        state.attempt_count += 1
        state.last_attempt = now
        state.last_error = None
        state.last_stage = "start"
        state.last_strategy = None
        state.last_network_status = None
        state.last_auth_status = None
        state.last_device_key_info = None
        state.last_cloud_bind = None

        try:
            if not supports_ble_wifi_recovery_device_type(device.device_data.device_type):
                state.last_result = "unsupported_device"
                state.last_stage = "unsupported_device"
                return False

            user_id = str(getattr(self._client, "user_id", "")).strip()
            if not user_id:
                state.last_result = "unsupported_auth_type"
                state.last_stage = "unsupported_auth_type"
                return False

            if not manual and not options.ble_wifi_recovery_enabled:
                state.last_result = "disabled"
                state.last_stage = "disabled"
                return False

            target_ssid = options.ble_wifi_ssid if ssid is None else ssid
            target_password = options.ble_wifi_password if password is None else password
            target_bssid = options.ble_wifi_bssid if bssid is None else bssid
            target_channel = options.ble_wifi_channel if channel is None else channel
            if not target_ssid:
                target_ssid = state.learned_ssid or ""
            if target_channel is None:
                target_channel = state.learned_channel
            target_ssid = target_ssid.strip()
            target_password = target_password.strip()
            target_bssid = target_bssid.strip() if target_bssid is not None else None
            target_channel = _normalize_wifi_channel(target_channel)
            used_shared_password = False

            if target_ssid and not target_password:
                shared_password = self._find_shared_wifi_password(sn, target_ssid)
                if shared_password:
                    target_password = shared_password
                    used_shared_password = True

            if not target_ssid or not target_password:
                state.last_result = "missing_credentials"
                state.last_stage = "missing_credentials"
                if not manual:
                    self._create_credentials_issue(sn, reason="missing_credentials")
                return False

            explicit_bssid = bssid is not None
            explicit_channel = channel is not None
            recovery_https_url = _recovery_https_url(self._client)
            recovery_mqtt_server = _recovery_mqtt_server(self._client)
            recovery_mqtt_info = getattr(self._client, "mqtt_info", None)
            provision_targets: list[tuple[str, str | None, int | None]] = []
            seen_targets: set[tuple[str | None, int | None]] = set()

            def add_provision_target(
                strategy: str,
                attempt_bssid: str | None,
                attempt_channel: int | None,
            ) -> None:
                normalized_bssid = attempt_bssid.strip() if attempt_bssid else None
                normalized_channel = _normalize_wifi_channel(attempt_channel)
                key = (normalized_bssid, normalized_channel)
                if key in seen_targets:
                    return
                seen_targets.add(key)
                provision_targets.append((strategy, normalized_bssid, normalized_channel))

            if explicit_bssid or explicit_channel:
                add_provision_target("explicit", target_bssid, target_channel)
                add_provision_target("ssid_only_fallback", None, None)
            else:
                if target_channel is not None:
                    add_provision_target("channel_only", None, target_channel)
                add_provision_target("ssid_only", None, None)
                if target_bssid or target_channel is not None:
                    add_provision_target("configured_pin_fallback", target_bssid, target_channel)

            recovered = False
            for strategy, attempt_bssid, attempt_channel in provision_targets:
                state.last_strategy = strategy
                state.last_stage = "discovery"
                discovery = self._find_device_discovery(sn)
                if discovery is None:
                    state.last_result = "device_not_seen"
                    state.last_stage = "device_not_seen"
                    return False

                _LOGGER.info(
                    "BLE recovery starting for %s via source=%s ssid=%s bssid=%s channel=%s manual=%s strategy=%s",
                    sn,
                    _discovery_source(discovery),
                    target_ssid,
                    attempt_bssid or "auto",
                    attempt_channel if attempt_channel is not None else "auto",
                    manual,
                    strategy,
                )
                provisioner = EcoflowBleProvisioner(
                    discovery.device,
                    sn,
                    user_id,
                    encrypt_type=_encrypt_type_from_advertisement(discovery.advertisement),
                    packet_version=_RIVER2_PACKET_VERSION,
                    timeout=max(10, options.ble_recovery_timeout_sec),
                )
                try:
                    dhodm_request_id = 10_000
                    state.last_stage = "connect"
                    await provisioner.connect()
                    _LOGGER.info("BLE recovery connected to %s strategy=%s", sn, strategy)
                    state.last_stage = "authenticate"
                    auth_status = await provisioner.authenticate()
                    state.last_auth_status = auth_status
                    _LOGGER.info(
                        "BLE recovery authenticated %s strategy=%s auth_status=%s",
                        sn,
                        strategy,
                        auth_status,
                    )
                    if auth_status.get("flow") == "key" and auth_status.get("key_auth_result") == "ok":
                        state.last_stage = "device_key_info"
                        try:
                            device_key_info = await provisioner.query_device_key_info()
                            state.last_device_key_info = device_key_info
                        except BleRecoveryError:
                            _LOGGER.warning(
                                "BLE device-key-info probe failed for %s strategy=%s",
                                sn,
                                strategy,
                                exc_info=True,
                            )
                    if recovery_https_url:
                        state.last_stage = "set_url"
                        try:
                            await provisioner.provision_device_url(https_url=recovery_https_url)
                            _LOGGER.info(
                                "BLE recovery URL preflight sent for %s strategy=%s https_url=%s",
                                sn,
                                strategy,
                                recovery_https_url,
                            )
                        except BleRecoveryError:
                            _LOGGER.debug(
                                "BLE recovery URL preflight failed for %s strategy=%s https_url=%s",
                                sn,
                                strategy,
                                recovery_https_url,
                                exc_info=True,
                            )
                    state.last_stage = "provision_cfg_net"
                    observed_network_status = await provisioner.provision_wifi_cfg_net(
                        ssid=target_ssid,
                        password=target_password,
                        https_url=recovery_https_url,
                    )
                    saw_cfg_net_status = any(key.startswith("0x35:") for key in observed_network_status)
                    if saw_cfg_net_status:
                        _LOGGER.info(
                            "BLE recovery cfg-net packet sent for %s strategy=%s observed_network_status=%s",
                            sn,
                            strategy,
                            observed_network_status,
                        )
                    else:
                        _LOGGER.info(
                            "BLE recovery cfg-net packet for %s strategy=%s produced no 0x35 wifi-state, falling back to legacy provisioning",
                            sn,
                            strategy,
                        )
                        state.last_stage = "provision"
                        observed_network_status = await provisioner.provision_wifi(
                            ssid=target_ssid,
                            password=target_password,
                            bssid=attempt_bssid,
                            channel=attempt_channel,
                            https_url=recovery_https_url,
                        )
                        _LOGGER.info("BLE recovery legacy provision packet sent for %s strategy=%s", sn, strategy)
                    if observed_network_status:
                        state.last_network_status = observed_network_status
                    if (
                        recovery_mqtt_info is not None
                        and recovery_mqtt_server
                        and recovery_mqtt_info.client_id
                        and recovery_mqtt_info.username
                        and recovery_mqtt_info.password
                    ):
                        state.last_stage = "set_mqtt"
                        restart_required = await provisioner.provision_mqtt_config(
                            request_id=dhodm_request_id,
                            server=recovery_mqtt_server,
                            client_id=recovery_mqtt_info.client_id,
                            username=recovery_mqtt_info.username,
                            password=recovery_mqtt_info.password,
                            topic_prefix=f"/shelly/thing/property/post/{sn}",
                            ssl_ca="ca.pem",
                        )
                        dhodm_request_id += 1
                        _LOGGER.info(
                            "BLE recovery MQTT config sent for %s strategy=%s restart_required=%s",
                            sn,
                            strategy,
                            restart_required,
                        )
                        state.last_stage = "set_rpc_udp"
                        restart_required = await provisioner.configure_rpc_udp(request_id=dhodm_request_id)
                        dhodm_request_id += 1
                        _LOGGER.info(
                            "BLE recovery Sys.SetConfig sent for %s strategy=%s restart_required=%s",
                            sn,
                            strategy,
                            restart_required,
                        )
                        state.last_stage = "set_ble"
                        restart_required = await provisioner.enable_ble_config(request_id=dhodm_request_id)
                        dhodm_request_id += 1
                        _LOGGER.info(
                            "BLE recovery BLE.SetConfig sent for %s strategy=%s restart_required=%s",
                            sn,
                            strategy,
                            restart_required,
                        )
                        state.last_stage = "reboot"
                        restart_required = await provisioner.reboot_device(request_id=dhodm_request_id)
                        dhodm_request_id += 1
                        _LOGGER.info(
                            "BLE recovery Shelly.Reboot sent for %s strategy=%s restart_required=%s",
                            sn,
                            strategy,
                            restart_required,
                        )
                        await asyncio.sleep(5)
                        state.last_stage = "probe_status"
                        await provisioner.request_wifi_status(request_id=dhodm_request_id)
                        dhodm_request_id += 1
                        await provisioner.request_mqtt_status(request_id=dhodm_request_id)
                        dhodm_request_id += 1
                        ap_follow_info_packets = await provisioner.query_ap_follow_info_list()
                        pd_wifi_info_packets = await provisioner.query_pd_wifi_info()
                        probed_network_status = await provisioner._observe_post_provision_packets(timeout=8)
                        pd_status_raw: bytes | None = None
                        pd_status_entry = probed_network_status.get("0x02")
                        if isinstance(pd_status_entry, dict):
                            pd_status_raw_hex = pd_status_entry.get("raw")
                            if isinstance(pd_status_raw_hex, str):
                                try:
                                    pd_status_raw = bytes.fromhex(pd_status_raw_hex)
                                except ValueError:
                                    pd_status_raw = None
                        if ap_follow_info_packets:
                            probed_network_status["_ap_follow_info"] = [
                                {
                                    "cmd_set": packet.cmd_set,
                                    "cmd_id": packet.cmd_id,
                                    "seq": packet.seq.hex(),
                                    "decoded": _decode_ap_follow_info_list(packet.payload),
                                    "raw": packet.payload.hex(),
                                }
                                for packet in ap_follow_info_packets
                            ]
                        if pd_wifi_info_packets:
                            probed_network_status["_pd_wifi_info"] = [
                                {
                                    "cmd_id": packet.cmd_id,
                                    "seq": packet.seq.hex(),
                                    "decoded_words": _decode_module_blob_words(packet.payload),
                                    "diff_vs_pd_status": (
                                        _diff_module_blob_words(packet.payload, pd_status_raw)
                                        if pd_status_raw is not None
                                        else None
                                    ),
                                    "raw": packet.payload.hex(),
                                }
                                for packet in pd_wifi_info_packets
                            ]
                        if probed_network_status:
                            state.last_network_status = probed_network_status
                        _LOGGER.warning(
                            "BLE recovery post-config status probe for %s strategy=%s network_status=%s",
                            sn,
                            strategy,
                            probed_network_status,
                        )
                        if (
                            not (state.last_device_key_info or {}).get("is_success")
                            and hasattr(self._client, "bound_device_encrypted")
                        ):
                            state.last_stage = "bind_cloud"
                            try:
                                bind_result = await self._client.bound_device_encrypted(
                                    sn,
                                    getattr(device.device_info, "name", None) or device.device_data.name or sn,
                                )
                                state.last_cloud_bind = {
                                    "path": "encrypted",
                                    "is_success": True,
                                    "response": bind_result.get("data", bind_result),
                                }
                                _LOGGER.warning(
                                    "BLE recovery encrypted cloud bind succeeded for %s strategy=%s bind_result=%s",
                                    sn,
                                    strategy,
                                    state.last_cloud_bind,
                                )
                            except Exception as err:
                                state.last_cloud_bind = {
                                    "path": "encrypted",
                                    "is_success": False,
                                    "error": str(err),
                                }
                                _LOGGER.warning(
                                    "BLE recovery encrypted cloud bind failed for %s strategy=%s",
                                    sn,
                                    strategy,
                                    exc_info=True,
                                )
                finally:
                    await provisioner.disconnect()

                state.last_stage = "wait_cloud"
                _LOGGER.info("BLE recovery waiting for cloud rejoin for %s strategy=%s", sn, strategy)
                recovered = await self._wait_for_cloud_recovery(sn, options.ble_recovery_timeout_sec)
                if recovered:
                    break

                state.last_error = f"device_did_not_rejoin_wifi:{strategy}"
                _LOGGER.warning(
                    "BLE recovery timed out for %s strategy=%s network_status=%s",
                    sn,
                    strategy,
                    state.last_network_status,
                )

            state.last_result = "success" if recovered else "timeout"
            if not recovered:
                if state.last_error is None:
                    state.last_error = "device_did_not_rejoin_wifi"
                state.last_stage = "timeout"
                if not manual:
                    self._create_credentials_issue(sn, reason="recovery_failed")
            else:
                state.last_stage = "success"
                if used_shared_password:
                    self._persist_wifi_credentials(sn, ssid=target_ssid, password=target_password)
                self._delete_credentials_issue(sn)
            return recovered
        except Exception as err:  # noqa: BLE001
            state.last_result = "failed"
            state.last_error = str(err)
            state.last_stage = "failed"
            if not manual:
                self._create_credentials_issue(sn, reason="recovery_failed")
            _LOGGER.warning("BLE Wi-Fi recovery failed for %s: %s", sn, err, exc_info=True)
            return False
        finally:
            state.in_progress = False
