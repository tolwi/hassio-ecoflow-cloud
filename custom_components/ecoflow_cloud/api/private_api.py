import base64
import hashlib
import logging
from time import time

import aiohttp
from homeassistant.util import uuid

from . import EcoflowException, EcoflowApiClient
from ..devices import EcoflowDeviceInfo, DiagnosticDevice

_LOGGER = logging.getLogger(__name__)

BASE_URI = "https://api.ecoflow.com"


class EcoflowPrivateApiClient(EcoflowApiClient):

    def __init__(self, ecoflow_username: str, ecoflow_password: str, group: str):
        super().__init__()
        self.ecoflow_password = ecoflow_password
        self.ecoflow_username = ecoflow_username
        self.group = group
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

            # Should be ANDROID_..str.._user_id !!!
            self.mqtt_info.client_id = f'ANDROID_{str(uuid.random_uuid_hex()).upper()}_{self.user_id}'


    # Failed to connect to MQTT: not authorised
    def gen_client_id(self):
        base = f'ANDROID_{str(uuid.random_uuid_hex()).upper()}_{self.user_id}'
        millis = int(time() * 1000)
        verify_info = "0000000000000000000000000000000000000000000000000000000000000000"
        pub = verify_info[:32]
        priv = verify_info[32:]
        k = priv + base + str(millis)
        res = base + "_" + pub + "_" + str(millis) + "_" + hashlib.md5(k.encode("utf-8")).hexdigest()
        return res

    async def fetch_all_available_devices(self):
        return []

    async def quota_all(self, device_sn: str | None):
        if not device_sn:
            target_devices = self.devices.keys()
        else:
            target_devices = [device_sn]

        for sn in target_devices:
            self.mqtt_client.send_get_message(sn, {"version": "1.1", "moduleType": 0, "operateType": "latestQuotas", "params": {}})

    def configure_device(self, device_sn: str, device_name: str, device_type: str, power_step: int = -1):
        info = self.__create_device_info(device_sn, device_name, device_type)

        from ..devices.registry import devices
        if device_type in devices:
            device = devices[device_type](info)
        else:
            device = DiagnosticDevice(info)

        device.power_step = power_step
        self.add_device(device)

        return device

    def __create_device_info(self, device_sn: str, device_name: str, device_type: str, status: int = -1) -> EcoflowDeviceInfo:
        return EcoflowDeviceInfo(
            public_api=False,
            sn=device_sn,
            name=device_name,
            device_type=device_type,
            status=status,
            data_topic=f"/app/device/property/{device_sn}",
            set_topic=f"/app/{self.user_id}/{device_sn}/thing/property/set",
            set_reply_topic=f"/app/{self.user_id}/{device_sn}/thing/property/set_reply",
            get_topic=f"/app/{self.user_id}/{device_sn}/thing/property/get",
            get_reply_topic=f"/app/{self.user_id}/{device_sn}/thing/property/get_reply"
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