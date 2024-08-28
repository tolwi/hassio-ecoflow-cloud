import json
import logging
import random
import ssl
import time
from typing import Any

from custom_components.ecoflow_cloud.api import EcoflowMqttInfo
from custom_components.ecoflow_cloud.devices import BaseDevice
import paho.mqtt.client as mqtt_client

_LOGGER = logging.getLogger(__name__)


class EcoflowMQTTClient:

    def __init__(self, mqtt_info: EcoflowMqttInfo, devices: dict[str, BaseDevice]):

        from ..devices import BaseDevice

        self.connected = False
        self.__mqtt_info = mqtt_info
        self.__devices: dict[str, BaseDevice] = devices
        self.__client: mqtt_client.Client = mqtt_client.Client(client_id=self.__mqtt_info.client_id, reconnect_on_failure=True)
        self.__client.username_pw_set(self.__mqtt_info.username, self.__mqtt_info.password)
        self.__client.tls_set(certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED)
        self.__client.tls_insecure_set(False)
        self.__client.on_connect = self.on_connect
        self.__client.on_disconnect = self.on_disconnect
        self.__client.on_message = self.on_message
        # self.__client.on_socket_close = self.on_socket_close

        _LOGGER.info(
            f"Connecting to MQTT Broker {self.__mqtt_info.url}:{self.__mqtt_info.port} with client id {self.__mqtt_info.client_id} and username {self.__mqtt_info.username}")
        self.__client.connect_async(self.__mqtt_info.url, self.__mqtt_info.port)
        self.__client.loop_start()

    def is_connected(self):
        return self.connected

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
        if rc == 0:
            self.connected = True
            for (sn, device) in self.__devices.items():
                _LOGGER.debug(f"Add Topics for  {sn}")
                for topic in device.device_info.topics():
                    self.__client.subscribe(topic, 1)
                    _LOGGER.info(f"Subscribed to MQTT topics {topic}")
        else:
            self.__log_with_reason("connect", client, userdata, rc)

    #
    # def on_socket_close(self, client, userdata, socket):
    #     _LOGGER.error(f"Unexpected MQTT Socket disconnection : {str(socket)}")

    def on_disconnect(self, client, userdata, rc):
        if not self.connected:
            # from homeassistant/components/mqtt/client.py
            # This function is re-entrant and may be called multiple times
            # when there is a broken pipe error.
            return
        self.connected = False
        if rc != 0:
            self.__log_with_reason("disconnect", client, userdata, rc)
            time.sleep(15)

    def on_message(self, client, userdata, message):
        try:
            for (sn, device) in self.__devices.items():
                if device.update_data(message.payload, message.topic):
                    _LOGGER.debug(f"Message for {sn} and Topic {message.topic}")
        except UnicodeDecodeError as error:
            _LOGGER.error(f"UnicodeDecodeError: {error}. Ignoring message and waiting for the next one.")

    def __log_with_reason(self, action: str, client, userdata, rc):
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

    def send_get_message(self, device_sn: str, command: dict):
        payload = self.__prepare_payload(command)
        self.__send(self.__devices[device_sn].device_info.get_topic, json.dumps(payload))

    def send_set_message(self, device_sn: str, mqtt_state: dict[str, Any], command: dict):
        self.__devices[device_sn].data.update_to_target_state(mqtt_state)
        payload = self.__prepare_payload(command)
        self.__send(self.__devices[device_sn].device_info.set_topic, json.dumps(payload))

    def stop(self):
        self.__client.loop_stop()
        self.__client.disconnect()
