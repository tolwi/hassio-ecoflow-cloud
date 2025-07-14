import json
import logging
import random
from abc import ABC, abstractmethod
from typing import Any, override

from aiohttp import ClientResponse
from attr import dataclass
from paho.mqtt.client import PayloadType

from .. import DeviceData

_LOGGER = logging.getLogger(__name__)


class EcoflowException(Exception):
    pass


@dataclass
class EcoflowMqttInfo:
    url: str
    port: int
    username: str
    password: str
    client_id: str | None = None


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


class EcoflowApiClient(ABC):
    def __init__(self):
        self.mqtt_info: EcoflowMqttInfo
        self.devices: dict[str, Any] = {}
        self.mqtt_client = None

    @abstractmethod
    async def login(self):
        pass

    @abstractmethod
    async def fetch_all_available_devices(self):
        pass

    @abstractmethod
    async def quota_all(self, device_sn: str | None):
        pass

    @abstractmethod
    def configure_device(self, device_data: DeviceData):
        pass

    def add_device(self, device):
        self.devices[device.device_data.sn] = device

    def remove_device(self, device):
        self.devices.pop(device.device_data.sn, None)

    def _accept_mqqt_certification(self, resp_json: dict):
        _LOGGER.info(f"Received MQTT credentials: {resp_json}")
        try:
            mqtt_url = resp_json["data"]["url"]
            mqtt_port = int(resp_json["data"]["port"])
            mqtt_username = resp_json["data"]["certificateAccount"]
            mqtt_password = resp_json["data"]["certificatePassword"]
            self.mqtt_info = EcoflowMqttInfo(
                mqtt_url, mqtt_port, mqtt_username, mqtt_password
            )
        except KeyError as key:
            raise EcoflowException(f"Failed to extract key {key} from {resp_json}")

        _LOGGER.info(f"Successfully extracted account: {self.mqtt_info.username}")

    async def _get_json_response(self, resp: ClientResponse):
        if resp.status != 200:
            raise EcoflowException(f"Got HTTP status code {resp.status}: {resp.reason}")

        try:
            json_resp = await resp.json()
            response_message = json_resp["message"]
        except KeyError as key:
            raise EcoflowException(f"Failed to extract key {key} from {resp}")
        except Exception as error:
            raise EcoflowException(
                f"Failed to parse response: {resp.text} Error: {error}"
            )

        if response_message.lower() != "success":
            raise EcoflowException(f"{response_message}")

        return json_resp

    def send_get_message(self, device_sn: str, command: dict | Message):
        if isinstance(command, dict):
            command = JSONMessage(command)

        self.mqtt_client.publish(
            self.devices[device_sn].device_info.get_topic, command.to_mqtt_payload()
        )

    def send_set_message(
        self, device_sn: str, mqtt_state: dict[str, Any], command: dict | Message
    ):
        if isinstance(command, dict):
            command = JSONMessage(command)

        self.devices[device_sn].data.update_to_target_state(mqtt_state)
        self.mqtt_client.publish(
            self.devices[device_sn].device_info.set_topic, command.to_mqtt_payload()
        )

    def start(self):
        from custom_components.ecoflow_cloud.api.ecoflow_mqtt import EcoflowMQTTClient

        self.mqtt_client = EcoflowMQTTClient(self.mqtt_info, self.devices)

    def stop(self):
        assert self.mqtt_client is not None
        self.mqtt_client.stop()
