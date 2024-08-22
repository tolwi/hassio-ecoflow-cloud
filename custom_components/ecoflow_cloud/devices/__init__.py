import dataclasses
import json
import logging
from abc import ABC, abstractmethod

from homeassistant.components.button import ButtonEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity

from .data_holder import EcoflowDataHolder
from ..api import EcoflowApiClient

_LOGGER = logging.getLogger(__name__)

@dataclasses.dataclass
class EcoflowDeviceInfo:
    public_api: bool
    sn: str
    name: str
    device_type: str
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


class BaseDevice(ABC):

    data: EcoflowDataHolder = None
    device_info: EcoflowDeviceInfo = None

    def __init__(self, device_info: EcoflowDeviceInfo):
        super().__init__()
        self.device_info = device_info
        self.serial_number = device_info.sn

    def configure(self, refresh_period: int, diag: bool = False):
        self.data = EcoflowDataHolder(refresh_period, diag)

    @staticmethod
    def charging_power_step() -> int:
        return 100

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
