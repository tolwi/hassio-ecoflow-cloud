from abc import ABC, abstractmethod

from ..mqtt.ecoflow_mqtt import EcoflowMQTTClient
from ..entities import BaseNumberEntity, BaseSelectEntity
from ..entities import BaseSensorEntity
from ..entities import BaseSwitchEntity


class BaseDevice(ABC):

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
