from homeassistant.components.number.const import NumberDeviceClass
from typing import Any, Callable

from homeassistant.components.number import NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ECOFLOW_DOMAIN
from .api import EcoflowApiClient, Message
from .devices import BaseDevice
from .entities import BaseNumberEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowApiClient = hass.data[ECOFLOW_DOMAIN][entry.entry_id]
    for sn, device in client.devices.items():
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
    _attr_device_class = NumberDeviceClass.POWER

    def __init__(
        self,
        client: EcoflowApiClient,
        device: BaseDevice,
        mqtt_key: str,
        title: str,
        min_value: int,
        max_value: int,
        command: Callable[[int], dict[str, Any] | Message]
        | Callable[[int, dict[str, Any]], dict[str, Any] | Message]
        | None,
        enabled: bool = True,
        auto_enable: bool = False,
    ):
        super().__init__(
            client,
            device,
            mqtt_key,
            title,
            min_value,
            max_value,
            command,
            enabled,
            auto_enable,
        )
        self._attr_native_step = self._device.charging_power_step()


class DynamicMaxPowerEntity(ValueUpdateEntity):
    """Writable power limit whose maximum is reported by the device.

    Writes are deliberately refused until a valid maximum has been received.
    This prevents a stale integration startup from sending an unsafe value.
    """

    _attr_icon = "mdi:transmission-tower-export"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = NumberDeviceClass.POWER
    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        client: EcoflowApiClient,
        device: BaseDevice,
        mqtt_key: str,
        title: str,
        min_value: int,
        max_key: str,
        command: Callable[[int], dict[str, Any] | Message],
    ):
        self._max_key = max_key
        self._device_max_available = False
        super().__init__(client, device, mqtt_key, title, min_value, min_value, command)
        self._attr_native_step = self._device.charging_power_step()

    def _updated(self, data: dict[str, Any]):
        if self._max_key in data:
            maximum = int(data[self._max_key])
            if maximum > self._attr_native_min_value:
                self._attr_native_max_value = maximum
                self._device_max_available = True
            else:
                self._device_max_available = False
        super()._updated(data)

    async def async_set_native_value(self, value: float):
        if not self._device_max_available:
            raise ValueError("Device power maximum is unavailable; refusing write")
        if not float(value).is_integer():
            raise ValueError("Power limit must be a whole number of watts")
        if value < self._attr_native_min_value or value > self._attr_native_max_value:
            raise ValueError(
                f"Power limit {value} W is outside the device range "
                f"{self._attr_native_min_value}-{self._attr_native_max_value} W"
            )
        if (value - self._attr_native_min_value) % self._attr_native_step:
            raise ValueError(f"Power limit must use {self._attr_native_step} W steps")
        await super().async_set_native_value(value)


class DeciChargingPowerEntity(ChargingPowerEntity):
    _attr_mode = NumberMode.BOX

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)

    async def async_set_native_value(self, value: float):
        if self._command:
            ival = int(value * 10)
            self.send_set_message(ival, self.command_dict(ival))


class AcChargingPowerInAmpereEntity(ValueUpdateEntity):
    _attr_mode = NumberMode.BOX
    _attr_native_step = 1

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val))

    async def async_set_native_value(self, value: float):
        if self._command:
            self.send_set_message(int(value), self.command_dict(int(value)))


class MinMaxLevelEntity(ValueUpdateEntity):
    def __init__(
        self,
        client: EcoflowApiClient,
        device: BaseDevice,
        mqtt_key: str,
        title: str,
        min_value: int,
        max_value: int,
        command: Callable[[int], dict[str, Any] | Message]
        | Callable[[int, dict[str, Any]], dict[str, Any] | Message]
        | None,
    ):
        super().__init__(client, device, mqtt_key, title, min_value, max_value, command, True, False)


class BrightnessLevelEntity(MinMaxLevelEntity):
    _attr_icon = "mdi:brightness-6"
    _attr_native_unit_of_measurement = PERCENTAGE


class BatteryBackupLevel(MinMaxLevelEntity):
    _attr_icon = "mdi:battery-charging-90"
    _attr_native_unit_of_measurement = PERCENTAGE
    _gap_min = 5

    def __init__(
        self,
        client: EcoflowApiClient,
        device: BaseDevice,
        mqtt_key: str,
        title: str,
        min_value: int,
        max_value: int,
        min_key: str,
        max_key: str,
        gap_min: int,
        command: Callable[[int], dict[str, Any]] | None,
    ):
        super().__init__(client, device, mqtt_key, title, min_value, max_value, command)
        self._min_key = min_key
        self._max_key = max_key
        self._gap_min = gap_min

    def _updated(self, data: dict[str, Any]):
        if self._min_key in data:
            self._attr_native_min_value = int(data[self._min_key]) + self._gap_min  # min + 5%
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

class MaxWattsEntity(LevelEntity):
    _attr_icon = "mdi:power-plug-off"


class SetTempEntity(ValueUpdateEntity):
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
