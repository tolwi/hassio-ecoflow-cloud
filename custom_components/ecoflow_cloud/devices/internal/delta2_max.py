from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import const, BaseDevice
from custom_components.ecoflow_cloud.entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, \
    BaseSelectEntity
from custom_components.ecoflow_cloud.number import ChargingPowerEntity, MinBatteryLevelEntity, MaxBatteryLevelEntity, \
    MaxGenStopLevelEntity, MinGenStartLevelEntity, BatteryBackupLevel
from custom_components.ecoflow_cloud.select import TimeoutDictSelectEntity
from custom_components.ecoflow_cloud.sensor import LevelSensorEntity, RemainSensorEntity, TempSensorEntity, \
    CyclesSensorEntity, \
    InWattsSensorEntity, OutWattsSensorEntity, StatusSensorEntity, MilliVoltSensorEntity, \
    InMilliVoltSensorEntity, OutMilliVoltSensorEntity, CapacitySensorEntity
from custom_components.ecoflow_cloud.switch import BeeperEntity, EnabledEntity


class Delta2Max(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [
            LevelSensorEntity(client, "bms_bmsStatus.soc", const.MAIN_BATTERY_LEVEL)
            .attr("bms_bmsStatus.designCap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("bms_bmsStatus.fullCap", const.ATTR_FULL_CAPACITY, 0)
            .attr("bms_bmsStatus.remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, "bms_bmsStatus.designCap", const.MAIN_DESIGN_CAPACITY, False),
            CapacitySensorEntity(client, "bms_bmsStatus.fullCap", const.MAIN_FULL_CAPACITY, False),
            CapacitySensorEntity(client, "bms_bmsStatus.remainCap", const.MAIN_REMAIN_CAPACITY, False),

            LevelSensorEntity(client, "bms_bmsStatus.soh", const.SOH),

            LevelSensorEntity(client, "bms_emsStatus.lcdShowSoc", const.COMBINED_BATTERY_LEVEL),

            InWattsSensorEntity(client, "pd.wattsInSum", const.TOTAL_IN_POWER),
            OutWattsSensorEntity(client, "pd.wattsOutSum", const.TOTAL_OUT_POWER),

            InWattsSensorEntity(client, "inv.inputWatts", const.AC_IN_POWER),
            OutWattsSensorEntity(client, "inv.outputWatts", const.AC_OUT_POWER),

            InMilliVoltSensorEntity(client, "inv.acInVol", const.AC_IN_VOLT),
            OutMilliVoltSensorEntity(client, "inv.invOutVol", const.AC_OUT_VOLT),

            InWattsSensorEntity(client, "mppt.inWatts", const.SOLAR_1_IN_POWER),
            InWattsSensorEntity(client, "mppt.pv2InWatts", const.SOLAR_2_IN_POWER),

            # OutWattsSensorEntity(client, "pd.carWatts", const.DC_OUT_POWER),
            # the same value as pd.carWatts
            OutWattsSensorEntity(client, "mppt.outWatts", const.DC_OUT_POWER),

            OutWattsSensorEntity(client, "pd.typec1Watts", const.TYPEC_1_OUT_POWER),
            OutWattsSensorEntity(client, "pd.typec2Watts", const.TYPEC_2_OUT_POWER),

            OutWattsSensorEntity(client, "pd.usb1Watts", const.USB_1_OUT_POWER),
            OutWattsSensorEntity(client, "pd.usb2Watts", const.USB_2_OUT_POWER),

            OutWattsSensorEntity(client, "pd.qcUsb1Watts", const.USB_QC_1_OUT_POWER),
            OutWattsSensorEntity(client, "pd.qcUsb2Watts", const.USB_QC_2_OUT_POWER),

            RemainSensorEntity(client, "bms_emsStatus.chgRemainTime", const.CHARGE_REMAINING_TIME),
            RemainSensorEntity(client, "bms_emsStatus.dsgRemainTime", const.DISCHARGE_REMAINING_TIME),

            TempSensorEntity(client, "inv.outTemp", "Inv Out Temperature"),
            CyclesSensorEntity(client, "bms_bmsStatus.cycles", const.CYCLES),

            TempSensorEntity(client, "bms_bmsStatus.temp", const.BATTERY_TEMP)
            .attr("bms_bmsStatus.minCellTemp", const.ATTR_MIN_CELL_TEMP, 0)
            .attr("bms_bmsStatus.maxCellTemp", const.ATTR_MAX_CELL_TEMP, 0),
            TempSensorEntity(client, "bms_bmsStatus.minCellTemp", const.MIN_CELL_TEMP, False),
            TempSensorEntity(client, "bms_bmsStatus.maxCellTemp", const.MAX_CELL_TEMP, False),

            MilliVoltSensorEntity(client, "bms_bmsStatus.vol", const.BATTERY_VOLT, False)
            .attr("bms_bmsStatus.minCellVol", const.ATTR_MIN_CELL_VOLT, 0)
            .attr("bms_bmsStatus.maxCellVol", const.ATTR_MAX_CELL_VOLT, 0),
            MilliVoltSensorEntity(client, "bms_bmsStatus.minCellVol", const.MIN_CELL_VOLT, False),
            MilliVoltSensorEntity(client, "bms_bmsStatus.maxCellVol", const.MAX_CELL_VOLT, False),

            # Optional Slave 1 Battery
            LevelSensorEntity(client, "bms_slave_bmsSlaveStatus_1.soc", const.SLAVE_N_BATTERY_LEVEL % 1, False, True)
            .attr("bms_slave_bmsSlaveStatus_1.designCap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("bms_slave_bmsSlaveStatus_1.fullCap", const.ATTR_FULL_CAPACITY, 0)
            .attr("bms_slave_bmsSlaveStatus_1.remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, "bms_slave_bmsSlaveStatus_1.designCap", const.SLAVE_N_DESIGN_CAPACITY % 1,
                                 False),
            CapacitySensorEntity(client, "bms_slave_bmsSlaveStatus_1.fullCap", const.SLAVE_N_FULL_CAPACITY % 1, False),
            CapacitySensorEntity(client, "bms_slave_bmsSlaveStatus_1.remainCap", const.SLAVE_N_REMAIN_CAPACITY % 1,
                                 False),

            TempSensorEntity(client, "bms_slave_bmsSlaveStatus_1.temp", const.SLAVE_N_BATTERY_TEMP % 1, False, True)
            .attr("bms_slave_bmsSlaveStatus_1.minCellTemp", const.ATTR_MIN_CELL_TEMP, 0)
            .attr("bms_slave_bmsSlaveStatus_1.maxCellTemp", const.ATTR_MAX_CELL_TEMP, 0),
            TempSensorEntity(client, "bms_slave_bmsSlaveStatus_1.minCellTemp", const.SLAVE_N_MIN_CELL_TEMP % 1, False),
            TempSensorEntity(client, "bms_slave_bmsSlaveStatus_1.maxCellTemp", const.SLAVE_N_MAX_CELL_TEMP % 1, False),

            MilliVoltSensorEntity(client, "bms_slave_bmsSlaveStatus_1.vol", const.SLAVE_N_BATTERY_VOLT % 1, False)
            .attr("bms_slave_bmsSlaveStatus_1.minCellVol", const.ATTR_MIN_CELL_VOLT, 0)
            .attr("bms_slave_bmsSlaveStatus_1.maxCellVol", const.ATTR_MAX_CELL_VOLT, 0),
            MilliVoltSensorEntity(client, "bms_slave_bmsSlaveStatus_1.minCellVol", const.SLAVE_N_MIN_CELL_VOLT % 1,
                                  False),
            MilliVoltSensorEntity(client, "bms_slave_bmsSlaveStatus_1.maxCellVol", const.SLAVE_N_MAX_CELL_VOLT % 1,
                                  False),

            CyclesSensorEntity(client, "bms_slave_bmsSlaveStatus_1.cycles", const.SLAVE_N_CYCLES % 1, False, True),
            LevelSensorEntity(client, "bms_slave_bmsSlaveStatus_1.soh", const.SLAVE_N_SOH % 1, False, True),
            InWattsSensorEntity(client, "bms_slave_bmsSlaveStatus_1.inputWatts", const.SLAVE_N_IN_POWER % 1, False,
                                True),
            OutWattsSensorEntity(client, "bms_slave_bmsSlaveStatus_1.outputWatts", const.SLAVE_N_OUT_POWER % 1, False,
                                 True),

            # Optional Slave 2 Battery
            LevelSensorEntity(client, "bms_slave_bmsSlaveStatus_2.soc", const.SLAVE_N_BATTERY_LEVEL % 2, False, True)
            .attr("bms_slave_bmsSlaveStatus_2.designCap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("bms_slave_bmsSlaveStatus_2.fullCap", const.ATTR_FULL_CAPACITY, 0)
            .attr("bms_slave_bmsSlaveStatus_2.remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, "bms_slave_bmsSlaveStatus_2.designCap", const.SLAVE_N_DESIGN_CAPACITY % 2,
                                 False),
            CapacitySensorEntity(client, "bms_slave_bmsSlaveStatus_2.fullCap", const.SLAVE_N_FULL_CAPACITY % 2, False),
            CapacitySensorEntity(client, "bms_slave_bmsSlaveStatus_2.remainCap", const.SLAVE_N_REMAIN_CAPACITY % 2,
                                 False),

            TempSensorEntity(client, "bms_slave_bmsSlaveStatus_2.temp", const.SLAVE_N_BATTERY_TEMP % 2, False, True)
            .attr("bms_slave_bmsSlaveStatus_2.minCellTemp", const.ATTR_MIN_CELL_TEMP, 0)
            .attr("bms_slave_bmsSlaveStatus_2.maxCellTemp", const.ATTR_MAX_CELL_TEMP, 0),
            TempSensorEntity(client, "bms_slave_bmsSlaveStatus_2.minCellTemp", const.SLAVE_N_MIN_CELL_TEMP % 2, False),
            TempSensorEntity(client, "bms_slave_bmsSlaveStatus_2.maxCellTemp", const.SLAVE_N_MAX_CELL_TEMP % 2, False),

            MilliVoltSensorEntity(client, "bms_slave_bmsSlaveStatus_2.vol", const.SLAVE_N_BATTERY_VOLT % 2, False)
            .attr("bms_slave_bmsSlaveStatus_2.minCellVol", const.ATTR_MIN_CELL_VOLT, 0)
            .attr("bms_slave_bmsSlaveStatus_2.maxCellVol", const.ATTR_MAX_CELL_VOLT, 0),
            MilliVoltSensorEntity(client, "bms_slave_bmsSlaveStatus_2.minCellVol", const.SLAVE_N_MIN_CELL_VOLT % 2,
                                  False),
            MilliVoltSensorEntity(client, "bms_slave_bmsSlaveStatus_2.maxCellVol", const.SLAVE_N_MAX_CELL_VOLT % 2,
                                  False),

            CyclesSensorEntity(client, "bms_slave_bmsSlaveStatus_2.cycles", const.SLAVE_N_CYCLES % 2, False, True),
            LevelSensorEntity(client, "bms_slave_bmsSlaveStatus_2.soh", const.SLAVE_N_SOH % 2, False, True),
            InWattsSensorEntity(client, "bms_slave_bmsSlaveStatus_2.inputWatts", const.SLAVE_N_IN_POWER % 2, False,
                                True),
            OutWattsSensorEntity(client, "bms_slave_bmsSlaveStatus_2.outputWatts", const.SLAVE_N_OUT_POWER % 2, False,
                                 True),

            StatusSensorEntity(client),

        ]

    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return [
            MaxBatteryLevelEntity(client, "bms_emsStatus.maxChargeSoc", const.MAX_CHARGE_LEVEL, 50, 100,
                                  lambda value: {"moduleType": 2, "operateType": "upsConfig",
                                                 "moduleSn": self.device_info.sn,
                                                 "params": {"maxChgSoc": int(value)}}),

            MinBatteryLevelEntity(client, "bms_emsStatus.minDsgSoc", const.MIN_DISCHARGE_LEVEL, 0, 30,
                                  lambda value: {"moduleType": 2, "operateType": "dsgCfg",
                                                 "moduleSn": self.device_info.sn,
                                                 "params": {"minDsgSoc": int(value)}}),

            BatteryBackupLevel(client, "pd.bpPowerSoc", const.BACKUP_RESERVE_LEVEL, 5, 100,
                               "bms_emsStatus.minDsgSoc", "bms_emsStatus.maxChargeSoc",
                               lambda value: {"moduleType": 1, "operateType": "watthConfig",
                                              "params": {"isConfig": 1, "bpPowerSoc": int(value), "minDsgSoc": 0,
                                                         "minChgSoc": 0}}),

            MinGenStartLevelEntity(client, "bms_emsStatus.minOpenOilEbSoc", const.GEN_AUTO_START_LEVEL, 0, 30,
                                   lambda value: {"moduleType": 2, "operateType": "openOilSoc",
                                                  "moduleSn": self.device_info.sn,
                                                  "params": {"openOilSoc": value}}),

            MaxGenStopLevelEntity(client, "bms_emsStatus.maxCloseOilEbSoc", const.GEN_AUTO_STOP_LEVEL, 50, 100,
                                  lambda value: {"moduleType": 2, "operateType": "closeOilSoc",
                                                 "moduleSn": self.device_info.sn,
                                                 "params": {"closeOilSoc": value}}),

            ChargingPowerEntity(client, "inv.SlowChgWatts", const.AC_CHARGING_POWER, 200, 2400,
                                lambda value: {"moduleType": 3, "operateType": "acChgCfg",
                                               "moduleSn": self.device_info.sn,
                                               "params": {"slowChgWatts": int(value), "fastChgWatts": 255,
                                                          "chgPauseFlag": 0}})

        ]

    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        return [
            BeeperEntity(client, "pd.beepMode", const.BEEPER,
                         lambda value: {"moduleType": 1, "operateType": "quietCfg",
                                        "moduleSn": self.device_info.sn,
                                        "params": {"enabled": value}}),

            EnabledEntity(client, "pd.dcOutState", const.USB_ENABLED,
                          lambda value: {"moduleType": 1, "operateType": "dcOutCfg",
                                         "moduleSn": self.device_info.sn,
                                         "params": {"enabled": value}}),

            EnabledEntity(client, "pd.newAcAutoOnCfg", const.AC_ALWAYS_ENABLED,
                          lambda value: {"moduleType": 1, "operateType": "newAcAutoOnCfg",
                                         "moduleSn": self.device_info.sn,
                                         "params": {"enabled": value, "minAcSoc": 5}}),

            EnabledEntity(client, "inv.cfgAcEnabled", const.AC_ENABLED,
                          lambda value: {"moduleType": 3, "operateType": "acOutCfg",
                                         "moduleSn": self.device_info.sn,
                                         "params": {"enabled": value, "out_voltage": -1,
                                                    "out_freq": 255, "xboost": 255}}),

            EnabledEntity(client, "inv.cfgAcXboost", const.XBOOST_ENABLED,
                          lambda value: {"moduleType": 3, "operateType": "acOutCfg",
                                         "moduleSn": self.device_info.sn,
                                         "params": {"xboost": value}}),
            EnabledEntity(client, "pd.carState", const.DC_ENABLED,
                          lambda value: {"moduleType": 5, "operateType": "mpptCar",
                                         "params": {"enabled": value}}),

            EnabledEntity(client, "pd.bpPowerSoc", const.BP_ENABLED,
                          lambda value: {"moduleType": 1,
                                         "operateType": "watthConfig",
                                         "params": {"bpPowerSoc": value,
                                                    "minChgSoc": 0,
                                                    "isConfig": value,
                                                    "minDsgSoc": 0}}),
        ]

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return [
            TimeoutDictSelectEntity(client, "pd.lcdOffSec", const.SCREEN_TIMEOUT, const.SCREEN_TIMEOUT_OPTIONS,
                                    lambda value: {"moduleType": 1, "operateType": "lcdCfg",
                                                   "moduleSn": self.device_info.sn,
                                                   "params": {"brighLevel": 255, "delayOff": value}}),

            TimeoutDictSelectEntity(client, "inv.standbyMin", const.UNIT_TIMEOUT, const.UNIT_TIMEOUT_OPTIONS,
                                    lambda value: {"moduleType": 1, "operateType": "standbyTime",
                                                   "moduleSn": self.device_info.sn,
                                                   "params": {"standbyMin": value}}),

            TimeoutDictSelectEntity(client, "mppt.carStandbyMin", const.AC_TIMEOUT, const.AC_TIMEOUT_OPTIONS,
                                    lambda value: {"moduleType": 5, "operateType": "standbyTime",
                                                   "moduleSn": self.device_info.sn,
                                                   "params": {"standbyMins": value}}),
        ]
