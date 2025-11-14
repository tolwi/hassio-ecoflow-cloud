from homeassistant.components.switch import SwitchEntity
from homeassistant.components.climate import ClimateEntity

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import const, BaseDevice
from custom_components.ecoflow_cloud.entities import BaseSensorEntity, BaseNumberEntity, BaseSelectEntity
from custom_components.ecoflow_cloud.sensor import LevelSensorEntity, RemainSensorEntity, TempSensorEntity, \
    WattsSensorEntity, MilliCelsiusSensorEntity, CapacitySensorEntity, QuotaStatusSensorEntity


class Wave2(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [
            # Power and Battery Entities
            LevelSensorEntity(client, self, "bms.soc", const.MAIN_BATTERY_LEVEL)
            .attr("bms.remainCap", const.ATTR_REMAIN_CAPACITY, 0),
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

            QuotaStatusSensorEntity(client, self)
        ]

    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return []

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return []

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return []

    def climates(self, client: EcoflowApiClient) -> list[ClimateEntity]:
        from ...climate import Wave2ClimateEntity
        return [Wave2ClimateEntity(client, self)]
