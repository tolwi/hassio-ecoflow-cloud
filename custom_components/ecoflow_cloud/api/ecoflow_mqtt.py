import json
import logging
import random
import ssl
import time
from typing import Any

import paho.mqtt.client as mqtt_client

from custom_components.ecoflow_cloud.api import EcoflowMqttInfo

_LOGGER = logging.getLogger(__name__)


class EcoflowMQTTClient:

    def __init__(self, mqtt_info: EcoflowMqttInfo, device):
        from ..devices import BaseDevice

        self.__mqtt_info = mqtt_info
        self.__device : BaseDevice = device
        self.__client = mqtt_client.Client(client_id=self.__mqtt_info.client_id, clean_session=True, reconnect_on_failure=True)
        self.__client.username_pw_set(self.__mqtt_info.username, self.__mqtt_info.password)
        self.__client.tls_set(certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED)
        self.__client.tls_insecure_set(False)
        self.__client.on_connect = self.on_connect
        self.__client.on_disconnect = self.on_disconnect
        self.__client.on_message = self.on_message

        _LOGGER.info(f"Connecting to MQTT Broker {self.__mqtt_info.url}:{self.__mqtt_info.port} with client id {self.__mqtt_info.client_id} and username {self.__mqtt_info.username}")
        self.__client.connect(self.__mqtt_info.url, self.__mqtt_info.port, 30)
        self.__client.loop_start()

    def is_connected(self):
        return self.__client.is_connected()

    def reconnect(self) -> bool:
        try:
            _LOGGER.info(f"Re-connecting to MQTT Broker {self.__mqtt_info.url}:{self.__mqtt_info.port}")
            self.__client.loop_stop(True)
            self.__client.reconnect()
            self.__client.loop_start()
            return True
        except Exception as e:
            _LOGGER.error(e)
            return False

    def on_connect(self, client, userdata, flags, rc):
        match rc:
            case 0:
                topics = []
                if self.__device.device_info.data_topic:
                    topics.append((self.__device.device_info.data_topic, 1))
                if self.__device.device_info.set_topic:
                    topics.append((self.__device.device_info.set_topic, 1))
                if self.__device.device_info.set_reply_topic:
                    topics.append((self.__device.device_info.set_reply_topic, 1))
                if self.__device.device_info.get_topic:
                    topics.append((self.__device.device_info.get_topic, 1))
                if self.__device.device_info.get_reply_topic:
                    topics.append((self.__device.device_info.get_reply_topic, 1))

                self.__client.subscribe(topics)
                _LOGGER.info(f"Subscribed to MQTT topics {topics}")
            case -1:
                _LOGGER.error(f"Failed to connect to MQTT: connection timed out ({self.__device})")
            case 1:
                _LOGGER.error(f"Failed to connect to MQTT: incorrect protocol version ({self.__device})")
            case 2:
                _LOGGER.error(f"Failed to connect to MQTT: invalid client identifier ({self.__device})")
            case 3:
                _LOGGER.error(f"Failed to connect to MQTT: server unavailable ({self.__device})")
            case 4:
                _LOGGER.error(f"Failed to connect to MQTT: bad username or password ({self.__device})")
            case 5:
                _LOGGER.error(f"Failed to connect to MQTT: not authorised ({self.__device}) - {userdata}")
            case _:
                _LOGGER.error(f"Failed to connect to MQTT: another error occured: {rc} ({self.__device})")

        return client


    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            _LOGGER.error(f"Unexpected MQTT disconnection: {rc}. Will auto-reconnect")
            time.sleep(5)
            # self.client.reconnect() ??

    def on_message(self, client, userdata, message):
        try:
            self.__device.update_data(message.payload, message.topic)
        except UnicodeDecodeError as error:
            _LOGGER.error(f"UnicodeDecodeError: {error}. Ignoring message and waiting for the next one.")

    message_id = 999900000 + random.randint(10000, 99999)

    def __prepare_payload(self, command: dict):
        self.message_id += 1
        payload = {"from": "HomeAssistant",
                   "id": f"{self.message_id}",
                   "version": "1.0"}
        payload.update(command)
        return payload

    def __send(self, topic: str, message: str):
        try:
            info = self.__client.publish(topic, message, 1)
            _LOGGER.debug("Sending " + message + " :" + str(info) + "(" + str(info.is_published()) + ")")
        except RuntimeError as error:
            _LOGGER.error(error)

    def send_get_message(self, command: dict):
        payload = self.__prepare_payload(command)
        self.__send(self.__device.device_info.get_topic, json.dumps(payload))

    def send_set_message(self, mqtt_state: dict[str, Any], command: dict):
        self.__device.data.update_to_target_state(mqtt_state)
        payload = self.__prepare_payload(command)
        self.__send(self.__device.device_info.set_topic, json.dumps(payload))

    def stop(self):
        self.__client.loop_stop()
        self.__client.disconnect()
