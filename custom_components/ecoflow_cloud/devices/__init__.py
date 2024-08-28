import dataclasses
import datetime
import json
import logging
from abc import ABC, abstractmethod

from homeassistant.components.button import ButtonEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt

from .data_holder import EcoflowDataHolder
from ..api import EcoflowApiClient

_LOGGER = logging.getLogger(__name__)

@dataclasses.dataclass
class EcoflowDeviceInfo:
    public_api: bool
    sn: str
    name: str
    device_type: str
    status: int
    data_topic: str
    set_topic: str
    set_reply_topic: str
    get_topic: str | None
    get_reply_topic: str | None
    status_topic: str | None = None

    def topics(self) -> list[str]:
        topics = [
            self.data_topic,
            self.get_topic,
            self.get_reply_topic,
            self.set_topic,
            self.set_reply_topic,
            self.status_topic
        ]
        return list(filter(lambda v: v is not None, topics))

@dataclasses.dataclass
class EcoflowBroadcastDataHolder:
    data_holder: EcoflowDataHolder
    changed: bool

class EcoflowDeviceUpdateCoordinator(DataUpdateCoordinator[EcoflowBroadcastDataHolder]):
    def __init__(self, hass, holder: EcoflowDataHolder, refresh_period: int) -> None:
        """Initialize the coordinator."""
        super().__init__(hass, _LOGGER, name="Ecoflow update coordinator", always_update=True,
                         update_interval= datetime.timedelta(seconds=max(refresh_period, 5)),
        )
        self.holder = holder
        self.__last_broadcast = dt.utcnow().replace(year=2000, month=1, day=1, hour=0, minute=0, second=0)

    async def _async_update_data(self) -> EcoflowBroadcastDataHolder:
        received_time = self.holder.last_received_time()
        changed = self.__last_broadcast < received_time
        self.__last_broadcast = received_time
        return EcoflowBroadcastDataHolder(self.holder, changed)

class BaseDevice(ABC):

    def __init__(self, device_info: EcoflowDeviceInfo):
        super().__init__()
        self.coordinator = None
        self.data = None
        self.device_info: EcoflowDeviceInfo = device_info
        self.power_step: int = -1

    def configure(self, hass: HomeAssistant, refresh_period: int, diag: bool = False):
        self.data = EcoflowDataHolder(diag)
        self.coordinator = EcoflowDeviceUpdateCoordinator(hass, self.data, refresh_period)

    @staticmethod
    def default_charging_power_step() -> int:
        return 100

    def charging_power_step(self) -> int:
        if self.power_step == -1:
            return self.default_charging_power_step()
        else:
            return self.power_step

    def flat_json(self) -> bool:
        return True

    @abstractmethod
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        pass

    @abstractmethod
    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        pass

    @abstractmethod
    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        pass

    @abstractmethod
    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        pass

    def buttons(self, client: EcoflowApiClient) -> list[ButtonEntity]:
        return []

    def update_data(self, raw_data, data_type: str) -> bool:
        if data_type == self.device_info.data_topic:
            raw = self._prepare_data(raw_data)
            self.data.update_data(raw)
        elif data_type == self.device_info.set_topic:
            raw = self._prepare_data(raw_data)
            self.data.add_set_message(raw)
        elif data_type == self.device_info.set_reply_topic:
            raw = self._prepare_data(raw_data)
            self.data.add_set_reply_message(raw)
        elif data_type == self.device_info.get_topic:
            raw = self._prepare_data(raw_data)
            self.data.add_get_message(raw)
        elif data_type == self.device_info.get_reply_topic:
            raw = self._prepare_data(raw_data)
            self.data.add_get_reply_message(raw)
        else:
            return False
        return True


    def _prepare_data(self, raw_data) -> dict[str, any]:
        try:
            try:
                payload = raw_data.decode("utf-8", errors='ignore')
                return json.loads(payload)
            except UnicodeDecodeError as error:
                _LOGGER.warning(f"UnicodeDecodeError: {error}. Trying to load json.")
                return json.loads(raw_data)
            except Exception as error:
                _LOGGER.warning(f"Exception: {error}. Trying to load json.")
                return json.loads(raw_data)
        except Exception as error1:
            _LOGGER.error(f"constant: {error1}. Ignoring message and waiting for the next one.")

class DiagnosticDevice(BaseDevice):

    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return []

    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return []

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return []

    def buttons(self, client: EcoflowApiClient) -> list[ButtonEntity]:
        return []

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return []
