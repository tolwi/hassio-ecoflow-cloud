import asyncio
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


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    client: EcoflowMQTTClient = hass.data[DOMAIN][entry.entry_id]

    from .devices.registry import devices

    # the following line waits here as long as possible,
    # so the client.data object gets filled with the data
    # from the mqtt queue.
    # this helps to figure out the exact sensor layout in the devices implementation.
    # 9 seconds is one second lower then the warning message of hass.
    # One second should be enaugh time to configure all entities.
    await asyncio.sleep(9)
    async_add_entities(devices[client.device_type].switches(client))


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


class BitMaskEnableEntity(EnabledEntity):
    def __init__(
        self,
        client: EcoflowMQTTClient,
        switchKey: str,
        title: str,
        command: Callable[[int, dict[str, Any] | None], dict[str, Any]] | None,
        enabled: bool = True,
        auto_enable: bool = False,
    ):
        splittedKey = switchKey.split(".")
        self.switchNumber = int(splittedKey[-1])
        mqtt_key = ".".join(splittedKey[:-1])
        super().__init__(client, mqtt_key, title, command, enabled, auto_enable)
        self.unique_id = self.gen_unique_id(client.device_sn, switchKey)

    def _update_value(self, val: Any) -> bool:
        bitmask = ("{0:06b}".format(val))[::-1]
        self._attr_is_on = bool(int(bitmask[self.switchNumber - 1]))
        # if self._attr_is_on == True:
        #     self.turn_on()
        # else:
        #     self.turn_off()
        # self.is_on = bool(int(bitmask[self.switchNumber - 1]))
        _LOGGER.debug(
            "Updating switch "
            + self._attr_unique_id
            + " with value "
            + str(val)
            + " to "
            + self._attr_is_on.__str__()
        )
        return True


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
