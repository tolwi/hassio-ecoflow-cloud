import math
import logging
from datetime import timedelta, datetime
from typing import Any, Mapping, OrderedDict

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.components.sensor import (SensorDeviceClass, SensorStateClass, SensorEntity)
from homeassistant.config_entries import ConfigEntry

from homeassistant.const import (PERCENTAGE,
                                 UnitOfElectricCurrent, UnitOfElectricPotential, UnitOfEnergy, UnitOfFrequency,
                                 UnitOfPower, UnitOfTemperature, UnitOfTime)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import utcnow
from homeassistant.util.dt import UTC

from . import DOMAIN, ATTR_STATUS_SN, ATTR_STATUS_DATA_LAST_UPDATE, ATTR_STATUS_UPDATES, \
    ATTR_STATUS_LAST_UPDATE, ATTR_STATUS_RECONNECTS, ATTR_STATUS_PHASE
from .entities import BaseSensorEntity, EcoFlowAbstractEntity, EcoFlowDictEntity
from .mqtt.ecoflow_mqtt import EcoflowMQTTClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowMQTTClient = hass.data[DOMAIN][entry.entry_id]

    from .devices.registry import devices
    async_add_entities(devices[client.device_type].sensors(client))


class MiscBinarySensorEntity(BinarySensorEntity, EcoFlowDictEntity):

    def _update_value(self, val: Any) -> bool:
        self._attr_is_on = bool(val)
        return True
    

class ChargingStateSensorEntity(BaseSensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:battery-charging"
    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING

    def _update_value(self, val: Any) -> bool:
        if val == 0:
            return super()._update_value("unused")
        elif val == 1:
            return super()._update_value("charging")
        elif val == 2:
            return super()._update_value("discharging")
        else:
            return False


class CyclesSensorEntity(BaseSensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:battery-heart-variant"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING


class FanSensorEntity(BaseSensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:fan"


class MiscSensorEntity(BaseSensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC


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


class SecondsRemainSensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
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
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_value = -1


class DecicelsiusSensorEntity(TempSensorEntity):
    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)

class MilliCelsiusSensorEntity(TempSensorEntity):
    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 100)

class VoltSensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_value = 0


class MilliVoltSensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfElectricPotential.MILLIVOLT
    _attr_suggested_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_value = 3


class InMilliVoltSensorEntity(MilliVoltSensorEntity):
    _attr_icon = "mdi:transmission-tower-import"
    _attr_suggested_display_precision = 0


class OutMilliVoltSensorEntity(MilliVoltSensorEntity):
    _attr_icon = "mdi:transmission-tower-export"
    _attr_suggested_display_precision = 0


class DecivoltSensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_value = 0

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class CentivoltSensorEntity(DecivoltSensorEntity):
    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class AmpSensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.MILLIAMPERE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_value = 0


class DeciampSensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_value = 0

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class WattsSensorEntity(BaseSensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_value = 0


class EnergySensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def _update_value(self, val: Any) -> bool:
        ival = int(val)
        if ival > 0:
            return super()._update_value(ival)
        else:
            return False


class CapacitySensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_native_unit_of_measurement = "mAh"
    _attr_state_class = SensorStateClass.MEASUREMENT


class DeciwattsSensorEntity(WattsSensorEntity):
    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class InWattsSensorEntity(WattsSensorEntity):
    _attr_icon = "mdi:transmission-tower-import"


class InWattsSolarSensorEntity(InWattsSensorEntity):
    _attr_icon = "mdi:solar-power"

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class OutWattsSensorEntity(WattsSensorEntity):
    _attr_icon = "mdi:transmission-tower-export"


class OutWattsDcSensorEntity(WattsSensorEntity):
    _attr_icon = "mdi:transmission-tower-export"

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class InVoltSensorEntity(VoltSensorEntity):
    _attr_icon = "mdi:transmission-tower-import"

class InVoltSolarSensorEntity(VoltSensorEntity):
    _attr_icon = "mdi:solar-power"

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)

class OutVoltDcSensorEntity(VoltSensorEntity):
    _attr_icon = "mdi:transmission-tower-export"
    
    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)      

class InAmpSensorEntity(AmpSensorEntity):
    _attr_icon = "mdi:transmission-tower-import"

class InAmpSolarSensorEntity(AmpSensorEntity):
    _attr_icon = "mdi:solar-power"

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) * 10)

class InEnergySensorEntity(EnergySensorEntity):
    _attr_icon = "mdi:transmission-tower-import"


class OutEnergySensorEntity(EnergySensorEntity):
    _attr_icon = "mdi:transmission-tower-export"


class FrequencySensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.FREQUENCY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfFrequency.HERTZ
    _attr_state_class = SensorStateClass.MEASUREMENT


class DecihertzSensorEntity(FrequencySensorEntity):
    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class StatusSensorEntity(SensorEntity, EcoFlowAbstractEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    DEADLINE_PHASE = 10
    CHECK_PHASES = [2, 4, 6]
    CONNECT_PHASES = [3, 5, 7]

    def __init__(self, client: EcoflowMQTTClient, check_interval_sec=30):
        super().__init__(client, "Status", "status")
        self._online = 0
        self.__check_interval_sec = check_interval_sec
        self._attrs = OrderedDict[str, Any]()
        self._attrs[ATTR_STATUS_SN] = client.device_sn
        self._attrs[ATTR_STATUS_DATA_LAST_UPDATE] = self._client.data.params_time()
        self._attrs[ATTR_STATUS_UPDATES] = 0
        self._attrs[ATTR_STATUS_LAST_UPDATE] = None
        self._attrs[ATTR_STATUS_RECONNECTS] = 0
        self._attrs[ATTR_STATUS_PHASE] = 0

    async def async_added_to_hass(self):
        await super().async_added_to_hass()

        params_d = self._client.data.params_observable().subscribe(self.__params_update)
        self.async_on_remove(params_d.dispose)

        self.async_on_remove(
            async_track_time_interval(self.hass, self.__check_status, timedelta(seconds=self.__check_interval_sec)))

        self._update_status((utcnow() - self._client.data.params_time()).total_seconds())

    def __check_status(self, now: datetime):
        data_outdated_sec = (now - self._client.data.params_time()).total_seconds()
        phase = math.ceil(data_outdated_sec / self.__check_interval_sec)
        self._attrs[ATTR_STATUS_PHASE] = phase
        time_to_reconnect = phase in self.CONNECT_PHASES
        time_to_check_status = phase in self.CHECK_PHASES

        if self._online == 1:
            if time_to_check_status or phase >= self.DEADLINE_PHASE:
                # online and outdated - refresh status to detect if device went offline
                self._update_status(data_outdated_sec)
            elif time_to_reconnect:
                # online, updated and outdated - reconnect
                self._attrs[ATTR_STATUS_RECONNECTS] = self._attrs[ATTR_STATUS_RECONNECTS] + 1
                self._client.reconnect()
                self.schedule_update_ha_state()

        elif not self._client.is_connected():  # validate connection even for offline device
            self._attrs[ATTR_STATUS_RECONNECTS] = self._attrs[ATTR_STATUS_RECONNECTS] + 1
            self._client.reconnect()
            self.schedule_update_ha_state()

    def __params_update(self, data: dict[str, Any]):
        self._attrs[ATTR_STATUS_DATA_LAST_UPDATE] = self._client.data.params_time()
        if self._online == 0:
            self._update_status(0)

        self.schedule_update_ha_state()

    def _update_status(self, data_outdated_sec):
        if data_outdated_sec > self.__check_interval_sec * self.DEADLINE_PHASE:
            self._online = 0
            self._attr_native_value = "assume_offline"
        else:
            self._online = 1
            self._attr_native_value = "assume_online"

        self._attrs[ATTR_STATUS_LAST_UPDATE] = utcnow()
        self._attrs[ATTR_STATUS_UPDATES] = self._attrs[ATTR_STATUS_UPDATES] + 1
        self.schedule_update_ha_state()

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return self._attrs


class QuotasStatusSensorEntity(StatusSensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, client: EcoflowMQTTClient):
        super().__init__(client)

    async def async_added_to_hass(self):

        get_reply_d = self._client.data.get_reply_observable().subscribe(self.__get_reply_update)
        self.async_on_remove(get_reply_d.dispose)

        await super().async_added_to_hass()

    def _update_status(self, update_delta_sec):
        if self._client.is_connected():
            self._attrs[ATTR_STATUS_UPDATES] = self._attrs[ATTR_STATUS_UPDATES] + 1
            self.send_get_message({"version": "1.1", "moduleType": 0, "operateType": "latestQuotas", "params": {}})
        else:
            super()._update_status(update_delta_sec)

    def __get_reply_update(self, data: list[dict[str, Any]]):
        d = data[0]
        if d["operateType"] == "latestQuotas":
            self._online = d["data"]["online"]
            self._attrs[ATTR_STATUS_LAST_UPDATE] = utcnow()

            if self._online == 1:
                self._attrs[ATTR_STATUS_SN] = d["data"]["sn"]
                self._attr_native_value = "online"

                # ?? self._client.data.update_data(d["data"]["quotaMap"])
            else:
                self._attr_native_value = "offline"

            self.schedule_update_ha_state()
