from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import const, BaseDevice
from custom_components.ecoflow_cloud.entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, \
    BaseSelectEntity
from custom_components.ecoflow_cloud.number import ChargingPowerEntity, MinBatteryLevelEntity, MaxBatteryLevelEntity, \
    MaxGenStopLevelEntity, MinGenStartLevelEntity, BatteryBackupLevel
from custom_components.ecoflow_cloud.select import TimeoutDictSelectEntity
from custom_components.ecoflow_cloud.sensor import LevelSensorEntity, RemainSensorEntity, TempSensorEntity, \
    CyclesSensorEntity, \
    InWattsSensorEntity, OutWattsSensorEntity, MilliVoltSensorEntity, InAmpSensorEntity, \
    InMilliVoltSensorEntity, OutMilliVoltSensorEntity, CapacitySensorEntity, QuotaStatusSensorEntity
from custom_components.ecoflow_cloud.switch import BeeperEntity, EnabledEntity


class Delta2Max(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [
            LevelSensorEntity(client, self, "bms_bmsStatus.soc", const.MAIN_BATTERY_LEVEL)
            .attr("bms_bmsStatus.designCap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("bms_bmsStatus.fullCap", const.ATTR_FULL_CAPACITY, 0)
            .attr("bms_bmsStatus.remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, self, "bms_bmsStatus.designCap", const.MAIN_DESIGN_CAPACITY, False),
            CapacitySensorEntity(client, self, "bms_bmsStatus.fullCap", const.MAIN_FULL_CAPACITY, False),
            CapacitySensorEntity(client, self, "bms_bmsStatus.remainCap", const.MAIN_REMAIN_CAPACITY, False),

            LevelSensorEntity(client, self, "bms_bmsStatus.soh", const.SOH),

            LevelSensorEntity(client, self, "bms_emsStatus.lcdShowSoc", const.COMBINED_BATTERY_LEVEL),

            InWattsSensorEntity(client, self, "pd.wattsInSum", const.TOTAL_IN_POWER),
            OutWattsSensorEntity(client, self, "pd.wattsOutSum", const.TOTAL_OUT_POWER),

            InWattsSensorEntity(client, self, "inv.inputWatts", const.AC_IN_POWER),
            OutWattsSensorEntity(client, self, "inv.outputWatts", const.AC_OUT_POWER),

            InMilliVoltSensorEntity(client, self, "inv.acInVol", const.AC_IN_VOLT),
            OutMilliVoltSensorEntity(client, self, "inv.invOutVol", const.AC_OUT_VOLT),

            InWattsSensorEntity(client, self, "mppt.inWatts", const.SOLAR_1_IN_POWER),
            InWattsSensorEntity(client, self, "mppt.pv2InWatts", const.SOLAR_2_IN_POWER),

            InMilliVoltSensorEntity(client, self, "mppt.inVol", const.SOLAR_1_IN_VOLTS), 
            InMilliVoltSensorEntity(client, self, "mppt.pv2InVol", const.SOLAR_2_IN_VOLTS), 
            InAmpSensorEntity(client, self, "mppt.inAmp", const.SOLAR_1_IN_AMPS),        
            InAmpSensorEntity(client, self, "mppt.pv2InAmp", const.SOLAR_2_IN_AMPS),     

            # OutWattsSensorEntity(client, self, "pd.carWatts", const.DC_OUT_POWER),
            # the same value as pd.carWatts
            OutWattsSensorEntity(client, self, "mppt.outWatts", const.DC_OUT_POWER),

            OutWattsSensorEntity(client, self, "pd.typec1Watts", const.TYPEC_1_OUT_POWER),
            OutWattsSensorEntity(client, self, "pd.typec2Watts", const.TYPEC_2_OUT_POWER),

            OutWattsSensorEntity(client, self, "pd.usb1Watts", const.USB_1_OUT_POWER),
            OutWattsSensorEntity(client, self, "pd.usb2Watts", const.USB_2_OUT_POWER),

            OutWattsSensorEntity(client, self, "pd.qcUsb1Watts", const.USB_QC_1_OUT_POWER),
            OutWattsSensorEntity(client, self, "pd.qcUsb2Watts", const.USB_QC_2_OUT_POWER),

            RemainSensorEntity(client, self, "bms_emsStatus.chgRemainTime", const.CHARGE_REMAINING_TIME),
            RemainSensorEntity(client, self, "bms_emsStatus.dsgRemainTime", const.DISCHARGE_REMAINING_TIME),

            TempSensorEntity(client, self, "inv.outTemp", "Inv Out Temperature"),
            CyclesSensorEntity(client, self, "bms_bmsStatus.cycles", const.CYCLES),

            TempSensorEntity(client, self, "bms_bmsStatus.temp", const.BATTERY_TEMP)
            .attr("bms_bmsStatus.minCellTemp", const.ATTR_MIN_CELL_TEMP, 0)
            .attr("bms_bmsStatus.maxCellTemp", const.ATTR_MAX_CELL_TEMP, 0),
            TempSensorEntity(client, self, "bms_bmsStatus.minCellTemp", const.MIN_CELL_TEMP, False),
            TempSensorEntity(client, self, "bms_bmsStatus.maxCellTemp", const.MAX_CELL_TEMP, False),

            MilliVoltSensorEntity(client, self, "bms_bmsStatus.vol", const.BATTERY_VOLT, False)
            .attr("bms_bmsStatus.minCellVol", const.ATTR_MIN_CELL_VOLT, 0)
            .attr("bms_bmsStatus.maxCellVol", const.ATTR_MAX_CELL_VOLT, 0),
            MilliVoltSensorEntity(client, self, "bms_bmsStatus.minCellVol", const.MIN_CELL_VOLT, False),
            MilliVoltSensorEntity(client, self, "bms_bmsStatus.maxCellVol", const.MAX_CELL_VOLT, False),
            LevelSensorEntity(client, self, "bms_bmsStatus.f32ShowSoc", const.BATTERY_LEVEL_SOC, False, True),

            # Optional Slave 1 Battery
            LevelSensorEntity(client, self, "bms_slave_bmsSlaveStatus_1.soc", const.SLAVE_N_BATTERY_LEVEL % 1, False, True)
            .attr("bms_slave_bmsSlaveStatus_1.designCap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("bms_slave_bmsSlaveStatus_1.fullCap", const.ATTR_FULL_CAPACITY, 0)
            .attr("bms_slave_bmsSlaveStatus_1.remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, self, "bms_slave_bmsSlaveStatus_1.designCap", const.SLAVE_N_DESIGN_CAPACITY % 1,False),
            CapacitySensorEntity(client, self, "bms_slave_bmsSlaveStatus_1.fullCap", const.SLAVE_N_FULL_CAPACITY % 1, False),
            CapacitySensorEntity(client, self, "bms_slave_bmsSlaveStatus_1.remainCap", const.SLAVE_N_REMAIN_CAPACITY % 1,False),

            TempSensorEntity(client, self, "bms_slave_bmsSlaveStatus_1.temp", const.SLAVE_N_BATTERY_TEMP % 1, False, True)
            .attr("bms_slave_bmsSlaveStatus_1.minCellTemp", const.ATTR_MIN_CELL_TEMP, 0)
            .attr("bms_slave_bmsSlaveStatus_1.maxCellTemp", const.ATTR_MAX_CELL_TEMP, 0),
            TempSensorEntity(client, self, "bms_slave_bmsSlaveStatus_1.minCellTemp", const.SLAVE_N_MIN_CELL_TEMP % 1, False),
            TempSensorEntity(client, self, "bms_slave_bmsSlaveStatus_1.maxCellTemp", const.SLAVE_N_MAX_CELL_TEMP % 1, False),

            MilliVoltSensorEntity(client, self, "bms_slave_bmsSlaveStatus_1.vol", const.SLAVE_N_BATTERY_VOLT % 1, False)
            .attr("bms_slave_bmsSlaveStatus_1.minCellVol", const.ATTR_MIN_CELL_VOLT, 0)
            .attr("bms_slave_bmsSlaveStatus_1.maxCellVol", const.ATTR_MAX_CELL_VOLT, 0),
            MilliVoltSensorEntity(client, self, "bms_slave_bmsSlaveStatus_1.minCellVol", const.SLAVE_N_MIN_CELL_VOLT % 1,False),
            MilliVoltSensorEntity(client, self, "bms_slave_bmsSlaveStatus_1.maxCellVol", const.SLAVE_N_MAX_CELL_VOLT % 1,False),

            CyclesSensorEntity(client, self, "bms_slave_bmsSlaveStatus_1.cycles", const.SLAVE_N_CYCLES % 1, False, True),
            LevelSensorEntity(client, self, "bms_slave_bmsSlaveStatus_1.soh", const.SLAVE_N_SOH % 1, False, True),
            InWattsSensorEntity(client, self, "bms_slave_bmsSlaveStatus_1.inputWatts", const.SLAVE_N_IN_POWER % 1, False,True),
            OutWattsSensorEntity(client, self, "bms_slave_bmsSlaveStatus_1.outputWatts", const.SLAVE_N_OUT_POWER % 1, False,True),
            LevelSensorEntity(client, self, "bms_slave_bmsSlaveStatus_1.f32ShowSoc", const.SLAVE_N_BATTERY_LEVEL_SOC % 1, False, True),

            # Optional Slave 2 Battery
            LevelSensorEntity(client, self, "bms_slave_bmsSlaveStatus_2.soc", const.SLAVE_N_BATTERY_LEVEL % 2, False, True)
            .attr("bms_slave_bmsSlaveStatus_2.designCap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("bms_slave_bmsSlaveStatus_2.fullCap", const.ATTR_FULL_CAPACITY, 0)
            .attr("bms_slave_bmsSlaveStatus_2.remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, self, "bms_slave_bmsSlaveStatus_2.designCap", const.SLAVE_N_DESIGN_CAPACITY % 2,False),
            CapacitySensorEntity(client, self, "bms_slave_bmsSlaveStatus_2.fullCap", const.SLAVE_N_FULL_CAPACITY % 2, False),
            CapacitySensorEntity(client, self, "bms_slave_bmsSlaveStatus_2.remainCap", const.SLAVE_N_REMAIN_CAPACITY % 2,False),

            TempSensorEntity(client, self, "bms_slave_bmsSlaveStatus_2.temp", const.SLAVE_N_BATTERY_TEMP % 2, False, True)
            .attr("bms_slave_bmsSlaveStatus_2.minCellTemp", const.ATTR_MIN_CELL_TEMP, 0)
            .attr("bms_slave_bmsSlaveStatus_2.maxCellTemp", const.ATTR_MAX_CELL_TEMP, 0),
            TempSensorEntity(client, self, "bms_slave_bmsSlaveStatus_2.minCellTemp", const.SLAVE_N_MIN_CELL_TEMP % 2, False),
            TempSensorEntity(client, self, "bms_slave_bmsSlaveStatus_2.maxCellTemp", const.SLAVE_N_MAX_CELL_TEMP % 2, False),

            MilliVoltSensorEntity(client, self, "bms_slave_bmsSlaveStatus_2.vol", const.SLAVE_N_BATTERY_VOLT % 2, False)
            .attr("bms_slave_bmsSlaveStatus_2.minCellVol", const.ATTR_MIN_CELL_VOLT, 0)
            .attr("bms_slave_bmsSlaveStatus_2.maxCellVol", const.ATTR_MAX_CELL_VOLT, 0),
            MilliVoltSensorEntity(client, self, "bms_slave_bmsSlaveStatus_2.minCellVol", const.SLAVE_N_MIN_CELL_VOLT % 2, False),
            MilliVoltSensorEntity(client, self, "bms_slave_bmsSlaveStatus_2.maxCellVol", const.SLAVE_N_MAX_CELL_VOLT % 2, False),

            CyclesSensorEntity(client, self, "bms_slave_bmsSlaveStatus_2.cycles", const.SLAVE_N_CYCLES % 2, False, True),
            LevelSensorEntity(client, self, "bms_slave_bmsSlaveStatus_2.soh", const.SLAVE_N_SOH % 2, False, True),
            InWattsSensorEntity(client, self, "bms_slave_bmsSlaveStatus_2.inputWatts", const.SLAVE_N_IN_POWER % 2, False, True),
            OutWattsSensorEntity(client, self, "bms_slave_bmsaSlaveStatus_2.outputWatts", const.SLAVE_N_OUT_POWER % 2, False, True),
            LevelSensorEntity(client, self, "bms_slave_bmsSlaveStatus_2.f32ShowSoc", const.SLAVE_N_BATTERY_LEVEL_SOC % 2, False, True),

                       
            QuotaStatusSensorEntity(client, self)

        ]

    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return [
            MaxBatteryLevelEntity(client, self, "bms_emsStatus.maxChargeSoc", const.MAX_CHARGE_LEVEL, 50, 100,
                                  lambda value: {"moduleType": 2, "operateType": "upsConfig",
                                                 "moduleSn": self.device_info.sn,
                                                 "params": {"maxChgSoc": int(value)}}),

            MinBatteryLevelEntity(client, self, "bms_emsStatus.minDsgSoc", const.MIN_DISCHARGE_LEVEL, 0, 30,
                                  lambda value: {"moduleType": 2, "operateType": "dsgCfg",
                                                 "moduleSn": self.device_info.sn,
                                                 "params": {"minDsgSoc": int(value)}}),

            BatteryBackupLevel(client, self, "pd.bpPowerSoc", const.BACKUP_RESERVE_LEVEL, 5, 100,
                               "bms_emsStatus.minDsgSoc", "bms_emsStatus.maxChargeSoc",
                               lambda value: {"moduleType": 1, "operateType": "watthConfig",
                                              "params": {"isConfig": 1, "bpPowerSoc": int(value), "minDsgSoc": 0,
                                                         "minChgSoc": 0}}),

            MinGenStartLevelEntity(client, self, "bms_emsStatus.minOpenOilEbSoc", const.GEN_AUTO_START_LEVEL, 0, 30,
                                   lambda value: {"moduleType": 2, "operateType": "openOilSoc",
                                                  "moduleSn": self.device_info.sn,
                                                  "params": {"openOilSoc": value}}),

            MaxGenStopLevelEntity(client, self, "bms_emsStatus.maxCloseOilEbSoc", const.GEN_AUTO_STOP_LEVEL, 50, 100,
                                  lambda value: {"moduleType": 2, "operateType": "closeOilSoc",
                                                 "moduleSn": self.device_info.sn,
                                                 "params": {"closeOilSoc": value}}),

            ChargingPowerEntity(client, self, "inv.SlowChgWatts", const.AC_CHARGING_POWER, 200, 2400,
                                lambda value: {"moduleType": 3, "operateType": "acChgCfg",
                                               "moduleSn": self.device_info.sn,
                                               "params": {"slowChgWatts": int(value), "fastChgWatts": 2000,
                                                          "chgPauseFlag": 0}})

        ]

    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        return [
            BeeperEntity(client, self, "pd.beepMode", const.BEEPER,
                         lambda value: {"moduleType": 1, "operateType": "quietCfg",
                                        "moduleSn": self.device_info.sn,
                                        "params": {"enabled": value}}),

            EnabledEntity(client, self, "pd.dcOutState", const.USB_ENABLED,
                          lambda value: {"moduleType": 1, "operateType": "dcOutCfg",
                                         "moduleSn": self.device_info.sn,
                                         "params": {"enabled": value}}),

            EnabledEntity(client, self, "pd.newAcAutoOnCfg", const.AC_ALWAYS_ENABLED,
                          lambda value: {"moduleType": 1, "operateType": "newAcAutoOnCfg",
                                         "moduleSn": self.device_info.sn,
                                         "params": {"enabled": value, "minAcSoc": 5}}),

            EnabledEntity(client, self, "inv.cfgAcEnabled", const.AC_ENABLED,
                          lambda value: {"moduleType": 3, "operateType": "acOutCfg",
                                         "moduleSn": self.device_info.sn,
                                         "params": {"enabled": value, "out_voltage": -1,
                                                    "out_freq": 255, "xboost": 255}}),

            EnabledEntity(client, self, "inv.cfgAcXboost", const.XBOOST_ENABLED,
                          lambda value: {"moduleType": 3, "operateType": "acOutCfg",
                                         "moduleSn": self.device_info.sn,
                                         "params": {"xboost": value}}),
            EnabledEntity(client, self, "pd.carState", const.DC_ENABLED,
                          lambda value: {"moduleType": 5, "operateType": "mpptCar",
                                         "params": {"enabled": value}}),

            EnabledEntity(client, self, "pd.watchIsConfig", const.BP_ENABLED,
                          lambda value: {"moduleType": 1,
                                         "operateType": "watthConfig",
                                         "params": {"bpPowerSoc": value * 50,
                                                    "minChgSoc": 0,
                                                    "isConfig": value,
                                                    "minDsgSoc": 0}}),
        ]

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return [
            TimeoutDictSelectEntity(client, self, "pd.lcdOffSec", const.SCREEN_TIMEOUT, const.SCREEN_TIMEOUT_OPTIONS,
                                    lambda value: {"moduleType": 1, "operateType": "lcdCfg",
                                                   "moduleSn": self.device_info.sn,
                                                   "params": {"brighLevel": 255, "delayOff": value}}),

            TimeoutDictSelectEntity(client, self, "inv.standbyMin", const.UNIT_TIMEOUT, const.UNIT_TIMEOUT_OPTIONS,
                                    lambda value: {"moduleType": 1, "operateType": "standbyTime",
                                                   "moduleSn": self.device_info.sn,
                                                   "params": {"standbyMin": value}}),

            TimeoutDictSelectEntity(client, self, "mppt.carStandbyMin", const.AC_TIMEOUT, const.AC_TIMEOUT_OPTIONS,
                                    lambda value: {"moduleType": 5, "operateType": "standbyTime",
                                                   "moduleSn": self.device_info.sn,
                                                   "params": {"standbyMins": value}}),
        ]
