from typing import Any
from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.sensor import StatusSensorEntity
from custom_components.ecoflow_cloud.devices.internal.delta3 import Delta3 as InternalDelta3
from custom_components.ecoflow_cloud.devices.public.data_bridge import to_plain


class Delta3(InternalDelta3):
    def _prepare_data(self, raw_data) -> dict[str, Any]:
        res = super()._prepare_data(raw_data)
        res = to_plain(res)
        return res

    def _status_sensor(self, client: EcoflowApiClient) -> StatusSensorEntity:
        return StatusSensorEntity(client, self)
