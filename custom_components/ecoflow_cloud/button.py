import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN
from .entities import BaseButtonEntity
from .mqtt.ecoflow_mqtt import EcoflowMQTTClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowMQTTClient = hass.data[DOMAIN][entry.entry_id]

    from .devices.registry import devices
    async_add_entities(devices[client.device_type].buttons(client))


class EnabledButtonEntity(BaseButtonEntity):

    def press(self, **kwargs: Any) -> None:
        if self._command:
            self.send_set_message(0, self.command_dict(0))

class DisabledButtonEntity(BaseButtonEntity):

    async def async_press(self, **kwargs: Any) -> None:
        if self._command:
            self.send_set_message(0, self.command_dict(0))

