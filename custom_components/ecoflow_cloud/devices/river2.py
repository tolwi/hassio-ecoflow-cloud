from homeassistant.const import Platform

from . import const, BaseDevice, EntityMigration, MigrationAction
from .const import ATTR_DESIGN_CAPACITY, ATTR_FULL_CAPACITY, ATTR_REMAIN_CAPACITY, BATTERY_CHARGING_STATE, \
    MAIN_DESIGN_CAPACITY, MAIN_FULL_CAPACITY, MAIN_REMAIN_CAPACITY
from ..entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, BaseSelectEntity
from ..mqtt.ecoflow_mqtt import EcoflowMQTTClient
from ..number import ChargingPowerEntity, MaxBatteryLevelEntity, MinBatteryLevelEntity, BatteryBackupLevel
from ..select import DictSelectEntity, TimeoutDictSelectEntity
from ..sensor import LevelSensorEntity, RemainSensorEntity, TempSensorEntity, \
    CyclesSensorEntity, InWattsSensorEntity, OutWattsSensorEntity, VoltSensorEntity, InAmpSensorEntity, \
    InVoltSensorEntity, QuotasStatusSensorEntity, MilliVoltSensorEntity, InMilliVoltSensorEntity, \
    OutMilliVoltSensorEntity, ChargingStateSensorEntity, CapacitySensorEntity
from ..switch import EnabledEntity


class River2(BaseDevice):

    def charging_power_step(self) -> int:
        return 50

    def sensors(self, client: EcoflowMQTTClient) -> list[BaseSensorEntity]:
        return [
            LevelSensorEntity(client, "bms_bmsStatus.soc", const.MAIN_BATTERY_LEVEL)
                .attr("bms_bmsStatus.designCap", ATTR_DESIGN_CAPACITY, 0)
                .attr("bms_bmsStatus.fullCap", ATTR_FULL_CAPACITY, 0)
                .attr("bms_bmsStatus.remainCap", ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, "bms_bmsStatus.designCap", MAIN_DESIGN_CAPACITY, False),
            CapacitySensorEntity(client, "bms_bmsStatus.fullCap", MAIN_FULL_CAPACITY, False),
            CapacitySensorEntity(client, "bms_bmsStatus.remainCap", MAIN_REMAIN_CAPACITY, False),

            LevelSensorEntity(client, "bms_bmsStatus.soh", const.SOH),

            LevelSensorEntity(client, "bms_emsStatus.lcdShowSoc", const.COMBINED_BATTERY_LEVEL),

            ChargingStateSensorEntity(client, "bms_emsStatus.chgState", BATTERY_CHARGING_STATE),

            InWattsSensorEntity(client, "pd.wattsInSum", const.TOTAL_IN_POWER),
            OutWattsSensorEntity(client, "pd.wattsOutSum", const.TOTAL_OUT_POWER),

            InAmpSensorEntity(client, "inv.dcInAmp", const.SOLAR_IN_CURRENT),
            InVoltSensorEntity(client, "inv.dcInVol", const.SOLAR_IN_VOLTAGE),

            InWattsSensorEntity(client, "inv.inputWatts", const.AC_IN_POWER),
            OutWattsSensorEntity(client, "inv.outputWatts", const.AC_OUT_POWER),

            InMilliVoltSensorEntity(client, "inv.acInVol", const.AC_IN_VOLT),
            OutMilliVoltSensorEntity(client, "inv.invOutVol", const.AC_OUT_VOLT),

            InWattsSensorEntity(client, "pd.typecChaWatts", const.TYPE_C_IN_POWER),
            InWattsSensorEntity(client, "mppt.inWatts", const.SOLAR_IN_POWER),


            OutWattsSensorEntity(client, "pd.carWatts", const.DC_OUT_POWER),
            OutWattsSensorEntity(client, "pd.typec1Watts", const.TYPEC_OUT_POWER),
            OutWattsSensorEntity(client, "pd.usb1Watts", const.USB_OUT_POWER),
            # OutWattsSensorEntity(client, "pd.usb2Watts", const.USB_2_OUT_POWER),

            RemainSensorEntity(client, "bms_emsStatus.chgRemainTime", const.CHARGE_REMAINING_TIME),
            RemainSensorEntity(client, "bms_emsStatus.dsgRemainTime", const.DISCHARGE_REMAINING_TIME),
            RemainSensorEntity(client, "pd.remainTime", const.REMAINING_TIME),

            TempSensorEntity(client, "inv.outTemp", "Inv Out Temperature"),
            CyclesSensorEntity(client, "bms_bmsStatus.cycles", const.CYCLES),

            TempSensorEntity(client, "bms_bmsStatus.temp", const.BATTERY_TEMP)
                .attr("bms_bmsStatus.minCellTemp", const.ATTR_MIN_CELL_TEMP, 0)
                .attr("bms_bmsStatus.maxCellTemp", const.ATTR_MAX_CELL_TEMP, 0),
            TempSensorEntity(client, "bms_bmsStatus.minCellTemp", const.MIN_CELL_TEMP, False),
            TempSensorEntity(client, "bms_bmsStatus.maxCellTemp", const.MAX_CELL_TEMP, False),

            VoltSensorEntity(client, "bms_bmsStatus.vol", const.BATTERY_VOLT, False)
                .attr("bms_bmsStatus.minCellVol", const.ATTR_MIN_CELL_VOLT, 0)
                .attr("bms_bmsStatus.maxCellVol", const.ATTR_MAX_CELL_VOLT, 0),
            MilliVoltSensorEntity(client, "bms_bmsStatus.minCellVol", const.MIN_CELL_VOLT, False),
            MilliVoltSensorEntity(client, "bms_bmsStatus.maxCellVol", const.MAX_CELL_VOLT, False),

            QuotasStatusSensorEntity(client),
            # FanSensorEntity(client, "bms_emsStatus.fanLevel", "Fan Level"),

        ]

    def numbers(self, client: EcoflowMQTTClient) -> list[BaseNumberEntity]:
        return [
            MaxBatteryLevelEntity(client, "bms_emsStatus.maxChargeSoc", const.MAX_CHARGE_LEVEL, 50, 100,
                                  lambda value: {"moduleType": 2, "operateType": "upsConfig",
                                                 "params": {"maxChgSoc": int(value)}}),

            MinBatteryLevelEntity(client, "bms_emsStatus.minDsgSoc", const.MIN_DISCHARGE_LEVEL, 0, 30,
                                  lambda value: {"moduleType": 2, "operateType": "dsgCfg",
                                                 "params": {"minDsgSoc": int(value)}}),

            ChargingPowerEntity(client, "mppt.cfgChgWatts", const.AC_CHARGING_POWER, 100, 360,
                                lambda value: {"moduleType": 5, "operateType": "acChgCfg",
                                               "params": {"chgWatts": int(value), "chgPauseFlag": 255}}),

            BatteryBackupLevel(client, "pd.bpPowerSoc", const.BACKUP_RESERVE_LEVEL, 5, 100,
                               "bms_emsStatus.minDsgSoc", "bms_emsStatus.maxChargeSoc",
                               lambda value: {"moduleType": 1, "operateType": "watthConfig",
                                              "params": {"isConfig": 1,
                                                         "bpPowerSoc": int(value),
                                                         "minDsgSoc": 0,
                                                         "minChgSoc": 0}}),
        ]

    def switches(self, client: EcoflowMQTTClient) -> list[BaseSwitchEntity]:
        return [
            EnabledEntity(client, "mppt.cfgAcEnabled", const.AC_ENABLED,
                          lambda value: {"moduleType": 5, "operateType": "acOutCfg",
                                         "params": {"enabled": value, "out_voltage": -1, "out_freq": 255,
                                                    "xboost": 255}}),

            EnabledEntity(client, "pd.acAutoOutConfig", const.AC_ALWAYS_ENABLED,
                          lambda value, params: {"moduleType": 1, "operateType": "acAutoOutConfig",
                                                 "params": {"acAutoOutConfig": value,
                                                            "minAcOutSoc": int(params.get("bms_emsStatus.minDsgSoc", 0)) + 5}}
                          ),

            EnabledEntity(client, "mppt.cfgAcXboost", const.XBOOST_ENABLED,
                          lambda value: {"moduleType": 5, "operateType": "acOutCfg",
                                         "params": {"enabled": 255, "out_voltage": -1, "out_freq": 255,
                                                    "xboost": value}}),

            EnabledEntity(client, "pd.carState", const.DC_ENABLED,
                          lambda value: {"moduleType": 5, "operateType": "mpptCar", "params": {"enabled": value}}),

            EnabledEntity(client, "pd.watchIsConfig", const.BP_ENABLED,
                          lambda value, params: {"moduleType": 1, "operateType": "watthConfig",
                                                 "params": {"isConfig": value,
                                                            "bpPowerSoc": value * 50,
                                                            "minDsgSoc": 0,
                                                            "minChgSoc": 0}})
        ]

    def selects(self, client: EcoflowMQTTClient) -> list[BaseSelectEntity]:
        return [
            DictSelectEntity(client, "mppt.dcChgCurrent", const.DC_CHARGE_CURRENT, const.DC_CHARGE_CURRENT_OPTIONS,
                             lambda value: {"moduleType": 5, "operateType": "dcChgCfg",
                                            "params": {"dcChgCfg": value}}),

            DictSelectEntity(client, "mppt.cfgChgType", const.DC_MODE, const.DC_MODE_OPTIONS,
                             lambda value: {"moduleType": 5, "operateType": "chaType",
                                            "params": {"chaType": value}}),

            TimeoutDictSelectEntity(client, "mppt.scrStandbyMin", const.SCREEN_TIMEOUT, const.SCREEN_TIMEOUT_OPTIONS,
                                    lambda value: {"moduleType": 5, "operateType": "lcdCfg",
                                                   "params": {"brighLevel": 255, "delayOff": value}}),

            TimeoutDictSelectEntity(client, "mppt.powStandbyMin", const.UNIT_TIMEOUT, const.UNIT_TIMEOUT_OPTIONS,
                                    lambda value: {"moduleType": 5, "operateType": "standby",
                                                   "params": {"standbyMins": value}}),

            TimeoutDictSelectEntity(client, "mppt.acStandbyMins", const.AC_TIMEOUT, const.AC_TIMEOUT_OPTIONS,
                                    lambda value: {"moduleType": 5, "operateType": "acStandby",
                                                   "params": {"standbyMins": value}})
        ]

    def migrate(self, version) -> list[EntityMigration]:
        if version == 2:
            return [
                EntityMigration("pd.soc", Platform.SENSOR, MigrationAction.REMOVE),
            ]
        return []
