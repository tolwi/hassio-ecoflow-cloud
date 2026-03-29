from __future__ import annotations

import asyncio
import hashlib
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
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak, async_discovered_service_info
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
_SUPPORTED_DEVICE_TYPES = {
    "RIVER_2",
    "RIVER_2_MAX",
    "RIVER_2_PRO",
    "RIVER 2",
    "RIVER 2 Max",
    "RIVER 2 Pro",
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

_WIFI_SSID_KEYS = {
    "modulewifissid",
    "wifissid",
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
        data = self.PREFIX + struct.pack("<B", self._frame_type << 4) + b"\x01"
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


def _build_network_message_payload(
    *,
    ssid: str,
    password: str,
    bssid: bytes | None,
    channel: int | None = None,
) -> bytes:
    message_cls = _network_message_class()
    message = message_cls()
    message.router_ssid = ssid
    message.router_pwd = password
    message.mesh_id = b""
    message.https_url = ""
    message.mesh_enable = 0
    if bssid is not None:
        message.router_bssid = bssid
    if channel is not None and channel >= 0:
        message.router_channel = channel
    return message.SerializeToString()


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


@dataclass(slots=True)
class BleRecoveryState:
    in_progress: bool = False
    attempt_count: int = 0
    last_attempt: Any = None
    last_result: str | None = None
    last_error: str | None = None
    learned_ssid: str | None = None


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

    async def _send_simple_request(self, payload: bytes, *, timeout: float = 10) -> bytes:
        await self._ensure_notify()
        self._drain_notifications()
        await self._write(SimplePacketAssembler.encode(payload), response=True)
        return await self._await_simple_payload(timeout)

    async def _send_packet_request(
        self,
        packet: Packet,
        *,
        timeout: float = 10,
        predicate: Callable[[Packet], bool] | None = None,
    ) -> list[Packet]:
        if self._session_encryption is None:
            raise BleRecoveryError("session_not_initialized")
        await self._ensure_notify()
        self._drain_notifications()
        assembler = RawHeaderAssembler(self._session_encryption) if self._encrypt_type == 1 else EncPacketAssembler(
            self._session_encryption
        )
        payload = await assembler.encode(packet)
        await self._write(payload, response=assembler.write_with_response)
        return await self._await_packets(timeout, predicate=predicate)

    async def _send_packet_no_reply(self, packet: Packet) -> None:
        if self._session_encryption is None:
            raise BleRecoveryError("session_not_initialized")
        await self._ensure_notify()
        self._drain_notifications()
        assembler = RawHeaderAssembler(self._session_encryption) if self._encrypt_type == 1 else EncPacketAssembler(
            self._session_encryption
        )
        payload = await assembler.encode(packet)
        await self._write(payload, response=assembler.write_with_response)

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

    async def authenticate(self) -> None:
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
        await self._send_packet_request(auth_status_packet, timeout=10)

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

    async def provision_wifi(
        self,
        *,
        ssid: str,
        password: str,
        bssid: str | None = None,
    ) -> None:
        payload = _build_network_message_payload(
            ssid=ssid,
            password=password,
            bssid=_parse_bssid(bssid),
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
            }
        return {
            ATTR_BLE_RECOVERY_ACTIVE: state.in_progress,
            ATTR_BLE_RECOVERY_ATTEMPTS: state.attempt_count,
            ATTR_BLE_RECOVERY_LAST_ATTEMPT: state.last_attempt,
            ATTR_BLE_RECOVERY_LAST_RESULT: state.last_result,
            ATTR_BLE_RECOVERY_LAST_ERROR: state.last_error,
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

    def _find_device_discovery(self, sn: str) -> BluetoothServiceInfoBleak | None:
        for discovery in async_discovered_service_info(self._hass):
            if _serial_from_advertisement(discovery.advertisement) == sn:
                return discovery
        return None

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

        try:
            if not supports_ble_wifi_recovery_device_type(device.device_data.device_type):
                state.last_result = "unsupported_device"
                return False

            user_id = str(getattr(self._client, "user_id", "")).strip()
            if not user_id:
                state.last_result = "unsupported_auth_type"
                return False

            if not manual and not options.ble_wifi_recovery_enabled:
                state.last_result = "disabled"
                return False

            discovery = self._find_device_discovery(sn)
            if discovery is None:
                state.last_result = "device_not_seen"
                return False

            target_ssid = options.ble_wifi_ssid if ssid is None else ssid
            target_password = options.ble_wifi_password if password is None else password
            target_bssid = options.ble_wifi_bssid if bssid is None else bssid
            if not target_ssid:
                target_ssid = state.learned_ssid or ""
            target_ssid = target_ssid.strip()
            target_password = target_password.strip()
            target_bssid = target_bssid.strip() if target_bssid is not None else None
            used_shared_password = False

            if target_ssid and not target_password:
                shared_password = self._find_shared_wifi_password(sn, target_ssid)
                if shared_password:
                    target_password = shared_password
                    used_shared_password = True

            if not target_ssid or not target_password:
                state.last_result = "missing_credentials"
                if not manual:
                    self._create_credentials_issue(sn, reason="missing_credentials")
                return False

            provisioner = EcoflowBleProvisioner(
                discovery.device,
                sn,
                user_id,
                encrypt_type=_encrypt_type_from_advertisement(discovery.advertisement),
                packet_version=_RIVER2_PACKET_VERSION,
                timeout=max(10, options.ble_recovery_timeout_sec),
            )
            try:
                await provisioner.connect()
                await provisioner.authenticate()
                await provisioner.provision_wifi(
                    ssid=target_ssid,
                    password=target_password,
                    bssid=target_bssid or None,
                )
            finally:
                await provisioner.disconnect()

            recovered = await self._wait_for_cloud_recovery(sn, options.ble_recovery_timeout_sec)
            state.last_result = "success" if recovered else "timeout"
            if not recovered:
                state.last_error = "device_did_not_rejoin_wifi"
                if not manual:
                    self._create_credentials_issue(sn, reason="recovery_failed")
            else:
                if used_shared_password:
                    self._persist_wifi_credentials(sn, ssid=target_ssid, password=target_password)
                self._delete_credentials_issue(sn)
            return recovered
        except Exception as err:  # noqa: BLE001
            state.last_result = "failed"
            state.last_error = str(err)
            if not manual:
                self._create_credentials_issue(sn, reason="recovery_failed")
            _LOGGER.warning("BLE Wi-Fi recovery failed for %s: %s", sn, err, exc_info=True)
            return False
        finally:
            state.in_progress = False
