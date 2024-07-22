from homeassistant.components.switch import SwitchEntity

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import const, BaseDevice
from custom_components.ecoflow_cloud.entities import BaseSensorEntity, BaseNumberEntity, BaseSelectEntity
from custom_components.ecoflow_cloud.number import SetTempEntity
from custom_components.ecoflow_cloud.select import DictSelectEntity
from custom_components.ecoflow_cloud.sensor import LevelSensorEntity, RemainSensorEntity, TempSensorEntity, \
    WattsSensorEntity, QuotasStatusSensorEntity, \
    MilliCelsiusSensorEntity, CapacitySensorEntity


class Wave2(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [
            # Power and Battery Entities
            LevelSensorEntity(client, "bms.soc", const.MAIN_BATTERY_LEVEL)
            .attr("bms.remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, "bms.remainCap", const.MAIN_REMAIN_CAPACITY, False),

            TempSensorEntity(client, "bms.tmp", const.BATTERY_TEMP)
            .attr("bms.minCellTemp", const.ATTR_MIN_CELL_TEMP, 0)
            .attr("bms.maxCellTemp", const.ATTR_MAX_CELL_TEMP, 0),
            TempSensorEntity(client, "bms.minCellTmp", const.MIN_CELL_TEMP, False),
            TempSensorEntity(client, "bms.maxCellTmp", const.MAX_CELL_TEMP, False),

            RemainSensorEntity(client, "pd.batChgRemain", const.CHARGE_REMAINING_TIME),
            RemainSensorEntity(client, "pd.batDsgRemain", const.DISCHARGE_REMAINING_TIME),

            # heat pump
            MilliCelsiusSensorEntity(client, "pd.condTemp", "Condensation temperature", False),
            MilliCelsiusSensorEntity(client, "pd.heatEnv", "Return air temperature in condensation zone", False),
            MilliCelsiusSensorEntity(client, "pd.coolEnv", "Air outlet temperature", False),
            MilliCelsiusSensorEntity(client, "pd.evapTemp", "Evaporation temperature", False),
            MilliCelsiusSensorEntity(client, "pd.motorOutTemp", "Exhaust temperature", False),
            MilliCelsiusSensorEntity(client, "pd.airInTemp", "Evaporation zone return air temperature", False),

            TempSensorEntity(client, "pd.coolTemp", "Air outlet temperature", False),
            TempSensorEntity(client, "pd.envTemp", "Ambient temperature", False),

            # power (pd)
            WattsSensorEntity(client, "pd.mpptPwr", "PV input power"),
            WattsSensorEntity(client, "pd.batPwrOut", "Battery output power"),
            WattsSensorEntity(client, "pd.pvPower", "PV charging power"),
            WattsSensorEntity(client, "pd.acPwrIn", "AC input power"),
            WattsSensorEntity(client, "pd.psdrPower ", "Power supply power"),
            WattsSensorEntity(client, "pd.sysPowerWatts", "System power"),
            WattsSensorEntity(client, "pd.batPower ", "Battery power"),

            # power (motor)
            WattsSensorEntity(client, "motor.power", "Motor operating power"),

            # power (power)
            WattsSensorEntity(client, "power.batPwrOut", "Battery output power"),
            WattsSensorEntity(client, "power.acPwrI", "AC input power"),
            WattsSensorEntity(client, "power.mpptPwr ", "PV input power"),

            QuotasStatusSensorEntity(client)

        ]

    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return [
            SetTempEntity(client, "pd.setTemp", "Set Temperature", 0, 40,
                          lambda value: {"moduleType": 1, "operateType": "setTemp",
                                         "sn": self.device_info.sn,
                                         "params": {"setTemp": int(value)}}),
        ]

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return [
            DictSelectEntity(client, "pd.fanValue", const.FAN_MODE, const.FAN_MODE_OPTIONS,
                             lambda value: {"moduleType": 1, "operateType": "fanValue",
                                            "sn": self.device_info.sn,
                                            "params": {"fanValue": value}}),
            DictSelectEntity(client, "pd.mainMode", const.MAIN_MODE, const.MAIN_MODE_OPTIONS,
                             lambda value: {"moduleType": 1, "operateType": "mainMode",
                                            "sn": self.device_info.sn,
                                            "params": {"mainMode": value}}),
            DictSelectEntity(client, "pd.powerMode", const.REMOTE_MODE, const.REMOTE_MODE_OPTIONS,
                             lambda value: {"moduleType": 1, "operateType": "powerMode",
                                            "sn": self.device_info.sn,
                                            "params": {"powerMode": value}}),
            DictSelectEntity(client, "pd.subMode", const.POWER_SUB_MODE, const.POWER_SUB_MODE_OPTIONS,
                             lambda value: {"moduleType": 1, "operateType": "subMode",
                                            "sn": self.device_info.sn,
                                            "params": {"subMode": value}}),
        ]

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return []
