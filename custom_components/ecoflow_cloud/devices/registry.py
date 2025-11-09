from collections import OrderedDict
from typing import Type

from custom_components.ecoflow_cloud.devices import BaseDevice, DiagnosticDevice

from .internal import (
    delta2 as internal_delta2,
    delta2_max as internal_delta2_max,
    delta3 as internal_delta3,
    delta_max as internal_delta_max,
    delta_mini as internal_delta_mini,
    delta_pro as internal_delta_pro,
    delta_pro_3 as internal_delta_pro_3,
    glacier as internal_glacier,
    powerstream as internal_powerstream,
    river2 as internal_river2,
    river2_max as internal_river2_max,
    river2_pro as internal_river2_pro,
    river3 as internal_river3,
    river_max as internal_river_max,
    river_mini as internal_river_mini,
    river_pro as internal_river_pro,
    smart_meter as internal_smart_meter,
    stream_ac as internal_stream_ac,
    wave2 as internal_wave2,
)
from .public import (
    delta2 as public_delta2,
    delta2_max as public_delta2_max,
    delta3 as public_delta3,
    delta_max as public_delta_max,
    delta_pro as public_delta_pro,
    delta_pro_3 as public_delta_pro_3,
    delta_pro_ultra as public_delta_pro_ultra,
    powerkit as public_powerkit,
    powerstream as public_powerstream,
    river2 as public_river2,
    river2_max as public_river2_max,
    river2_pro as public_river2_pro,
    smart_home_panel_2 as public_smart_home_panel_2,
    smart_meter as public_smart_meter,
    smart_plug as public_smart_plug,
    stream_ac as public_stream_ac,
    stream_microinverter as public_stream_microinverter,
    wave2 as public_wave2,
    powerocean as public_powerocean,
)

devices: OrderedDict[str, Type[BaseDevice]] = OrderedDict[str, Type[BaseDevice]](
    {
        "DELTA_2": internal_delta2.Delta2,
        "DELTA_3": internal_delta3.Delta3,
        "RIVER_2": internal_river2.River2,
        "RIVER_2_MAX": internal_river2_max.River2Max,
        "RIVER_2_PRO": internal_river2_pro.River2Pro,
        "RIVER_3": internal_river3.River3,
        "DELTA_PRO": internal_delta_pro.DeltaPro,
        "DELTA_PRO_3": internal_delta_pro_3.DeltaPro3,
        "RIVER_MAX": internal_river_max.RiverMax,
        "RIVER_PRO": internal_river_pro.RiverPro,
        "RIVER_MINI": internal_river_mini.RiverMini,
        "DELTA_MINI": internal_delta_mini.DeltaMini,
        "DELTA_MAX": internal_delta_max.DeltaMax,
        "DELTA_2_MAX": internal_delta2_max.Delta2Max,
        "POWERSTREAM": internal_powerstream.PowerStream,
        "GLACIER": internal_glacier.Glacier,
        "WAVE_2": internal_wave2.Wave2,
        "SMART_METER": internal_smart_meter.SmartMeter,
        "STREAM_AC": internal_stream_ac.StreamAC,
        "STREAM_PRO": internal_stream_ac.StreamAC,
        "STREAM_ULTRA": internal_stream_ac.StreamAC,
        "DIAGNOSTIC": DiagnosticDevice,
    }
)

device_by_product: OrderedDict[str, Type[BaseDevice]] = OrderedDict[
    str, Type[BaseDevice]
](
    {
        "DELTA Max": public_delta_max.DeltaMax,
        "DELTA Pro": public_delta_pro.DeltaPro,
        "DELTA Pro Ultra": public_delta_pro_ultra.DeltaProUltra,
        "DELTA 2": public_delta2.Delta2,
        "DELTA 2 Max": public_delta2_max.Delta2Max,
        "DELTA 3": public_delta3.Delta3,
        "RIVER 2": public_river2.River2,
        "RIVER 2 Max": public_river2_max.River2Max,
        "RIVER 2 Pro": public_river2_pro.River2Pro,
        "Smart Plug": public_smart_plug.SmartPlug,
        "PowerStream": public_powerstream.PowerStream,
        "WAVE 2": public_wave2.Wave2,
        "Delta Pro 3": public_delta_pro_3.DeltaPro3,
        "Power Kits": public_powerkit.PowerKit,
        "Smart Meter": public_smart_meter.SmartMeter,
        "Stream AC": public_stream_ac.StreamAC,
        "Stream PRO": public_stream_ac.StreamAC,
        "Stream Ultra": public_stream_ac.StreamAC,
        "Stream Microinverter" : public_stream_microinverter.StreamMicroinveter,
        "Smart Home Panel 2": public_smart_home_panel_2.SmartHomePanel2,
        "Power Ocean": public_powerocean.PowerOcean,
        "Diagnostic": DiagnosticDevice,
    }
)

device_support_sub_devices = ["Power Kits"]
