from __future__ import annotations  # for DeviceData.parent: DeviceData

import dataclasses


@dataclasses.dataclass
class DeviceOptions:
    refresh_period: int
    power_step: int
    diagnostic_mode: bool


@dataclasses.dataclass
class DeviceData:
    sn: str
    name: str
    device_type: str
    options: DeviceOptions
    display_name: str | None
    parent: DeviceData | None
