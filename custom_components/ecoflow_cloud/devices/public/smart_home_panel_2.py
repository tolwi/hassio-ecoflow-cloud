from .data_bridge import to_plain
from ...api import EcoflowApiClient
from ...sensor import StatusSensorEntity, WattsSensorEntity, InWattsSensorEntity
from .. import BaseDevice, const
from ...entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, BaseSelectEntity
from custom_components.ecoflow_cloud.switch import EnabledEntity
from custom_components.ecoflow_cloud.select import DictSelectEntity

class SmartHomePanel2(BaseDevice):

    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        params = self.data.params
        return [
            InWattsSensorEntity(client, self, "'wattInfo.gridWatt'", const.AC_IN_POWER),
            WattsSensorEntity(client, self, "'loadInfo.hall1Watt'[0]", "Breaker 1 Energy"),
            WattsSensorEntity(client, self, "'loadInfo.hall1Watt'[1]", "Breaker 2 Energy"),
            WattsSensorEntity(client, self, "'loadInfo.hall1Watt'[2]", "Breaker 3 Energy"),
            WattsSensorEntity(client, self, "'loadInfo.hall1Watt'[3]", "Breaker 4 Energy"),
            WattsSensorEntity(client, self, "'loadInfo.hall1Watt'[4]", "Breaker 5 Energy"),
            WattsSensorEntity(client, self, "'loadInfo.hall1Watt'[5]", "Breaker 6 Energy"),
            WattsSensorEntity(client, self, "'loadInfo.hall1Watt'[6]", "Breaker 7 Energy"),
            WattsSensorEntity(client, self, "'loadInfo.hall1Watt'[7]", "Breaker 8 Energy"),
            WattsSensorEntity(client, self, "'loadInfo.hall1Watt'[8]", "Breaker 9 Energy"),
            WattsSensorEntity(client, self, "'loadInfo.hall1Watt'[9]", "Breaker 10 Energy"),
            WattsSensorEntity(client, self, "'loadInfo.hall1Watt'[10]", "Breaker 11 Energy"),
            WattsSensorEntity(client, self, "'loadInfo.hall1Watt'[11]", "Breaker 12 Energy")
        ]
    
    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return [
        ]

    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        return [
            EnabledEntity(
                client,
                self,
                "epsModeInfo",
                "EPS Mode",
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "PD303_APP_SET",
                    "params": {"epsModeInfo": value == 1}
                },
            ),
        ]

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return [
        ]
    
    def flat_json(self):
        return False