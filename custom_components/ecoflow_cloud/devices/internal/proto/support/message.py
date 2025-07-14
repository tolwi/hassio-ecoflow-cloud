import json
import logging
from typing import override

from google.protobuf.message import Message as ProtoMessageRaw
from paho.mqtt.client import PayloadType

from .....api import JSONMessage, JSONType, Message
from .....api.private_api import PrivateAPIMessageProtocol
from .const import AddressId, Command, DirectionId, get_expected_payload_type

_LOGGER = logging.getLogger(__name__)


class ProtoMessage(PrivateAPIMessageProtocol, Message):
    def __init__(
        self,
        *,
        command: Command | None = None,
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

    def _verify_command_and_payload(self) -> None:
        if (
            self.command is not None
            and self.payload is not None
            and not isinstance(self.payload, get_expected_payload_type(self.command))
        ):
            _LOGGER.warning(
                'Command "%s": allowed payload types %s, got %s',
                self.command.name,
                get_expected_payload_type(self.command),
                type(self.payload),
            )

    def to_proto_message(self) -> ProtoMessageRaw:
        from .. import ecopacket_pb2 as ecopacket

        packet = ecopacket.SendHeaderMsg()
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

        if self.need_ack:
            message.need_ack = self.need_ack

        message.seq = JSONMessage.gen_seq()

        return packet

    def to_json_message(self) -> JSONType:
        from google.protobuf.json_format import MessageToDict

        packet = JSONMessage.prepare_payload({})

        if self.device_sn is not None:
            packet["sn"] = self.device_sn

        if self.command is not None:
            packet["cmdCode"] = self.command.name

        if self.payload is not None:
            packet["params"] = MessageToDict(
                self.payload, preserving_proto_field_name=False
            )

        return packet

    @override
    def private_api_to_mqtt_payload(self) -> PayloadType:
        self._verify_command_and_payload()
        return self.to_proto_message().SerializeToString()

    @override
    def to_mqtt_payload(self) -> PayloadType:
        self._verify_command_and_payload()
        return json.dumps(self.to_json_message())
