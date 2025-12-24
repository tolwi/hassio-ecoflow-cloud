from typing import Any
from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.sensor import StatusSensorEntity
from custom_components.ecoflow_cloud.devices.internal.delta2_max import Delta2Max as InternalDelta2Max
from custom_components.ecoflow_cloud.devices.public.data_bridge import to_plain


class Delta2Max(InternalDelta2Max):
    def _prepare_data(self, raw_data) -> dict[str, Any]:
        res = super()._prepare_data(raw_data)
        res = to_plain(res)
        return res

    def _status_sensor(self, client: EcoflowApiClient) -> StatusSensorEntity:
        return StatusSensorEntity(client, self)
