from . import const, BaseDevice
from .. import EcoflowMQTTClient
from ..entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, BaseSelectEntity
from ..number import ChargingPowerEntity
from ..select import DictSelectEntity, TimeoutDictSelectEntity
from ..sensor import LevelSensorEntity, RemainSensorEntity, TempSensorEntity, CyclesSensorEntity, \
    InWattsSensorEntity, OutWattsSensorEntity, VoltSensorEntity

import struct
from typing import Any, Callable, Iterable

class PowerStream(BaseDevice):
    def sensors(self, client: EcoflowMQTTClient) -> list[BaseSensorEntity]:
        return []

    def numbers(self, client: EcoflowMQTTClient) -> list[BaseNumberEntity]:
        return []

    def switches(self, client: EcoflowMQTTClient) -> list[BaseSwitchEntity]:
        return []

    def selects(self, client: EcoflowMQTTClient) -> list[BaseSelectEntity]:
        return []