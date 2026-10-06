from collections.abc import Sequence
from typing import Any, override

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import PERCENTAGE, UnitOfTime

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.binary_sensor import MiscBinarySensorEntity
from custom_components.ecoflow_cloud.devices import BaseInternalDevice, const
from custom_components.ecoflow_cloud.entities import BaseSensorEntity
from custom_components.ecoflow_cloud.sensor import (
    MilliampSensorEntity,
    MilliVoltSensorEntity,
    MiscSensorEntity,
    OutWattsSensorEntity,
    QuotaStatusSensorEntity,
    TempSensorEntity,
    WattsSensorEntity,
)
from custom_components.ecoflow_cloud.switch import EnabledEntity


_MODULE_TYPE = 2


class _FuelLevelSensorEntity(BaseSensorEntity):
    # Not SensorDeviceClass.BATTERY: this is the fuel tank, not a battery.
    _attr_icon = "mdi:gas-station"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT


class _MinutesSensorEntity(BaseSensorEntity):
    # RemainSensorEntity clamps to 5000 min, too low for the generator's
    # remaining time (up to 5999) and for its cumulative motor run time.
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_state_class = SensorStateClass.MEASUREMENT

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(max(int(val), 0))


class _RunTimeSensorEntity(_MinutesSensorEntity):
    _attr_state_class = SensorStateClass.TOTAL_INCREASING


def _command(operate_type: str, params: dict[str, Any]) -> dict[str, Any]:
    return {"moduleType": _MODULE_TYPE, "operateType": operate_type, "params": params}


class SmartGenerator(BaseInternalDevice):
    """EcoFlow Smart Generator (gasoline and Dual Fuel)."""

    @override
    def sensors(self, client: EcoflowApiClient) -> Sequence[SensorEntity]:
        return [
            OutWattsSensorEntity(client, self, "pd.acPower", const.AC_OUT_POWER),
            OutWattsSensorEntity(client, self, "pd.dcPower", const.DC_OUT_POWER),
            OutWattsSensorEntity(client, self, "pd.totalPower", const.TOTAL_OUT_POWER),
            WattsSensorEntity(client, self, "pd.oilMaxOutPower", const.GEN_MAX_OUTPUT_POWER),
            _FuelLevelSensorEntity(client, self, "pd.oilVal", "Fuel Level"),
            _MinutesSensorEntity(client, self, "pd.remainTime", const.REMAINING_TIME),
            _RunTimeSensorEntity(client, self, "pd.motorUseTime", "Motor Run Time"),
            MilliVoltSensorEntity(client, self, "pd.acVol", const.AC_OUT_VOLT),
            MilliVoltSensorEntity(client, self, "pd.dcVol", const.DC_OUT_VOLTAGE),
            MilliampSensorEntity(client, self, "pd.acCur", "AC Out Current"),
            MilliampSensorEntity(client, self, "pd.dcCur", "DC Out Current"),
            TempSensorEntity(client, self, "pd.temp", const.TEMPERATURE),
            MiscSensorEntity(client, self, "pd.sysMode", "System Mode", diagnostic=True),
            MiscSensorEntity(client, self, "pd.errCode", const.ERROR_CODE, diagnostic=True),
            MiscSensorEntity(client, self, "pd.type", "Generator Type", False, diagnostic=True),
            MiscSensorEntity(client, self, "pd.num", "Unit Number", False, diagnostic=True),
            MiscSensorEntity(client, self, "pd.ver", "Firmware Version", False, diagnostic=True),
            MiscSensorEntity(client, self, "pd.cellId", "Cell ID", False, diagnostic=True),
            QuotaStatusSensorEntity(client, self),
        ]

    @override
    def binary_sensors(self, client: EcoflowApiClient) -> Sequence[BinarySensorEntity]:
        return [
            MiscBinarySensorEntity(client, self, "pd.dcState", "DC Output State"),
        ]

    @override
    def numbers(self, client: EcoflowApiClient) -> Sequence[NumberEntity]:
        return []

    @override
    def switches(self, client: EcoflowApiClient) -> Sequence[SwitchEntity]:
        return [
            EnabledEntity(
                client,
                self,
                "pd.motorState",
                "Generator Motor",
                lambda value: _command("motorCtrl", {"enable": value}),
            ),
            EnabledEntity(
                client,
                self,
                "pd.acState",
                const.AC_ENABLED,
                lambda value: _command("acCtrl", {"enable": value}),
            ),
        ]

    @override
    def selects(self, client: EcoflowApiClient) -> Sequence[SelectEntity]:
        return []
