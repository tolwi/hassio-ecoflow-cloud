from typing import Type

from .internal import (delta2 as internal_delta2,
                       river2 as internal_river2,
                       river2_max as internal_river2_max,
                       river2_pro as internal_river2_pro,
                       delta2_max as internal_delta2_max,
                       delta_pro as internal_delta_pro,
                       river_max as internal_river_max,
                       river_pro as internal_river_pro,
                       river_mini as internal_river_mini,
                       delta_mini as internal_delta_mini,
                       delta_max as internal_delta_max,
                       powerstream as internal_powerstream,
                       glacier as internal_glacier,
                       wave2 as internal_wave2, )
from .public import (delta2 as public_delta2,
                     river2 as public_river2,
                     river2_max as public_river2_max,
                     smart_plug as public_smart_plug,
                     )
from ..config.const import EcoflowModel
from ..devices import BaseDevice, DiagnosticDevice

devices: dict[str, Type[BaseDevice]] = {
    EcoflowModel.DELTA_2.name: internal_delta2.Delta2,
    EcoflowModel.RIVER_2.name: internal_river2.River2,
    EcoflowModel.RIVER_2_MAX.name: internal_river2_max.River2Max,
    EcoflowModel.RIVER_2_PRO.name: internal_river2_pro.River2Pro,
    EcoflowModel.DELTA_PRO.name: internal_delta_pro.DeltaPro,
    EcoflowModel.RIVER_MAX.name: internal_river_max.RiverMax,
    EcoflowModel.RIVER_PRO.name: internal_river_pro.RiverPro,
    EcoflowModel.RIVER_MINI.name: internal_river_mini.RiverMini(),
    EcoflowModel.DELTA_MINI.name: internal_delta_mini.DeltaMini,
    EcoflowModel.DELTA_MAX.name: internal_delta_max.DeltaMax,
    EcoflowModel.DELTA_2_MAX.name: internal_delta2_max.Delta2Max,
    EcoflowModel.POWERSTREAM.name: internal_powerstream.PowerStream,
    EcoflowModel.GLACIER.name: internal_glacier.Glacier,
    EcoflowModel.WAVE_2.name: internal_wave2.Wave2,
    EcoflowModel.DIAGNOSTIC.name: DiagnosticDevice
}

device_by_product: dict[str, Type[BaseDevice]] = {
    "DELTA 2": public_delta2.Delta2,
    "RIVER 2": public_river2.River2,
    "RIVER 2 Max": public_river2_max.River2Max,
    "Smart Plug": public_smart_plug.SmartPlug # key is not verified
}