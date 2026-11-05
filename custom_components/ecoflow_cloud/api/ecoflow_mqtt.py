from __future__ import annotations

import logging
import ssl
import threading
from collections.abc import Callable
from typing import Any

from homeassistant.core import callback
from paho.mqtt.client import Client, ConnectFlags, DisconnectFlags, MQTTMessage, PayloadType
from paho.mqtt.enums import CallbackAPIVersion
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode

from ..devices import BaseDevice
from . import EcoflowMqttInfo

_LOGGER = logging.getLogger(__name__)

# paho maps the v3.1.1 CONNACK codes 4 and 5 onto these names; "Banned" is MQTT 5 only
AUTH_FAILURE_REASONS = frozenset({"Bad user name or password", "Not authorized", "Banned"})


class EcoflowMQTTClient:
    def __init__(self, mqtt_info: EcoflowMqttInfo, devices: dict[str, BaseDevice]):
        self.connected = False
        self.auth_failed = False
        self.on_auth_failure: Callable[[], None] | None = None
        self.__mqtt_info = mqtt_info
        self.__devices: dict[str, BaseDevice] = devices
        self.__bootstrap_lock = threading.RLock()
        self.__bootstrap_timers: list[threading.Timer] = []
        self.__bootstrap_generation = 0
        self.__subscription_mid: int | None = None
        self.__stopped = False

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
        self.__client.on_subscribe = self._on_subscribe
        self.__client.on_socket_close = self._on_socket_close

        _LOGGER.info(
            f"Connecting to MQTT Broker {self.__mqtt_info.url}:{self.__mqtt_info.port} with client id {self.__mqtt_info.client_id} and username {self.__mqtt_info.username}"
        )
        try:
            self.__client.connect(self.__mqtt_info.url, self.__mqtt_info.port, keepalive=15)
            self.__client.loop_start()
        except TimeoutError:
            _LOGGER.exception("Initial EcoFlow MQTT connection timed out; entities will retry reconnect from status updates")

    def is_connected(self):
        return self.__client.is_connected()

    def reconnect(self) -> bool:
        self.__cancel_bootstrap()
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
            with self.__bootstrap_lock:
                if self.__stopped:
                    return
                self.__cancel_bootstrap()
                self.connected = True
                self.auth_failed = False
                target_topics = [(topic, 1) for topic in self.__target_topics()]
                result, mid = self.__client.subscribe(target_topics)
                if result == 0:
                    self.__subscription_mid = mid
            _LOGGER.info(f"Subscribed to MQTT topics {target_topics}")
        elif rc.getName() in AUTH_FAILURE_REASONS:
            self.__handle_auth_failure(client, userdata, rc)
        else:
            self.__log_with_reason("connect", client, userdata, rc)

    @callback
    def _on_disconnect(
        self,
        client: Client,
        userdata: Any,
        disconnect_flags: DisconnectFlags,
        reason_code: ReasonCode,
        properties: Properties | None,
    ) -> None:
        self.__cancel_bootstrap()
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
        with self.__bootstrap_lock:
            self.__stopped = True
            self.__cancel_bootstrap()
        self.__client.unsubscribe(self.__target_topics())
        self.__client.loop_stop()
        self.__client.disconnect()

    def __cancel_bootstrap(self) -> None:
        with self.__bootstrap_lock:
            self.__bootstrap_generation += 1
            self.__subscription_mid = None
            for timer in self.__bootstrap_timers:
                timer.cancel()
            self.__bootstrap_timers.clear()

    @callback
    def _on_subscribe(
        self, client: Client, userdata: Any, mid: int, reason_codes: list[ReasonCode], properties: Properties | None = None
    ) -> None:
        from ..devices.internal.powerstream import PowerStream

        with self.__bootstrap_lock:
            if self.__stopped or mid != self.__subscription_mid:
                return
            self.__subscription_mid = None
            if not reason_codes or any(reason.is_failure for reason in reason_codes):
                return
            generation = self.__bootstrap_generation
            for device in self.__devices.values():
                if not isinstance(device, PowerStream) or "20_1.supplyPriority" in device.data.params:
                    continue
                for delay in (2, 10, 30):
                    timer = threading.Timer(delay, self.__bootstrap_powerstream, args=(device, generation))
                    timer.daemon = True
                    self.__bootstrap_timers.append(timer)
                    timer.start()

    def __bootstrap_powerstream(self, device: BaseDevice, generation: int) -> None:
        with self.__bootstrap_lock:
            if self.__stopped or generation != self.__bootstrap_generation or not self.is_connected():
                return
            if "20_1.supplyPriority" in device.data.params:
                return
            # Read only: never publish to a set topic or populate a target-state cache.
            self.publish(device.device_info.get_topic, device.get_quota_message().to_mqtt_payload())
            _LOGGER.debug("Requested missing PowerStream mode after MQTT subscription confirmation")

    def __handle_auth_failure(self, client, userdata, reason_code: ReasonCode) -> None:
        if self.auth_failed:
            return
        self.auth_failed = True
        # paho would otherwise retry the rejected credentials forever
        self.__client.loop_stop()
        self.__log_with_reason("connect", client, userdata, reason_code)
        if self.on_auth_failure is not None:
            self.on_auth_failure()

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
