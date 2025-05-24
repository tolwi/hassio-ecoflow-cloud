from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import const, BaseDevice
from custom_components.ecoflow_cloud.entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, \
    BaseSelectEntity
from custom_components.ecoflow_cloud.sensor import WattsSensorEntity

class SmartMeter(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [
            WattsSensorEntity(client, self, "powGetSysGrid", const.SMART_METER_POWER_GLOBAL),
            WattsSensorEntity(client, self, "gridConnectionPowerL1", const.SMART_METER_POWER_L1),
            WattsSensorEntity(client, self, "gridConnectionPowerL2", const.SMART_METER_POWER_L2),
            WattsSensorEntity(client, self, "gridConnectionPowerL3", const.SMART_METER_POWER_L3)
        ]

    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return []

    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        return []

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return []