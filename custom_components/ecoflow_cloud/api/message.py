import json
import random
from abc import ABC, abstractmethod
from typing import override

from paho.mqtt.client import PayloadType


class Message(ABC):
    @abstractmethod
    def to_mqtt_payload(self) -> PayloadType:
        raise NotImplementedError()


JSONType = None | bool | int | float | str | list["JSONType"] | dict[str, "JSONType"]
JSONDict = dict[str, JSONType]


class JSONMessage(Message):
    def __init__(self, data: JSONDict) -> None:
        super().__init__()
        self.data = data

    @staticmethod
    def gen_seq() -> int:
        return 999900000 + random.randint(10000, 99999)

    @staticmethod
    def prepare_payload(command: JSONDict) -> JSONDict:
        payload: JSONDict = {
            "from": "HomeAssistant",
            "id": str(JSONMessage.gen_seq()),
            "version": "1.0",
        }
        payload.update(command)
        return payload

    @override
    def to_mqtt_payload(self) -> PayloadType:
        return json.dumps(JSONMessage.prepare_payload(self.data))
