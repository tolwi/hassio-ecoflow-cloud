import asyncio
import base64
import hashlib
import json
import logging
import ssl
import threading
from time import time
from typing import Any

import aiohttp
from homeassistant.components.diagnostics import async_redact_data
from homeassistant.util import uuid

from ..devices import EcoflowDeviceInfo
from . import API_RESPONSE_TO_REDACT, EcoflowApiClient, EcoflowAuthException, EcoflowException
from .message import JSONMessage

_LOGGER = logging.getLogger(__name__)


class EcoflowPrivateApiClient(EcoflowApiClient):
    def __init__(self, api_domain: str, ecoflow_username: str, ecoflow_password: str, group: str):
        super().__init__()
        self.api_domain = api_domain
        self.ecoflow_password = ecoflow_password
        self.ecoflow_username = ecoflow_username
        self.group = group
        self.user_id = None
        self.token = None
        self.user_name = None

    async def login(self):
        async with aiohttp.ClientSession() as session:
            url = f"https://{self.api_domain}/auth/login"
            headers = {"lang": "en_US", "content-type": "application/json"}
            data = {
                "email": self.ecoflow_username,
                "password": base64.b64encode(self.ecoflow_password.encode()).decode(),
                "scene": "IOT_APP",
                "userType": "ECOFLOW",
            }

            _LOGGER.info(f"Login to EcoFlow API {url}")

            resp = await session.post(url, headers=headers, json=data)
            try:
                response = await self._get_json_response(resp)
            except EcoflowException as error:
                # an error code from /auth/login means the credentials were rejected;
                # transport and parse failures carry no code and stay retryable
                if error.code is None:
                    raise
                raise EcoflowAuthException(str(error), code=error.code) from error

            try:
                self.token = response["data"]["token"]
                self.user_id = response["data"]["user"]["userId"]
                self.user_name = response["data"]["user"].get("name", "<no user name>")
            except KeyError as key:
                _LOGGER.debug("Login response: %s", async_redact_data(response, API_RESPONSE_TO_REDACT))
                raise EcoflowException(f"Failed to extract key {key} from login response")

            _LOGGER.info(f"Successfully logged in: {self.user_name}")

            _LOGGER.info("Requesting IoT MQTT credentials")
            response = await self.__call_api("/iot-auth/app/certification")
            self._accept_mqqt_certification(response)

            # Should be ANDROID_..str.._user_id !!!
            self.mqtt_info.client_id = f"ANDROID_{str(uuid.random_uuid_hex()).upper()}_{self.user_id}"

    # Failed to connect to MQTT: not authorised
    def gen_client_id(self):
        base = f"ANDROID_{str(uuid.random_uuid_hex()).upper()}_{self.user_id}"
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
            target_devices = self.devices
        else:
            target_devices = {device_sn: self.devices[device_sn]}

        requested_topics: set[str | None] = set()
        for sn, device in target_devices.items():
            # settings the quotas do not carry (e.g. the names of a panel's circuits)
            for message in device.startup_set_messages():
                self.mqtt_client.publish(device.device_info.set_topic, JSONMessage(message).to_mqtt_payload())
            # sub devices (Power Kits modules) share their parent's topics: one latestQuotas serves them all
            if device.device_info.get_topic in requested_topics:
                continue
            requested_topics.add(device.device_info.get_topic)
            self.send_get_message(sn, device.get_quota_message())

    def _device_registry(self) -> dict[str, Any]:
        from ..devices.registry import devices
        return devices

    async def fetch_latest_quotas(self, device_sn: str, timeout: float = 15.0) -> dict[str, Any] | None:
        """Ask one device for its ``latestQuotas`` over a short-lived MQTT session.

        Returns the reply's ``data`` dict (``online``, ``quotaMap``, ...), or None when
        the device did not answer in time. Used by the config flow, which has no
        running MQTT client, to discover the modules of a Power Kit.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._fetch_latest_quotas_sync, device_sn, timeout)

    def _fetch_latest_quotas_sync(self, device_sn: str, timeout: float) -> dict[str, Any] | None:
        # everything blocking (DNS, TLS, the wait) stays on this executor thread
        import paho.mqtt.client as mqtt
        from paho.mqtt.enums import CallbackAPIVersion

        get_topic = f"/app/{self.user_id}/{device_sn}/thing/property/get"
        reply_topic = f"/app/{self.user_id}/{device_sn}/thing/property/get_reply"
        request = JSONMessage(
            {"version": "1.1", "moduleType": 0, "operateType": "latestQuotas", "params": {}}
        ).to_mqtt_payload()

        done = threading.Event()
        reply: dict[str, Any] = {}

        def on_connect(client, userdata, flags, reason_code, properties=None):
            if reason_code.is_failure:
                _LOGGER.warning("MQTT connect for module discovery of %s failed: %s", device_sn, reason_code)
                done.set()
                return
            client.subscribe(reply_topic, 1)

        def on_subscribe(client, userdata, mid, reason_codes, properties=None):
            client.publish(get_topic, request, 1)

        def on_message(client, userdata, message):
            try:
                data = json.loads(message.payload)
            except ValueError:
                return
            if (
                isinstance(data, dict)
                and data.get("operateType") == "latestQuotas"
                and isinstance(data.get("data"), dict)
            ):
                reply.update(data["data"])
                done.set()

        client = mqtt.Client(
            CallbackAPIVersion.VERSION2,
            client_id=f"ANDROID_{str(uuid.random_uuid_hex()).upper()}_{self.user_id}",
        )
        client.username_pw_set(self.mqtt_info.username, self.mqtt_info.password)
        client.tls_set_context(ssl.create_default_context())
        client.on_connect = on_connect
        client.on_subscribe = on_subscribe
        client.on_message = on_message

        _LOGGER.info("Requesting latestQuotas of %s for module discovery", device_sn)
        client.connect(self.mqtt_info.url, self.mqtt_info.port, keepalive=15)
        client.loop_start()
        try:
            if not done.wait(timeout):
                _LOGGER.warning("No latestQuotas reply from %s within %s s", device_sn, timeout)
                return None
            return reply or None
        finally:
            client.loop_stop()
            client.disconnect()

    def _create_device_info(
        self, device_sn: str, device_name: str, device_type: str, status: int = -1
    ) -> EcoflowDeviceInfo:
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
            get_reply_topic=f"/app/{self.user_id}/{device_sn}/thing/property/get_reply",
        )

    async def __call_api(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            headers = {
                "lang": "en_US",
                "authorization": f"Bearer {self.token}",
                "content-type": "application/json",
            }
            user_data = {"userId": self.user_id}
            req_params = {}
            if params is not None:
                req_params.update(params)

            resp = await session.get(
                f"https://{self.api_domain}{endpoint}",
                data=user_data,
                params=req_params,
                headers=headers,
            )
            _LOGGER.info(f"Request: {endpoint} {req_params}: got {resp}")
            return await self._get_json_response(resp)
