import enum
import logging
from datetime import datetime

from homeassistant.util import dt

_LOGGER = logging.getLogger(__name__)

_EPOCH = dt.utcnow().replace(year=2000, month=1, day=1, hour=0, minute=0, second=0)


class OnlineStatus(enum.Enum):
    ONLINE = (True, "online")
    ASSUME_OFFLINE = (None, "assume_offline")
    OFFLINE = (False, "offline")

    def __init__(self, online: bool | None, label: str):
        self.online = online
        self.label = label


class StatusTracker:
    """Single source of truth for device online status.

    Receives two types of signals:
    - on_data_received(): implicit online — any MQTT/API message with actual params arrived
    - on_explicit_status(online): explicit — status topic, latestQuotas reply, or API device list
    """

    def __init__(self, assume_offline_sec: int, initial_status: int = -1):
        self._assume_offline_sec = assume_offline_sec
        self._force_offline_sec = assume_offline_sec * 3
        self._last_data_time: datetime = _EPOCH
        self._explicit_offline: bool = False
        self._explicit_status_count: int = 0
        self._explicit_status_last_time: datetime | None = None
        self._data_received_count: int = 0

        if initial_status >= 0:
            self.on_explicit_status(initial_status == 1)

    @property
    def assume_offline_sec(self) -> int:
        return self._assume_offline_sec

    def on_data_received(self):
        """Called when any MQTT/API message with actual params arrives."""
        self._last_data_time = dt.utcnow()
        self._explicit_offline = False
        self._data_received_count += 1

    def on_explicit_status(self, online: bool):
        """Called when status topic, latestQuotas reply, or API device list provides explicit status."""
        self._explicit_status_count += 1
        self._explicit_status_last_time = dt.utcnow()
        if online:
            self._last_data_time = dt.utcnow()
            self._explicit_offline = False
        else:
            self._explicit_offline = True

    @property
    def status(self) -> OnlineStatus:
        if self._explicit_offline:
            return OnlineStatus.OFFLINE
        age = (dt.utcnow() - self._last_data_time).total_seconds()
        if age < self._assume_offline_sec:
            return OnlineStatus.ONLINE
        if age < self._force_offline_sec:
            return OnlineStatus.ASSUME_OFFLINE
        return OnlineStatus.OFFLINE

    @property
    def is_online(self) -> bool:
        return self.status == OnlineStatus.ONLINE

    @property
    def is_offline(self) -> bool:
        return self.status == OnlineStatus.OFFLINE

    @property
    def wants_status_poll(self) -> bool:
        """True when status is uncertain or offline and an explicit poll would help clarify."""
        return not self.is_online

    @property
    def last_data_time(self) -> datetime:
        return self._last_data_time
