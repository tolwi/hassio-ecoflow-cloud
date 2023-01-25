from typing import Callable

from homeassistant.components.number import NumberEntity
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, POWER_WATT, TIME_SECONDS, TIME_MINUTES
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, EcoFlowBaseEntity
from .config_flow import EcoflowModel
from .mqtt.ecoflow_mqtt import EcoflowMQTTClient


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowMQTTClient = hass.data[DOMAIN][entry.entry_id]

    if client.device_type == EcoflowModel.DIAGNOSTIC.name:
        return

    entities = []
    entities.extend([
        LevelEntity(client, "bms_emsStatus.maxChargeSoc", "Max Charge Level", 50, 100,
                    lambda value: {"moduleType": 2, "operateType": "upsConfig", "params": {"maxChgSoc": int(value)}}),
        LevelEntity(client, "bms_emsStatus.minDsgSoc", "Min Discharge Level", 0, 30,
                    lambda value: {"moduleType": 2, "operateType": "upsConfig", "params": {"minDsgSoc": int(value)}})
    ])

    if client.device_type == EcoflowModel.RIVER_2_MAX.name:
        entities.extend([
            ChargingPowerEntity(client, "mppt.cfgChgWatts", "AC Charging Power", 100, 660,
                                lambda value: {"moduleType": 5, "operateType": "acChgCfg",
                                               "params": {"chgWatts": int(value), "chgPauseFlag": 255}}),

            PeriodSecondsEntity(client, "mppt.scrStandbyMin", "Screen Timeout", 0, 300,
                                lambda value: {"moduleType": 5, "operateType": "lcdCfg",
                                               "params": {"brighLevel": 255, "delayOff": value}}),

            PeriodMinutesEntity(client, "mppt.powStandbyMin", "Unit Timeout", 0, 1440,
                                lambda value: {"moduleType": 5, "operateType": "standby",
                                               "params": {"standbyMins": value}}),

            PeriodMinutesEntity(client, "mppt.acStandbyMins", "AC Timeout", 0, 1440,
                                lambda value: {"moduleType": 5, "operateType": "acStandby",
                                               "params": {"standbyMins": value}}),
        ])

    if client.device_type == EcoflowModel.DELTA_2.name:
        entities.extend([
            ChargingPowerEntity(client, "mppt.cfgChgWatts", "AC Charging Power", 200, 1200,
                                lambda value: {"moduleType": 5, "operateType": "acChgCfg",
                                               "params": {"chgWatts": int(value), "chgPauseFlag": 255}}),

            PeriodSecondsEntity(client, "pd.lcdOffSec", "Screen Timeout", 0, 300,
                                lambda value: {"moduleType": 1, "operateType": "lcdCfg",
                                               "params": {"brighLevel": 255, "delayOff": value}}),

            PeriodMinutesEntity(client, "pd.standbyMin", "Unit Timeout", 0, 1440,
                                lambda value: {"moduleType": 1, "operateType": "standbyTime",
                                               "params": {"standbyMins": value}}),

            PeriodMinutesEntity(client, "mppt.acStandbyMins", "AC Timeout", 0, 1440,
                                lambda value: {"moduleType": 5, "operateType": "standbyTime",
                                               "params": {"standbyMins": value}}),

            PeriodMinutesEntity(client, "mppt.acStandbyMins", "DC (12V) Timeout", 0, 1440,
                                lambda value: {"moduleType": 5, "operateType": "carStandby",
                                               "params": {"standbyMins": value}}),
        ])

    async_add_entities(entities)


class BaseEntity(NumberEntity, EcoFlowBaseEntity):
    _attr_entity_category = EntityCategory.CONFIG


class ValueUpdateEntity(BaseEntity):
    def __init__(self, client: EcoflowMQTTClient, mqtt_key: str, title: str, min_value: int, max_value: int,
                 command: Callable[[int], dict[str, any]], enabled: bool = True):
        super().__init__(client, mqtt_key, title, enabled)
        self._attr_native_max_value = max_value
        self._attr_native_min_value = min_value
        self.__command = command

    async def async_set_native_value(self, value: float):
        data = self.__command(int(value))
        self._client.send_message(data)


class PeriodSecondsEntity(ValueUpdateEntity):
    _attr_native_step = 30
    _attr_native_unit_of_measurement = TIME_SECONDS


class PeriodMinutesEntity(ValueUpdateEntity):
    _attr_native_step = 30
    _attr_native_unit_of_measurement = TIME_MINUTES


class ChargingPowerEntity(ValueUpdateEntity):
    _attr_native_step = 10
    _attr_icon = "mdi:transmission-tower-import"
    _attr_native_unit_of_measurement = POWER_WATT
    _attr_device_class = SensorDeviceClass.POWER


class LevelEntity(ValueUpdateEntity):
    _attr_native_step = 5
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.BATTERY
