from collections import OrderedDict

from custom_components.ecoflow_cloud.devices import BaseDevice, DiagnosticDevice
from custom_components.ecoflow_cloud.devices.internal import (
    alternator as internal_alternator,
)
from custom_components.ecoflow_cloud.devices.internal import (
    delta2 as internal_delta2,
)
from custom_components.ecoflow_cloud.devices.internal import (
    delta2_max as internal_delta2_max,
)
from custom_components.ecoflow_cloud.devices.internal import (
    delta3 as internal_delta3,
)
from custom_components.ecoflow_cloud.devices.internal import (
    delta3_1500 as internal_delta3_1500,
)
from custom_components.ecoflow_cloud.devices.internal import (
    delta_max as internal_delta_max,
)
from custom_components.ecoflow_cloud.devices.internal import (
    delta_mini as internal_delta_mini,
)
from custom_components.ecoflow_cloud.devices.internal import (
    delta_pro as internal_delta_pro,
)
from custom_components.ecoflow_cloud.devices.internal import (
    delta_pro_3 as internal_delta_pro_3,
)
from custom_components.ecoflow_cloud.devices.internal import (
    delta_pro_ultra_x as internal_delta_pro_ultra_x,
)
from custom_components.ecoflow_cloud.devices.internal import (
    glacier as internal_glacier,
)
from custom_components.ecoflow_cloud.devices.internal import (
    glacier_classic as internal_glacier_classic,
)
from custom_components.ecoflow_cloud.devices.internal import (
    powerstream as internal_powerstream,
)
from custom_components.ecoflow_cloud.devices.internal import (
    river2 as internal_river2,
)
from custom_components.ecoflow_cloud.devices.internal import (
    river2_max as internal_river2_max,
)
from custom_components.ecoflow_cloud.devices.internal import (
    river2_pro as internal_river2_pro,
)
from custom_components.ecoflow_cloud.devices.internal import (
    river3 as internal_river3,
)
from custom_components.ecoflow_cloud.devices.internal import (
    river_max as internal_river_max,
)
from custom_components.ecoflow_cloud.devices.internal import (
    river_mini as internal_river_mini,
)
from custom_components.ecoflow_cloud.devices.internal import (
    river_pro as internal_river_pro,
)
from custom_components.ecoflow_cloud.devices.internal import (
    smart_home_panel_3 as internal_smart_home_panel_3,
)
from custom_components.ecoflow_cloud.devices.internal import (
    smart_meter as internal_smart_meter,
)
from custom_components.ecoflow_cloud.devices.internal import (
    smart_plug as internal_smart_plug,
)
from custom_components.ecoflow_cloud.devices.internal import (
    stream_ac as internal_stream_ac,
)
from custom_components.ecoflow_cloud.devices.internal import (
    wave2 as internal_wave2,
)
from custom_components.ecoflow_cloud.devices.internal import (
    wave3 as internal_wave3,
)
from custom_components.ecoflow_cloud.devices.public import (
    delta2 as public_delta2,
)
from custom_components.ecoflow_cloud.devices.public import (
    delta2_max as public_delta2_max,
)
from custom_components.ecoflow_cloud.devices.public import (
    # delta3 as public_delta3,
    delta3_max_plus as public_delta3_max_plus,
)
from custom_components.ecoflow_cloud.devices.public import (
    delta_max as public_delta_max,
)
from custom_components.ecoflow_cloud.devices.public import (
    delta_pro as public_delta_pro,
)
from custom_components.ecoflow_cloud.devices.public import (
    delta_pro_3 as public_delta_pro_3,
)
from custom_components.ecoflow_cloud.devices.public import (
    delta_pro_ultra as public_delta_pro_ultra,
)
from custom_components.ecoflow_cloud.devices.public import (
    powerkit as public_powerkit,
)
from custom_components.ecoflow_cloud.devices.public import (
    powerocean as public_powerocean,
)
from custom_components.ecoflow_cloud.devices.public import (
    powerstream as public_powerstream,
)
from custom_components.ecoflow_cloud.devices.public import (
    # river2 as public_river2,
    # river2_max as public_river2_max,
    river2_pro as public_river2_pro,
)
from custom_components.ecoflow_cloud.devices.public import (
    smart_home_panel as public_smart_home_panel,
)
from custom_components.ecoflow_cloud.devices.public import (
    smart_home_panel_2 as public_smart_home_panel_2,
)
from custom_components.ecoflow_cloud.devices.public import (
    smart_meter as public_smart_meter,
)
from custom_components.ecoflow_cloud.devices.public import (
    smart_plug as public_smart_plug,
)
from custom_components.ecoflow_cloud.devices.public import (
    stream_ac as public_stream_ac,
)
from custom_components.ecoflow_cloud.devices.public import (
    stream_microinverter as public_stream_microinverter,
)
from custom_components.ecoflow_cloud.devices.public import (
    wave2 as public_wave2,
)

devices: OrderedDict[str, type[BaseDevice]] = OrderedDict[str, type[BaseDevice]](
    {
        "ALTERNATOR": internal_alternator.Alternator,
        "DELTA_2": internal_delta2.Delta2,
        "DELTA_3": internal_delta3.Delta3,
        "DELTA_3_1500": internal_delta3_1500.Delta31500,
        "DELTA_3_MAX_PLUS": internal_delta3.Delta3,
        "RIVER_2": internal_river2.River2,
        "RIVER_2_MAX": internal_river2_max.River2Max,
        "RIVER_2_PRO": internal_river2_pro.River2Pro,
        "RIVER_3": internal_river3.River3,
        "DELTA_PRO": internal_delta_pro.DeltaPro,
        "DELTA_PRO_3": internal_delta_pro_3.DeltaPro3,
        "DELTA_PRO_ULTRA_X": internal_delta_pro_ultra_x.DeltaProUltraX,
        "SMART_HOME_PANEL_3": internal_smart_home_panel_3.SmartHomePanel3,
        "RIVER_MAX": internal_river_max.RiverMax,
        "RIVER_PRO": internal_river_pro.RiverPro,
        "RIVER_MINI": internal_river_mini.RiverMini,
        "DELTA_MINI": internal_delta_mini.DeltaMini,
        "DELTA_MAX": internal_delta_max.DeltaMax,
        "DELTA_2_MAX": internal_delta2_max.Delta2Max,
        "POWERSTREAM": internal_powerstream.PowerStream,
        "GLACIER": internal_glacier.Glacier,
        "GLACIER_CLASSIC": internal_glacier_classic.GlacierClassic,
        "WAVE_2": internal_wave2.Wave2,
        "WAVE_3": internal_wave3.Wave3,
        "SMART_METER": internal_smart_meter.SmartMeter,
        "SMART_PLUG": internal_smart_plug.SmartPlug,
        "STREAM_AC": internal_stream_ac.StreamAC,
        "STREAM_PRO": internal_stream_ac.StreamAC,
        "STREAM_ULTRA": internal_stream_ac.StreamAC,
        "DIAGNOSTIC": DiagnosticDevice,
    }
)

device_by_product: OrderedDict[str, type[BaseDevice]] = OrderedDict[str, type[BaseDevice]](
    {
        "DELTA Max": public_delta_max.DeltaMax,
        "DELTA Pro": public_delta_pro.DeltaPro,
        "DELTA Pro Ultra": public_delta_pro_ultra.DeltaProUltra,
        "DELTA 2": public_delta2.Delta2,
        "DELTA 2 Max": public_delta2_max.Delta2Max,
        # "DELTA 3": public_delta3.Delta3,
        # "RIVER 2": public_river2.River2,
        # "RIVER 2 Max": public_river2_max.River2Max,
        "RIVER 2 Pro": public_river2_pro.River2Pro,
        "Smart Plug": public_smart_plug.SmartPlug,
        "PowerStream": public_powerstream.PowerStream,
        "WAVE 2": public_wave2.Wave2,
        "Delta Pro 3": public_delta_pro_3.DeltaPro3,
        "DELTA 3 Max Plus": public_delta3_max_plus.Delta3MaxPlus,
        "Power Kits": public_powerkit.PowerKit,
        "Smart Meter": public_smart_meter.SmartMeter,
        "Stream AC": public_stream_ac.StreamAC,
        "Stream PRO": public_stream_ac.StreamAC,
        "Stream Ultra": public_stream_ac.StreamAC,
        "Stream Microinverter": public_stream_microinverter.StreamMicroinveter,
        "Smart Home Panel": public_smart_home_panel.SmartHomePanel,
        "Smart Home Panel 2": public_smart_home_panel_2.SmartHomePanel2,
        "Power Ocean": public_powerocean.PowerOcean,
        "Diagnostic": DiagnosticDevice,
    }
)

device_support_sub_devices = ["Power Kits"]
