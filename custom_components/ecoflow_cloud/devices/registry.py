from typing import Type, OrderedDict

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
from .public import (delta_pro as public_delta_pro,
                     delta2 as public_delta2,
                     delta2_max as public_delta2_max,
                     river2 as public_river2,
                     river2_max as public_river2_max,
                     river2_pro as public_river2_pro,
                     smart_plug as public_smart_plug,
                     powerstream as public_powerstream,
                     )
from ..devices import BaseDevice, DiagnosticDevice

devices: OrderedDict[str, Type[BaseDevice]] = OrderedDict[str, Type[BaseDevice]]({
    "DELTA_2": internal_delta2.Delta2,
    "RIVER_2": internal_river2.River2,
    "RIVER_2_MAX": internal_river2_max.River2Max,
    "RIVER_2_PRO": internal_river2_pro.River2Pro,
    "DELTA_PRO": internal_delta_pro.DeltaPro,
    "RIVER_MAX": internal_river_max.RiverMax,
    "RIVER_PRO": internal_river_pro.RiverPro,
    "RIVER_MINI": internal_river_mini.RiverMini,
    "DELTA_MINI": internal_delta_mini.DeltaMini,
    "DELTA_MAX": internal_delta_max.DeltaMax,
    "DELTA_2_MAX": internal_delta2_max.Delta2Max,
    "POWERSTREAM": internal_powerstream.PowerStream,
    "GLACIER": internal_glacier.Glacier,
    "WAVE_2": internal_wave2.Wave2,
    "DIAGNOSTIC": DiagnosticDevice
})

device_by_product: OrderedDict[str, Type[BaseDevice]] = OrderedDict[str, Type[BaseDevice]]({
    "DELTA Pro": public_delta_pro.DeltaPro,
    "DELTA 2": public_delta2.Delta2,
    "DELTA 2 Max": public_delta2_max.Delta2Max,
    "RIVER 2": public_river2.River2,
    "RIVER 2 Max": public_river2_max.River2Max,
    "RIVER 2 Pro": public_river2_pro.River2Pro,
    "Smart Plug": public_smart_plug.SmartPlug,
    "PowerStream": public_powerstream.PowerStream,
    "Diagnostic": DiagnosticDevice
})