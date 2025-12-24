from typing import Any, Sequence

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.binary_sensor import MiscBinarySensorEntity
from custom_components.ecoflow_cloud.devices import BaseDevice, const
from custom_components.ecoflow_cloud.devices.public.data_bridge import to_plain
from custom_components.ecoflow_cloud.sensor import (
    EnergySensorEntity,
    InAmpSensorEntity,
    MiscSensorEntity,
    QuotaStatusSensorEntity,
    VoltSensorEntity,
    WattsSensorEntity,
)


class SmartMeter(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> Sequence[SensorEntity]:
        timezoneEntity = MiscSensorEntity(client, self, "utcTimezone", const.UTC_TIMEZONE, False)
        timezoneEntity.attr("utcTimezoneId", const.UTC_TIMEZONE_ID, "Unknown")
        return [
            WattsSensorEntity(client, self, "powGetSysGrid", const.SMART_METER_POWER_GLOBAL),
            WattsSensorEntity(client, self, "gridConnectionPowerL1", const.SMART_METER_POWER_L1, False),
            WattsSensorEntity(client, self, "gridConnectionPowerL2", const.SMART_METER_POWER_L2, False),
            WattsSensorEntity(client, self, "gridConnectionPowerL3", const.SMART_METER_POWER_L3, False),
            InAmpSensorEntity(client, self, "gridConnectionAmpL1", const.SMART_METER_IN_AMPS_L1, False),
            InAmpSensorEntity(client, self, "gridConnectionAmpL2", const.SMART_METER_IN_AMPS_L2, False),
            InAmpSensorEntity(client, self, "gridConnectionAmpL3", const.SMART_METER_IN_AMPS_L3, False),
            VoltSensorEntity(client, self, "gridConnectionVolL1", const.SMART_METER_VOLT_L1, False),
            VoltSensorEntity(client, self, "gridConnectionVolL2", const.SMART_METER_VOLT_L2, False),
            VoltSensorEntity(client, self, "gridConnectionVolL3", const.SMART_METER_VOLT_L3, False),
            EnergySensorEntity(
                client, self, "gridConnectionDataRecord.todayActiveL1", const.SMART_METER_RECORD_TODAY_ACTIVE_L1, False
            ),
            EnergySensorEntity(
                client, self, "gridConnectionDataRecord.todayActiveL2", const.SMART_METER_RECORD_TODAY_ACTIVE_L2, False
            ),
            EnergySensorEntity(
                client, self, "gridConnectionDataRecord.todayActiveL3", const.SMART_METER_RECORD_TODAY_ACTIVE_L3, False
            ),
            EnergySensorEntity(
                client, self, "gridConnectionDataRecord.todayActive", const.SMART_METER_RECORD_ACTIVE_TODAY
            ),
            EnergySensorEntity(
                client,
                self,
                "gridConnectionDataRecord.totalActiveEnergy",
                const.SMART_METER_RECORD_NET_ENERGY_CONSUMPTION,
            ),
            EnergySensorEntity(
                client,
                self,
                "gridConnectionDataRecord.totalReactiveEnergy",
                const.SMART_METER_RECORD_LIFETIME_ENERGY_DELIVERY,
            ),
            # Configurable?
            timezoneEntity,
            # Configurable?
            MiscSensorEntity(
                client, self, "gridConnectionPowerFactor", const.SMART_METER_GRID_CONNECTION_POWER_FACTOR, False
            ),
            MiscSensorEntity(client, self, "gridConnectionSta", const.SMART_METER_GRID_CONNECTION_STATE, False),
            # Configurable?
            MiscSensorEntity(client, self, "countryCode", const.COUNTRY_CODE, False),
            # Configurable?
            MiscSensorEntity(client, self, "townCode", const.TOWN_CODE, False),
            # Configurable?
            MiscSensorEntity(client, self, "systemGroupId", const.SYSTEM_GROUP_ID, False),
            self._status_sensor(client),
        ]

    def binary_sensors(self, client: EcoflowApiClient) -> Sequence[BinarySensorEntity]:
        return [
            MiscBinarySensorEntity(client, self, "gridConnectionFlagL1", const.SMART_METER_FLAG_L1, False),
            MiscBinarySensorEntity(client, self, "gridConnectionFlagL2", const.SMART_METER_FLAG_L2, False),
            MiscBinarySensorEntity(client, self, "gridConnectionFlagL3", const.SMART_METER_FLAG_L3, False),
            # Configurable?
            MiscBinarySensorEntity(client, self, "factoryModeEnable", const.FACTORY_MODE, False, diagnostic=True),
            # Configurable?
            MiscBinarySensorEntity(client, self, "debugModeEnable", const.DEBUG_MODE, False, diagnostic=True),
        ]

    def numbers(self, client: EcoflowApiClient) -> Sequence[NumberEntity]:
        return []

    def switches(self, client: EcoflowApiClient) -> Sequence[SwitchEntity]:
        return []

    def selects(self, client: EcoflowApiClient) -> Sequence[SelectEntity]:
        return []

    def _prepare_data(self, raw_data) -> dict[str, Any]:
        res = super()._prepare_data(raw_data)
        res = to_plain(res)
        return res

    def _status_sensor(self, client: EcoflowApiClient) -> QuotaStatusSensorEntity:
        return QuotaStatusSensorEntity(client, self)
