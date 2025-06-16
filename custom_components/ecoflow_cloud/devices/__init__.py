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
from .. import DeviceData

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

    quota_all: str = "/iot-open/sign/device/quota/all"

    def topics(self) -> list[str]:
        topics = [
            self.data_topic,
            self.get_topic,
            self.get_reply_topic,
            self.set_topic,
            self.set_reply_topic,
            self.status_topic,
        ]
        return list(filter(lambda v: v is not None, topics))


@dataclasses.dataclass
class EcoflowBroadcastDataHolder:
    data_holder: EcoflowDataHolder
    changed: bool


class EcoflowDeviceUpdateCoordinator(DataUpdateCoordinator[EcoflowBroadcastDataHolder]):
    def __init__(self, hass, holder: EcoflowDataHolder, refresh_period: int) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Ecoflow update coordinator",
            always_update=True,
            update_interval=datetime.timedelta(seconds=max(refresh_period, 5)),
        )
        self.holder = holder
        self.__last_broadcast = dt.utcnow().replace(
            year=2000, month=1, day=1, hour=0, minute=0, second=0
        )

    async def _async_update_data(self) -> EcoflowBroadcastDataHolder:
        received_time = self.holder.last_received_time()
        changed = self.__last_broadcast < received_time
        self.__last_broadcast = received_time
        return EcoflowBroadcastDataHolder(self.holder, changed)


class BaseDevice(ABC):
    def __init__(self, device_info: EcoflowDeviceInfo, device_data: DeviceData):
        super().__init__()
        self.coordinator = None
        self.data = None
        self.device_info: EcoflowDeviceInfo = device_info
        self.power_step: int = device_data.options.power_step
        self.device_data: DeviceData = device_data

    def configure(self, hass: HomeAssistant):
        if self.device_data.parent is not None:
            self.data = EcoflowDataHolder(
                self.device_data.sn, self.device_data.options.diagnostic_mode
            )
        else:
            self.data = EcoflowDataHolder(
                None, self.device_data.options.diagnostic_mode
            )
        self.coordinator = EcoflowDeviceUpdateCoordinator(
            hass, self.data, self.device_data.options.refresh_period
        )

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
            raw = self._prepare_data_data_topic(raw_data)
            self.data.update_data(raw)
        elif data_type == self.device_info.set_topic:
            raw = self._prepare_data_set_topic(raw_data)
            self.data.add_set_message(raw)
        elif data_type == self.device_info.set_reply_topic:
            raw = self._prepare_data_set_reply_topic(raw_data)
            self.data.add_set_reply_message(raw)
        elif data_type == self.device_info.get_topic:
            raw = self._prepare_data_get_topic(raw_data)
            self.data.add_get_message(raw)
        elif data_type == self.device_info.get_reply_topic:
            raw = self._prepare_data_get_reply_topic(raw_data)
            self.data.add_get_reply_message(raw)
        else:
            return False
        return True

    def _prepare_data_data_topic(self, raw_data) -> dict[str, any]:
        return self._prepare_data(raw_data)

    def _prepare_data_set_topic(self, raw_data) -> dict[str, any]:
        return self._prepare_data(raw_data)

    def _prepare_data_set_reply_topic(self, raw_data) -> dict[str, any]:
        return self._prepare_data(raw_data)

    def _prepare_data_get_topic(self, raw_data) -> dict[str, any]:
        return self._prepare_data(raw_data)

    def _prepare_data_get_reply_topic(self, raw_data) -> dict[str, any]:
        return self._prepare_data(raw_data)

    def _prepare_data(self, raw_data) -> dict[str, any]:
        try:
            # Check if data is binary protobuf data (contains non-printable characters)
            if isinstance(raw_data, bytes):
                # Try to detect if this is binary protobuf data
                if self._is_binary_data(raw_data):
                    _LOGGER.warning("Received binary protobuf data but device doesn't override _prepare_data(). "
                                  "This device may need protobuf support. Skipping message.")
                    return {}
                
            # Try UTF-8 decoding for JSON data
            try:
                if isinstance(raw_data, bytes):
                    payload = raw_data.decode("utf-8")
                else:
                    payload = raw_data
                return json.loads(payload)
            except UnicodeDecodeError as error:
                _LOGGER.warning(f"UnicodeDecodeError: {error}. Data may be binary protobuf format.")
                return {}
            except json.JSONDecodeError as error:
                _LOGGER.warning(f"JSON decode error: {error}. Invalid JSON format.")
                return {}
        except Exception as error1:
            _LOGGER.error(
                f"Data processing error: {error1}. Ignoring message and waiting for the next one."
            )
            return {}

    def _is_binary_data(self, data: bytes) -> bool:
        """Check if data contains binary protobuf indicators."""
        if len(data) < 4:
            return False
        
        # Check for common protobuf binary patterns
        # Protobuf messages often start with field tags (low values)
        first_bytes = data[:4]
        
        # Check for high concentration of non-printable characters
        non_printable_count = sum(1 for byte in first_bytes if byte < 32 or byte > 126)
        
        # If more than half the first bytes are non-printable, likely binary
        return non_printable_count >= 2


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
