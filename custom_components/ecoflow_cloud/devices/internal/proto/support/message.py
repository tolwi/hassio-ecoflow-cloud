import json
import logging
from typing import Protocol, override

from google.protobuf.message import Message as ProtoMessageRaw
from paho.mqtt.client import PayloadType

from .....api.message import JSONMessage, JSONType, Message
from .....api.private_api import PrivateAPIMessageProtocol

import enum


# https://github.com/tomvd/local-powerstream/issues/4#issuecomment-2781354316
class AddressId(enum.Enum):
    IOT = 1
    IOT2 = 2
    APP = 32
    MQTT = 53


class DirectionId(enum.Enum):
    DEFAULT = 1


_LOGGER = logging.getLogger(__name__)


class ProtoCommand(Protocol):
    """Protocol for command objects with func, id, and name properties."""

    @property
    def func(self) -> int: ...
    @property
    def id(self) -> int: ...
    @property
    def name(self) -> str: ...


class ProtoMessage(PrivateAPIMessageProtocol, Message):
    def __init__(
        self,
        *,
        create_packet: type[ProtoMessageRaw],
        command: ProtoCommand | None = None,
        payload: ProtoMessageRaw | None = None,
        src: AddressId | None = None,
        dest: AddressId | None = None,
        need_ack: bool | None = True,
        dir_src: DirectionId | None = None,
        dir_dest: DirectionId | None = None,
        from_: str | None = None,
        device_sn: str | None = None,
    ) -> None:
        super().__init__()
        self.command = command
        self.payload = payload
        self.src = src
        self.dest = dest
        self.dir_src = dir_src
        self.dir_dest = dir_dest
        self.need_ack = need_ack
        self.from_ = from_
        self.device_sn = device_sn
        self.create_packet = create_packet

    def to_proto_message(self) -> ProtoMessageRaw:
        """Convert to protobuf message using device-specific header types."""
        packet = self.create_packet()
        message = packet.msg.add()

        if self.command is not None:
            message.cmd_func = self.command.func
            message.cmd_id = self.command.id

        if self.payload is not None:
            payload_serialized = self.payload.SerializeToString()
            message.pdata = payload_serialized
            message.data_len = len(payload_serialized)

        if self.src is not None:
            message.src = self.src.value
        if self.dest is not None:
            message.dest = self.dest.value
        if self.device_sn is not None:
            message.device_sn = self.device_sn
        if self.need_ack is not None:
            message.need_ack = self.need_ack

        message.seq = JSONMessage.gen_seq()

        return packet

    def to_json_message(self) -> JSONType:
        from google.protobuf.json_format import MessageToDict

        packet = JSONMessage.prepare_payload({})

        if self.device_sn is not None:
            packet["sn"] = self.device_sn

        if self.command is not None:
            if hasattr(self.command, "name"):
                packet["cmdCode"] = self.command.name
            else:
                packet["cmdCode"] = str(self.command)

        if self.payload is not None:
            packet["params"] = MessageToDict(
                self.payload, preserving_proto_field_name=False
            )

        return packet

    @override
    def private_api_to_mqtt_payload(self) -> PayloadType:
        return self.to_proto_message().SerializeToString()

    @override
    def to_mqtt_payload(self) -> PayloadType:
        return json.dumps(self.to_json_message())
