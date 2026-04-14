from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import BaseInternalDevice, const
from custom_components.ecoflow_cloud.number import LevelEntity, MaxBatteryLevelEntity, MinBatteryLevelEntity
from custom_components.ecoflow_cloud.select import DictSelectEntity
from custom_components.ecoflow_cloud.sensor import (
    LevelSensorEntity,
    MiscSensorEntity,
    RemainSensorEntity,
    TempSensorEntity,
    WattsSensorEntity,
    InWattsSensorEntity,
    OutWattsSensorEntity
)
from custom_components.ecoflow_cloud.switch import BeeperEntity

class Wave3(BaseInternalDevice):
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            InWattsSensorEntity(client, self, "powInSumW", const.TOTAL_IN_POWER),
            OutWattsSensorEntity(client, self, "powOutSumW", const.TOTAL_OUT_POWER),
            WattsSensorEntity(client, self, "powGetAc", "AC Output Power"),
            InWattsSensorEntity(client, self, "powGetAcIn", "AC Input Power"),
            WattsSensorEntity(client, self, "powGetBms", "Battery Power"),
            InWattsSensorEntity(client, self, "powGetPv", "Solar Input Power"),
            WattsSensorEntity(client, self, "powGetDcp", "DCP Power"),
            WattsSensorEntity(client, self, "powGetQcusb1", "USB 1 Power"),
            WattsSensorEntity(client, self, "powGetTypec1", "Type-C 1 Power"),
            WattsSensorEntity(client, self, "powGetSelfConsume", "Self Consumption Power"),

            LevelSensorEntity(client, self, "bmsBattSoc", const.MAIN_BATTERY_LEVEL),
            LevelSensorEntity(client, self, "bmsBattSoh", "Main Battery SOH"),
            LevelSensorEntity(client, self, "cmsBattSoc", "Overall SOC"),
            LevelSensorEntity(client, self, "cmsBattSoh", "Overall SOH"),
            RemainSensorEntity(client, self, "bmsDsgRemTime", const.DISCHARGE_REMAINING_TIME),
            RemainSensorEntity(client, self, "bmsChgRemTime", const.CHARGE_REMAINING_TIME),

            TempSensorEntity(client, self, "tempAmbient", "Ambient Temperature"),
            TempSensorEntity(client, self, "tempIndoorSupplyAir", "Indoor Supply Air Temp"),
            TempSensorEntity(client, self, "bmsMinCellTemp", const.MIN_CELL_TEMP),
            TempSensorEntity(client, self, "bmsMaxCellTemp", const.MAX_CELL_TEMP),
            TempSensorEntity(client, self, "bmsMinMosTemp", "Min MOS Temp"),
            TempSensorEntity(client, self, "bmsMaxMosTemp", "Max MOS Temp"),

            LevelSensorEntity(client, self, "condensateWaterLevel", "Condensate Water Level"),
            MiscSensorEntity(client, self, "errcode", "Error Code"),
            MiscSensorEntity(client, self, "bmsErrCode", "BMS Error Code"),
            MiscSensorEntity(client, self, "pdErrCode", "PD Error Code"),
            MiscSensorEntity(client, self, "waveOperatingMode", "Operating Mode Raw"),
            MiscSensorEntity(client, self, "cmsBmsRunState", "BMS Run State"),
            MiscSensorEntity(client, self, "bmsChgDsgState", "Battery Charge/Discharge State"),
            MiscSensorEntity(client, self, "plugInInfoAcInFlag", "AC In Plug Status"),
            MiscSensorEntity(client, self, "plugInInfoAcInFeq", "AC Input Frequency"),
        ]

    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return [
            MaxBatteryLevelEntity(client, self, "cmsMaxChgSoc", const.MAX_CHARGE_LEVEL, 50, 100,
                                  lambda value: {"moduleType": 0, "operateType": "cmsMaxChgSoc", "params": {"cmsMaxChgSoc": value}}),
            MinBatteryLevelEntity(client, self, "cmsMinDsgSoc", const.MIN_DISCHARGE_LEVEL, 0, 30,
                                  lambda value: {"moduleType": 0, "operateType": "cmsMinDsgSoc", "params": {"cmsMinDsgSoc": value}}),
            LevelEntity(client, self, "lcdLight", "Screen Brightness", 0, 100,
                        lambda value: {"moduleType": 0, "operateType": "lcdLight", "params": {"lcdLight": value}}),
        ]

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return [
            BeeperEntity(client, self, "enBeep", const.BEEPER,
                         lambda value: {"moduleType": 0, "operateType": "enBeep", "params": {"enBeep": value}}),
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return [
            DictSelectEntity(client, self, "waveOperatingMode", "Operating Mode", {
                0: "None", 1: "Cooling", 2: "Heating", 3: "Fan", 4: "Dehumidifying", 5: "Thermostatic"
            }, lambda value: {"moduleType": 0, "operateType": "waveOperatingMode", "params": {"waveOperatingMode": value}}),

            DictSelectEntity(client, self, "devStandbyTime", "Device Timeout", {
                0: "Never", 30: "30 min", 60: "1 hr", 120: "2 hr", 240: "4 hr", 360: "6 hr", 720: "12 hr", 1440: "24 hr"
            }, lambda value: {"moduleType": 0, "operateType": "devStandbyTime", "params": {"devStandbyTime": value}}),
        ]