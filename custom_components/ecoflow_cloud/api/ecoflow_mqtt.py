import json
import logging
import random
import ssl
import time
from _socket import SocketType
from typing import Any

from homeassistant.core import callback

from custom_components.ecoflow_cloud.api import EcoflowMqttInfo
from custom_components.ecoflow_cloud.devices import BaseDevice

_LOGGER = logging.getLogger(__name__)


class EcoflowMQTTClient:

    def __init__(self, mqtt_info: EcoflowMqttInfo, devices: dict[str, BaseDevice]):

        from ..devices import BaseDevice
        self.connected = False
        self.__mqtt_info = mqtt_info
        self.__devices: dict[str, BaseDevice] = devices

        from homeassistant.components.mqtt.async_client import AsyncMQTTClient
        self.__client: AsyncMQTTClient = AsyncMQTTClient(
                                                         client_id=self.__mqtt_info.client_id,
                                                         reconnect_on_failure=True,
                                                         clean_session=True)

        # self.__client._connect_timeout = 15.0
        self.__client.setup()
        self.__client.username_pw_set(self.__mqtt_info.username, self.__mqtt_info.password)
        self.__client.tls_set(certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED)
        self.__client.tls_insecure_set(False)
        self.__client.on_connect = self._on_connect
        self.__client.on_disconnect = self._on_disconnect
        self.__client.on_message = self._on_message
        self.__client.on_socket_close = self._on_socket_close

        _LOGGER.info(
            f"Connecting to MQTT Broker {self.__mqtt_info.url}:{self.__mqtt_info.port} with client id {self.__mqtt_info.client_id} and username {self.__mqtt_info.username}")
        self.__client.connect(self.__mqtt_info.url, self.__mqtt_info.port, keepalive=15)
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

    @callback
    def _on_socket_close(self, client, userdata: Any, sock: SocketType) -> None:
        _LOGGER.error(f"Unexpected MQTT Socket disconnection : {str(sock)}")

    @callback
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            target_topics = [(topic, 1) for topic in self.__target_topics()]
            self.__client.subscribe(target_topics)
            _LOGGER.info(f"Subscribed to MQTT topics {target_topics}")
        else:
            self.__log_with_reason("connect", client, userdata, rc)

    @callback
    def _on_disconnect(self, client, userdata, rc):
        if not self.connected:
            # from homeassistant/components/mqtt/client.py
            # This function is re-entrant and may be called multiple times
            # when there is a broken pipe error.
            return
        self.connected = False
        if rc != 0:
            self.__log_with_reason("disconnect", client, userdata, rc)
            time.sleep(5)

    @callback
    def _on_message(self, client, userdata, message):
        try:
            for (sn, device) in self.__devices.items():
                if device.update_data(message.payload, message.topic):
                    _LOGGER.debug(f"Message for {sn} and Topic {message.topic}")
        except UnicodeDecodeError as error:
            _LOGGER.error(f"UnicodeDecodeError: {error}. Ignoring message and waiting for the next one.")

    def send_get_message(self, device_sn: str, command: dict):
        payload = self.__prepare_payload(command)
        self.__send(self.__devices[device_sn].device_info.get_topic, json.dumps(payload))

    def send_set_message(self, device_sn: str, mqtt_state: dict[str, Any], command: dict):
        self.__devices[device_sn].data.update_to_target_state(mqtt_state)
        payload = self.__prepare_payload(command)
        self.__send(self.__devices[device_sn].device_info.set_topic, json.dumps(payload))

    def stop(self):
        self.__client.unsubscribe(self.__target_topics())
        self.__client.loop_stop()
        self.__client.disconnect()

    def __log_with_reason(self, action: str, client, userdata, rc):
        import paho.mqtt.client as mqtt_client
        _LOGGER.error(f"MQTT {action}: {mqtt_client.error_string(rc)} ({self.__mqtt_info.client_id}) - {userdata}")

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
            _LOGGER.error(error, "Error on topic " + topic + " and message " + message)
        except Exception as error:
            _LOGGER.debug(error, "Error on topic " + topic + " and message " + message)

    def __target_topics(self) -> list[str]:
        topics = []
        for (sn, device) in self.__devices.items():
            for topic in device.device_info.topics():
                topics.append(topic)
        return topics
