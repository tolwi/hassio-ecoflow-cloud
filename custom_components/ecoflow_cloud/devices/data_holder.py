import dataclasses
import logging
from collections.abc import Callable
from typing import Any, TypeVar

import jsonpath_ng.ext as jp
from homeassistant.util import dt
from datetime import datetime, timezone as _timezone

_LOGGER = logging.getLogger(__name__)

_T = TypeVar("_T")


class BoundFifoList(list[_T]):
    def __init__(self, maxlen=20) -> None:
        super().__init__()
        self.maxlen = maxlen

    def append(self, __object: _T) -> None:
        super().insert(0, __object)
        while len(self) >= self.maxlen:
            self.pop()


@dataclasses.dataclass
class PreparedData:
    online: bool | None
    params: dict[str, Any] | None
    raw_data: dict[str, Any] | None


class EcoflowDataHolder:
    def __init__(
        self,
        module_sn: str | None = None,
        collect_raw: bool = False,
    ):
        self.online = True
        self.module_sn = module_sn

        self.params = dict[str, Any]()

        self.__collect_raw = collect_raw
        self.set_params = BoundFifoList[dict[str, Any]]()
        self.set_params_time = datetime.now(_timezone.utc).replace(year=2000, month=1, day=1, hour=0, minute=0, second=0)

        self.set = BoundFifoList[dict[str, Any]]()
        self.set_reply = BoundFifoList[dict[str, Any]]()
        self.set_reply_time = datetime.now(_timezone.utc).replace(year=2000, month=1, day=1, hour=0, minute=0, second=0)

        self.get = BoundFifoList[dict[str, Any]]()
        self.get_reply = BoundFifoList[dict[str, Any]]()
        self.get_reply_time = datetime.now(_timezone.utc).replace(year=2000, month=1, day=1, hour=0, minute=0, second=0)

        self.set_status = BoundFifoList[dict[str, Any]]()
        self.set_status_time = datetime.now(_timezone.utc).replace(year=2000, month=1, day=1, hour=0, minute=0, second=0)

    def last_received_time(self):
        return max(
            self.set_status_time,
            self.set_params_time,
            # 1. get_reply can receive '"message": "The device is not online"'
            # 2. if device is online - get_reply message will update params, so param_time will be updated as well
            # , self.get_reply_time, self.set_reply_time
        )

    def add_set_message(self, data: PreparedData):
        self.__accept_prepared_data(data, self.set.append)
        self.set_time = datetime.now(_timezone.utc)

    def add_set_reply_message(self, data: PreparedData):
        self.__accept_prepared_data(data, self.set_reply.append)
        self.set_reply_time = datetime.now(_timezone.utc)

    def add_get_message(self, data: PreparedData):
        self.__accept_prepared_data(data, self.get.append)
        self.get_time = datetime.now(_timezone.utc)

    def add_get_reply_message(self, data: PreparedData):
        self.__accept_prepared_data(data, self.get_reply.append)
        self.get_reply_time = datetime.now(_timezone.utc)

    def update_to_target_state(self, target_state: dict[str, Any]):
        # key can be xpath!
        for key, value in target_state.items():
            jp.parse(key).update(self.params, value)

        self.set_params_time = datetime.now(_timezone.utc)

    def add_status(self, data: PreparedData):
        self.__accept_prepared_data(data, self.set_status.append)
        self.set_status_time = datetime.now(_timezone.utc)

    def add_data(self, data: PreparedData):
        if data.params is not None and self.module_sn is not None:
            if "moduleSn" not in data.params:
                return
            if data.params["moduleSn"] != self.module_sn:
                return

        self.__accept_prepared_data(data, self.__update_params)

    def __update_params(self, params: dict[str, Any]):
        if "params" in params:
            # Only treat as "changed" if at least one value differs.
            # MQTT can publish the same values frequently; updating timestamps on no-op
            # updates forces the coordinator to trigger all entities and can be CPU heavy.
            incoming = params["params"]
            for key, value in incoming.items():
                if self.params.get(key) != value:
                    self.params.update(incoming)
                    self.set_params_time = dt.utcnow()
                    break

    def __accept_prepared_data(self, data: PreparedData, raw_data_acceptor: Callable[[dict[str, Any]], None]):
        if data.online is not None:
            self.online = data.online

        if data.params is not None:
            self.__update_params(data.params)
            self.online = True

        if self.__collect_raw and data.raw_data is not None:
            raw_data_acceptor(data.raw_data)
