import random

from homeassistant.components.number import NumberEntity
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, POWER_WATT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, EcoFlowBaseEntity
from .mqtt.ecoflow_mqtt import EcoflowMQTTClient
from .config_flow import EcoflowModel

commands = {
    "bms_emsStatus.maxChargeSoc": lambda value: {"moduleType": 2, "operateType": "upsConfig", "params": {"maxChgSoc": int(value)}},
    "bms_emsStatus.minDsgSoc": lambda value: {"moduleType": 2, "operateType": "upsConfig", "params": {"minDsgSoc": int(value)}},
    "mppt.cfgChgWatts": lambda value: {"moduleType": 5, "operateType": "acChgCfg", "params": {"chgWatts": int(value), "chgPauseFlag": 255}}
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowMQTTClient = hass.data[DOMAIN][entry.entry_id]
    entities = []
    entities.extend([
        LevelEntity(client, "2", "bms_emsStatus.maxChargeSoc", "Max Charge Level", 50, 100),
        LevelEntity(client, "2", "bms_emsStatus.minDsgSoc", "Min discharge Level", 0, 30)
    ])

    if client.device_type == EcoflowModel.RIVER_2_MAX.name:
        entities.extend([
            ChargingPowerEntity(client, "5", "mppt.cfgChgWatts", "AC Charging Speed", 100, 660),
            ])

    if client.device_type == EcoflowModel.DELTA_2.name:
        entities.extend([
            ChargingPowerEntity(client, "5", "mppt.cfgChgWatts", "AC Charging Speed", 200, 1200),
            ])

    async_add_entities(entities)


class BaseEntity(NumberEntity, EcoFlowBaseEntity):
    _attr_entity_category = EntityCategory.CONFIG


class ValueUpdateEntity(BaseEntity):
    def __init__(self, client: EcoflowMQTTClient, module_type: str, mqtt_key: str, title: str, min_value: int, max_value: int, enabled: bool = True):
        super().__init__(client, module_type, mqtt_key, title, enabled)
        self._attr_native_max_value = max_value
        self._attr_native_min_value = min_value

    async def async_set_native_value(self, value: float):
        if self._mqtt_key in commands:
            self._client.send_message(commands[self._mqtt_key](value))


class ChargingPowerEntity(ValueUpdateEntity):
    _attr_native_step = 10
    _attr_icon = "mdi:transmission-tower-import"
    _attr_native_unit_of_measurement = POWER_WATT
    _attr_device_class = SensorDeviceClass.POWER


class LevelEntity(ValueUpdateEntity):
    _attr_native_step = 5
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.BATTERY
