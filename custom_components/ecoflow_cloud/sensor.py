from datetime import timedelta, datetime
from typing import Any, Mapping

from homeassistant.components.sensor import (SensorDeviceClass, SensorStateClass, SensorEntity)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (PERCENTAGE, POWER_WATT, TEMP_CELSIUS,
                                 UnitOfElectricPotential, UnitOfElectricCurrent, UnitOfTime)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval

from . import DOMAIN, OPTS_REFRESH_PERIOD_SEC, ATTR_STATUS_SN, ATTR_STATUS_UPDATES
from .entities import BaseSensorEntity, EcoFlowAbstractEntity
from .mqtt.ecoflow_mqtt import EcoflowMQTTClient


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowMQTTClient = hass.data[DOMAIN][entry.entry_id]

    from .devices.registry import devices
    async_add_entities(devices[client.device_type].sensors(client))


class CyclesSensorEntity(BaseSensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:battery-heart-variant"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING


class FanSensorEntity(BaseSensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:fan"


class LevelSensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT


class RemainSensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_value = 0

    def _update_value(self, val: Any) -> Any:
        ival = int(val)
        if ival < 0 or ival > 5000:
            ival = 0

        return super()._update_value(ival)


class TempSensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = TEMP_CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_value = -1


class VoltSensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfElectricPotential.MILLIVOLT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_value = 0


class AmpSensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.MILLIAMPERE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_value = 0


class WattsSensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = POWER_WATT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_value = 0


class InWattsSensorEntity(WattsSensorEntity):
    _attr_icon = "mdi:transmission-tower-import"


class InWattsSolarSensorEntity(InWattsSensorEntity):
    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class OutWattsSensorEntity(WattsSensorEntity):
    _attr_icon = "mdi:transmission-tower-export"


class InVoltSensorEntity(VoltSensorEntity):
    _attr_icon = "mdi:transmission-tower-import"


class InAmpSensorEntity(AmpSensorEntity):
    _attr_icon = "mdi:transmission-tower-import"


class QuotasStatusSensorEntity(SensorEntity, EcoFlowAbstractEntity):
    # _attr_icon = "mdi:transmission-tower-import"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, client: EcoflowMQTTClient):
        super().__init__(client, "Status", "status")
        self._data_refresh_sec = int(client.config_entry.options[OPTS_REFRESH_PERIOD_SEC])
        self.__online = -1
        self.__attrs = dict[str, Any]()
        self.__attrs[ATTR_STATUS_UPDATES] = 0

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        d = self._client.data.get_reply_observable().subscribe(self.__updated)
        self.async_on_remove(d.dispose)

        self.__get_latest_quotas()

        self.async_on_remove(
            async_track_time_interval(self.hass, self.__check_latest_quotas, timedelta(seconds=self._data_refresh_sec)))

    def __check_latest_quotas(self, now: datetime):
        update_delta_sec = (now - self._client.data.last_params_broadcast_time()).total_seconds()

        if (self.__online == 1 and update_delta_sec > self._data_refresh_sec * 3) or (
                self.__online != 1 and update_delta_sec < self._data_refresh_sec):
            self.__get_latest_quotas()

    def __get_latest_quotas(self):
        self.send_get_message({"version": "1.1", "moduleType": 0, "operateType": "latestQuotas", "params": {}})

    def __updated(self, data: list[dict[str, Any]]):
        d = data[0]
        if d["operateType"] == "latestQuotas":
            self.__online = d["data"]["online"]

            self.__attrs[ATTR_STATUS_UPDATES] = self.__attrs[ATTR_STATUS_UPDATES] + 1

            if self.__online == 1:
                self.__attrs[ATTR_STATUS_SN] = d["data"]["sn"]
                self._attr_native_value = "online"

                #?? self._client.data.update_data(d["data"]["quotaMap"])
            else:
                self._attr_native_value = "offline"

            self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return self.__attrs
