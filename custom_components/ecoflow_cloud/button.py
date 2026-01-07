import logging
from typing import Any

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.ecoflow_cloud.entities import EcoFlowAbstractEntity

from . import ECOFLOW_DOMAIN
from .api import EcoflowApiClient
from .entities import BaseButtonEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowApiClient = hass.data[ECOFLOW_DOMAIN][entry.entry_id]
    for sn, device in client.devices.items():
        async_add_entities(device.buttons(client))
        async_add_entities([ReconnectButtonEntity(client, device)])


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
