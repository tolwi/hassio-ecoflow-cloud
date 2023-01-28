from typing import Any, Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN
from .entities import BaseSwitchEntity
from .mqtt.ecoflow_mqtt import EcoflowMQTTClient


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
        self._attr_is_on = bool(val)
        return True

    def turn_on(self, **kwargs: Any) -> None:
        self._attr_is_on = True
        if self.__command:
            data = self.__command(1)
            self._client.send_message(data)

    def turn_off(self, **kwargs: Any) -> None:
        self._attr_is_on = False
        if self.__command:
            data = self.__command(0)
            self._client.send_message(data)


class DisabledEntity(BaseSwitchEntity):

    def __init__(self, client: EcoflowMQTTClient, mqtt_key: str, title: str,
                 command: Callable[[int], dict[str, any]] | None, enabled: bool = True, auto_enable: bool = False):
        super().__init__(client, mqtt_key, title, enabled, auto_enable)
        self.__command = command

    def _update_value(self, val: Any) -> bool:
        self._attr_is_off = bool(val)
        return True

    def turn_on(self, **kwargs: Any) -> None:
        self._attr_is_on = True
        if self.__command:
            data = self.__command(0)
            self._client.send_message(data)

    def turn_off(self, **kwargs: Any) -> None:
        self._attr_is_on = False
        if self.__command:
            data = self.__command(1)
            self._client.send_message(data)


class BeeperEntity(DisabledEntity):
    _attr_entity_category = EntityCategory.CONFIG
