from . import const, BaseDevice
from ..mqtt.ecoflow_mqtt import EcoflowMQTTClient
from ..entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, BaseSelectEntity
from ..number import LevelEntity, ChargingPowerEntity
from ..select import DictSelectEntity
from ..sensor import LevelSensorEntity, WattsSensorEntity, RemainSensorEntity, TempSensorEntity, \
    CyclesSensorEntity, FanSensorEntity
from ..switch import EnabledEntity


class River2Max(BaseDevice):
    def sensors(self, client: EcoflowMQTTClient) -> list[BaseSensorEntity]:
        return [
            LevelSensorEntity(client, "pd.soc", const.MAIN_BATTERY_LEVEL),
            WattsSensorEntity(client, "pd.wattsInSum", const.TOTAL_IN_POWER),
            WattsSensorEntity(client, "pd.wattsOutSum", const.TOTAL_OUT_POWER),
            RemainSensorEntity(client, "bms_emsStatus.chgRemainTime", const.CHARGE_REMAINING_TIME),
            RemainSensorEntity(client, "bms_emsStatus.dsgRemainTime", const.DISCHARGE_REMAINING_TIME),

            TempSensorEntity(client, "inv.outTemp", "Inv Out Temperature"),
            TempSensorEntity(client, "bms_bmsStatus.temp", const.BATTERY_TEMP),
            CyclesSensorEntity(client, "bms_bmsStatus.cycles", const.CYCLES),

            FanSensorEntity(client, "bms_emsStatus.fanLevel", "Fan Level"),

        ]

    def numbers(self, client: EcoflowMQTTClient) -> list[BaseNumberEntity]:
        return [
            LevelEntity(client, "bms_emsStatus.maxChargeSoc", const.MAX_CHARGE_LEVEL, 50, 100,
                        lambda value: {"moduleType": 2, "operateType": "upsConfig",
                                       "params": {"maxChgSoc": int(value)}}),

            LevelEntity(client, "bms_emsStatus.minDsgSoc", const.MIN_DISCHARGE_LEVEL, 0, 30,
                        lambda value: {"moduleType": 2, "operateType": "upsConfig",
                                       "params": {"minDsgSoc": int(value)}}),

            ChargingPowerEntity(client, "mppt.cfgChgWatts", const.AC_CHARGING_POWER, 100, 660,
                                lambda value: {"moduleType": 5, "operateType": "acChgCfg",
                                               "params": {"chgWatts": int(value), "chgPauseFlag": 255}}),
        ]

    def switches(self, client: EcoflowMQTTClient) -> list[BaseSwitchEntity]:
        return [
            EnabledEntity(client, "mppt.cfgAcEnabled", const.AC_ENABLED,
                          lambda value: {"moduleType": 5, "operateType": "acOutCfg",
                                         "params": {"enabled": value, "out_voltage": -1, "out_freq": 255,
                                                    "xboost": 255}}),

            EnabledEntity(client, "pd.carState", const.DC_ENABLED,
                          lambda value: {"moduleType": 5, "operateType": "mpptCar", "params": {"enabled": value}})
        ]

    def selects(self, client: EcoflowMQTTClient) -> list[BaseSelectEntity]:
        return [
            DictSelectEntity(client, "mppt.dcChgCurrent", const.DC_CHARGE_CURRENT, const.DC_CHARGE_CURRENT_OPTIONS,
                             lambda value: {"moduleType": 5, "operateType": "dcChgCfg",
                                            "params": {"dcChgCfg": value}}),

            DictSelectEntity(client, "mppt.scrStandbyMin", const.SCREEN_TIMEOUT, const.SCREEN_TIMEOUT_OPTIONS,
                             lambda value: {"moduleType": 5, "operateType": "lcdCfg",
                                            "params": {"brighLevel": 255, "delayOff": value}}),

            DictSelectEntity(client, "mppt.powStandbyMin", const.UNIT_TIMEOUT, const.UNIT_TIMEOUT_OPTIONS,
                             lambda value: {"moduleType": 5, "operateType": "standby",
                                            "params": {"standbyMins": value}}),

            DictSelectEntity(client, "mppt.acStandbyMins", const.AC_TIMEOUT, const.AC_TIMEOUT_OPTIONS,
                             lambda value: {"moduleType": 5, "operateType": "acStandby",
                                            "params": {"standbyMins": value}})
        ]
