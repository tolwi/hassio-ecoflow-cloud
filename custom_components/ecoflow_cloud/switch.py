import logging
from typing import Any, Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN
from .entities import BaseSwitchEntity
from .mqtt.ecoflow_mqtt import EcoflowMQTTClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowMQTTClient = hass.data[DOMAIN][entry.entry_id]

    from .devices.registry import devices
    if client.device_type in devices:
        entities = devices[client.device_type].switches(client)
        async_add_entities(entities)


class EnabledEntity(BaseSwitchEntity):
    def __init__(self, client: EcoflowMQTTClient, mqtt_key: str, title: str,
                 command: Callable[[int], dict[str, any]] | None, enabled: bool = True, auto_enable: bool = False):
        super().__init__(client, mqtt_key, title, enabled, auto_enable)
        self.__command = command

    def _update_value(self, val: Any) -> bool:
        _LOGGER.debug("Updating switch " + self._attr_unique_id + " to " + str(val))
        self._attr_is_on = bool(val)
        return True

    def turn_on(self, **kwargs: Any) -> None:
        if self.__command:
            self.send_message(1, self.__command(1))

    def turn_off(self, **kwargs: Any) -> None:
        if self.__command:
            self.send_message(0, self.__command(0))


class DisabledEntity(BaseSwitchEntity):

    def __init__(self, client: EcoflowMQTTClient, mqtt_key: str, title: str,
                 command: Callable[[int], dict[str, any]] | None, enabled: bool = True, auto_enable: bool = False):
        super().__init__(client, mqtt_key, title, enabled, auto_enable)
        self.__command = command

    def _update_value(self, val: Any) -> bool:
        _LOGGER.debug("Updating switch " + self._attr_unique_id + " to " + str(val))
        self._attr_is_on = not bool(val)
        return True

    async def async_turn_on(self, **kwargs: Any) -> None:
        if self.__command:
            self.send_message(0, self.__command(0))

    async def async_turn_off(self, **kwargs: Any) -> None:
        if self.__command:
            self.send_message(1, self.__command(1))


class BeeperEntity(DisabledEntity):
    _attr_entity_category = EntityCategory.CONFIG

    @property
    def icon(self) -> str | None:
        if self.is_on:
            return "mdi:volume-high"
        else:
            return "mdi:volume-mute"


