from typing import Sequence
from ...api import EcoflowApiClient
from ...sensor import QuotaStatusSensorEntity
from ...devices import const, BaseDevice
from .data_bridge import to_plain
from custom_components.ecoflow_cloud.entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, \
    BaseSelectEntity
from custom_components.ecoflow_cloud.sensor import MiscSensorEntity, WattsSensorEntity, InAmpSensorEntity, MilliVoltSensorEntity, \
    EnergySensorEntity, MiscBinarySensorEntity

class SmartMeter(BaseDevice):

    def sensors(self, client: EcoflowApiClient) -> Sequence[BaseSensorEntity]:
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

            MilliVoltSensorEntity(client, self, "gridConnectionVolL1", const.SMART_METER_VOLT_L1, False),
            MilliVoltSensorEntity(client, self, "gridConnectionVolL2", const.SMART_METER_VOLT_L2, False),
            MilliVoltSensorEntity(client, self, "gridConnectionVolL3", const.SMART_METER_VOLT_L3, False),

            MiscBinarySensorEntity(client, self, "gridConnectionFlagL1", const.SMART_METER_FLAG_L1, False),
            MiscBinarySensorEntity(client, self, "gridConnectionFlagL2", const.SMART_METER_FLAG_L2, False),
            MiscBinarySensorEntity(client, self, "gridConnectionFlagL3", const.SMART_METER_FLAG_L3, False),

            EnergySensorEntity(client, self, "gridConnectionDataRecord.todayActiveL1", const.SMART_METER_RECORD_TODAY_ACTIVE_L1,False),
            EnergySensorEntity(client, self, "gridConnectionDataRecord.todayActiveL2", const.SMART_METER_RECORD_TODAY_ACTIVE_L2, False),
            EnergySensorEntity(client, self, "gridConnectionDataRecord.todayActiveL3", const.SMART_METER_RECORD_TODAY_ACTIVE_L3, False),

            EnergySensorEntity(client, self, "gridConnectionDataRecord.todayActive", const.SMART_METER_RECORD_ACTIVE_TODAY),
            EnergySensorEntity(client, self, "gridConnectionDataRecord.totalActiveEnergy", const.SMART_METER_RECORD_NET_ENERGY_CONSUMPTION),
            EnergySensorEntity(client, self, "gridConnectionDataRecord.totalReactiveEnergy", const.SMART_METER_RECORD_LIFETIME_ENERGY_DELIVERY),

            # Configurable?
            timezoneEntity,
            # Configurable?
            MiscSensorEntity(client, self, "gridConnectionPowerFactor",
                             const.SMART_METER_GRID_CONNECTION_POWER_FACTOR, False),
            MiscSensorEntity(client, self, "gridConnectionSta", const.SMART_METER_GRID_CONNECTION_STATE, False),
            # Configurable?
            MiscSensorEntity(client, self, "countryCode", const.COUNTRY_CODE, False),
            # Configurable?
            MiscSensorEntity(client, self, "townCode", const.TOWN_CODE, False),
            # Configurable?
            MiscSensorEntity(client, self, "systemGroupId", const.SYSTEM_GROUP_ID, False),

            # Configurable?
            MiscBinarySensorEntity(client, self, "factoryModeEnable", const.FACTORY_MODE, False,
                                   diagnostic=True),
            # Configurable?
            MiscBinarySensorEntity(client, self, "debugModeEnable", const.DEBUG_MODE, False, diagnostic=True),

            self._status_sensor(client),
        ]

    def numbers(self, client: EcoflowApiClient) -> Sequence[BaseNumberEntity]:
        return []

    def switches(self, client: EcoflowApiClient) -> Sequence[BaseSwitchEntity]:
        return []

    def selects(self, client: EcoflowApiClient) -> Sequence[BaseSelectEntity]:
        return []

    def _prepare_data(self, raw_data) -> dict[str, any]:
        res = super()._prepare_data(raw_data)
        res = to_plain(res)
        return res

    def _status_sensor(self, client: EcoflowApiClient) -> QuotaStatusSensorEntity:
        return QuotaStatusSensorEntity(client, self)


