from abc import ABC, abstractmethod
from enum import StrEnum

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.button import ButtonEntity
from homeassistant.const import Platform

from ..mqtt.ecoflow_mqtt import EcoflowMQTTClient


class MigrationAction(StrEnum):
    REMOVE = "remove"


class EntityMigration:

    def __init__(self, key: str, domain: Platform, action: MigrationAction, **kwargs):
        self.key = key
        self.domain = domain
        self.action = action
        self.args = kwargs


class BaseDevice(ABC):

    def charging_power_step(self) -> int:
        return 100

    @abstractmethod
    def sensors(self, client: EcoflowMQTTClient) -> list[SensorEntity]:
        pass

    @abstractmethod
    def numbers(self, client: EcoflowMQTTClient) -> list[NumberEntity]:
        pass

    @abstractmethod
    def switches(self, client: EcoflowMQTTClient) -> list[SwitchEntity]:
        pass

    @abstractmethod
    def buttons(self, client: EcoflowMQTTClient) -> list[ButtonEntity]:
        pass

    @abstractmethod
    def selects(self, client: EcoflowMQTTClient) -> list[SelectEntity]:
        pass

    def buttons(self, client: EcoflowMQTTClient) -> list[ButtonEntity]:
        return []

    def migrate(self, version) -> list[EntityMigration]:
        return []


class DiagnosticDevice(BaseDevice):

    def sensors(self, client: EcoflowMQTTClient) -> list[SensorEntity]:
        return []

    def numbers(self, client: EcoflowMQTTClient) -> list[NumberEntity]:
        return []

    def switches(self, client: EcoflowMQTTClient) -> list[SwitchEntity]:
        return []

    def buttons(self, client: EcoflowMQTTClient) -> list[ButtonEntity]:
        return []

    def selects(self, client: EcoflowMQTTClient) -> list[SelectEntity]:
        return []
