import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ECOFLOW_DOMAIN
from .api import EcoflowApiClient
from .entities import BaseButtonEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowApiClient = hass.data[ECOFLOW_DOMAIN][entry.entry_id]
    for (sn, device) in client.devices.items():
        async_add_entities(device.buttons(client))


class EnabledButtonEntity(BaseButtonEntity):

    def press(self, **kwargs: Any) -> None:
        if self._command:
            self.send_set_message(0, self.command_dict(0))


class DisabledButtonEntity(BaseButtonEntity):

    async def async_press(self, **kwargs: Any) -> None:
        if self._command:
            self.send_set_message(0, self.command_dict(0))
