import base64
import json
import logging
import random
import ssl
import time
from datetime import datetime
from typing import Any

import paho.mqtt.client as mqtt_client
import requests
from homeassistant import const
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, DOMAIN
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import utcnow
from reactivex import Subject, Observable

from .utils import LimitedSizeOrderedDict

_LOGGER = logging.getLogger(__name__)


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


class EcoflowCommandInfo():

    def __init__(self, target_state: dict[str, Any] | None, command: dict[str, Any]) -> None:
        self.target_state = target_state
        self.command = command
        self.reply: dict[str, Any] = {}
        self.time = utcnow().timestamp()


    def diagnostic_dict(self) -> dict[str, Any]:
        return {
            "target_state": self.target_state,
            "command": self.command,
            "reply": self.reply
        }


class EcoflowDataHolder:
    def __init__(self, collect_raw: bool = False):
        self.__collect_raw = collect_raw
        self.set_commands = LimitedSizeOrderedDict[int, EcoflowCommandInfo]()
        self.get_commands = LimitedSizeOrderedDict[int, EcoflowCommandInfo]()
        self.raw_data = list[dict[str, Any]]()
        self.params = dict[str, Any]()
        self.__broadcast_time: datetime = utcnow()
        self.__observable = Subject[dict[str, Any]]()

    def observable(self) -> Observable[dict[str, Any]]:
        return self.__observable

    def put_set_command(self, cmd_id: int, cmd: EcoflowCommandInfo) -> EcoflowCommandInfo:
        self.set_commands.append(cmd_id, cmd)
        return cmd

    def add_set_command(self, target_state: dict[str, Any] | None, cmd: dict[str, Any]) -> EcoflowCommandInfo:
        cmd_id = int(cmd["id"])
        if cmd_id not in self.set_commands:
            self.set_commands.append(cmd_id, EcoflowCommandInfo(target_state, cmd))
            if target_state is not None:
                self.__update_to_target_state(target_state)
        return self.set_commands[cmd_id]

    def add_set_command_reply(self, cmd: dict[str, Any]) -> EcoflowCommandInfo | None:
        cmd_id = int(cmd["id"])
        if cmd_id in self.set_commands:
            cmd_info = self.set_commands[cmd_id]
            cmd_info.reply = cmd
            return cmd_info

    def add_get_command(self, target_state: dict[str, Any] | None, cmd: dict[str, Any]):
        cmd_id = int(cmd["id"])
        if id not in self.get_commands:
            self.get_commands.append(cmd_id, EcoflowCommandInfo(target_state, cmd))

    def add_get_command_reply(self, cmd: dict[str, Any]):
        cmd_id = int(cmd["id"])
        if id in self.get_commands:
            self.get_commands[cmd_id].reply = cmd

    def __update_to_target_state(self, target_state: dict[str, Any]):
        self.params.update(target_state)
        self.__broadcast()

    def update_data(self, raw: dict[str, Any]):
        self.__add_raw_data(raw)
        self.params.update(raw['params'])

        if (utcnow() - self.__broadcast_time).total_seconds() > 5:
            self.__broadcast()

    def __broadcast(self):
        self.__broadcast_time = utcnow()
        self.__observable.on_next(self.params)

    def __trim_list(self, src: list, size: int):
        while len(src) >= size:
            src.pop(0)

    def __add_raw_data(self, raw: dict[str, Any]):
        if self.__collect_raw:
            self.__trim_list(self.raw_data, 20)
            self.raw_data.append(raw)


class EcoflowMQTTClient:

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, auth: EcoflowAuthentication):

        self.auth = auth

        self.device_type = entry.data[const.CONF_TYPE]
        self.device_sn = entry.data[const.CONF_DEVICE_ID]
        self._data_topic = f"/app/device/property/{self.device_sn}"
        self._set_topic = f"/app/{auth.user_id}/{self.device_sn}/thing/property/set"
        self._set_reply_topic = f"/app/{auth.user_id}/{self.device_sn}/thing/property/set_reply"
        self._get_topic = f"/app/{auth.user_id}/{self.device_sn}/thing/property/get"
        self._get_reply_topic = f"/app/{auth.user_id}/{self.device_sn}/thing/property/get_reply"
        self.data = EcoflowDataHolder(self.device_type == "DIAGNOSTIC")

        self.device_info_main = DeviceInfo(
            identifiers={(DOMAIN, self.device_sn)},
            manufacturer="EcoFlow",
            name=entry.title,
        )

        self.client = mqtt_client.Client(f'hassio-mqtt-{self.device_sn}-{entry.title.replace(" ", "-")}')
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
                self.client.subscribe([(self._data_topic, 0),
                                       (self._set_topic, 1), (self._set_reply_topic, 1),
                                       (self._get_topic, 1), (self._get_reply_topic, 1)])
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
            self.data.add_set_command(None, raw)
        elif message.topic == self._set_reply_topic:
            self.data.add_set_command_reply(raw)
        elif message.topic == self._get_topic:
            self.data.add_get_command(None, raw)
        elif message.topic == self._get_reply_topic:
            self.data.add_get_command_reply(raw)

    message_id = 999900000 + random.randint(10000, 99999)

    def resend_message(self, msg: EcoflowCommandInfo):
        self.message_id += 1
        payload = {}
        payload.update(msg.command)
        payload["id"] = f"{self.message_id}"

        self.data.put_set_command(self.message_id, msg)

        info = self.client.publish(self._set_topic, json.dumps(payload), 1)
        _LOGGER.debug("ReSending " + json.dumps(payload) + " :" + str(info) + "(" + str(info.is_published()) + ")")

    def send_message(self, mqtt_state: dict[str, Any], command: dict):
        self.message_id += 1
        payload = {"from": "HomeAssistant",
                   "id": f"{self.message_id}",
                   "version": "1.0"}
        payload.update(command)
        self.data.add_set_command(mqtt_state, payload)

        info = self.client.publish(self._set_topic, json.dumps(payload), 1)
        _LOGGER.debug("Sending " + json.dumps(payload) + " :" + str(info) + "(" + str(info.is_published()) + ")")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
