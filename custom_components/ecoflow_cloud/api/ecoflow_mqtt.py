from __future__ import annotations

import logging
import ssl
from typing import Any, Callable

from homeassistant.core import callback
from paho.mqtt.client import Client, ConnectFlags, DisconnectFlags, MQTTMessage, PayloadType
from paho.mqtt.enums import CallbackAPIVersion
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode

from ..devices import BaseDevice
from . import EcoflowMqttInfo

_LOGGER = logging.getLogger(__name__)

# MQTT v3.1.1 CONNACK code 5 / v5 reason code names that indicate auth failure
_AUTH_FAILURE_NAMES = {"Not authorized", "Bad user name or password", "Banned"}


class EcoflowMQTTClient:
    def __init__(
        self,
        mqtt_info: EcoflowMqttInfo,
        devices: dict[str, BaseDevice],
        auth_failure_callback: Callable[[], None] | None = None,
        connect_success_callback: Callable[[], None] | None = None,
    ):
        self.connected = False
        self.__mqtt_info = mqtt_info
        self.__devices: dict[str, BaseDevice] = devices
        self.__auth_failure_callback = auth_failure_callback
        self.__connect_success_callback = connect_success_callback
        self.__auth_failure_notified = False

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
        # Be polite to the EcoFlow broker: don't hammer reconnects.
        # Defaults are min=1s, max=120s; we use 30s -> 300s to avoid tripping
        # any per-account connection rate limits on transient drops.
        self.__client.reconnect_delay_set(min_delay=30, max_delay=300)
        self.__client.on_connect = self._on_connect
        self.__client.on_disconnect = self._on_disconnect
        self.__client.on_message = self._on_message
        self.__client.on_socket_close = self._on_socket_close

        _LOGGER.info(
            f"Connecting to MQTT Broker {self.__mqtt_info.url}:{self.__mqtt_info.port} with client id {self.__mqtt_info.client_id} and username {self.__mqtt_info.username}"
        )
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
    def _on_connect(
        self, client: Client, userdata: Any, flags: ConnectFlags, rc: ReasonCode, properties: Properties | None = None
    ):
        if rc == 0:
            self.connected = True
            self.__auth_failure_notified = False
            target_topics = [(topic, 1) for topic in self.__target_topics()]
            self.__client.subscribe(target_topics)
            _LOGGER.info(f"Subscribed to MQTT topics {target_topics}")
            if self.__connect_success_callback is not None:
                try:
                    self.__connect_success_callback()
                except Exception:  # noqa: BLE001
                    _LOGGER.exception("Connect success callback raised")
        else:
            self.__log_with_reason("connect", client, userdata, rc)
            if rc.getName() in _AUTH_FAILURE_NAMES:
                self.__handle_auth_failure()

    @callback
    def _on_disconnect(
        self,
        client: Client,
        userdata: Any,
        disconnect_flags: DisconnectFlags,
        reason_code: ReasonCode,
        properties: Properties | None,
    ) -> None:
        if not self.connected:
            # from homeassistant/components/mqtt/client.py
            # This function is re-entrant and may be called multiple times
            # when there is a broken pipe error.
            return
        self.connected = False
        if reason_code.is_failure:
            self.__log_with_reason("disconnect", client, userdata, reason_code)

    @callback
    def _on_message(self, client, userdata, message: MQTTMessage):
        try:
            for sn, device in self.__devices.items():
                if device.update_data(message.payload, message.topic):
                    _LOGGER.debug(f"Message for {sn} and Topic {message.topic} : {message.payload.hex()}")
        except UnicodeDecodeError as error:
            _LOGGER.error(f"UnicodeDecodeError: {error}. Ignoring message and waiting for the next one.")
        except Exception:
            _LOGGER.error("Unexpected error processing MQTT message on topic %s", message.topic, exc_info=True)

    def stop(self):
        self.__client.unsubscribe(self.__target_topics())
        self.__client.loop_stop()
        self.__client.disconnect()

    def __handle_auth_failure(self) -> None:
        # MQTT broker rejected our credentials. The token from /certification is
        # short-lived; ask the API client to refresh it. Stop paho's reconnect loop
        # so it doesn't keep hammering with stale creds.
        if self.__auth_failure_notified:
            return
        self.__auth_failure_notified = True
        _LOGGER.warning(
            "MQTT credentials rejected for %s; pausing reconnect loop and requesting refresh",
            self.__mqtt_info.client_id,
        )
        try:
            self.__client.loop_stop()
        except Exception:  # noqa: BLE001
            pass
        if self.__auth_failure_callback is not None:
            try:
                self.__auth_failure_callback()
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Auth failure callback raised")

    def update_credentials(self, mqtt_info: EcoflowMqttInfo) -> None:
        self.__mqtt_info = mqtt_info
        self.__client.username_pw_set(mqtt_info.username, mqtt_info.password)
        self.__auth_failure_notified = False

    def __log_with_reason(self, action: str, client, userdata, reason_code: ReasonCode):
        _LOGGER.error(f"MQTT {action}: {reason_code.getName()} ({self.__mqtt_info.client_id}) - {userdata}")

    def publish(self, topic: str, message: PayloadType) -> None:
        try:
            info = self.__client.publish(topic, message, 1)
            _LOGGER.debug("Sending " + str(message) + " :" + str(info) + "(" + str(info.is_published()) + ")")
        except RuntimeError as error:
            _LOGGER.error("Error on topic %s and message %s: %s", topic, message, error)
        except Exception as error:
            _LOGGER.debug("Error on topic %s and message %s: %s", topic, message, error)

    def __target_topics(self) -> list[str]:
        topics = []
        for device in self.__devices.values():
            for topic in device.device_info.topics():
                topics.append(topic)
        # Remove duplicates that can occur when multiple devices have the same topic (for example sub devices)
        return list(set(topics))
