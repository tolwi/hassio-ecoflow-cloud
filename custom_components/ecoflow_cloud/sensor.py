import logging
import math
import struct
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
from homeassistant.util import dt

from . import DOMAIN, ATTR_STATUS_SN, ATTR_STATUS_DATA_LAST_UPDATE, ATTR_STATUS_LAST_UPDATE, ATTR_STATUS_RECONNECTS, \
    ATTR_STATUS_PHASE, ATTR_MQTT_CONNECTED
from .api import EcoflowApiClient
from .devices import BaseDevice
from .entities import BaseSensorEntity, EcoFlowAbstractEntity, EcoFlowDictEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowApiClient = hass.data[DOMAIN][entry.entry_id]
    for (sn, device) in client.devices.items():
        async_add_entities(device.sensors(client))


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

class BeSensorEntity(BaseSensorEntity):
    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(struct.unpack('<I', struct.pack('>I', val))[0]))

class BeMilliVoltSensorEntity(BeSensorEntity):
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfElectricPotential.MILLIVOLT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_value = 0

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

    def __init__(self, client: EcoflowApiClient,  device: BaseDevice, check_interval_sec=30):
        super().__init__(client, device, "Status", "status")
        self._online = -1
        self._last_update = dt.utcnow().replace(year=2000, month=1, day=1, hour=0, minute=0, second=0)
        self._attrs = OrderedDict[str, Any]()
        self._attrs[ATTR_STATUS_SN] = self._device.device_info.sn
        self._attrs[ATTR_STATUS_DATA_LAST_UPDATE] = None
        self._attrs[ATTR_MQTT_CONNECTED] = None
        self._attrs[ATTR_STATUS_LAST_UPDATE] = None
        self.__check_interval_sec = max(check_interval_sec, self._device.data.update_period_sec)

    async def async_added_to_hass(self):
        get_reply_d = self._device.data.status_observable().subscribe(self._status_update_consumer)
        self.async_on_remove(get_reply_d.dispose)

        params_d = self._device.data.params_observable().subscribe(self._params_update_consumer)
        self.async_on_remove(params_d.dispose)

        self.async_on_remove(
            async_track_time_interval(self.hass, self.__check_status, timedelta(seconds=self.__check_interval_sec)))

        await super().async_added_to_hass()

    def __check_status(self, now: datetime) -> None:
        data_outdated_sec_f = (dt.utcnow() - self._last_update).total_seconds()
        if self._actualize_status(int(data_outdated_sec_f), self.__check_interval_sec):
            self.schedule_update_ha_state()

    def _actualize_status(self, data_outdated_sec: int, check_interval_sec: int) -> bool:
        changed = False
        if self._online != 0 and data_outdated_sec > check_interval_sec:
            self._online = 0
            self._attr_native_value = "assume_offline"
            self._attrs[ATTR_MQTT_CONNECTED] = self._client.mqtt_client.is_connected()
            changed = True
        elif self._online != 1 and 0 < data_outdated_sec <= check_interval_sec:
            self._online = 1
            self._attr_native_value = "online"
            self._attrs[ATTR_MQTT_CONNECTED] = self._client.mqtt_client.is_connected()
            changed = True
        # _LOGGER.info("....... %s: _actualize_status (%s, %s) --- %s", self._device.device_info.sn, str(data_outdated_sec),
        #              str(check_interval_sec), self._attr_native_value)
        return changed

    def _status_update_consumer(self, data: dict[str, Any]):
        self._attrs[ATTR_STATUS_LAST_UPDATE] = self.__timestamp_or_now(data)
        self._attrs[ATTR_MQTT_CONNECTED] = self._client.mqtt_client.is_connected()
        if dict["status"] == 1:
            self._online = 1
            self._attr_native_value = "online"
        else:
            self._online = 0
            self._attr_native_value = "offline"

        self._last_update = max(self._attrs[ATTR_STATUS_LAST_UPDATE], self._last_update)
        self.schedule_update_ha_state()

    def _params_update_consumer(self, data: dict[str, Any]):
        self._attrs[ATTR_STATUS_DATA_LAST_UPDATE] = self.__timestamp_or_now(data)
        self._attrs[ATTR_MQTT_CONNECTED] = self._client.mqtt_client.is_connected()
        self._last_update = max(self._attrs[ATTR_STATUS_DATA_LAST_UPDATE], self._last_update)
        self._actualize_status(0, self.__check_interval_sec)
        self.schedule_update_ha_state()

    def __timestamp_or_now(self, data: dict[str, Any]):
        res = dt.utcnow()
        if "timestamp" in data:
            res = dt.utc_from_timestamp(int(data["timestamp"]) / 1000)
        return res

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return self._attrs


class ReconnectStatusSensorEntity(StatusSensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    CONNECT_PHASES = [3, 5, 7]

    def __init__(self, client: EcoflowApiClient, check_interval_sec=30):
        super().__init__(client, check_interval_sec)
        self._attrs[ATTR_STATUS_PHASE] = 0
        self._attrs[ATTR_STATUS_RECONNECTS] = 0

    def _actualize_status(self, data_outdated_sec: int, check_interval_sec: int) -> bool:
        phase = math.ceil(data_outdated_sec / check_interval_sec)
        self._attrs[ATTR_STATUS_PHASE] = phase
        time_to_reconnect = phase in self.CONNECT_PHASES

        if self._online == 1 and time_to_reconnect:
            self._attrs[ATTR_STATUS_RECONNECTS] = self._attrs[ATTR_STATUS_RECONNECTS] + 1
            self._client.mqtt_client.reconnect()
            return True
        else:
            return super()._actualize_status(data_outdated_sec, check_interval_sec)

