from . import const, BaseDevice
from .. import EcoflowMQTTClient
from ..entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, BaseSelectEntity
from ..number import ChargingPowerEntity, MinBatteryLevelEntity, MaxBatteryLevelEntity, \
    MaxGenStopLevelEntity, MinGenStartLevelEntity
from ..select import DictSelectEntity, TimeoutDictSelectEntity
from ..sensor import LevelSensorEntity, RemainSensorEntity, TempSensorEntity, CyclesSensorEntity, \
    InWattsSensorEntity, OutWattsSensorEntity
from ..switch import BeeperEntity, EnabledEntity


class Delta2(BaseDevice):
    def sensors(self, client: EcoflowMQTTClient) -> list[BaseSensorEntity]:
        return [
            LevelSensorEntity(client, "pd.soc", const.MAIN_BATTERY_LEVEL),
            LevelSensorEntity(client, "bms_emsStatus.lcdShowSoc", const.COMBINED_BATTERY_LEVEL),
            InWattsSensorEntity(client, "pd.wattsInSum", const.TOTAL_IN_POWER),
            OutWattsSensorEntity(client, "pd.wattsOutSum", const.TOTAL_OUT_POWER),

            InWattsSensorEntity(client, "inv.inputWatts", const.AC_IN_POWER),
            InWattsSensorEntity(client, "mppt.inWatts", const.SOLAR_IN_POWER),

            OutWattsSensorEntity(client, "inv.outputWatts", const.AC_OUT_POWER),

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
            TempSensorEntity(client, "bms_bmsStatus.temp", const.BATTERY_TEMP),
            CyclesSensorEntity(client, "bms_bmsStatus.cycles", const.CYCLES),

            # FanSensorEntity(client, "bms_emsStatus.fanLevel", "Fan Level"),

            # Optional Slave Battery
            LevelSensorEntity(client, "bms_slave.soc", const.SLAVE_BATTERY_LEVEL, False, True),
            TempSensorEntity(client, "bms_slave.temp", const.SLAVE_BATTERY_TEMP, False, True),
            CyclesSensorEntity(client, "bms_slave.cycles", const.SLAVE_CYCLES, False, True),
            InWattsSensorEntity(client, "bms_slave.inputWatts", const.SLAVE_IN_POWER, False, True),
            OutWattsSensorEntity(client, "bms_slave.outputWatts", const.SLAVE_OUT_POWER, False, True)

        ]

    def numbers(self, client: EcoflowMQTTClient) -> list[BaseNumberEntity]:
        return [
            MaxBatteryLevelEntity(client, "bms_emsStatus.maxChargeSoc", const.MAX_CHARGE_LEVEL, 50, 100,
                                  lambda value: {"moduleType": 2, "operateType": "upsConfig",
                                                 "params": {"maxChgSoc": int(value)}}),

            MinBatteryLevelEntity(client, "bms_emsStatus.minDsgSoc", const.MIN_DISCHARGE_LEVEL, 0, 30,
                                  lambda value: {"moduleType": 2, "operateType": "dsgCfg",
                                                 "params": {"minDsgSoc": int(value)}}),

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

            EnabledEntity(client, "pd.acAutoOnCfg", const.AC_ALWAYS_ENABLED,
                          lambda value: {"moduleType": 1, "operateType": "acAutoOn", "params": {"cfg": value}}),

            EnabledEntity(client, "pd.pvChgPrioSet", const.PV_PRIO,
                          lambda value: {"moduleType": 1, "operateType": "pvChangePrio", "params": {"pvChangeSet": value}}),

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
                                                   "params": {"standbyMins": value}}),

            TimeoutDictSelectEntity(client, "mppt.acStandbyMins", const.AC_TIMEOUT, const.AC_TIMEOUT_OPTIONS,
                                    lambda value: {"moduleType": 5, "operateType": "standbyTime",
                                                   "params": {"standbyMins": value}}),

            TimeoutDictSelectEntity(client, "mppt.carStandbyMin", const.DC_TIMEOUT, const.DC_TIMEOUT_OPTIONS,
                                    lambda value: {"moduleType": 5, "operateType": "carStandby",
                                                   "params": {"standbyMins": value}})

        ]
