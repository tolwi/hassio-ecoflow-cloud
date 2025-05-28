from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import const, BaseDevice
from custom_components.ecoflow_cloud.entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, \
    BaseSelectEntity
from custom_components.ecoflow_cloud.sensor import WattsSensorEntity

class StreamAC(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [
            WattsSensorEntity(client, self, "sysGridConnectionPower", const.STREAM_POWER_AC),
            WattsSensorEntity(client, self, "powGetSysGrid", const.STREAM_POWER_GRID),
            WattsSensorEntity(client, self, "powGetPvSum", const.STREAM_POWER_PV),
            WattsSensorEntity(client, self, "powGetBpCms", const.STREAM_POWER_BATTERY)
        ]

    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return []

    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        return []

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return []