from custom_components.ecoflow_cloud.config_flow import EcoflowModel
from custom_components.ecoflow_cloud.devices import BaseDevice, DiagnosticDevice
from custom_components.ecoflow_cloud.devices.delta2 import Delta2
from custom_components.ecoflow_cloud.devices.delta_pro import DeltaPro
from custom_components.ecoflow_cloud.devices.river2 import River2
from custom_components.ecoflow_cloud.devices.river2max import River2Max
from custom_components.ecoflow_cloud.devices.river_max import RiverMax
from custom_components.ecoflow_cloud.devices.river_pro import RiverPro

devices: dict[str, BaseDevice] = {
    EcoflowModel.DELTA_2.name: Delta2(),
    EcoflowModel.RIVER_2.name: River2(),
    EcoflowModel.RIVER_2_MAX.name: River2Max(),
    EcoflowModel.DELTA_PRO.name: DeltaPro(),
    EcoflowModel.RIVER_MAX.name: RiverMax(),
    EcoflowModel.RIVER_PRO.name: RiverPro(),
    EcoflowModel.DIAGNOSTIC.name: DiagnosticDevice()
}
