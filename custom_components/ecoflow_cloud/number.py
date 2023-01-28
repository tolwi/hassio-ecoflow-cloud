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
    def __init__(self, client: EcoflowMQTTClient, mqtt_key: str, title: str, min_value: int, max_value: int,
                 command: Callable[[int], dict[str, any]] | None, enabled: bool = True, auto_enable: bool = False) -> object:
        super().__init__(client, mqtt_key, title, enabled, auto_enable)
        self._attr_native_max_value = max_value
        self._attr_native_min_value = min_value
        self.__command = command

    async def async_set_native_value(self, value: float):
        if self.__command:
            data = self.__command(int(value))
            self._client.send_message(data)

class ChargingPowerEntity(ValueUpdateEntity):
    _attr_native_step = 100
    _attr_icon = "mdi:transmission-tower-import"
    _attr_native_unit_of_measurement = POWER_WATT
    _attr_device_class = SensorDeviceClass.POWER

class LevelEntity(ValueUpdateEntity):
    _attr_native_step = 5
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.BATTERY
