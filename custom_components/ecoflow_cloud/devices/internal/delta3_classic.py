"""EcoFlow DELTA 3 Classic device implementation.

The DELTA 3 Classic uses the same private MQTT/protobuf channel, telemetry field
numbers and control commands as the DELTA 3, so it reuses the whole Delta3
decode path and command builders (including Grid Bypass, tested on hardware in
both directions). It differs in two ways:

1. The 12 V output reports ``flow_info_12v = 0`` (not 4) when switched off, so
   the DC (12V) Enabled switch would otherwise stay unknown.
2. It never reports ``plug_in_info_pv_dc_amp_max`` (not even in the get-all
   snapshot), so the DC (12V) Charge Current select would stay unknown and is
   left out. The app's "car charging current" (4-8 A) is not in any declared
   field either: with it set to 6 A, ``plug_in_info_pv_chg_amp_max`` still
   reported 8.
"""

from typing import Any, override

from homeassistant.components.select import SelectEntity

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import const
from custom_components.ecoflow_cloud.devices.internal.delta3 import Delta3
from custom_components.ecoflow_cloud.entities import EcoFlowAbstractEntity


class Delta3Classic(Delta3):
    """EcoFlow DELTA 3 Classic."""

    @override
    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return [
            s
            for s in super().selects(client)
            if not (isinstance(s, EcoFlowAbstractEntity) and s.title() == const.DC_CHARGE_CURRENT)
        ]

    @override
    def _decode_message_by_type(self, pdata: bytes, header_info: dict[str, Any]) -> dict[str, Any]:
        result = super()._decode_message_by_type(pdata, header_info)
        # The DELTA 3 maps flow_info_12v 14 -> on and 4 -> off; the Classic
        # sends 0 for off.
        if result.get("flow_info_12v") == 0 and "cfg_dc12v_out_open" not in result:
            result["cfg_dc12v_out_open"] = 0
        return result
