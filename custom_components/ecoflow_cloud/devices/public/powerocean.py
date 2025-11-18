from ...api import EcoflowApiClient
from .. import BaseDevice
from .data_bridge import to_plain

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
    def flat_json(self):
        return True

    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [
            SolarPowerSensorEntity(client, self, "mpptPwr", "mpptPwr"),
            LevelSensorEntity(client, self, "bpSoc", "bpSoc"),
            WattsSensorEntity(client, self, "bpPwr", "bpPwr"),
            SystemPowerSensorEntity(client, self, "sysLoadPwr", "sysLoadPwr"),
            SystemPowerSensorEntity(client, self, "sysGridPwr", "sysGridPwr"),

            # String 1
            SolarPowerSensorEntity(
                client, self, "96_1.mpptHeartBeat[0].mpptPv[0].pwr", "mpptPv1.pwr"
            ),
            SolarAmpSensorEntity(
                client, self, "96_1.mpptHeartBeat[0].mpptPv[0].amp", "mpptPv1.amp"
            ),
            VoltSensorEntity(
                client, self, "96_1.mpptHeartBeat[0].mpptPv[0].vol", "mpptPv1.vol"
            ),
            # String 2
            SolarPowerSensorEntity(
                client, self, "96_1.mpptHeartBeat[0].mpptPv[1].pwr", "mpptPv2.pwr"
            ),
            SolarAmpSensorEntity(
                client, self, "96_1.mpptHeartBeat[0].mpptPv[1].amp", "mpptPv2.amp"
            ),
            VoltSensorEntity(
                client, self, "96_1.mpptHeartBeat[0].mpptPv[1].vol", "mpptPv2.vol"
            ),
            VoltSensorEntity(client, self, "96_1.pcsAPhase.vol", "pcsAPhase.vol"),
            AmpSensorEntity(client, self, "96_1.pcsAPhase.amp", "pcsAPhase.amp"),
            WattsSensorEntity(
                client, self, "96_1.pcsAPhase.actPwr", "pcsAPhase.actPwr"
            ),
            WattsSensorEntity(
                client, self, "96_1.pcsAPhase.reactPwr", "pcsAPhase.reactPwr"
            ),
            WattsSensorEntity(
                client, self, "96_1.pcsAPhase.apparentPwr", "pcsAPhase.apparentPwr"
            ),
            VoltSensorEntity(client, self, "96_1.pcsBPhase.vol", "pcsBPhase.vol"),
            AmpSensorEntity(client, self, "96_1.pcsBPhase.amp", "pcsBPhase.amp"),
            WattsSensorEntity(
                client, self, "96_1.pcsBPhase.actPwr", "pcsBPhase.actPwr"
            ),
            WattsSensorEntity(
                client, self, "96_1.pcsBPhase.reactPwr", "pcsBPhase.reactPwr"
            ),
            WattsSensorEntity(
                client, self, "96_1.pcsBPhase.apparentPwr", "pcsBPhase.apparentPwr"
            ),
            VoltSensorEntity(client, self, "96_1.pcsCPhase.vol", "pcsCPhase.vol"),
            AmpSensorEntity(client, self, "96_1.pcsCPhase.amp", "pcsCPhase.amp"),
            WattsSensorEntity(
                client, self, "96_1.pcsCPhase.actPwr", "pcsCPhase.actPwr"
            ),
            WattsSensorEntity(
                client, self, "96_1.pcsCPhase.reactPwr", "pcsCPhase.reactPwr"
            ),
            WattsSensorEntity(
                client, self, "96_1.pcsCPhase.apparentPwr", "pcsCPhase.apparentPwr"
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
        res = to_plain(res)
        return res

    def _status_sensor(self, client: EcoflowApiClient) -> StatusSensorEntity:
        return StatusSensorEntity(client, self)