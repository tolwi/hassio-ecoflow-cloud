import base64
import json
import logging
import random
import ssl
import time
import uuid
from datetime import datetime
from typing import Any

import paho.mqtt.client as mqtt_client
import requests
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, DOMAIN
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import utcnow
from reactivex import Subject, Observable

from .proto import powerstream_pb2 as powerstream, ecopacket_pb2 as ecopacket
from .utils import BoundFifoList
from ..config.const import (
    CONF_DEVICE_TYPE,
    CONF_DEVICE_ID,
    OPTS_REFRESH_PERIOD_SEC,
    EcoflowModel,
)

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
        data = {
            "email": self.ecoflow_username,
            "password": base64.b64encode(self.ecoflow_password.encode()).decode(),
            "scene": "IOT_APP",
            "userType": "ECOFLOW",
        }

        _LOGGER.info(f"Login to EcoFlow API {url}")
        request = requests.post(url, json=data, headers=headers)
        response = self.get_json_response(request)

        try:
            self.token = response["data"]["token"]
            self.user_id = response["data"]["user"]["userId"]
            user_name = response["data"]["user"].get("name", "<no user name>")
        except KeyError as key:
            raise EcoflowException(
                f"Failed to extract key {key} from response: {response}"
            )

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
            raise EcoflowException(
                f"Got HTTP status code {request.status_code}: {request.text}"
            )

        try:
            response = json.loads(request.text)
            response_message = response["message"]
        except KeyError as key:
            raise EcoflowException(f"Failed to extract key {key} from {response}")
        except Exception as error:
            raise EcoflowException(
                f"Failed to parse response: {request.text} Error: {error}"
            )

        if response_message.lower() != "success":
            raise EcoflowException(f"{response_message}")

        return response


class EcoflowDataHolder:
    def __init__(self, update_period_sec: int, collect_raw: bool = False):
        self.__update_period_sec = update_period_sec
        self.__collect_raw = collect_raw
        self.set = BoundFifoList[dict[str, Any]]()
        self.set_reply = BoundFifoList[dict[str, Any]]()
        self.get = BoundFifoList[dict[str, Any]]()
        self.get_reply = BoundFifoList[dict[str, Any]]()
        self.params = dict[str, Any]()

        self.raw_data = BoundFifoList[dict[str, Any]]()

        self.__params_time = utcnow().replace(
            year=2000, month=1, day=1, hour=0, minute=0, second=0
        )
        self.__params_broadcast_time = utcnow().replace(
            year=2000, month=1, day=1, hour=0, minute=0, second=0
        )
        self.__params_observable = Subject[dict[str, Any]]()

        self.__set_reply_observable = Subject[list[dict[str, Any]]]()
        self.__get_reply_observable = Subject[list[dict[str, Any]]]()

    def params_observable(self) -> Observable[dict[str, Any]]:
        return self.__params_observable

    def get_reply_observable(self) -> Observable[list[dict[str, Any]]]:
        return self.__get_reply_observable

    def set_reply_observable(self) -> Observable[list[dict[str, Any]]]:
        return self.__set_reply_observable

    def add_set_message(self, msg: dict[str, Any]):
        self.set.append(msg)

    def add_set_reply_message(self, msg: dict[str, Any]):
        self.set_reply.append(msg)
        self.__set_reply_observable.on_next(self.set_reply)

    def add_get_message(self, msg: dict[str, Any]):
        self.get.append(msg)

    def add_get_reply_message(self, msg: dict[str, Any]):
        self.get_reply.append(msg)
        self.__get_reply_observable.on_next(self.get_reply)

    def update_to_target_state(self, target_state: dict[str, Any]):
        self.params.update(target_state)
        self.__broadcast()

    def update_data(self, raw: dict[str, Any]):
        self.__add_raw_data(raw)
        # self.__params_time = datetime.fromtimestamp(raw['timestamp'], UTC)
        self.__params_time = utcnow()
        self.params["timestamp"] = raw["timestamp"]
        self.params.update(raw["params"])

        if (
            utcnow() - self.__params_broadcast_time
        ).total_seconds() > self.__update_period_sec:
            self.__broadcast()

    def __broadcast(self):
        self.__params_broadcast_time = utcnow()
        self.__params_observable.on_next(self.params)

    def __add_raw_data(self, raw: dict[str, Any]):
        if self.__collect_raw:
            self.raw_data.append(raw)

    def params_time(self) -> datetime:
        return self.__params_time


class EcoflowMQTTClient:
    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, auth: EcoflowAuthentication
    ):
        self.auth = auth
        self.config_entry = entry
        self.device_type = entry.data[CONF_DEVICE_TYPE]
        self.device_sn = entry.data[CONF_DEVICE_ID]

        self._data_topic = f"/app/device/property/{self.device_sn}"
        self._set_topic = f"/app/{auth.user_id}/{self.device_sn}/thing/property/set"
        self._set_reply_topic = (
            f"/app/{auth.user_id}/{self.device_sn}/thing/property/set_reply"
        )
        self._get_topic = f"/app/{auth.user_id}/{self.device_sn}/thing/property/get"
        self._get_reply_topic = (
            f"/app/{auth.user_id}/{self.device_sn}/thing/property/get_reply"
        )

        self.data = EcoflowDataHolder(
            entry.options.get(OPTS_REFRESH_PERIOD_SEC), self.device_type == "DIAGNOSTIC"
        )

        self.device_info_main = DeviceInfo(
            identifiers={(DOMAIN, self.device_sn)},
            manufacturer="EcoFlow",
            name=entry.title,
            model=self.device_type,
        )

        self.client = mqtt_client.Client(
            client_id=f"ANDROID_-{str(uuid.uuid4()).upper()}_{auth.user_id}",
            clean_session=True,
            reconnect_on_failure=True,
        )
        self.client.username_pw_set(self.auth.mqtt_username, self.auth.mqtt_password)
        self.client.tls_set(certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED)
        self.client.tls_insecure_set(False)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        if self.device_type == EcoflowModel.POWERSTREAM.name:
            self.client.on_message = self.on_bytes_message
        else:
            self.client.on_message = self.on_json_message

        _LOGGER.info(
            f"Connecting to MQTT Broker {self.auth.mqtt_url}:{self.auth.mqtt_port}"
        )
        self.client.connect(self.auth.mqtt_url, self.auth.mqtt_port, 30)
        self.client.loop_start()

    def is_connected(self):
        return self.client.is_connected()

    def reconnect(self) -> bool:
        try:
            _LOGGER.info(
                f"Re-connecting to MQTT Broker {self.auth.mqtt_url}:{self.auth.mqtt_port}"
            )
            self.client.loop_stop(True)
            self.client.reconnect()
            self.client.loop_start()
            return True
        except Exception as e:
            _LOGGER.error(e)
            return False

    def on_connect(self, client, userdata, flags, rc):
        match rc:
            case 0:
                self.client.subscribe(
                    [
                        (self._data_topic, 1),
                        (self._set_topic, 1),
                        (self._set_reply_topic, 1),
                        (self._get_topic, 1),
                        (self._get_reply_topic, 1),
                    ]
                )
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
            # self.client.reconnect() ??

    def on_json_message(self, client, userdata, message):
        try:
            payload = message.payload.decode("utf-8", errors="ignore")
            try:
                raw = json.loads(payload)
            except:
                # Sometimes there will be messages that are not json formatted.
                # That happens for example when the ecoflow app connects to the
                # mqtt topic.
                return

            if message.topic == self._data_topic:
                self.data.update_data(raw)
            elif message.topic == self._set_topic:
                self.data.add_set_message(raw)
            elif message.topic == self._set_reply_topic:
                self.data.add_set_reply_message(raw)
            elif message.topic == self._get_topic:
                self.data.add_get_message(raw)
            elif message.topic == self._get_reply_topic:
                self.data.add_get_reply_message(raw)
        except UnicodeDecodeError as error:
            _LOGGER.error(
                f"UnicodeDecodeError: {error}. Ignoring message and waiting for the next one."
            )

    def on_bytes_message(self, client, userdata, message):
        try:
            payload = message.payload

            while True:
                packet = ecopacket.SendHeaderMsg()
                packet.ParseFromString(payload)

                _LOGGER.debug(
                    'cmd id %u payload "%s"', packet.msg.cmd_id, payload.hex()
                )

                if packet.msg.cmd_id != 1:
                    _LOGGER.info("Unsupported EcoPacket cmd id %u", packet.msg.cmd_id)

                else:
                    heartbeat = powerstream.InverterHeartbeat()
                    heartbeat.ParseFromString(packet.msg.pdata)

                    raw = {"params": {}}

                    for descriptor in heartbeat.DESCRIPTOR.fields:
                        if not heartbeat.HasField(descriptor.name):
                            continue

                        raw["params"][descriptor.name] = getattr(
                            heartbeat, descriptor.name
                        )

                    _LOGGER.info("Found %u fields", len(raw["params"]))

                    raw["timestamp"] = utcnow()

                    self.data.update_data(raw)

                if packet.ByteSize() >= len(payload):
                    break

                _LOGGER.info("Found another frame in payload")

                packetLength = len(payload) - packet.ByteSize()
                payload = payload[:packetLength]

        except Exception as error:
            _LOGGER.error(error)
            _LOGGER.info(message.payload.hex())

    message_id = 999900000 + random.randint(10000, 99999)

    def __prepare_payload(self, command: dict):
        self.message_id += 1
        payload = {
            "from": "HomeAssistant",
            "id": f"{self.message_id}",
            "version": "1.0",
        }
        payload.update(command)
        return payload

    def __send(self, topic: str, message: str):
        try:
            info = self.client.publish(topic, message, 1)
            _LOGGER.debug(
                "Sending "
                + message
                + " :"
                + str(info)
                + "("
                + str(info.is_published())
                + ")"
            )
        except RuntimeError as error:
            _LOGGER.error(error)

    def send_get_message(self, command: dict):
        payload = self.__prepare_payload(command)
        self.__send(self._get_topic, json.dumps(payload))

    def send_set_message(self, mqtt_state: dict[str, Any], command: dict):
        self.data.update_to_target_state(mqtt_state)
        payload = self.__prepare_payload(command)
        self.__send(self._set_topic, json.dumps(payload))

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
