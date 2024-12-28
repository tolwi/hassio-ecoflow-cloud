from custom_components.ecoflow_cloud.DeviceOptions import (
    DeviceOptions,
    DeviceOptionsImport,
)
from typing import Any

import dataclasses


@dataclasses.dataclass
class DeviceData:
    sn: str
    name: str
    device_type: str
    options: DeviceOptions


class DeviceDataImport(DeviceData):
    def __init__(self, data: dict[str, Any]):
        self.sn = data["sn"]
        self.name = data["name"]
        self.device_type = data["device_type"]
        self.options = DeviceOptionsImport(data.get("options", {}))


@dataclasses.dataclass
class ChildDeviceData(DeviceData):
    parent: DeviceData


class ChildDeviceDataImport(ChildDeviceData):
    def __init__(self, data: dict[str, Any]):
        self.sn = data["sn"]
        self.name = data["name"]
        self.device_type = data["device_type"]
        self.options = DeviceOptionsImport(data.get("options", {}))
        self.parent = DeviceDataImport(data["parent"])


class DeviceDataImportFactory:
    @staticmethod
    def create(data: dict[str, Any]) -> DeviceData:
        if "parent" in data:
            return ChildDeviceDataImport(data)
        return DeviceDataImport(data)
