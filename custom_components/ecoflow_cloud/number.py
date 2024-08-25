from typing import Callable, Any

from homeassistant.components.number import NumberMode
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ECOFLOW_DOMAIN
from .api import EcoflowApiClient
from .entities import BaseNumberEntity
from .devices import BaseDevice


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowApiClient = hass.data[ECOFLOW_DOMAIN][entry.entry_id]
    for (sn, device) in client.devices.items():
        async_add_entities(device.numbers(client))


class ValueUpdateEntity(BaseNumberEntity):
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    async def async_set_native_value(self, value: float):
        if self._command:
            ival = int(value)
            self.send_set_message(ival, self.command_dict(ival))


class ChargingPowerEntity(ValueUpdateEntity):
    _attr_icon = "mdi:transmission-tower-import"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER

    def __init__(self, client: EcoflowApiClient, device: BaseDevice, mqtt_key: str, title: str, min_value: int, max_value: int,
                 command: Callable[[int], dict[str, Any]] | None,
                 enabled: bool = True, auto_enable: bool = False):
        super().__init__(client, device, mqtt_key, title, min_value, max_value, command, enabled, auto_enable)
        self._attr_native_step = self._device.charging_power_step()


class DeciChargingPowerEntity(ChargingPowerEntity):
    _attr_mode = NumberMode.BOX

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)

    async def async_set_native_value(self, value: float):
        if self._command:
            ival = int(value * 10)
            self.send_set_message(ival, self.command_dict(ival))

class MinMaxLevelEntity(ValueUpdateEntity):
    def __init__(self, client: EcoflowApiClient, device: BaseDevice, mqtt_key: str, title: str,
                 min_value: int, max_value: int,
                 command: Callable[[int], dict[str, Any]] | None):
        super().__init__(client, device, mqtt_key, title, min_value, max_value, command, True, False)



class BrightnessLevelEntity(MinMaxLevelEntity):
    _attr_icon = "mdi:brightness-6"
    _attr_native_unit_of_measurement = PERCENTAGE


class BatteryBackupLevel(MinMaxLevelEntity):
    _attr_icon = "mdi:battery-charging-90"
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, client: EcoflowApiClient, device: BaseDevice, mqtt_key: str, title: str,
                 min_value: int, max_value: int,
                 min_key: str, max_key: str,
                 command: Callable[[int], dict[str, Any]] | None):
        super().__init__(client, device, mqtt_key, title, min_value, max_value, command)
        self._min_key = min_key
        self._max_key = max_key

    def _updated(self, data: dict[str, Any]):
        if self._min_key in data:
            self._attr_native_min_value = int(data[self._min_key]) + 5  # min + 5%
        if self._max_key in data:
            self._attr_native_max_value = int(data[self._max_key])
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


class SetTempEntity(ValueUpdateEntity):
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
