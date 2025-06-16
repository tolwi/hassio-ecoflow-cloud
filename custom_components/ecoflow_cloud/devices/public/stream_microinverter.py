from ...api import EcoflowApiClient
from ...entities import (
    BaseNumberEntity,
    BaseSelectEntity,
    BaseSensorEntity,
    BaseSwitchEntity,
)
from ...sensor import (
    StatusSensorEntity,
    InAmpSensorEntity,
    WattsSensorEntity,
    VoltSensorEntity,
)
from .. import BaseDevice, const
from .data_bridge import to_plain


class StreamMicroinveter(BaseDevice):

    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [
            WattsSensorEntity(client, self, "gridConnectionPower", const.STREAM_POWER_AC),
            WattsSensorEntity(client, self, "powGetPv", const.STREAM_POWER_PV_1, False, True),
            WattsSensorEntity(client, self, "powGetPv2", const.STREAM_POWER_PV_2, False, True),

            VoltSensorEntity(client, self, "gridConnectionVol", const.STREAM_POWER_VOL, False),
            VoltSensorEntity(client, self, "plugInInfoPvVol", const.STREAM_IN_VOL_PV_1, False, True),
            VoltSensorEntity(client, self, "plugInInfoPv2Vol", const.STREAM_IN_VOL_PV_2, False, True),

            InAmpSensorEntity(client, self, "gridConnectionAmp", const.STREAM_POWER_AMP, False),
            InAmpSensorEntity(client, self, "plugInInfoPvAmp", const.STREAM_IN_AMPS_PV_1, False, True),
            InAmpSensorEntity(client, self, "plugInInfoPv2Amp", const.STREAM_IN_AMPS_PV_2, False, True),

            StatusSensorEntity(client, self)
        ]


    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return []

    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        return []

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return []

    def _prepare_data(self, raw_data) -> dict[str, any]:
        res = super()._prepare_data(raw_data)
        res = to_plain(res)
        return res

    def _status_sensor(self, client: EcoflowApiClient) -> StatusSensorEntity:
        return StatusSensorEntity(client, self)


