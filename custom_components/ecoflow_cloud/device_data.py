from __future__ import annotations  # for DeviceData.parent: DeviceData

import dataclasses


@dataclasses.dataclass
class DeviceOptions:
    refresh_period: int
    power_step: int
    diagnostic_mode: bool
    verbose_status_mode: bool
    assume_offline_sec: int
    ble_wifi_recovery_enabled: bool
    ble_wifi_ssid: str
    ble_wifi_password: str
    ble_wifi_bssid: str
    ble_wifi_channel: int | None
    ble_recovery_timeout_sec: int
    ble_recovery_cooldown_sec: int


@dataclasses.dataclass
class DeviceData:
    sn: str
    name: str
    device_type: str
    options: DeviceOptions
    display_name: str | None
    parent: DeviceData | None
