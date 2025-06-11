from ...api import EcoflowApiClient
from .. import BaseDevice
from .data_bridge import to_plain_other

from ...sensor import (
    VoltSensorEntity,
    WattsSensorEntity,
    LevelSensorEntity,
    AmpSensorEntity,
    SolarPowerSensorEntity,
    SolarAmpSensorEntity,
    SystemPowerSensorEntity,
    StatusSensorEntity,
)
from ...entities import (
    BaseSensorEntity,
    BaseNumberEntity,
    BaseSwitchEntity,
    BaseSelectEntity,
)

import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


class PowerOcean(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [
            SolarPowerSensorEntity(client, self, "mpptPwr", "mpptPwr"),
            LevelSensorEntity(client, self, "bpSoc", "bpSoc"),
            WattsSensorEntity(client, self, "bpPwr", "bpPwr"),
            SystemPowerSensorEntity(client, self, "sysLoadPwr", "sysLoadPwr"),
            SystemPowerSensorEntity(client, self, "sysGridPwr", "sysGridPwr"),
            # TODO: flatten Structure?
            # String 1
            SolarPowerSensorEntity(client, self, "mpptPv1.pwr", "mpptPv1.pwr"),
            SolarAmpSensorEntity(client, self, "mpptPv1.amp", "mpptPv1.amp"),
            VoltSensorEntity(client, self, "mpptPv1.vol", "mpptPv1.vol"),
            # String 2
            SolarPowerSensorEntity(client, self, "mpptPv2.pwr", "mpptPv2.pwr"),
            SolarAmpSensorEntity(client, self, "mpptPv2.amp", "mpptPv2.amp"),
            VoltSensorEntity(client, self, "mpptPv2.vol", "mpptPv2.vol"),
            VoltSensorEntity(client, self, "pcsAPhase.vol", "pcsAPhase.vol"),
            AmpSensorEntity(client, self, "pcsAPhase.amp", "pcsAPhase.amp"),
            WattsSensorEntity(client, self, "pcsAPhase.actPwr", "pcsAPhase.actPwr"),
            WattsSensorEntity(client, self, "pcsAPhase.reactPwr", "pcsAPhase.reactPwr"),
            WattsSensorEntity(
                client, self, "pcsAPhase.apparentPwr", "pcsAPhase.apparentPwr"
            ),
            VoltSensorEntity(client, self, "pcsBPhase.vol", "pcsBPhase.vol"),
            AmpSensorEntity(client, self, "pcsBPhase.amp", "pcsBPhase.amp"),
            WattsSensorEntity(client, self, "pcsBPhase.actPwr", "pcsBPhase.actPwr"),
            WattsSensorEntity(client, self, "pcsBPhase.reactPwr", "pcsBPhase.reactPwr"),
            WattsSensorEntity(
                client, self, "pcsBPhase.apparentPwr", "pcsBPhase.apparentPwr"
            ),
            VoltSensorEntity(client, self, "pcsCPhase.vol", "pcsCPhase.vol"),
            AmpSensorEntity(client, self, "pcsCPhase.amp", "pcsCPhase.amp"),
            WattsSensorEntity(client, self, "pcsCPhase.actPwr", "pcsCPhase.actPwr"),
            WattsSensorEntity(client, self, "pcsCPhase.reactPwr", "pcsCPhase.reactPwr"),
            WattsSensorEntity(
                client, self, "pcsCPhase.apparentPwr", "pcsCPhase.apparentPwr"
            ),
            StatusSensorEntity(client, self),
        ]

    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return []

    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        return []

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return []

    def _prepare_data(self, raw_data) -> dict[str, "Any"]:
        res = super()._prepare_data(raw_data)
        _LOGGER.info(f"_prepare_data {raw_data}")
        res = to_plain_other(res)
        return res

    def _status_sensor(self, client: EcoflowApiClient) -> StatusSensorEntity:
        return StatusSensorEntity(client, self)
