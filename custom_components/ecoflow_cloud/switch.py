import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ECOFLOW_DOMAIN
from .api import EcoflowApiClient
from .entities import BaseSwitchEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowApiClient = hass.data[ECOFLOW_DOMAIN][entry.entry_id]
    for (sn, device) in client.devices.items():
        async_add_entities(device.switches(client))


class EnabledEntity(BaseSwitchEntity):

    def _update_value(self, val: Any) -> bool:
        _LOGGER.debug("Updating switch " + self._attr_unique_id + " to " + str(val))
        self._attr_is_on = bool(val)
        return True

    def turn_on(self, **kwargs: Any) -> None:
        if self._command:
            self.send_set_message(1, self.command_dict(1))

    def turn_off(self, **kwargs: Any) -> None:
        if self._command:
            self.send_set_message(0, self.command_dict(0))


class DisabledEntity(BaseSwitchEntity):

    def _update_value(self, val: Any) -> bool:
        _LOGGER.debug("Updating switch " + self._attr_unique_id + " to " + str(val))
        self._attr_is_on = not bool(val)
        return True

    async def async_turn_on(self, **kwargs: Any) -> None:
        if self._command:
            self.send_set_message(0, self.command_dict(0))

    async def async_turn_off(self, **kwargs: Any) -> None:
        if self._command:
            self.send_set_message(1, self.command_dict(1))


class FanModeEntity(BaseSwitchEntity):  # for River Max

    def _update_value(self, val: Any) -> bool:
        _LOGGER.debug("Updating switch " + self._attr_unique_id + " to " + str(val))
        self._attr_is_on = val == 1
        return True

    def turn_on(self, **kwargs: Any) -> None:
        if self._command:
            self.send_set_message(1, self.command_dict(1))

    def turn_off(self, **kwargs: Any) -> None:
        if self._command:
            self.send_set_message(3, self.command_dict(3))


class BeeperEntity(DisabledEntity):
    _attr_entity_category = EntityCategory.CONFIG

    @property
    def icon(self) -> str | None:
        if self.is_on:
            return "mdi:volume-high"
        else:
            return "mdi:volume-mute"


class InvertedBeeperEntity(EnabledEntity):
    _attr_entity_category = EntityCategory.CONFIG

    @property
    def icon(self) -> str | None:
        if self.is_on:
            return "mdi:volume-high"
        else:
            return "mdi:volume-mute"
