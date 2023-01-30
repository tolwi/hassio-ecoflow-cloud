from custom_components.ecoflow_cloud.config_flow import EcoflowModel
from custom_components.ecoflow_cloud.devices import BaseDevice
from custom_components.ecoflow_cloud.devices.delta2 import Delta2
from custom_components.ecoflow_cloud.devices.delta_pro import DeltaPro
from custom_components.ecoflow_cloud.devices.river2max import River2Max

devices: dict[str, BaseDevice] = {
        EcoflowModel.DELTA_2.name: Delta2(),
        EcoflowModel.RIVER_2_MAX.name: River2Max(),
        EcoflowModel.DELTA_PRO.name: DeltaPro(),
        EcoflowModel.RIVER_MAX.name: River2Max()
}