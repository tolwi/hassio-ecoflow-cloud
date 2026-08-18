from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import UnitOfTemperature

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import BaseInternalDevice, const
from custom_components.ecoflow_cloud.number import SetTempEntity
from custom_components.ecoflow_cloud.select import DictSelectEntity
from custom_components.ecoflow_cloud.sensor import (
    CapacitySensorEntity,
    LevelSensorEntity,
    MilliCelsiusSensorEntity,
    QuotaStatusSensorEntity,
    RemainSensorEntity,
    TempSensorEntity,
    WattsSensorEntity,
)

SETPOINT_RANGE_CELSIUS = (16, 30)
SETPOINT_RANGE_FAHRENHEIT = (60, 86)


class Wave2SetTempEntity(SetTempEntity):
    """Setpoint entity that follows the unit the device itself is set to."""

    _reported_unit: UnitOfTemperature | None = None

    def _current_unit(self) -> UnitOfTemperature:
        if str(self._device.data.params.get("pd.tempSys")).strip().lower() in {"1", "f", "fahrenheit"}:
            return UnitOfTemperature.FAHRENHEIT
        return UnitOfTemperature.CELSIUS

    def _current_range(self) -> tuple[int, int]:
        if self._current_unit() == UnitOfTemperature.FAHRENHEIT:
            return SETPOINT_RANGE_FAHRENHEIT
        return SETPOINT_RANGE_CELSIUS

    @property
    def native_unit_of_measurement(self) -> UnitOfTemperature | None:
        return self._current_unit()

    @property
    def native_min_value(self) -> float:
        return self._current_range()[0]

    @property
    def native_max_value(self) -> float:
        return self._current_range()[1]

    def _updated(self, data: dict[str, Any]):
        super()._updated(data)
        # A unit flip alone leaves setTemp untouched, so nothing else would repaint the entity.
        if self._reported_unit != self._current_unit():
            self._reported_unit = self._current_unit()
            self.schedule_update_ha_state()


class Wave2(BaseInternalDevice):
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            # Power and Battery Entities
            LevelSensorEntity(client, self, "bms.soc", const.MAIN_BATTERY_LEVEL).attr(
                "bms.remainCap", const.ATTR_REMAIN_CAPACITY, 0
            ),
            CapacitySensorEntity(client, self, "bms.remainCap", const.MAIN_REMAIN_CAPACITY, False),
            TempSensorEntity(client, self, "bms.tmp", const.BATTERY_TEMP)
            .attr("bms.minCellTemp", const.ATTR_MIN_CELL_TEMP, 0)
            .attr("bms.maxCellTemp", const.ATTR_MAX_CELL_TEMP, 0),
            TempSensorEntity(client, self, "bms.minCellTmp", const.MIN_CELL_TEMP, False),
            TempSensorEntity(client, self, "bms.maxCellTmp", const.MAX_CELL_TEMP, False),
            RemainSensorEntity(client, self, "pd.batChgRemain", const.CHARGE_REMAINING_TIME),
            RemainSensorEntity(client, self, "pd.batDsgRemain", const.DISCHARGE_REMAINING_TIME),
            # heat pump
            MilliCelsiusSensorEntity(client, self, "pd.condTemp", "Condensation temperature", False),
            MilliCelsiusSensorEntity(client, self, "pd.heatEnv", "Return air temperature in condensation zone", False),
            MilliCelsiusSensorEntity(client, self, "pd.coolEnv", "Air outlet temperature", False),
            MilliCelsiusSensorEntity(client, self, "pd.evapTemp", "Evaporation temperature", False),
            MilliCelsiusSensorEntity(client, self, "pd.motorOutTemp", "Exhaust temperature", False),
            MilliCelsiusSensorEntity(client, self, "pd.airInTemp", "Evaporation zone return air temperature", False),
            TempSensorEntity(client, self, "pd.coolTemp", "Air outlet temperature", False),
            TempSensorEntity(client, self, "pd.envTemp", "Ambient temperature", False),
            # power (pd)
            WattsSensorEntity(client, self, "pd.mpptPwr", "PV input power"),
            WattsSensorEntity(client, self, "pd.batPwrOut", "Battery output power"),
            WattsSensorEntity(client, self, "pd.pvPower", "PV charging power"),
            WattsSensorEntity(client, self, "pd.acPwrIn", "AC input power"),
            WattsSensorEntity(client, self, "pd.psdrPower ", "Power supply power"),
            WattsSensorEntity(client, self, "pd.sysPowerWatts", "System power"),
            WattsSensorEntity(client, self, "pd.batPower ", "Battery power"),
            # power (motor)
            WattsSensorEntity(client, self, "motor.power", "Motor operating power"),
            # power (power)
            WattsSensorEntity(client, self, "power.batPwrOut", "Battery output power"),
            WattsSensorEntity(client, self, "power.acPwrI", "AC input power"),
            WattsSensorEntity(client, self, "power.mpptPwr ", "PV input power"),
            QuotaStatusSensorEntity(client, self),
        ]

    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return [
            Wave2SetTempEntity(
                client,
                self,
                "pd.setTemp",
                "Set Temperature",
                *SETPOINT_RANGE_CELSIUS,
                lambda value: {
                    "moduleType": 1,
                    "operateType": "setTemp",
                    "sn": self.device_info.sn,
                    "params": {"setTemp": int(value)},
                },
            ),
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return [
            DictSelectEntity(
                client,
                self,
                "pd.fanValue",
                const.FAN_MODE,
                const.FAN_MODE_OPTIONS,
                lambda value: {
                    "moduleType": 1,
                    "operateType": "fanValue",
                    "sn": self.device_info.sn,
                    "params": {"fanValue": value},
                },
            ),
            DictSelectEntity(
                client,
                self,
                "pd.mainMode",
                const.MAIN_MODE,
                const.MAIN_MODE_OPTIONS,
                lambda value: {
                    "moduleType": 1,
                    "operateType": "mainMode",
                    "sn": self.device_info.sn,
                    "params": {"mainMode": value},
                },
            ),
            DictSelectEntity(
                client,
                self,
                "pd.powerMode",
                const.REMOTE_MODE,
                const.REMOTE_MODE_OPTIONS,
                lambda value: {
                    "moduleType": 1,
                    "operateType": "powerMode",
                    "sn": self.device_info.sn,
                    "params": {"powerMode": value},
                },
            ),
            DictSelectEntity(
                client,
                self,
                "pd.subMode",
                const.POWER_SUB_MODE,
                const.POWER_SUB_MODE_OPTIONS,
                lambda value: {
                    "moduleType": 1,
                    "operateType": "subMode",
                    "sn": self.device_info.sn,
                    "params": {"subMode": value},
                },
            ),
            DictSelectEntity(
                client,
                self,
                "pd.tempSys",
                const.TEMP_UNIT,
                const.TEMP_UNIT_OPTIONS,
                lambda value: {
                    "moduleType": 1,
                    "operateType": "tempSys",
                    "sn": self.device_info.sn,
                    "params": {"mode": value},
                },
            ),
        ]

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return []
