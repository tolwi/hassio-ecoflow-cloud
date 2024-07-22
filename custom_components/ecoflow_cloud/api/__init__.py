import logging
from abc import abstractmethod

from aiohttp import ClientResponse
from attr import dataclass

_LOGGER = logging.getLogger(__name__)


class EcoflowException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

@dataclass
class EcoflowMqttInfo:
    url: str
    port: int
    username: str
    password: str
    client_id: str


class EcoflowApiClient:

    def __init__(self):
        self.mqtt_info: EcoflowMqttInfo | None = None
        self.device = None
        self.mqtt_client = None

    @abstractmethod
    async def login(self):
        pass

    @abstractmethod
    async def quota_all(self):
        pass

    @abstractmethod
    def configure_device(self, device_sn: str, device_name: str, device_type: str):
        pass

    def _accept_mqqt_certification(self, resp_json: dict, mqtt_client_id: str):
        _LOGGER.info(f"Received MQTT credentials: {resp_json}")
        try:
            mqtt_url = resp_json["data"]["url"]
            mqtt_port = int(resp_json["data"]["port"])
            mqtt_username = resp_json["data"]["certificateAccount"]
            mqtt_password = resp_json["data"]["certificatePassword"]
            self.mqtt_info = EcoflowMqttInfo(mqtt_url, mqtt_port, mqtt_username, mqtt_password, mqtt_client_id)
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
            raise EcoflowException(f"Failed to parse response: {resp.text} Error: {error}")

        if response_message.lower() != "success":
            raise EcoflowException(f"{response_message}")

        return json_resp

    def stop(self):
        self.mqtt_client.stop()
