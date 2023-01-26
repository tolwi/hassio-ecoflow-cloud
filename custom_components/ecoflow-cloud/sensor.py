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
        WattsEntity(client, "pd.wattsInSum", "Total In Power"),
        WattsEntity(client, "pd.wattsOutSum", "Total Out Power"),

    ])

    if client.device_type in [EcoflowModel.DELTA_2.name,
                              EcoflowModel.RIVER_2,
                              EcoflowModel.RIVER_2_MAX.name,
                              EcoflowModel.RIVER_2_PRO,
                              ]:
        entities.extend([
            RemainEntity(client, "bms_emsStatus.chgRemainTime", "Charge Remaining Time"),
            RemainEntity(client, "bms_emsStatus.dsgRemainTime", "Discharge Remaining Time"),

            TempEntity(client, "inv.outTemp", "Inv Out Temperature"),
            TempEntity(client, "bms_bmsStatus.temp", "Battery Temperature"),
            CyclesEntity(client, "bms_bmsStatus.cycles", "Cycles"),

            FanEntity(client, "bms_emsStatus.fanLevel", "Fan Level")
        ])
    if client.device_type == EcoflowModel.DELTA_2.name:
        # disabled 2nd battery
        entities.extend([
            LevelEntity(client, "bms_slave.soc", "Slave Battery Level", False, True),
            TempEntity(client, "bms_slave.temp", "Slave Battery Temperature", False, True),
            CyclesEntity(client, "bms_slave.cycles", "Slave Cycles", False, True)
        ])

    if client.device_type == EcoflowModel.DELTA_PRO.name:
        entities.extend([
            RemainEntity(client, "ems.chgRemainTime", "Charge Remaining Time"),
            RemainEntity(client, "ems.dsgRemainTime", "Discharge Remaining Time"),
            TempEntity(client, "bmsMaster.temp", "Battery Temperature"),
            CyclesEntity(client, "bmsMaster.cycles", "Cycles")
        ])

    async_add_entities(entities)


class BaseEntity(SensorEntity, EcoFlowBaseEntity):

    def _update_value(self, val: Any) -> bool:
        if self._attr_native_value != val:
            self._attr_native_value = val
            return True
        else:
            return False


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
    _attr_native_value = -1

    def _update_value(self, val: Any) -> Any:
        # value is in minutes, but there is no simple way to change unit of measurement - so let's just multiply by 60 :)
        ival = int(val) * 60
        if ival < 0 or ival > 5000 * 60:
            ival = 0

        if self._attr_native_value != ival:
            self._attr_native_value = ival
            return True
        else:
            return False


class TempEntity(BaseEntity):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = TEMP_CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_value = 0


class WattsEntity(BaseEntity):
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = POWER_WATT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_value = 0
    __values: list[int] = [0, 0, 0]

    def _update_value(self, val: Any) -> Any:
        ival = int(val)
        self.__values.pop(0)
        self.__values.append(ival)
        if ival == 0 and any(filter(lambda v: v > 0, self.__values)):
            return False
        else:
            self._attr_native_value = ival
            return True
