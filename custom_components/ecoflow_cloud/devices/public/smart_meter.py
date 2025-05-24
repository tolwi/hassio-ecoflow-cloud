from ...api import EcoflowApiClient
from ...sensor import StatusSensorEntity
from ..internal.smart_meter import SmartMeter as InternalSmartMeter
from .data_bridge import to_plain


class SmartMeter(InternalSmartMeter):

    def _prepare_data(self, raw_data) -> dict[str, any]:
        res = super()._prepare_data(raw_data)
        res = to_plain(res)
        return res

    def _status_sensor(self, client: EcoflowApiClient) -> StatusSensorEntity:
        return StatusSensorEntity(client, self)


