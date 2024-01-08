from homeassistant.const import Platform

from . import const, BaseDevice, EntityMigration, MigrationAction
from .const import ATTR_DESIGN_CAPACITY, ATTR_FULL_CAPACITY, ATTR_REMAIN_CAPACITY, MAIN_DESIGN_CAPACITY, \
    MAIN_FULL_CAPACITY, MAIN_REMAIN_CAPACITY, SLAVE_DESIGN_CAPACITY, SLAVE_FULL_CAPACITY, SLAVE_REMAIN_CAPACITY
from .. import EcoflowMQTTClient
from ..entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, BaseSelectEntity
from ..number import ChargingPowerEntity, MinBatteryLevelEntity, MaxBatteryLevelEntity, \
    MaxGenStopLevelEntity, MinGenStartLevelEntity, BatteryBackupLevel
from ..select import DictSelectEntity, TimeoutDictSelectEntity
from ..sensor import LevelSensorEntity, RemainSensorEntity, TempSensorEntity, CyclesSensorEntity, \
    InWattsSensorEntity, OutWattsSensorEntity, QuotasStatusSensorEntity, MilliVoltSensorEntity, InMilliVoltSensorEntity, \
    OutMilliVoltSensorEntity, CapacitySensorEntity
from ..switch import BeeperEntity, EnabledEntity


class Delta2(BaseDevice):
    def sensors(self, client: EcoflowMQTTClient) -> list[BaseSensorEntity]:
        return [
            LevelSensorEntity(client, "bms_bmsStatus.soc", const.MAIN_BATTERY_LEVEL)
                .attr("bms_bmsStatus.designCap", ATTR_DESIGN_CAPACITY, 0)
                .attr("bms_bmsStatus.fullCap", ATTR_FULL_CAPACITY, 0)
                .attr("bms_bmsStatus.remainCap", ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, "bms_bmsStatus.designCap", MAIN_DESIGN_CAPACITY, False),
            CapacitySensorEntity(client, "bms_bmsStatus.fullCap", MAIN_FULL_CAPACITY, False),
            CapacitySensorEntity(client, "bms_bmsStatus.remainCap", MAIN_REMAIN_CAPACITY, False),

            LevelSensorEntity(client, "bms_emsStatus.lcdShowSoc", const.COMBINED_BATTERY_LEVEL),
            InWattsSensorEntity(client, "pd.wattsInSum", const.TOTAL_IN_POWER),
            OutWattsSensorEntity(client, "pd.wattsOutSum", const.TOTAL_OUT_POWER),

            InWattsSensorEntity(client, "inv.inputWatts", const.AC_IN_POWER),
            OutWattsSensorEntity(client, "inv.outputWatts", const.AC_OUT_POWER),

            InMilliVoltSensorEntity(client, "inv.acInVol", const.AC_IN_VOLT),
            OutMilliVoltSensorEntity(client, "inv.invOutVol", const.AC_OUT_VOLT),

            InWattsSensorEntity(client, "mppt.inWatts", const.SOLAR_IN_POWER),



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

            # Optional Slave Battery
            LevelSensorEntity(client, "bms_slave.soc", const.SLAVE_BATTERY_LEVEL, False, True)
                .attr("bms_slave.designCap", ATTR_DESIGN_CAPACITY, 0)
                .attr("bms_slave.fullCap", ATTR_FULL_CAPACITY, 0)
                .attr("bms_slave.remainCap", ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, "bms_slave.designCap", SLAVE_DESIGN_CAPACITY, False),
            CapacitySensorEntity(client, "bms_slave.fullCap", SLAVE_FULL_CAPACITY, False),
            CapacitySensorEntity(client, "bms_slave.remainCap", SLAVE_REMAIN_CAPACITY, False),

            TempSensorEntity(client, "bms_slave.temp", const.SLAVE_BATTERY_TEMP, False, True)
                .attr("bms_slave.minCellTemp", const.ATTR_MIN_CELL_TEMP, 0)
                .attr("bms_slave.maxCellTemp", const.ATTR_MAX_CELL_TEMP, 0),
            TempSensorEntity(client, "bms_slave.minCellTemp", const.SLAVE_MIN_CELL_TEMP, False),
            TempSensorEntity(client, "bms_slave.maxCellTemp", const.SLAVE_MAX_CELL_TEMP, False),

            MilliVoltSensorEntity(client, "bms_slave.vol", const.SLAVE_BATTERY_VOLT, False)
                .attr("bms_slave.minCellVol", const.ATTR_MIN_CELL_VOLT, 0)
                .attr("bms_slave.maxCellVol", const.ATTR_MAX_CELL_VOLT, 0),
            MilliVoltSensorEntity(client, "bms_slave.minCellVol", const.SLAVE_MIN_CELL_VOLT, False),
            MilliVoltSensorEntity(client, "bms_slave.maxCellVol", const.SLAVE_MAX_CELL_VOLT, False),

            CyclesSensorEntity(client, "bms_slave.cycles", const.SLAVE_CYCLES, False, True),
            InWattsSensorEntity(client, "bms_slave.inputWatts", const.SLAVE_IN_POWER, False, True),
            OutWattsSensorEntity(client, "bms_slave.outputWatts", const.SLAVE_OUT_POWER, False, True),
            QuotasStatusSensorEntity(client),

        ]

    def numbers(self, client: EcoflowMQTTClient) -> list[BaseNumberEntity]:
        return [
            MaxBatteryLevelEntity(client, "bms_emsStatus.maxChargeSoc", const.MAX_CHARGE_LEVEL, 50, 100,
                                  lambda value: {"moduleType": 2, "operateType": "upsConfig",
                                                 "params": {"maxChgSoc": int(value)}}),

            MinBatteryLevelEntity(client, "bms_emsStatus.minDsgSoc", const.MIN_DISCHARGE_LEVEL, 0, 30,
                                  lambda value: {"moduleType": 2, "operateType": "dsgCfg",
                                                 "params": {"minDsgSoc": int(value)}}),

            BatteryBackupLevel(client, "pd.bpPowerSoc", const.BACKUP_RESERVE_LEVEL, 5, 100,
                               "bms_emsStatus.minDsgSoc", "bms_emsStatus.maxChargeSoc",
                               lambda value: {"moduleType": 1, "operateType": "watthConfig",
                                              "params": {"isConfig": 1, "bpPowerSoc": int(value), "minDsgSoc": 0,
                                                         "minChgSoc": 0}}),

            MinGenStartLevelEntity(client, "bms_emsStatus.minOpenOilEb", const.GEN_AUTO_START_LEVEL, 0, 30,
                                   lambda value: {"moduleType": 2, "operateType": "closeOilSoc",
                                                  "params": {"closeOilSoc": value}}),

            MaxGenStopLevelEntity(client, "bms_emsStatus.maxCloseOilEb", const.GEN_AUTO_STOP_LEVEL, 50, 100,
                                  lambda value: {"moduleType": 2, "operateType": "openOilSoc",
                                                 "params": {"openOilSoc": value}}),

            ChargingPowerEntity(client, "mppt.cfgChgWatts", const.AC_CHARGING_POWER, 200, 1200,
                                lambda value: {"moduleType": 5, "operateType": "acChgCfg",
                                               "params": {"chgWatts": int(value), "chgPauseFlag": 255}})

        ]

    def switches(self, client: EcoflowMQTTClient) -> list[BaseSwitchEntity]:
        return [
            BeeperEntity(client, "mppt.beepState", const.BEEPER,
                         lambda value: {"moduleType": 5, "operateType": "quietMode", "params": {"enabled": value}}),

            EnabledEntity(client, "pd.dcOutState", const.USB_ENABLED,
                          lambda value: {"moduleType": 1, "operateType": "dcOutCfg", "params": {"enabled": value}}),
            
            EnabledEntity(client, "pd.acAutoOutConfig", const.AC_ALWAYS_ENABLED,
                          lambda value, params: {"moduleType": 1, "operateType": "acAutoOutConfig",
                                                 "params": {"acAutoOutConfig": value,
                                                            "minAcOutSoc": int(params.get("bms_emsStatus.minDsgSoc", 0)) + 5}}),

            EnabledEntity(client, "pd.pvChgPrioSet", const.PV_PRIO,
                          lambda value: {"moduleType": 1, "operateType": "pvChangePrio",
                                         "params": {"pvChangeSet": value}}),

            EnabledEntity(client, "mppt.cfgAcEnabled", const.AC_ENABLED,
                          lambda value: {"moduleType": 5, "operateType": "acOutCfg",
                                         "params": {"enabled": value, "out_voltage": -1, "out_freq": 255,
                                                    "xboost": 255}}),

            EnabledEntity(client, "mppt.cfgAcXboost", const.XBOOST_ENABLED,
                          lambda value: {"moduleType": 5, "operateType": "acOutCfg",
                                         "params": {"enabled": 255, "out_voltage": -1, "out_freq": 255,
                                                    "xboost": value}}),

            EnabledEntity(client, "pd.carState", const.DC_ENABLED,
                          lambda value: {"moduleType": 5, "operateType": "mpptCar", "params": {"enabled": value}}),

            EnabledEntity(client, "pd.bpPowerSoc", const.BP_ENABLED,
                          lambda value: {"moduleType": 1,
                                         "operateType": "watthConfig",
                                         "params": {"bpPowerSoc": value,
                                                    "minChgSoc": 0,
                                                    "isConfig": value,
                                                    "minDsgSoc": 0}}),
            ]

    def selects(self, client: EcoflowMQTTClient) -> list[BaseSelectEntity]:
        return [
            DictSelectEntity(client, "mppt.dcChgCurrent", const.DC_CHARGE_CURRENT, const.DC_CHARGE_CURRENT_OPTIONS,
                             lambda value: {"moduleType": 5, "operateType": "dcChgCfg",
                                            "params": {"dcChgCfg": value}}),

            TimeoutDictSelectEntity(client, "pd.lcdOffSec", const.SCREEN_TIMEOUT, const.SCREEN_TIMEOUT_OPTIONS,
                                    lambda value: {"moduleType": 1, "operateType": "lcdCfg",
                                                   "params": {"brighLevel": 255, "delayOff": value}}),

            TimeoutDictSelectEntity(client, "pd.standbyMin", const.UNIT_TIMEOUT, const.UNIT_TIMEOUT_OPTIONS,
                                    lambda value: {"moduleType": 1, "operateType": "standbyTime",
                                                   "params": {"standbyMin": value}}),

            TimeoutDictSelectEntity(client, "mppt.acStandbyMins", const.AC_TIMEOUT, const.AC_TIMEOUT_OPTIONS,
                                    lambda value: {"moduleType": 5, "operateType": "standbyTime",
                                                   "params": {"standbyMins": value}}),

            TimeoutDictSelectEntity(client, "mppt.carStandbyMin", const.DC_TIMEOUT, const.DC_TIMEOUT_OPTIONS,
                                    lambda value: {"moduleType": 5, "operateType": "carStandby",
                                                   "params": {"standbyMins": value}})

        ]

    def migrate(self, version) -> list[EntityMigration]:
        if version == 2:
            return [
                EntityMigration("pd.soc", Platform.SENSOR, MigrationAction.REMOVE)
            ]
        return []
