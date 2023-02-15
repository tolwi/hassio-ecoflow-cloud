from abc import ABC, abstractmethod

from ..mqtt.ecoflow_mqtt import EcoflowMQTTClient
from ..entities import BaseNumberEntity, BaseSelectEntity
from ..entities import BaseSensorEntity
from ..entities import BaseSwitchEntity


class BaseDevice(ABC):

    def charging_power_step(self) -> int:
        return 100

    @abstractmethod
    def sensors(self, client: EcoflowMQTTClient) -> list[BaseSensorEntity]:
        pass

    @abstractmethod
    def numbers(self, client: EcoflowMQTTClient) -> list[BaseNumberEntity]:
        pass

    @abstractmethod
    def switches(self, client: EcoflowMQTTClient) -> list[BaseSwitchEntity]:
        pass

    @abstractmethod
    def selects(self, client: EcoflowMQTTClient) -> list[BaseSelectEntity]:
        pass


class DiagnosticDevice(BaseDevice):

    def sensors(self, client: EcoflowMQTTClient) -> list[BaseSensorEntity]:
        return []

    def numbers(self, client: EcoflowMQTTClient) -> list[BaseNumberEntity]:
        return []

    def switches(self, client: EcoflowMQTTClient) -> list[BaseSwitchEntity]:
        return []

    def selects(self, client: EcoflowMQTTClient) -> list[BaseSelectEntity]:
        return []
