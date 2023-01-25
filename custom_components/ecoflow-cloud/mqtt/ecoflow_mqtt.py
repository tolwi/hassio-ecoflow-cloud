import base64
import json
import logging
import random
import ssl
import time
from datetime import datetime, timedelta
from queue import Queue
from typing import Any

import paho.mqtt.client as mqtt_client
import requests
from homeassistant import const
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, DOMAIN
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import utcnow
from reactivex import Subject, Observable
from reactivex.subject import ReplaySubject

_LOGGER = logging.getLogger(__name__)
DISCONNECT_TIME = timedelta(seconds=5)

module_by_prefix = {
    "pd": "1",
    "bms_emsStatus": "2",
    "bms_bmsStatus": "2",
    "inv": "3",
    "mppt": "5"
}

class EcoflowException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)


class EcoflowAuthentication:
    def __init__(self, ecoflow_username, ecoflow_password):
        self.ecoflow_username = ecoflow_username
        self.ecoflow_password = ecoflow_password
        self.user_id = None
        self.token = None
        self.mqtt_url = "mqtt.mqtt.com"
        self.mqtt_port = 8883
        self.mqtt_username = None
        self.mqtt_password = None

    def authorize(self):
        url = "https://api.ecoflow.com/auth/login"
        headers = {"lang": "en_US", "content-type": "application/json"}
        data = {"email": self.ecoflow_username,
                "password": base64.b64encode(self.ecoflow_password.encode()).decode(),
                "scene": "IOT_APP",
                "userType": "ECOFLOW"}

        _LOGGER.info(f"Login to EcoFlow API {url}")
        request = requests.post(url, json=data, headers=headers)
        response = self.get_json_response(request)

        try:
            self.token = response["data"]["token"]
            self.user_id = response["data"]["user"]["userId"]
            user_name = response["data"]["user"]["name"]
        except KeyError as key:
            raise EcoflowException(f"Failed to extract key {key} from response: {response}")

        _LOGGER.info(f"Successfully logged in: {user_name}")

        url = "https://api.ecoflow.com/iot-auth/app/certification"
        headers = {"lang": "en_US", "authorization": f"Bearer {self.token}"}
        data = {"userId": self.user_id}

        _LOGGER.info(f"Requesting IoT MQTT credentials {url}")
        request = requests.get(url, data=data, headers=headers)
        response = self.get_json_response(request)

        try:
            self.mqtt_url = response["data"]["url"]
            self.mqtt_port = int(response["data"]["port"])
            self.mqtt_username = response["data"]["certificateAccount"]
            self.mqtt_password = response["data"]["certificatePassword"]
        except KeyError as key:
            raise EcoflowException(f"Failed to extract key {key} from {response}")

        _LOGGER.info(f"Successfully extracted account: {self.mqtt_username}")

    def get_json_response(self, request):
        if request.status_code != 200:
            raise EcoflowException(f"Got HTTP status code {request.status_code}: {request.text}")

        try:
            response = json.loads(request.text)
            response_message = response["message"]
        except KeyError as key:
            raise EcoflowException(f"Failed to extract key {key} from {response}")
        except Exception as error:
            raise EcoflowException(f"Failed to parse response: {request.text} Error: {error}")

        if response_message.lower() != "success":
            raise EcoflowException(f"{response_message}")

        return response


class EcoflowDataHolder:

    def __init__(self):
        self.commands = list[dict[str, Any]]()
        self.raw_data = list[dict[str, Any]]()
        self.data = dict[str, dict[str, Any]]()
        self.broadcast_time = dict[str, datetime]()
        self.subjects = dict[str, Subject[dict[str, Any]]]()

        for i in range(1, 6):
            self.data[str(i)] = dict[str, Any]()
            self.broadcast_time[str(i)] = utcnow()
            self.subjects[str(i)] = ReplaySubject[dict[str, Any]](window=DISCONNECT_TIME)

    def topic(self, module_type: str) -> Observable[dict[str, Any]]:
        return self.subjects[module_type]

    def add_command(self, cmd: dict[str, Any]):
        while len(self.commands) >= 20:
            self.commands.pop(0)

        self.commands.append(cmd)

    def update_data(self, raw: dict[str, Any]):
        self.__add_raw_data(raw)

        module_type: str = raw.get('moduleType', "NONE")
        params: dict[str, Any] = raw['params']

        if module_type not in self.data:
            self.data[module_type] = dict[str, Any]()

        self.data[module_type].update(params)

        if module_type in self.broadcast_time:
            if (utcnow() - self.broadcast_time[module_type]).total_seconds() > 5:
                self.broadcast_time[module_type] = utcnow()
                self.subjects[module_type].on_next(self.data[module_type])
                _LOGGER.debug("Broadcast on %s: $s", (module_type, str(self.data[module_type])))

    def __add_raw_data(self, raw: dict[str, Any]):
        while len(self.raw_data) >= 20:
            self.raw_data.pop(0)
        self.raw_data.append(raw)


class EcoflowMQTTClient:

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, auth: EcoflowAuthentication):

        self.data = EcoflowDataHolder()
        self.auth = auth

        self.device_type = entry.data[const.CONF_TYPE]
        self.device_sn = entry.data[const.CONF_DEVICE_ID]
        self._data_topic = f"/app/device/property/{self.device_sn}"
        self._set_topic = f"/app/{auth.user_id}/{self.device_sn}/thing/property/set"

        self.device_info_main = DeviceInfo(
            identifiers={(DOMAIN, self.device_sn)},
            manufacturer="EcoFlow",
            name=entry.title,
        )

        self.client = mqtt_client.Client(f'hassio-mqtt-{self.device_sn}-{entry.title.replace(" ","-")}')
        self.client.username_pw_set(self.auth.mqtt_username, self.auth.mqtt_password)
        self.client.tls_set(certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED)
        self.client.tls_insecure_set(False)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        _LOGGER.info(f"Connecting to MQTT Broker {self.auth.mqtt_url}:{self.auth.mqtt_port}")
        self.client.connect(self.auth.mqtt_url, self.auth.mqtt_port)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        match rc:
            case 0:
                self.client.subscribe([(self._data_topic, 0), (self._set_topic, 0)])
                _LOGGER.info(f"Subscribed to MQTT topic {self._data_topic}")
            case -1:
                _LOGGER.error("Failed to connect to MQTT: connection timed out")
            case 1:
                _LOGGER.error("Failed to connect to MQTT: incorrect protocol version")
            case 2:
                _LOGGER.error("Failed to connect to MQTT: invalid client identifier")
            case 3:
                _LOGGER.error("Failed to connect to MQTT: server unavailable")
            case 4:
                _LOGGER.error("Failed to connect to MQTT: bad username or password")
            case 5:
                _LOGGER.error("Failed to connect to MQTT: not authorised")
            case _:
                _LOGGER.error(f"Failed to connect to MQTT: another error occured: {rc}")

        return client

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            _LOGGER.error(f"Unexpected MQTT disconnection: {rc}. Will auto-reconnect")
            time.sleep(5)

    def on_message(self, client, userdata, message):
        payload = message.payload.decode("utf-8")
        raw = json.loads(payload)

        if message.topic == self._data_topic:
            self.data.update_data(raw)
        elif message.topic == self._set_topic:
            self.data.add_command(raw)

    def send_message(self, command: dict):
        message_id = 999900000 + random.randint(10000, 99999)
        payload = {"from": "HomeAssistant",
                   "id": f"{message_id}",
                   "version": "1.0"}
        payload.update(command)
        self.client.publish(self._set_topic, json.dumps(payload))

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
