"""EcoFlow Delta 3 Plus device implementation.

The Delta 3 Plus is a dual-MPPT variant of the Delta 3. It shares the Delta 3
core-telemetry field numbers and the Delta 3 control-command (set_dp3) field
numbers, so it reuses the entire Delta3 decode path and command builders. The
only difference is solar: the Plus reports a second MPPT channel (channel 2)
in addition to channel 1. This subclass adds the channel-2 solar sensors on
top of the inherited Delta 3 entity set.
"""

from typing import override

from homeassistant.components.sensor import SensorEntity

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices.internal.delta3 import Delta3
from custom_components.ecoflow_cloud.sensor import (
    InMilliampSensorEntity,
    InVoltSensorEntity,
    InWattsSensorEntity,
    TempSensorEntity,
)


class Delta3Plus(Delta3):
    """EcoFlow Delta 3 Plus (dual-MPPT solar)."""

    @override
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        sensors = super().sensors(client)
        # The Delta 3 Plus reports a second MPPT channel (channel 2) in addition
        # to the single channel the base Delta 3 decodes. Add its solar sensors.
        sensors.append(InWattsSensorEntity(client, self, "pow_get_pv2", "Solar Input Power (MPPT 2)"))
        sensors.append(InVoltSensorEntity(client, self, "plug_in_info_pv2_vol", "Solar Input Voltage (MPPT 2)"))
        sensors.append(InMilliampSensorEntity(client, self, "plug_in_info_pv2_amp", "Solar Input Current (MPPT 2)"))
        sensors.append(TempSensorEntity(client, self, "temp_pv2", "Solar PV Temperature (MPPT 2)"))
        return sensors
