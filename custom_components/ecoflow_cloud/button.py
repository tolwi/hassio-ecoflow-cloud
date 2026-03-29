import logging
from typing import Any

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.ecoflow_cloud.entities import EcoFlowAbstractEntity

from . import ECOFLOW_DOMAIN
from .api import EcoflowApiClient
from .ble import supports_ble_wifi_recovery_device_type
from .entities import BaseButtonEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowApiClient = hass.data[ECOFLOW_DOMAIN][entry.entry_id]
    for sn, device in client.devices.items():
        async_add_entities(device.buttons(client))
        extra: list[ButtonEntity] = [ReconnectButtonEntity(client, device)]
        if (
            client.ble_recovery_manager is not None
            and client.ble_recovery_manager.supports_device(device.device_data)
            and supports_ble_wifi_recovery_device_type(device.device_data.device_type)
        ):
            extra.append(BleRecoverWifiButtonEntity(client, device))
        async_add_entities(extra)


class EnabledButtonEntity(BaseButtonEntity):
    def press(self, **kwargs: Any) -> None:
        if self._command:
            self.send_set_message(0, self.command_dict(0))


class DisabledButtonEntity(BaseButtonEntity):
    async def async_press(self, **kwargs: Any) -> None:
        if self._command:
            self.send_set_message(0, self.command_dict(0))


class ReconnectButtonEntity(ButtonEntity, EcoFlowAbstractEntity):
    def __init__(self, client: EcoflowApiClient, device):
        super().__init__(client, device, "Reconnect", "reconnect")
        self._attr_device_class = ButtonDeviceClass.RESTART

    async def async_press(self) -> None:
        await self.hass.async_add_executor_job(self._client.stop)
        await self._client.login()
        await self.hass.async_add_executor_job(self._client.start)


class BleRecoverWifiButtonEntity(ButtonEntity, EcoFlowAbstractEntity):
    def __init__(self, client: EcoflowApiClient, device):
        super().__init__(client, device, "Recover Wi-Fi via BLE", "recover_wifi_ble")
        self._attr_device_class = ButtonDeviceClass.RESTART

    async def async_press(self) -> None:
        if self._client.ble_recovery_manager is None:
            return

        await self._client.ble_recovery_manager.async_recover(
            self._device.device_info.sn,
            reason="manual",
            manual=True,
        )
