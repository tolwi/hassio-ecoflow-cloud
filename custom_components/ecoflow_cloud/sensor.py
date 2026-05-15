import logging
import re
import struct
from datetime import datetime, timedelta
from typing import Any, Mapping, OrderedDict, override

from homeassistant.components.integration.sensor import IntegrationSensor  # pyright: ignore[reportMissingImports]
from homeassistant.components.sensor import (  # pyright: ignore[reportMissingImports]
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry  # pyright: ignore[reportMissingImports]
from homeassistant.const import (  # pyright: ignore[reportMissingImports]
    PERCENTAGE,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import (  # pyright: ignore[reportMissingImports]
    Event,
    EventStateChangedData,
    HomeAssistant,
    callback,
)
from homeassistant.helpers.entity import EntityCategory  # pyright: ignore[reportMissingImports]
from homeassistant.helpers.entity_platform import AddEntitiesCallback  # pyright: ignore[reportMissingImports]
from homeassistant.helpers.event import async_track_state_change_event  # pyright: ignore[reportMissingImports]
from homeassistant.util import dt  # pyright: ignore[reportMissingImports]

from . import (
    ATTR_DATA_UPDATES,
    ATTR_MQTT_CONNECTED,
    ATTR_QUOTA_REQUESTS,
    ATTR_STATUS_RECONNECTS,
    ATTR_STATUS_DATA_LAST_UPDATE,
    ATTR_STATUS_LAST_UPDATE,
    ATTR_STATUS_SN,
    ATTR_STATUS_UPDATES,
    ECOFLOW_DOMAIN,
)
from .api import EcoflowApiClient
from .devices import BaseDevice, const
from .entities import (
    BaseSensorEntity,
    EcoFlowAbstractDataEntity,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowApiClient = hass.data[ECOFLOW_DOMAIN][entry.entry_id]
    for sn, device in client.devices.items():
        sensors = device.sensors(client)
        # Add regular sensors
        async_add_entities(sensors)

        # Add integral energy sensors for power sensors that have it enabled
        integral_sensors = filter(lambda s: isinstance(s, WattsSensorEntity) and s.energy_enabled(), sensors)
        async_add_entities([s.energy_sensor() for s in integral_sensors])

        # Add power difference sensors for new HA Energy panel "now" tab
        total_in_power = next(
            filter(
                lambda s: isinstance(s, InWattsSensorEntity) and s.title() == const.TOTAL_IN_POWER,
                sensors,
            ),
            None,
        )
        total_out_power = next(
            filter(
                lambda s: isinstance(s, OutWattsSensorEntity) and s.title() == const.TOTAL_OUT_POWER,
                sensors,
            ),
            None,
        )
        if total_in_power and total_out_power:
            async_add_entities(
                [
                    WattsDifferenceSensorEntity(
                        client,
                        device,
                        const.POWER_DIFFERENCE,
                        total_in_power,
                        total_out_power,
                    )
                ]
            )


class ChargingStateSensorEntity(BaseSensorEntity):
    _attr_default_value: Any = 0
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:battery-charging"

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
    _attr_default_value: Any = 0
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
    _attr_default_value: Any = 0

    def _update_value(self, val: Any) -> Any:
        ival = int(val)
        if ival < 0 or ival > 5000:
            ival = 0

        return super()._update_value(ival)


class SecondsRemainSensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_default_value: Any = 0

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
    _attr_native_value = 0


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
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_default_value: Any = 0
    _attr_suggested_display_precision = 1


class MilliVoltSensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = UnitOfElectricPotential.MILLIVOLT
    _attr_suggested_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_default_value: Any = 3


class BeSensorEntity(BaseSensorEntity):
    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(struct.unpack("<I", struct.pack(">I", val))[0]))


class BeMilliVoltSensorEntity(BeSensorEntity):
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = UnitOfElectricPotential.MILLIVOLT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_default_value: Any = 0


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
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_default_value: Any = 0

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class CentivoltSensorEntity(DecivoltSensorEntity):
    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class AmpSensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_default_value: Any = 0


class MilliampSensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.MILLIAMPERE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_default_value: Any = 0


class DeciampSensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_default_value: Any = 0

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class WattsSensorEntity(BaseSensorEntity):
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_default_value: Any = 0
    _attr_suggested_display_precision = 0

    def __init__(
        self,
        client,
        device,
        mqtt_key,
        title,
        enabled=True,
        auto_enable=False,
        diagnostic=None,
    ):
        super().__init__(
            client,
            device,
            mqtt_key,
            title,
            enabled,
            auto_enable,
            diagnostic,
        )
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


class InRawVoltSolarSensorEntity(VoltSensorEntity):
    _attr_icon = "mdi:solar-power"
    _attr_suggested_display_precision = 0


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

class InRawAmpSolarSensorEntity(AmpSensorEntity):
    _attr_icon = "mdi:solar-power"
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
    _attr_default_value: Any = 0
    _attr_device_class = SensorDeviceClass.FREQUENCY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfFrequency.HERTZ
    _attr_state_class = SensorStateClass.MEASUREMENT


class DecihertzSensorEntity(FrequencySensorEntity):
    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class StatusSensorEntity(SensorEntity, EcoFlowAbstractDataEntity):  # type: ignore[misc]
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        client: EcoflowApiClient,
        device: BaseDevice,
        title: str = "Status",
        key: str = "status",
        poll_when_silent: bool = False,
        scheduled_refresh_sec: int | None = None,
    ):
        from .devices.status_tracker import OnlineStatus

        super().__init__(client, device, title, key)
        self._attr_force_update = False
        self._tracker = device.status_tracker
        self._prev_status: OnlineStatus | None = None
        self._poll_when_silent = poll_when_silent
        self._scheduled_refresh_sec = scheduled_refresh_sec
        self._last_poll = dt.utcnow().replace(year=2000, month=1, day=1, hour=0, minute=0, second=0)
        self._last_scheduled = dt.utcnow()
        self._poll_count = 0

        self._attrs = OrderedDict[str, Any]()
        self._attrs[ATTR_STATUS_SN] = self._device.device_info.sn
        self._attrs[ATTR_STATUS_DATA_LAST_UPDATE] = None
        self._attrs[ATTR_MQTT_CONNECTED] = None
        self._attrs[ATTR_STATUS_RECONNECTS] = 0
        if poll_when_silent or scheduled_refresh_sec is not None:
            self._attrs[ATTR_QUOTA_REQUESTS] = 0

    def _handle_coordinator_update(self) -> None:
        from .devices.status_tracker import OnlineStatus

        status = self._tracker.status
        changed = status != self._prev_status

        if self._schedule_mqtt_reconnect():
            changed = True

        # Active polling when device goes silent
        if self._poll_when_silent and status == OnlineStatus.ASSUME_OFFLINE:
            if (dt.utcnow() - self._last_poll).total_seconds() >= self._tracker.assume_offline_sec:
                self.hass.async_create_background_task(
                    self._client.quota_all(self._device.device_info.sn),
                    f"get quota {self._device.device_info.sn}",
                )
                self._last_poll = dt.utcnow()
                self._poll_count += 1
                self._attrs[ATTR_QUOTA_REQUESTS] = self._poll_count
                changed = True

        # Scheduled periodic refresh regardless of status
        if self._scheduled_refresh_sec is not None:
            if (dt.utcnow() - self._last_scheduled).total_seconds() > self._scheduled_refresh_sec:
                self.hass.async_create_background_task(
                    self._client.quota_all(self._device.device_info.sn), "get quota"
                )
                self._last_scheduled = dt.utcnow()
                self._poll_count += 1
                self._attrs[ATTR_QUOTA_REQUESTS] = self._poll_count
                _LOGGER.debug("Reload quota for device %s", self._device.device_info.sn)
                changed = True

        if changed:
            self._prev_status = status
            if status.online is not None or self._device.device_data.options.verbose_status_mode:
                self._attr_native_value = status.label
                self._actualize_attributes()
                self.schedule_update_ha_state()

    def _schedule_mqtt_reconnect(self) -> bool:
        reconnect_count = self._client.schedule_mqtt_reconnect()
        if reconnect_count is None:
            return False

        self._attrs[ATTR_STATUS_RECONNECTS] = reconnect_count
        self.hass.async_create_background_task(
            self._async_reconnect_mqtt(),
            f"reconnect ecoflow mqtt {self._device.device_info.sn}",
        )
        return True

    async def _async_reconnect_mqtt(self) -> None:
        await self.hass.async_add_executor_job(self._client.mqtt_client.reconnect)

    def _format_age(self, timestamp: datetime | None) -> str | None:
        if timestamp is None:
            return None
        age = (dt.utcnow() - timestamp).total_seconds()
        if age < self._tracker.assume_offline_sec:
            return f"< {self._tracker.assume_offline_sec} sec"
        return str(timestamp)

    def _actualize_attributes(self):
        self._attrs[ATTR_STATUS_DATA_LAST_UPDATE] = self._format_age(self._tracker.last_data_time)
        self._attrs[ATTR_STATUS_LAST_UPDATE] = self._format_age(self._tracker._explicit_status_last_time)
        if self._device.device_data.options.verbose_status_mode:
            self._attrs[ATTR_STATUS_UPDATES] = self._tracker._explicit_status_count
            self._attrs[ATTR_DATA_UPDATES] = self._tracker._data_received_count
        self._attrs[ATTR_MQTT_CONNECTED] = self._client.mqtt_client.is_connected()
        self._attrs[ATTR_STATUS_RECONNECTS] = self._client.mqtt_reconnect_count

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return self._attrs


class QuotaStatusSensorEntity(StatusSensorEntity):
    """StatusSensorEntity that polls quota when device goes silent."""

    def __init__(
        self,
        client: EcoflowApiClient,
        device: BaseDevice,
        title: str = "Status",
        key: str = "status",
    ):
        super().__init__(client, device, title, key, poll_when_silent=True)


class QuotaScheduledStatusSensorEntity(QuotaStatusSensorEntity):
    """QuotaStatusSensorEntity with additional periodic scheduled refresh."""

    def __init__(
        self,
        client: EcoflowApiClient,
        device: BaseDevice,
        reload_delay: int = 3600,
        title: str = "Status (Scheduled)",
        key: str = "status.scheduled",
    ):
        super().__init__(client, device, title, key)
        self._scheduled_refresh_sec = reload_delay


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
            name=f"{base._device.device_info.name} {base.title().replace(f'{const.POWER}', f' {const.ENERGY}')}",
            round_digits=4,
            source_entity=base.entity_id,
            unique_id=f"{base._attr_unique_id}_energy",
            unit_prefix="k",
            unit_time=UnitOfTime.HOURS,
            max_sub_interval=timedelta(seconds=60),
        )
        self.device_info = base.device_info
        self._attr_entity_registry_enabled_default = enabled_default and base.enabled_default


class SolarPowerSensorEntity(WattsSensorEntity):
    _attr_entity_category = None
    _attr_suggested_display_precision = 1
    _attr_icon = "mdi:solar-power"


class SolarAmpSensorEntity(AmpSensorEntity):
    _attr_suggested_display_precision = 1
    _attr_icon = "mdi:current-dc"


class SystemPowerSensorEntity(WattsSensorEntity):
    _attr_entity_category = None
    _attr_suggested_display_precision = 1


# Code based on HA's native MinMaxSensor helper sensor for combining multiple sensors with math operations
class WattsDifferenceSensorEntity(SensorEntity, EcoFlowAbstractDataEntity):
    """Sensor to calculate power consumed as output minus input power for Energy panel."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_should_poll = False

    def __init__(
        self,
        client: EcoflowApiClient,
        device: BaseDevice,
        title: str,
        input: InWattsSensorEntity,
        output: OutWattsSensorEntity,
    ):
        super().__init__(client, device, title, re.sub(r"[^a-zA-Z0-9-]", "_", title.lower()))

        self._output_sensor = output
        self._input_sensor = input
        self._difference: float | None = None
        self._states: dict[str, float | str] = {}

    async def async_added_to_hass(self) -> None:
        """Handle added to Hass."""
        source_entity_ids = [
            self._input_sensor.entity_id,
            self._output_sensor.entity_id,
        ]
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                source_entity_ids,
                self._async_difference_sensor_state_listener,
            )
        )

        # Replay current state of source entities
        for entity_id in source_entity_ids:
            state = self.hass.states.get(entity_id)
            state_event: Event[EventStateChangedData] = Event(
                "", {"entity_id": entity_id, "new_state": state, "old_state": None}
            )
            self._async_difference_sensor_state_listener(state_event, update_state=False)

        self._calc_difference()

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        value: float | None = self._difference
        return value

    @callback
    def _async_difference_sensor_state_listener(
        self, event: Event[EventStateChangedData], update_state: bool = True
    ) -> None:
        """Handle the sensor state changes."""
        new_state = event.data["new_state"]
        entity = event.data["entity_id"]

        if (
            new_state is None
            or new_state.state is None
            or new_state.state
            in [
                STATE_UNKNOWN,
                STATE_UNAVAILABLE,
            ]
        ):
            self._states[entity] = STATE_UNKNOWN
            if not update_state:
                return

            self._calc_difference()
            self.async_write_ha_state()
            return

        try:
            self._states[entity] = float(new_state.state)
        except ValueError:
            _LOGGER.warning("Unable to store state. Only numerical states are supported")

        if not update_state:
            return

        self._calc_difference()
        self.async_write_ha_state()

    @callback
    def _calc_difference(self) -> None:
        """Calculate the difference."""
        input_val = self._states.get(self._input_sensor.entity_id)
        output_val = self._states.get(self._output_sensor.entity_id)
        if input_val is None or output_val is None or input_val is STATE_UNKNOWN or output_val is STATE_UNKNOWN:
            self._difference = None
            return
        self._difference = float(output_val) - float(input_val)        
