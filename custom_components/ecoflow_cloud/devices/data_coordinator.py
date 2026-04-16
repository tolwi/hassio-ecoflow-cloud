"""Per-device coordinator that broadcasts data changes to HA entities.

Each BaseDevice creates one instance. On each poll cycle it checks whether the
underlying EcoflowDataHolder received new data since the last broadcast and
notifies listening entities accordingly.
"""

from __future__ import annotations

import dataclasses
import datetime
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt

from .data_holder import EcoflowDataHolder

_LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class EcoflowBroadcastDataHolder:
    data_holder: EcoflowDataHolder
    changed: bool


class DeviceDataCoordinator(DataUpdateCoordinator[EcoflowBroadcastDataHolder]):
    def __init__(self, hass: HomeAssistant, holder: EcoflowDataHolder, refresh_period: int) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Ecoflow update coordinator",
            always_update=True,
            update_interval=datetime.timedelta(seconds=max(refresh_period, 5)),
        )
        self.holder = holder
        self.__last_broadcast = dt.utcnow().replace(year=2000, month=1, day=1, hour=0, minute=0, second=0)

    async def _async_update_data(self) -> EcoflowBroadcastDataHolder:
        received_time = self.holder.last_received_time()
        changed = self.__last_broadcast < received_time
        self.__last_broadcast = received_time
        return EcoflowBroadcastDataHolder(self.holder, changed)
