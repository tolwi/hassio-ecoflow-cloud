from ...api import EcoflowApiClient
from ...sensor import StatusSensorEntity
from ..internal.stream_ac import StreamAC as InternalStreamAC
from .data_bridge import to_plain


class StreamAC(InternalStreamAC):

    def _prepare_data(self, raw_data) -> dict[str, any]:
        res = super()._prepare_data(raw_data)
        res = to_plain(res)
        return res

    def _status_sensor(self, client: EcoflowApiClient) -> StatusSensorEntity:
        return StatusSensorEntity(client, self)


