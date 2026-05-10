import logging
from abc import ABC, abstractmethod
from typing import Any

from aiohttp import ClientResponse
from attr import dataclass
from homeassistant.core import HomeAssistant

from ..device_data import DeviceData
from .message import JSONMessage, Message

_LOGGER = logging.getLogger(__name__)


class EcoflowException(Exception):
    pass


class EcoflowAuthException(EcoflowException):
    """Raised when EcoFlow API rejects credentials (access/secret keys or username/password)."""


@dataclass
class EcoflowMqttInfo:
    url: str
    port: int
    username: str
    password: str
    client_id: str | None = None


class EcoflowApiClient(ABC):
    def __init__(self):
        from custom_components.ecoflow_cloud.api.ecoflow_mqtt import EcoflowMQTTClient

        self.mqtt_info: EcoflowMqttInfo
        self.devices: dict[str, Any] = {}
        self.mqtt_client: EcoflowMQTTClient
        self.hass: HomeAssistant | None = None
        self.entry_id: str | None = None
        self._auth_refresh_in_progress = False
        self._consecutive_auth_failures = 0

    @abstractmethod
    async def login(self):
        pass

    @abstractmethod
    async def fetch_all_available_devices(self):
        pass

    @abstractmethod
    async def quota_all(self, device_sn: str | None):
        pass

    @abstractmethod
    def _create_device_info(
        self, device_sn: str, device_name: str, device_type: str, status: int = -1
    ) -> Any:
        pass

    @abstractmethod
    def _device_registry(self) -> dict[str, Any]:
        pass

    def configure_device(self, device_data: DeviceData, api_devices_info: dict[str, Any] | None = None):
        sn = device_data.parent.sn if device_data.parent is not None else device_data.sn
        status = -1
        if api_devices_info and sn in api_devices_info:
            status = api_devices_info[sn].status

        if device_data.parent is not None:
            info = self._create_device_info(device_data.parent.sn, device_data.name, device_data.parent.device_type, status)
        else:
            info = self._create_device_info(device_data.sn, device_data.name, device_data.device_type, status)

        from ..devices import DiagnosticDevice

        registry = self._device_registry()
        if device_data.device_type in registry:
            device = registry[device_data.device_type](info, device_data)
        elif device_data.parent is not None and device_data.parent.device_type in registry:
            device = registry[device_data.parent.device_type](info, device_data)
        else:
            device = DiagnosticDevice(info, device_data)

        self.add_device(device)
        return device

    def add_device(self, device):
        self.devices[device.device_data.sn] = device

    def remove_device(self, device):
        self.devices.pop(device.device_data.sn, None)

    def _accept_mqqt_certification(self, resp_json: dict):
        _LOGGER.info(f"Received MQTT credentials: {resp_json}")
        try:
            mqtt_url = resp_json["data"]["url"]
            mqtt_port = int(resp_json["data"]["port"])
            mqtt_username = resp_json["data"]["certificateAccount"]
            mqtt_password = resp_json["data"]["certificatePassword"]
            self.mqtt_info = EcoflowMqttInfo(mqtt_url, mqtt_port, mqtt_username, mqtt_password)
        except KeyError as key:
            raise EcoflowException(f"Failed to extract key {key} from {resp_json}")

        _LOGGER.info(f"Successfully extracted account: {self.mqtt_info.username}")

    async def _get_json_response(self, resp: ClientResponse) -> dict[str, Any]:
        if resp.status in (401, 403):
            raise EcoflowAuthException(f"HTTP {resp.status}: {resp.reason}")
        if resp.status != 200:
            raise EcoflowException(f"Got HTTP status code {resp.status}: {resp.reason}")

        try:
            json_resp = await resp.json()
            response_message = json_resp["message"]
        except KeyError as key:
            raise EcoflowException(f"Failed to extract key {key} from {resp}")
        except Exception as error:
            raise EcoflowException(f"Failed to parse response: {resp.text} Error: {error}")

        if response_message.lower() != "success":
            lowered = response_message.lower()
            if any(
                kw in lowered
                for kw in (
                    "unauthor",
                    "access denied",
                    "accesskey",
                    "secretkey",
                    "invalid sign",
                    "sign error",
                    "incorrect password",
                    "account doesn't exist",
                    "token",
                )
            ):
                raise EcoflowAuthException(response_message)
            raise EcoflowException(f"{response_message}")

        return json_resp

    def send_get_message(self, device_sn: str, command: dict | Message):
        if isinstance(command, dict):
            command = JSONMessage(command)

        self.mqtt_client.publish(self.devices[device_sn].device_info.get_topic, command.to_mqtt_payload())

    def send_set_message(self, device_sn: str, mqtt_state: dict[str, Any], command: dict | Message):
        if isinstance(command, dict):
            command = JSONMessage(command)

        self.devices[device_sn].data.update_to_target_state(mqtt_state)
        self.mqtt_client.publish(self.devices[device_sn].device_info.set_topic, command.to_mqtt_payload())

    def start(self, hass: HomeAssistant | None = None, entry_id: str | None = None):
        _LOGGER.debug("Starting MQTT client for %s", self.mqtt_info.client_id)
        from custom_components.ecoflow_cloud.api.ecoflow_mqtt import EcoflowMQTTClient

        if hass is not None:
            self.hass = hass
        if entry_id is not None:
            self.entry_id = entry_id

        self.mqtt_client = EcoflowMQTTClient(
            self.mqtt_info,
            self.devices,
            auth_failure_callback=self._on_mqtt_auth_failure,
            connect_success_callback=self._on_mqtt_connect_success,
        )

    def _on_mqtt_auth_failure(self) -> None:
        # Called from paho thread. Hop to the event loop to refresh credentials.
        if self.hass is None:
            _LOGGER.error("MQTT auth failure but no HomeAssistant reference; cannot refresh credentials")
            return
        if self._auth_refresh_in_progress:
            return
        self.hass.loop.call_soon_threadsafe(
            lambda: self.hass.async_create_task(self._async_refresh_credentials())
        )

    def _on_mqtt_connect_success(self) -> None:
        self._consecutive_auth_failures = 0

    async def _async_refresh_credentials(self) -> None:
        import asyncio

        if self._auth_refresh_in_progress:
            return
        self._auth_refresh_in_progress = True
        try:
            self._consecutive_auth_failures += 1

            # Polite backoff so we never poke the broker faster than once a
            # minute on an auth-fail loop. EcoFlow's broker appears to throttle
            # / temp-ban accounts that reconnect too aggressively.
            backoff = {1: 30, 2: 60, 3: 180, 4: 300}.get(self._consecutive_auth_failures, 300)
            if self._consecutive_auth_failures > 4:
                _LOGGER.error(
                    "MQTT auth keeps failing for %s after %d refreshes; triggering reauth",
                    self.mqtt_info.client_id,
                    self._consecutive_auth_failures,
                )
                self._trigger_reauth()
                return

            _LOGGER.info(
                "Waiting %ds before refreshing EcoFlow MQTT credentials (attempt %d)",
                backoff,
                self._consecutive_auth_failures,
            )
            await asyncio.sleep(backoff)

            _LOGGER.info(
                "Refreshing EcoFlow MQTT credentials (attempt %d)", self._consecutive_auth_failures
            )
            try:
                await self.login()
            except EcoflowAuthException as ex:
                _LOGGER.error("Credential refresh failed (auth): %s", ex)
                self._trigger_reauth()
                return
            except Exception as ex:  # noqa: BLE001
                _LOGGER.warning("Credential refresh failed: %s", ex)
                return

            try:
                await self.hass.async_add_executor_job(self._restart_mqtt_with_new_credentials)
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Failed to restart MQTT client with refreshed credentials")
        finally:
            self._auth_refresh_in_progress = False

    def _restart_mqtt_with_new_credentials(self) -> None:
        try:
            self.mqtt_client.stop()
        except Exception:  # noqa: BLE001
            _LOGGER.debug("Error while stopping MQTT client during credential refresh", exc_info=True)
        from custom_components.ecoflow_cloud.api.ecoflow_mqtt import EcoflowMQTTClient

        self.mqtt_client = EcoflowMQTTClient(
            self.mqtt_info,
            self.devices,
            auth_failure_callback=self._on_mqtt_auth_failure,
            connect_success_callback=self._on_mqtt_connect_success,
        )

    def _trigger_reauth(self) -> None:
        if self.hass is None or self.entry_id is None:
            return
        entry = self.hass.config_entries.async_get_entry(self.entry_id)
        if entry is None:
            return
        self.hass.loop.call_soon_threadsafe(entry.async_start_reauth, self.hass)

    def stop(self):
        _LOGGER.debug("Stopping MQTT client for %s", self.mqtt_info.client_id)
        assert self.mqtt_client is not None
        self.mqtt_client.stop()
