import dataclasses
from typing import Any


@dataclasses.dataclass
class DeviceOptions:
    refresh_period: int
    power_step: int
    diagnostic_mode: bool


class DeviceOptionsImport(DeviceOptions):
    def __init__(self, data: dict[str, Any]):
        self.refresh_period = data["refresh_period"]
        self.power_step = data["power_step"]
        self.diagnostic_mode = data["diagnostic_mode"]
