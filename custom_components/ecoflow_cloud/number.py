from typing import Callable, Any

from homeassistant.components.number import NumberMode
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, POWER_WATT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, OPTS_POWER_STEP
from .entities import BaseNumberEntity
from .mqtt.ecoflow_mqtt import EcoflowMQTTClient


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowMQTTClient = hass.data[DOMAIN][entry.entry_id]

    from .devices.registry import devices
    async_add_entities(devices[client.device_type].numbers(client))


class ValueUpdateEntity(BaseNumberEntity):
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    async def async_set_native_value(self, value: float):
        if self._command:
            ival = int(value)
            self.send_set_message(ival, self.command_dict(ival))


class ChargingPowerEntity(ValueUpdateEntity):
    _attr_icon = "mdi:transmission-tower-import"
    _attr_native_unit_of_measurement = POWER_WATT
    _attr_device_class = SensorDeviceClass.POWER

    def __init__(self, client: EcoflowMQTTClient, mqtt_key: str, title: str, min_value: int, max_value: int,
                 command: Callable[[int], dict[str, any]] | None, enabled: bool = True, auto_enable: bool = False):
        super().__init__(client, mqtt_key, title, min_value, max_value, command, enabled, auto_enable)

        self._attr_native_step = client.config_entry.options[OPTS_POWER_STEP]


class BatteryBackupLevel(ValueUpdateEntity):
    _attr_icon = "mdi:battery-charging-90"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.BATTERY

    def __init__(self, client: EcoflowMQTTClient, mqtt_key: str, title: str,
                 min_value: int, max_value: int,
                 min_key: str, max_key: str,
                 command: Callable[[int], dict[str, any]] | None):
        super().__init__(client, mqtt_key, title, min_value, max_value, command, True, False)
        self.__min_key = min_key
        self.__max_key = max_key

    def _updated(self, data: dict[str, Any]):
        if self.__min_key in data:
            self._attr_native_min_value = int(data[self.__min_key]) + 5  # min + 5%
        if self.__max_key in data:
            self._attr_native_max_value = int(data[self.__max_key])
        super()._updated(data)


class LevelEntity(ValueUpdateEntity):
    _attr_native_unit_of_measurement = PERCENTAGE


class MinBatteryLevelEntity(LevelEntity):
    _attr_icon = "mdi:battery-charging-10"


class MaxBatteryLevelEntity(LevelEntity):
    _attr_icon = "mdi:battery-charging-90"


class MinGenStartLevelEntity(LevelEntity):
    _attr_icon = "mdi:engine"


class MaxGenStopLevelEntity(LevelEntity):
    _attr_icon = "mdi:engine-off"
