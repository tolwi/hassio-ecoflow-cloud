from __future__ import annotations

import logging
import ssl
import time
from typing import TYPE_CHECKING, Any

from homeassistant.core import callback
from paho.mqtt.client import Client, ConnectFlags, DisconnectFlags, MQTTMessage, PayloadType
from paho.mqtt.enums import CallbackAPIVersion
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode

from ..devices import BaseDevice
from . import EcoflowMqttInfo

_LOGGER = logging.getLogger(__name__)


class EcoflowMQTTClient:
    def __init__(self, mqtt_info: EcoflowMqttInfo, devices: dict[str, BaseDevice]):
        self.connected = False
        self.__mqtt_info = mqtt_info
        self.__devices: dict[str, BaseDevice] = devices

        from homeassistant.components.mqtt.async_client import AsyncMQTTClient

        self.__client: AsyncMQTTClient = AsyncMQTTClient(
            client_id=self.__mqtt_info.client_id,
            reconnect_on_failure=True,
            clean_session=True,
            callback_api_version=CallbackAPIVersion.VERSION2,
        )

        # self.__client._connect_timeout = 15.0
        self.__client.setup()
        self.__client.username_pw_set(self.__mqtt_info.username, self.__mqtt_info.password)
        self.__client.tls_set(certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED)
        self.__client.tls_insecure_set(False)
        self.__client.on_connect = self._on_connect
        self.__client.on_disconnect = self._on_disconnect
        self.__client.on_message = self._on_message
        self.__client.on_socket_close = self._on_socket_close

        _LOGGER.info(f"Connecting to MQTT Broker {self.__mqtt_info.url}:{self.__mqtt_info.port} with client id {self.__mqtt_info.client_id} and username {self.__mqtt_info.username}")
        self.__client.connect(self.__mqtt_info.url, self.__mqtt_info.port, keepalive=15)
        self.__client.loop_start()

    def is_connected(self):
        return self.__client.is_connected()

    def reconnect(self) -> bool:
        try:
            _LOGGER.info(f"Re-connecting to MQTT Broker {self.__mqtt_info.url}:{self.__mqtt_info.port}")
            self.__client.loop_stop()
            self.__client.reconnect()
            self.__client.loop_start()
            return True
        except Exception as e:
            _LOGGER.error(e)
            return False

    @callback
    def _on_socket_close(self, client: Client, userdata: Any, sock: Any) -> None:
        _LOGGER.info(f"MQTT Socket disconnection : {str(sock)}")

    @callback
    def _on_connect(self, client: Client, userdata: Any, flags: ConnectFlags, rc: ReasonCode, properties: Properties | None = None):
        if rc == 0:
            self.connected = True
            target_topics = [(topic, 1) for topic in self.__target_topics()]
            self.__client.subscribe(target_topics)
            _LOGGER.info(f"Subscribed to MQTT topics {target_topics}")
        else:
            self.__log_with_reason("connect", client, userdata, rc)

    @callback
    def _on_disconnect(
        self,
        client: Client,
        userdata: Any,
        disconnect_flags_or_rc: None | DisconnectFlags | int | ReasonCode = None,
        reason_code: ReasonCode | None = None,
        properties: Properties | None = None,
    ) -> None:
        if not self.connected:
            # from homeassistant/components/mqtt/client.py
            # This function is re-entrant and may be called multiple times
            # when there is a broken pipe error.
            return
        self.connected = False

        # Handle both paho-mqtt v1 (3 args) and v2 (5 args) callback styles
        if reason_code is None:
            # v1 style: disconnect_flags_or_rc is actually the return code
            rc = disconnect_flags_or_rc
            if rc is not None and rc != 0:
                _LOGGER.error(f"MQTT disconnect: rc={rc} ({self.__mqtt_info.client_id}) - {userdata}")
        else:
            # v2 style: we have DisconnectFlags and ReasonCode
            if reason_code.is_failure:
                self.__log_with_reason("disconnect", client, userdata, reason_code)

    @callback
    def _on_message(self, client, userdata, message: MQTTMessage):
        try:
            for sn, device in self.__devices.items():
                try:
                    if device.update_data(message.payload, message.topic):
                        _LOGGER.debug(
                            "Message for %s and Topic %s : %s",
                            sn,
                            message.topic,
                            message.payload.hex(),
                        )
                except UnicodeDecodeError as error:
                    _LOGGER.error(
                        "UnicodeDecodeError for device %s topic %s: %s. Ignoring message.",
                        sn,
                        message.topic,
                        error,
                    )
                except Exception:
                    # Any uncaught exception here risks killing the MQTT loop thread and
                    # silently stopping all subsequent updates.
                    _LOGGER.exception(
                        "Unhandled exception processing MQTT message for device %s topic %s",
                        sn,
                        message.topic,
                    )
        except Exception:
            _LOGGER.exception("Unhandled exception in MQTT on_message callback")

    def stop(self):
        self.__client.unsubscribe(self.__target_topics())
        self.__client.loop_stop()
        self.__client.disconnect()

    def __log_with_reason(self, action: str, client, userdata, reason_code: ReasonCode):
        _LOGGER.error(f"MQTT {action}: {reason_code.getName()} ({self.__mqtt_info.client_id}) - {userdata}")

    def publish(self, topic: str, message: PayloadType) -> None:
        try:
            info = self.__client.publish(topic, message, 1)
            _LOGGER.debug("Sending " + str(message) + " :" + str(info) + "(" + str(info.is_published()) + ")")
        except RuntimeError as error:
            _LOGGER.error(error, "Error on topic " + topic + " and message " + str(message))
        except Exception as error:
            _LOGGER.debug(error, "Error on topic " + topic + " and message " + str(message))

    def __target_topics(self) -> list[str]:
        topics = []
        for device in self.__devices.values():
            for topic in device.device_info.topics():
                topics.append(topic)
        # Remove duplicates that can occur when multiple devices have the same topic (for example sub devices)
        return list(set(topics))
