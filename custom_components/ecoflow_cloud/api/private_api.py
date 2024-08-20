import base64
import logging
import uuid

import aiohttp

from . import EcoflowException, EcoflowApiClient
from .ecoflow_mqtt import EcoflowMQTTClient
from ..devices import EcoflowDeviceInfo, DiagnosticDevice

_LOGGER = logging.getLogger(__name__)

BASE_URI = "https://api.ecoflow.com"


class EcoflowPrivateApiClient(EcoflowApiClient):

    def __init__(self, ecoflow_username: str, ecoflow_password: str, installation_site: str):
        super().__init__()
        self.ecoflow_password = ecoflow_password
        self.ecoflow_username = ecoflow_username
        self.installation_site = installation_site
        self.user_id = None
        self.token = None
        self.user_name = None


    async def login(self):
        async with aiohttp.ClientSession() as session:
            url = f"{BASE_URI}/auth/login"
            headers = {"lang": "en_US", "content-type": "application/json"}
            data = {"email": self.ecoflow_username,
                    "password": base64.b64encode(self.ecoflow_password.encode()).decode(),
                    "scene": "IOT_APP",
                    "userType": "ECOFLOW"}

            _LOGGER.info(f"Login to EcoFlow API {url}")

            resp = await session.post(url, headers=headers, json=data)
            response = await self._get_json_response(resp)

            try:
                self.token = response["data"]["token"]
                self.user_id = response["data"]["user"]["userId"]
                self.user_name = response["data"]["user"].get("name", "<no user name>")
            except KeyError as key:
                raise EcoflowException(f"Failed to extract key {key} from response: {response}")

            _LOGGER.info(f"Successfully logged in: {self.user_name}")

            _LOGGER.info(f"Requesting IoT MQTT credentials")
            response = await self.__call_api("/iot-auth/app/certification")
            self._accept_mqqt_certification(response)

    async def fetch_all_available_devices(self):
        return []

    async def quota_all(self, device_sn: str):
        self.mqtt_client.send_get_message(device_sn, {"version": "1.1", "moduleType": 0, "operateType": "latestQuotas", "params": {}})

    def configure_device(self, device_sn: str, device_name: str, device_type: str):
        info = self.__create_device_info(device_sn, device_name, device_type)

        from ..devices.registry import devices
        if device_type in devices:
            self.add_device(devices[device_type](info))
        else:
            self.add_device(DiagnosticDevice(info))

        if self.mqtt_client:
            self.mqtt_client.reconnect()
        else:
            self.mqtt_info.client_id = f'HomeAssistant-{self.installation_site}'
            self.mqtt_client = EcoflowMQTTClient(self.mqtt_info, self.devices)

    def __create_device_info(self, device_sn: str, device_name: str, device_type: str) -> EcoflowDeviceInfo:
        return EcoflowDeviceInfo(
            public_api=False,
            sn=device_sn,
            name=device_name,
            device_type=device_type,
            data_topic=f"/app/device/property/{device_sn}",
            set_topic=f"/app/{self.user_id}/{device_sn}/thing/property/set",
            set_reply_topic=f"/app/{self.user_id}/{device_sn}/thing/property/set_reply",
            get_topic=f"/app/{self.user_id}/{device_sn}/thing/property/get",
            get_reply_topic=f"/app/{self.user_id}/{device_sn}/thing/property/get_reply",
            client_id= f'HomeAssistant-{self.installation_site}-{device_type}'
        )

    async def __call_api(self, endpoint: str, params: dict[str: any] | None = None) -> dict:
        async with aiohttp.ClientSession() as session:
            headers = {"lang": "en_US", "authorization": f"Bearer {self.token}", "content-type": "application/json"}
            user_data = {"userId": self.user_id}
            req_params = {}
            if params is not None:
                req_params.update(params)

            resp = await session.get(f"{BASE_URI}{endpoint}", data=user_data, params=req_params, headers=headers)
            _LOGGER.info(f"Request: {endpoint} {req_params}: got {resp}")
            return await self._get_json_response(resp)