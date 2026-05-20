from collections.abc import Sequence

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import BaseDevice
from custom_components.ecoflow_cloud.sensor import (
    InWattsSensorEntity,
    LevelSensorEntity,
    OutWattsSensorEntity,
    RemainSensorEntity,
)


class Delta3MaxPlus(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> Sequence[SensorEntity]:
        return [
            LevelSensorEntity(client, self, "cmsBattSoc", "Batterie"),
            InWattsSensorEntity(client, self, "powInSumW", "Puissance Entrée Totale"),
            OutWattsSensorEntity(client, self, "powOutSumW", "Puissance Sortie Totale"),
            InWattsSensorEntity(client, self, "powGetAcIn", "Puissance Entrée AC"),
            InWattsSensorEntity(client, self, "powGetPv", "Puissance Solaire (PV1)"),
            InWattsSensorEntity(client, self, "powGetPv2", "Puissance Solaire (PV2)"),
            LevelSensorEntity(client, self, "cmsMaxChgSoc", "Limite Charge Max"),
            LevelSensorEntity(client, self, "cmsMinDsgSoc", "Limite Décharge Min"),
            RemainSensorEntity(client, self, "cmsChgRemTime", "Temps de Charge Restant"),
            RemainSensorEntity(client, self, "cmsDsgRemTime", "Temps de Décharge Restant"),
        ]

    def numbers(self, client: EcoflowApiClient) -> Sequence[NumberEntity]:
        return []

    def switches(self, client: EcoflowApiClient) -> Sequence[SwitchEntity]:
        return []

    def selects(self, client: EcoflowApiClient) -> Sequence[SelectEntity]:
        return []
