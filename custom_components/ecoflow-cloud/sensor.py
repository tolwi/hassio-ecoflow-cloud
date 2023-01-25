from typing import Any

from homeassistant.components.sensor import (SensorDeviceClass, SensorEntity,
                                             SensorStateClass)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (PERCENTAGE, POWER_WATT,
                                 TEMP_CELSIUS, TIME_MINUTES, TIME_SECONDS)
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
        LevelEntity(client, "pd.soc", "Main Battery Level"),
        RemainEntity(client, "bms_emsStatus.chgRemainTime", "Charge Remaining Time"),
        RemainEntity(client, "bms_emsStatus.dsgRemainTime", "Discharge Remaining Time"),

        WattsEntity(client, "pd.wattsInSum", "Total In Power"),
        WattsEntity(client, "pd.wattsOutSum", "Total Out Power"),

        TempEntity(client, "inv.outTemp", "Inv Out Temperature"),
        TempEntity(client, "bms_bmsStatus.temp", "Battery Temperature"),
        CyclesEntity(client, "bms_bmsStatus.cycles", "Cycles"),

        FanEntity(client, "bms_emsStatus.fanLevel", "Fan Level")
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
            return 0
        else:
            # value is in minutes, but there is no simple way to change unit of measurement - so let's just multiply by 60 :)
            return int(val) * 60


class TempEntity(BaseEntity):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = TEMP_CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT


class WattsEntity(BaseEntity):
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = POWER_WATT
    _attr_state_class = SensorStateClass.MEASUREMENT
