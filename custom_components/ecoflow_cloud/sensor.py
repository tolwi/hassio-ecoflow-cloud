import enum
import logging
import struct
from datetime import timedelta
from typing import Any, Mapping, OrderedDict, override

from homeassistant.components.binary_sensor import ( # pyright: ignore[reportMissingImports]
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.components.sensor import ( # pyright: ignore[reportMissingImports]
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.components.integration.sensor import IntegrationSensor # pyright: ignore[reportMissingImports]
from homeassistant.config_entries import ConfigEntry # pyright: ignore[reportMissingImports]
from homeassistant.const import ( # pyright: ignore[reportMissingImports]
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant # pyright: ignore[reportMissingImports]
from homeassistant.helpers.entity import EntityCategory # pyright: ignore[reportMissingImports]
from homeassistant.helpers.entity_platform import AddEntitiesCallback # pyright: ignore[reportMissingImports]
from homeassistant.util import dt # pyright: ignore[reportMissingImports]

from . import (
    ATTR_MQTT_CONNECTED,
    ATTR_QUOTA_REQUESTS,
    ATTR_STATUS_DATA_LAST_UPDATE,
    ATTR_STATUS_PHASE,
    ATTR_STATUS_RECONNECTS,
    ATTR_STATUS_SN,
    ECOFLOW_DOMAIN,
)
from .api import EcoflowApiClient
from .devices import BaseDevice, const
from .entities import (
    BaseSensorEntity,
    EcoFlowAbstractEntity,
    EcoFlowDictEntity,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    client: EcoflowApiClient = hass.data[ECOFLOW_DOMAIN][entry.entry_id]
    for sn, device in client.devices.items():
        sensors = device.sensors(client)
        # Add regular sensors
        async_add_entities(sensors)

        # Add IntegralEnergySensors
        integralSensors = filter(
            lambda s: isinstance(s, WattsSensorEntity) and s.energy_enabled(), sensors
        )
        async_add_entities(map(lambda s: s.energy_sensor(), integralSensors))


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


class CelsiusSensorEntity(TempSensorEntity):
    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val))


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
    _attr_suggested_display_precision = 1


class MilliVoltSensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfElectricPotential.MILLIVOLT
    _attr_suggested_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_value = 3


class BeSensorEntity(BaseSensorEntity):
    def _update_value(self, val: Any) -> bool:
        return super()._update_value(
            int(struct.unpack("<I", struct.pack(">I", val))[0])
        )


class BeMilliVoltSensorEntity(BeSensorEntity):
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfElectricPotential.MILLIVOLT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_value = 0


class DeciMilliVoltSensorEntity(MilliVoltSensorEntity):
    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


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
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_value = 0


class MilliampSensorEntity(BaseSensorEntity):
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
    _attr_suggested_display_precision = 0

    def __init__(
        self, client, device, mqtt_key, title, enabled=True, auto_enable=False, diagnostic=None
    ):
        super().__init__(client, device, mqtt_key, title, enabled, auto_enable, diagnostic)
        self._energy_enabled = False
        self._energy_enabled_default = True

    def with_energy(self, enabled_default: bool = True):
        self._energy_enabled = True
        self._energy_enabled_default = enabled_default
        return self

    def energy_enabled(self):
        return self._energy_enabled

    def energy_sensor(self):
        if not self._energy_enabled:
            return None
        return IntegralEnergySensorEntity(self, self._energy_enabled_default)


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
    _attr_native_unit_of_measurement = "mAh"
    _attr_state_class = SensorStateClass.MEASUREMENT


class CumulativeCapacitySensorEntity(CapacitySensorEntity):
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def _update_value(self, val: Any) -> bool:
        ival = int(val)
        if ival > 0:
            return super()._update_value(ival)
        else:
            return False


class DeciwattsSensorEntity(WattsSensorEntity):
    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class InWattsSensorEntity(WattsSensorEntity):
    _attr_icon = "mdi:transmission-tower-import"


class InWattsSolarSensorEntity(InWattsSensorEntity):
    _attr_icon = "mdi:solar-power"

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class InRawWattsSolarSensorEntity(InWattsSensorEntity):
    _attr_icon = "mdi:solar-power"


class InRawTotalWattsSolarSensorEntity(InRawWattsSolarSensorEntity):
    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 1000)


class InRawWattsAltSensorEntity(InWattsSensorEntity):
    _attr_icon = "mdi:engine"


class OutWattsSensorEntity(WattsSensorEntity):
    _attr_icon = "mdi:transmission-tower-export"


class OutWattsDcSensorEntity(WattsSensorEntity):
    _attr_icon = "mdi:transmission-tower-export"

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class InVoltSensorEntity(VoltSensorEntity):
    _attr_icon = "mdi:transmission-tower-import"


class OutVoltSensorEntity(VoltSensorEntity):
    _attr_icon = "mdi:transmission-tower-export"


class InVoltSolarSensorEntity(VoltSensorEntity):
    _attr_icon = "mdi:solar-power"

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class OutVoltDcSensorEntity(VoltSensorEntity):
    _attr_icon = "mdi:transmission-tower-export"

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class OutAmpSensorEntity(AmpSensorEntity):
    _attr_icon = "mdi:transmission-tower-export"


class InAmpSensorEntity(AmpSensorEntity):
    _attr_icon = "mdi:transmission-tower-import"
    _attr_suggested_display_precision = 2


class OutMilliampSensorEntity(MilliampSensorEntity):
    _attr_icon = "mdi:transmission-tower-export"


class InMilliampSensorEntity(MilliampSensorEntity):
    _attr_icon = "mdi:transmission-tower-import"


class InMilliampSolarSensorEntity(MilliampSensorEntity):
    _attr_icon = "mdi:solar-power"

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) * 10)


class InEnergySensorEntity(EnergySensorEntity):
    _attr_icon = "mdi:transmission-tower-import"


class OutEnergySensorEntity(EnergySensorEntity):
    _attr_icon = "mdi:transmission-tower-export"


class InEnergySolarSensorEntity(InEnergySensorEntity):
    _attr_icon = "mdi:solar-power"


class _ResettingMixin(EnergySensorEntity):
    @override
    def _update_value(self, val: Any) -> bool:
        # Skip the "if val == 0: False" logic
        return super(EnergySensorEntity, self)._update_value(val)


class ResettingInEnergySensorEntity(_ResettingMixin, InEnergySensorEntity):
    pass


class ResettingInEnergySolarSensorEntity(_ResettingMixin, InEnergySolarSensorEntity):
    pass


class ResettingOutEnergySensorEntity(_ResettingMixin, OutEnergySensorEntity):
    pass


class FrequencySensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.FREQUENCY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfFrequency.HERTZ
    _attr_state_class = SensorStateClass.MEASUREMENT


class DecihertzSensorEntity(FrequencySensorEntity):
    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class _OnlineStatus(enum.Enum):
    UNKNOWN = enum.auto()
    ASSUME_OFFLINE = enum.auto()
    OFFLINE = enum.auto()
    ONLINE = enum.auto()


class StatusSensorEntity(SensorEntity, EcoFlowAbstractEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    offline_barrier_sec: int = 120  # 2 minutes

    def __init__(
        self,
        client: EcoflowApiClient,
        device: BaseDevice,
        title: str = "Status",
        key: str = "status",
    ):
        super().__init__(client, device, title, key)
        self._attr_force_update = False

        self._online = _OnlineStatus.UNKNOWN
        self._last_update = dt.utcnow().replace(
            year=2000, month=1, day=1, hour=0, minute=0, second=0
        )
        self._skip_count = 0
        self._offline_skip_count = int(
            self.offline_barrier_sec / self.coordinator.update_interval.seconds
        )
        self._attrs = OrderedDict[str, Any]()
        self._attrs[ATTR_STATUS_SN] = self._device.device_info.sn
        self._attrs[ATTR_STATUS_DATA_LAST_UPDATE] = None
        self._attrs[ATTR_MQTT_CONNECTED] = None

    def _handle_coordinator_update(self) -> None:
        changed = False
        update_time = self.coordinator.data.data_holder.last_received_time()
        if self._last_update < update_time:
            self._last_update = max(update_time, self._last_update)
            self._skip_count = 0
            self._actualize_attributes()
            changed = True
        else:
            self._skip_count += 1

        changed = self._actualize_status() or changed

        if changed:
            self.schedule_update_ha_state()

    def _actualize_status(self) -> bool:
        changed = False
        if self._skip_count == 0:
            status = self.coordinator.data.data_holder.status.get("status")
            if status == 0 and self._online != _OnlineStatus.OFFLINE:
                self._online = _OnlineStatus.OFFLINE
                self._attr_native_value = "offline"
                self._actualize_attributes()
                changed = True
            elif status == 1 and self._online != _OnlineStatus.ONLINE:
                self._online = _OnlineStatus.ONLINE
                self._attr_native_value = "online"
                self._actualize_attributes()
                changed = True
        elif (
            self._online not in {_OnlineStatus.OFFLINE, _OnlineStatus.ASSUME_OFFLINE}
            and self._skip_count >= self._offline_skip_count
        ):
            self._online = _OnlineStatus.ASSUME_OFFLINE
            self._attr_native_value = "assume_offline"
            self._actualize_attributes()
            changed = True
        return changed

    def _actualize_attributes(self):
        if self._online in {_OnlineStatus.OFFLINE, _OnlineStatus.ONLINE}:
            self._attrs[ATTR_STATUS_DATA_LAST_UPDATE] = (
                f"< {self.offline_barrier_sec} sec"
            )
        else:
            self._attrs[ATTR_STATUS_DATA_LAST_UPDATE] = self._last_update

        self._attrs[ATTR_MQTT_CONNECTED] = self._client.mqtt_client.is_connected()

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return self._attrs


class QuotaStatusSensorEntity(StatusSensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        client: EcoflowApiClient,
        device: BaseDevice,
        title: str = "Status",
        key: str = "status",
    ):
        super().__init__(client, device, title, key)
        self._attrs[ATTR_QUOTA_REQUESTS] = 0

    def _actualize_status(self) -> bool:
        changed = False
        if (
            self._online != _OnlineStatus.ASSUME_OFFLINE
            and self._skip_count >= self._offline_skip_count * 2
        ):
            self._online = _OnlineStatus.ASSUME_OFFLINE
            self._attr_native_value = "assume_offline"
            self._attrs[ATTR_MQTT_CONNECTED] = self._client.mqtt_client.is_connected()
            changed = True
        elif (
            self._online != _OnlineStatus.ASSUME_OFFLINE
            and self._skip_count >= self._offline_skip_count
        ):
            self.hass.async_create_background_task(
                self._client.quota_all(self._device.device_info.sn), "get quota"
            )
            self._attrs[ATTR_QUOTA_REQUESTS] = self._attrs[ATTR_QUOTA_REQUESTS] + 1
            changed = True
        elif self._online != _OnlineStatus.ONLINE and self._skip_count == 0:
            self._online = _OnlineStatus.ONLINE
            self._attr_native_value = "online"
            self._attrs[ATTR_MQTT_CONNECTED] = self._client.mqtt_client.is_connected()
            changed = True
        return changed


class QuotaScheduledStatusSensorEntity(QuotaStatusSensorEntity):
    def __init__(
        self, client: EcoflowApiClient, device: BaseDevice, reload_delay: int = 3600
    ):
        super().__init__(client, device, "Status (Scheduled)", "status.scheduled")
        self.offline_barrier_sec: int = reload_delay
        self._quota_last_update = dt.utcnow()

    def _actualize_status(self) -> bool:
        changed = super()._actualize_status()
        quota_diff = dt.as_timestamp(dt.utcnow()) - dt.as_timestamp(
            self._quota_last_update
        )
        # if delay passed, reload quota
        if quota_diff > (self.offline_barrier_sec):
            self._attr_native_value = "updating"
            self._quota_last_update = dt.utcnow()
            self.hass.async_create_background_task(
                self._client.quota_all(self._device.device_info.sn), "get quota"
            )
            self._attrs[ATTR_QUOTA_REQUESTS] = self._attrs[ATTR_QUOTA_REQUESTS] + 1
            _LOGGER.debug("Reload quota for device %s", self._device.device_info.sn)
            changed = True
        else:
            if self._attr_native_value == "updating":
                changed = True
            self._attr_native_value = "online"
        return changed


class ReconnectStatusSensorEntity(StatusSensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    CONNECT_PHASES = [3, 5, 7]

    def __init__(self, client: EcoflowApiClient, device: BaseDevice):
        super().__init__(client, device)
        self._attrs[ATTR_STATUS_PHASE] = 0
        self._attrs[ATTR_STATUS_RECONNECTS] = 0

    def _actualize_status(self) -> bool:
        time_to_reconnect = self._skip_count in self.CONNECT_PHASES

        if self._online == _OnlineStatus.ONLINE and time_to_reconnect:
            self._attrs[ATTR_STATUS_RECONNECTS] = (
                self._attrs[ATTR_STATUS_RECONNECTS] + 1
            )
            self._client.mqtt_client.reconnect()
            return True
        else:
            return super()._actualize_status()


class IntegralEnergySensorEntity(IntegrationSensor):
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_entity_registry_visible_default = False

    def __init__(self, base: WattsSensorEntity, enabled_default: bool = True):
        super().__init__(
            base.coordinator.hass,
            integration_method="left",
            name=f"{base._device.device_info.name} {base._attr_name.replace(f'{const.POWER}', f' {const.ENERGY}')}",
            round_digits=4,
            source_entity=base.entity_id,
            unique_id=f"{base._attr_unique_id}_energy",
            unit_prefix="k",
            unit_time="h",
            max_sub_interval=timedelta(seconds=60),
        )
        self.device_info = base.device_info
        self._attr_entity_registry_enabled_default = enabled_default and base.enabled_default