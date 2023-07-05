from abc import ABC, abstractmethod

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity

from ..mqtt.ecoflow_mqtt import EcoflowMQTTClient
from ..entities import BaseNumberEntity, BaseSelectEntity
from ..entities import BaseSensorEntity
from ..entities import BaseSwitchEntity


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
    def selects(self, client: EcoflowMQTTClient) -> list[SelectEntity]:
        pass


class DiagnosticDevice(BaseDevice):

    def sensors(self, client: EcoflowMQTTClient) -> list[SensorEntity]:
        return []

    def numbers(self, client: EcoflowMQTTClient) -> list[NumberEntity]:
        return []

    def switches(self, client: EcoflowMQTTClient) -> list[SwitchEntity]:
        return []

    def selects(self, client: EcoflowMQTTClient) -> list[SelectEntity]:
        return []
