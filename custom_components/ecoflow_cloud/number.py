from typing import Callable

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, POWER_WATT, TIME_SECONDS, TIME_MINUTES, ELECTRIC_CURRENT_MILLIAMPERE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN
from .entities import BaseNumberEntity
from .mqtt.ecoflow_mqtt import EcoflowMQTTClient


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowMQTTClient = hass.data[DOMAIN][entry.entry_id]

    from .devices.registry import devices
    if client.device_type in devices:
        entities = devices[client.device_type].numbers(client)
        async_add_entities(entities)


class ValueUpdateEntity(BaseNumberEntity):

    async def async_set_native_value(self, value: float):
        if self._command:
            ival = int(value)
            self.send_message(ival, self.command_dict(ival))

class ChargingPowerEntity(ValueUpdateEntity):
    _attr_native_step = 100
    _attr_icon = "mdi:transmission-tower-import"
    _attr_native_unit_of_measurement = POWER_WATT
    _attr_device_class = SensorDeviceClass.POWER


class LevelEntity(ValueUpdateEntity):
    _attr_native_step = 5
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.BATTERY


class MinBatteryLevelEntity(LevelEntity):
    _attr_icon = "mdi:battery-charging-10"


class MaxBatteryLevelEntity(LevelEntity):
    _attr_icon = "mdi:battery-charging-90"


class MinGenStartLevelEntity(LevelEntity):
    _attr_icon = "mdi:engine"


class MaxGenStopLevelEntity(LevelEntity):
    _attr_icon = "mdi:engine-off"