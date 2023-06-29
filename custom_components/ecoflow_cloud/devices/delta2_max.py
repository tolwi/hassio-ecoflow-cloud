from . import const, BaseDevice
from .. import EcoflowMQTTClient
from ..entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, BaseSelectEntity
from ..number import ChargingPowerEntity, MinBatteryLevelEntity, MaxBatteryLevelEntity, \
    MaxGenStopLevelEntity, MinGenStartLevelEntity
from ..select import DictSelectEntity, TimeoutDictSelectEntity
from ..sensor import LevelSensorEntity, RemainSensorEntity, TempSensorEntity, CyclesSensorEntity, \
    InWattsSensorEntity, OutWattsSensorEntity, VoltSensorEntity
from ..switch import BeeperEntity, EnabledEntity


class Delta2Max(BaseDevice):
    def sensors(self, client: EcoflowMQTTClient) -> list[BaseSensorEntity]:
        return [
            LevelSensorEntity(client, "pd.soc", const.MAIN_BATTERY_LEVEL),
            LevelSensorEntity(client, "bms_emsStatus.f32LcdShowSoc", const.COMBINED_BATTERY_LEVEL),
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
            CyclesSensorEntity(client, "bms_bmsStatus.cycles", const.CYCLES),

            TempSensorEntity(client, "bms_bmsStatus.temp", const.BATTERY_TEMP),
            TempSensorEntity(client, "bms_bmsStatus.minCellTemp", const.MIN_CELL_TEMP),
            TempSensorEntity(client, "bms_bmsStatus.maxCellTemp", const.MAX_CELL_TEMP),

            VoltSensorEntity(client, "bms_bmsStatus.vol", const.BATTERY_VOLT),
            VoltSensorEntity(client, "bms_bmsStatus.minCellVol", const.MIN_CELL_VOLT),
            VoltSensorEntity(client, "bms_bmsStatus.maxCellVol", const.MAX_CELL_VOLT),

            # Optional Slave Battery
            #LevelSensorEntity(client, "bms_slave.soc", const.SLAVE_BATTERY_LEVEL, False, True),
            #TempSensorEntity(client, "bms_slave.temp", const.SLAVE_BATTERY_TEMP, False, True),
            #TempSensorEntity(client, "bms_slave.minCellTemp", const.SLAVE_MIN_CELL_TEMP, False),
            #TempSensorEntity(client, "bms_slave.maxCellTemp", const.SLAVE_MAX_CELL_TEMP, False),

            #VoltSensorEntity(client, "bms_slave.vol", const.SLAVE_BATTERY_VOLT, False),
            #VoltSensorEntity(client, "bms_slave.minCellVol", const.SLAVE_MIN_CELL_VOLT, False),
            #VoltSensorEntity(client, "bms_slave.maxCellVol", const.SLAVE_MAX_CELL_VOLT, False),

            #CyclesSensorEntity(client, "bms_slave.cycles", const.SLAVE_CYCLES, False, True),
            #InWattsSensorEntity(client, "bms_slave.inputWatts", const.SLAVE_IN_POWER, False, True),
            #OutWattsSensorEntity(client, "bms_slave.outputWatts", const.SLAVE_OUT_POWER, False, True)

        ]

    def numbers(self, client: EcoflowMQTTClient) -> list[BaseNumberEntity]:
        return [
            MaxBatteryLevelEntity(client, "bms_emsStatus.maxChargeSoc", const.MAX_CHARGE_LEVEL, 50, 100,
                                  lambda value: {"moduleType": 2, "operateType": "upsConfig",
                                                 "moduleSn": client.device_sn,
                                                 "params": {"maxChgSoc": int(value)}}),

            MinBatteryLevelEntity(client, "bms_emsStatus.minDsgSoc", const.MIN_DISCHARGE_LEVEL, 0, 30,
                                  lambda value: {"moduleType": 2, "operateType": "dsgCfg",
                                                 "moduleSn": client.device_sn,
                                                 "params": {"minDsgSoc": int(value)}}),

            MinGenStartLevelEntity(client, "bms_emsStatus.minOpenOilEbSoc", const.GEN_AUTO_START_LEVEL, 0, 30,
                                   lambda value: {"moduleType": 2, "operateType": "closeOilSoc",
                                                  "moduleSn": client.device_sn,
                                                  "params": {"closeOilSoc": value}}),

            MaxGenStopLevelEntity(client, "bms_emsStatus.maxCloseOilEbSoc", const.GEN_AUTO_STOP_LEVEL, 50, 100,
                                  lambda value: {"moduleType": 2, "operateType": "openOilSoc",
                                                 "moduleSn": client.device_sn,
                                                 "params": {"openOilSoc": value}}),

            ChargingPowerEntity(client, "inv.SlowChgWatts", const.AC_CHARGING_POWER, 200, 2400,
                                lambda value: {"moduleType": 3, "operateType": "acChgCfg",
                                               "moduleSn": client.device_sn,
                                               "params": {"slowChgWatts": int(value), "fastChgWatts":255, "chgPauseFlag": 0}})

        ]

    def switches(self, client: EcoflowMQTTClient) -> list[BaseSwitchEntity]:
        return [
            BeeperEntity(client, "pd.beepMode", const.BEEPER,
                         lambda value: {"moduleType": 1, "operateType": "quietCfg",
                                        "moduleSn": client.device_sn,
                                        "params": {"enabled": value}}),

            EnabledEntity(client, "pd.dcOutState", const.USB_ENABLED,
                          lambda value: {"moduleType": 1, "operateType": "dcOutCfg",
                                        "moduleSn": client.device_sn,
                                        "params": {"enabled": value }}),

            EnabledEntity(client, "pd.newAcAutoOnCfg", const.AC_ALWAYS_ENABLED,
                          lambda value: {"moduleType": 1, "operateType": "newAcAutoOnCfg",
                                         "moduleSn": client.device_sn,
                                         "params": {"enabled": value, "minAcSoc": 5}}),

            EnabledEntity(client, "inv.cfgAcEnabled", const.AC_ENABLED,
                          lambda value: {"moduleType": 3, "operateType": "acOutCfg",
                                         "moduleSn": client.device_sn,
                                         "params": {"enabled": value }}),

            EnabledEntity(client, "inv.cfgAcXboost", const.XBOOST_ENABLED,
                          lambda value: {"moduleType": 3, "operateType": "acOutCfg",
                                         "moduleSn": client.device_sn,
                                         "params": {"xboost": value}})
        ]

    def selects(self, client: EcoflowMQTTClient) -> list[BaseSelectEntity]:
        return [
            TimeoutDictSelectEntity(client, "pd.lcdOffSec", const.SCREEN_TIMEOUT, const.SCREEN_TIMEOUT_OPTIONS,
                                    lambda value: {"moduleType": 1, "operateType": "lcdCfg",
                                                   "moduleSn": "R351ZEB4HF4E0717",
                                                   "params": {"brighLevel": 255, "delayOff": value}}),

            TimeoutDictSelectEntity(client, "inv.standbyMin", const.UNIT_TIMEOUT, const.UNIT_TIMEOUT_OPTIONS,
                                    lambda value: {"moduleType": 1, "operateType": "standbyTime",
                                                   "moduleSn": "R351ZEB4HF4E0717",
                                                   "params": {"standbyMin": value}}),

            TimeoutDictSelectEntity(client, "mppt.carStandbyMin", const.AC_TIMEOUT, const.AC_TIMEOUT_OPTIONS,
                                    lambda value: {"moduleType": 5, "operateType": "standbyTime",
                                                   "moduleSn": "R351ZEB4HF4E0717",
                                                   "params": {"standbyMins": value}}),
        ]
