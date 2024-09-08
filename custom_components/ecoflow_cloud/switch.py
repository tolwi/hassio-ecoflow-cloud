import asyncio
import inspect
import logging
from typing import Any, Callable, get_type_hints

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
    def __init__(
        self,
        client: EcoflowMQTTClient,
        mqtt_key: str,
        title: str,
        command: Callable[[int, dict[str, Any] | None], dict[str, Any]] | None,
        enabled: bool = True,
        auto_enable: bool = False,
        enableValue: Any = None,
    ):
        super().__init__(client, mqtt_key, title, command, enabled, auto_enable)
        self._enable_value = enableValue

    def _update_value(self, val: Any) -> bool:
        _LOGGER.debug("Updating switch " + self._attr_unique_id + " to " + str(val))
        if self._enable_value is not None:
            if self._enable_value == val:
                self._attr_is_on = True
            else:
                self._attr_is_on = False
        else:
            self._attr_is_on = bool(val)
        return True

    def turn_on(self, **kwargs: Any) -> None:
        if self._command:
            self.send_set_message(1, self.command_dict(1))

    def turn_off(self, **kwargs: Any) -> None:
        if self._command:
            self.send_set_message(0, self.command_dict(0))


class BitMaskEnableEntity(EnabledEntity):
    """
    This class represents a switch that is on the data layer to ecoflow
    a bitmask. (so a combination of multiple switches)

    The bitmap system of ecoflow is quite simple. Essentialy each switch has it's own bit bit.
    Because this implemantion is based on a the powerkits DC panel,
    this implementation only works for 6 switches bitmask.
    So we need 6 bits to address each switch. For example if we want to turn on switch of we need:
    `000001`
    If we want to turn on switch 5 we need:
    `010000`
    To turn on switches we add infront of the bitmask two more bits and set the first one to 1:
    `10000001`
    The strange thing is now that `10000001` turns actually the second switch on.
    So in the turn on mode we always need to calculate minus one.
    So to turn on switch one you need the bitmask:
    `10000000`

    These bitmasks needs then to be converted to int. (this class does this automatically)
    And this int is the value.
    """

    def __init__(
        self,
        client: EcoflowMQTTClient,
        switchKey: str,
        title: str,
        command: Callable[[str, int, dict[str, Any] | None], dict[str, Any]]
        | Callable[[int, dict[str, Any] | None], dict[str, Any]]
        | None,
        enabled: bool = True,
        auto_enable: bool = False,
    ):
        """
        Init the bitmask switsch

        :param str switchKey: The key that should be formatted
        like that: `maintopic.sn.subtopic.switchnumber`
        Switchnumber is 1 based, not zero based!
        :param str title: The switch name used in the has UI.
        :param str command: a Lambda that accepts as a first
        parameter the sn (serial number) and a a second parameter the value (precalculated bitmask).
        :param bool enabled: defines if this switch is enabled by default
        :param bool auto_enable: defines if this switch is enabled by default
        """
        # TODO: We don't know right now a good solution to the problem of lambda overloading
        test = list(inspect.signature(command).parameters.items())
        name, param = test[0]
        type = param.annotation
        splittedKey = switchKey.split(".")
        self.switchNumber = int(splittedKey[-1])
        self.bitmask = "000000"
        mqtt_key = ".".join(splittedKey[:-1])
        super().__init__(
            client,
            mqtt_key,
            title,
            lambda value: command(splittedKey[1], value),
            enabled,
            auto_enable,
        )
        self.unique_id = self.gen_unique_id(client.device_sn, switchKey)

    def _update_value(self, val: Any) -> bool:
        self.bitmask = ("{0:06b}".format(val))[::-1]
        self._attr_is_on = bool(int(self.bitmask[self.switchNumber - 1]))
        _LOGGER.debug(
            "Updating switch "
            + self._attr_unique_id
            + " with value "
            + str(val)
            + " to "
            + self._attr_is_on.__str__()
        )
        return True

    def turn_on(self, **kwargs: Any) -> None:
        if self._command:
            # 128 is `1000000`, what is the bitmask ofset to turn on things
            # TODO: if this class should be used for other bitmap switches,
            # this 128 needs to be replaced, with the correct offset
            self.send_set_message(1, self.command_dict(128 + (self.switchNumber - 1)))

    def turn_off(self, **kwargs: Any) -> None:
        if self._command:
            self.send_set_message(0, self.command_dict((self.switchNumber - 1)))


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
