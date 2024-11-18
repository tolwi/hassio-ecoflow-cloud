import hashlib
import hmac
import logging
import random
import time
from datetime import datetime

import aiohttp
from homeassistant.util import dt

from . import EcoflowApiClient
from ..devices import DiagnosticDevice, EcoflowDeviceInfo

_LOGGER = logging.getLogger(__name__)

BASE_URI = "https://api-e.ecoflow.com/iot-open/sign"


# from FB
# client_id limits for MQTT connections
# If you are using MQTT to connect to the API be aware that only 10 unique client IDs are allowed per day.
# As such, it is suggested that you choose a static client_id for your application or integration to use consistently.
# If your code generates a unique client_id (as mine did) for each connection,
# you can exceed this limit very quickly when testing or debugging code.

class EcoflowPublicApiClient(EcoflowApiClient):

    def __init__(self, access_key: str, secret_key: str, group: str):
        super().__init__()
        self.access_key = access_key
        self.secret_key = secret_key
        self.group = group
        self.nonce = str(random.randint(10000, 1000000))
        self.timestamp = str(int(time.time() * 1000))

    async def login(self):
        _LOGGER.info(f"Requesting IoT MQTT credentials")
        response = await self.call_api("/certification")
        self._accept_mqqt_certification(response)
        self.mqtt_info.client_id = f"Hassio-{self.mqtt_info.username}-{self.group.replace(' ', '-')}"

    async def fetch_all_available_devices(self) -> list[EcoflowDeviceInfo]:
        _LOGGER.info(f"Requesting all devices")
        response = await self.call_api("/device/list")
        result = list()
        for device in response["data"]:
            sn = device["sn"]
            product_name = device["productName"]
            device_name = device.get("deviceName", f"{product_name}-{sn}")
            status = int(device["online"])
            result.append(self.__create_device_info(sn, device_name, product_name, status))

        return result

    def configure_device(self, device_sn: str, device_name: str, device_type: str, power_step = -1):
        info = self.__create_device_info(device_sn, device_name, device_type)

        from custom_components.ecoflow_cloud.devices.registry import device_by_product
        if device_type in device_by_product:
            device = device_by_product[device_type](info)
        else:
            device = DiagnosticDevice(info)

        device.power_step = power_step
        self.add_device(device)
        return device

    async def quota_all(self, device_sn: str | None):
        if not device_sn:
            target_devices = self.devices.keys()
            # update all statuses
            devices = await self.fetch_all_available_devices()
            for device in devices:
                if device.sn in self.devices:
                    self.devices[device.sn].data.update_status({"params": {"status" : device.status}})
        else:
            target_devices = [device_sn]

        for sn in target_devices:
            raw = await self.call_api("/device/quota/all", {"sn": sn})
            if "data" in raw:
                self.devices[sn].data.update_data({"params": raw["data"]})

    async def call_api(self, endpoint: str, params: dict[str, str] = None) -> dict:
        async with aiohttp.ClientSession() as session:
            params_str = ""
            if params is not None:
                params_str = self.__sort_and_concat_params(params)

            sign = self.__gen_sign(params_str)

            headers = {
                'accessKey': self.access_key,
                'nonce': self.nonce,
                'timestamp': self.timestamp,
                'sign': sign
            }

            resp = await session.get(f"{BASE_URI}{endpoint}?{params_str}", headers=headers)
            return await self._get_json_response(resp)

    def __create_device_info(self, device_sn: str, device_name: str, device_type: str, status: int = -1) -> EcoflowDeviceInfo:
        return EcoflowDeviceInfo(
            public_api=True,
            sn=device_sn,
            name=device_name,
            device_type=device_type,
            status=status,
            data_topic=f"/open/{self.mqtt_info.username}/{device_sn}/quota",
            set_topic=f"/open/{self.mqtt_info.username}/{device_sn}/set",
            set_reply_topic=f"/open/{self.mqtt_info.username}/{device_sn}/set_reply",
            get_topic=None,
            get_reply_topic=None,
            status_topic=f"/open/{self.mqtt_info.username}/{device_sn}/status"
        )

    def __gen_sign(self, query_params: str | None) -> str:
        target_str = f"accessKey={self.access_key}&nonce={self.nonce}&timestamp={self.timestamp}"
        if query_params:
            target_str = query_params + "&" + target_str

        return self.__encrypt_hmac_sha256(target_str, self.secret_key)

    def __sort_and_concat_params(self, params: dict[str, str]) -> str:
        # Sort the dictionary items by key
        sorted_items = sorted(params.items(), key=lambda x: x[0])

        # Create a list of "key=value" strings
        param_strings = [f"{key}={value}" for key, value in sorted_items]

        # Join the strings with '&'
        return "&".join(param_strings)

    def __encrypt_hmac_sha256(self, message: str, secret_key: str) -> str:
        # Convert the message and secret key to bytes
        message_bytes = message.encode('utf-8')
        secret_bytes = secret_key.encode('utf-8')

        # Create the HMAC
        hmac_obj = hmac.new(secret_bytes, message_bytes, hashlib.sha256)

        # Get the hexadecimal representation of the HMAC
        hmac_digest = hmac_obj.hexdigest()

        return hmac_digest
