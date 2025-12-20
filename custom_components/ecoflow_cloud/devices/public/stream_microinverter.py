from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import BaseDevice, const
from custom_components.ecoflow_cloud.devices.public.data_bridge import to_plain
from custom_components.ecoflow_cloud.sensor import (
    CelsiusSensorEntity,
    FrequencySensorEntity,
    InAmpSensorEntity,
    StatusSensorEntity,
    VoltSensorEntity,
    WattsSensorEntity,
)


class StreamMicroinveter(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
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
            CelsiusSensorEntity(client, self, "invNtcTemp3", "Inverter NTC Temperature"),
            FrequencySensorEntity(client, self, "gridConnectionFreq", "Grid Frequency"),
            StatusSensorEntity(client, self),
        ]

    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return []

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return []

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return []

    def _prepare_data(self, raw_data) -> dict[str, Any]:
        res = super()._prepare_data(raw_data)
        res = to_plain(res)
        return res

    def _status_sensor(self, client: EcoflowApiClient) -> StatusSensorEntity:
        return StatusSensorEntity(client, self)
