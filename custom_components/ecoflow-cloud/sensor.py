from typing import Any

from homeassistant.components.sensor import (SensorDeviceClass, SensorEntity,
                                             SensorStateClass)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (ELECTRIC_CURRENT_AMPERE,
                                 ELECTRIC_POTENTIAL_VOLT, ENERGY_WATT_HOUR,
                                 FREQUENCY_HERTZ, PERCENTAGE, POWER_WATT,
                                 TEMP_CELSIUS, TIME_SECONDS)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, EcoFlowBaseEntity
from .mqtt.ecoflow_mqtt import EcoflowMQTTClient
from .config_flow import EcoflowModel


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowMQTTClient = hass.data[DOMAIN][entry.entry_id]
    entities = []

    entities.extend([
        LevelEntity(client, "1", "pd.soc", "Main Battery Level"),
        RemainEntity(client, "2", "bms_emsStatus.chgRemainTime", "Charge Remaining Time"),
        RemainEntity(client, "2", "bms_emsStatus.dsgRemainTime", "Discharge Remaining Time"),

        WattsEntity(client, "1", "pd.wattsInSum", "Total In Power"),
        WattsEntity(client, "1", "pd.wattsOutSum", "Total Out Power"),

        TempEntity(client, "3", "inv.outTemp", "Inv Out temperature"),
        CyclesEntity(client, "2", "bms_bmsStatus.cycles", "Cycles"),
        FanEntity(client, "2", "bms_emsStatus.fanLevel", "Fan Level")
        ])

    # if client.device_type == EcoflowModel.DELTA2.name:
    #     pass
    #
    # if client.device_type == EcoflowModel.RIVER2.name:
    #     pass

    async_add_entities(entities)


class BaseEntity(SensorEntity, EcoFlowBaseEntity):
    pass


class CyclesEntity(BaseEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:battery-heart-variant"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING


class FanEntity(BaseEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:fan"


class LevelEntity(BaseEntity):
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT


class RemainEntity(BaseEntity):
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = TIME_SECONDS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def _prepare_value(self, val: Any) -> Any:
        if int(val) < 0 or int(val) >= 5000:
            return "0"
        else:
            return val


class TempEntity(BaseEntity):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = TEMP_CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT


class WattsEntity(BaseEntity):
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = POWER_WATT
    _attr_state_class = SensorStateClass.MEASUREMENT





