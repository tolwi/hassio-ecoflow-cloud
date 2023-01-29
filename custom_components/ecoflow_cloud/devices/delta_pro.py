from . import const, BaseDevice
from ..mqtt.ecoflow_mqtt import EcoflowMQTTClient
from ..entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, BaseSelectEntity
from ..number import LevelEntity, ChargingPowerEntity
from ..select import DictSelectEntity
from ..sensor import LevelSensorEntity, WattsSensorEntity, RemainSensorEntity, TempSensorEntity, \
    CyclesSensorEntity
from ..switch import BeeperEntity, EnabledEntity


class DeltaPro(BaseDevice):
    def sensors(self, client: EcoflowMQTTClient) -> list[BaseSensorEntity]:
        return [
            LevelSensorEntity(client, "pd.soc", const.MAIN_BATTERY_LEVEL),
            WattsSensorEntity(client, "pd.wattsInSum", const.TOTAL_IN_POWER),
            WattsSensorEntity(client, "pd.wattsOutSum", const.TOTAL_OUT_POWER),
            RemainSensorEntity(client, "ems.chgRemainTime", const.CHARGE_REMAINING_TIME),
            RemainSensorEntity(client, "ems.dsgRemainTime", const.DISCHARGE_REMAINING_TIME),
            TempSensorEntity(client, "bmsMaster.temp", const.BATTERY_TEMP),
            CyclesSensorEntity(client, "bmsMaster.cycles", const.CYCLES)
        ]

    def numbers(self, client: EcoflowMQTTClient) -> list[BaseNumberEntity]:
        return [
            LevelEntity(client, "ems.maxChargeSoc", const.MAX_CHARGE_LEVEL, 50, 100,
                        lambda value: {"moduleType": 0, "operateType": "TCP",
                                       "params": {"id": 49, "maxChgSoc": value }}),
            LevelEntity(client, "ems.minDsgSoc", const.MIN_DISCHARGE_LEVEL, 0, 30,
                        lambda value: {"moduleType": 0, "operateType": "TCP",
                                       "params": {"id": 51, "minDsgSoc": value }}),

            LevelEntity(client, "ems.minOpenOilEbSoc", "Generator Auto Start Level", 0, 30,
                        lambda value: {"moduleType": 0, "operateType": "TCP",
                                       "params": {"openOilSoc": value, "id": 52}}),

            LevelEntity(client, "ems.maxCloseOilEbSoc", "Generator Auto Stop Level", 50, 100,
                        lambda value: {"moduleType": 0, "operateType": "TCP",
                                       "params": {"closeOilSoc": value, "id": 53}}),

            ChargingPowerEntity(client, "inv.cfgSlowChgWatts", const.AC_CHARGING_POWER, 200, 2900,
                                lambda value: {"moduleType": 0, "operateType": "TCP",
                                               "params": {"slowChgPower": value, "id": 69}}),

        ]

    def switches(self, client: EcoflowMQTTClient) -> list[BaseSwitchEntity]:
        return [
            BeeperEntity(client, "mppt.beepState", const.BEEPER,
                         lambda value: {"moduleType": 0, "operateType": "TCP", "params": {"id": 38, "enabled": value}}),
            EnabledEntity(client, "pd.dcOutState", const.USB_ENABLED,
                          lambda value: {"moduleType": 0, "operateType": "TCP",
                                         "params": {"id": 34, "enabled": value}}),
            EnabledEntity(client, "inv.cfgAcEnabled", const.AC_ENABLED,
                          lambda value: {"moduleType": 0, "operateType": "TCP",
                                         "params": {"id": 66, "enabled": value}}),

            EnabledEntity(client, "inv.cfgAcXboost", const.XBOOST_ENABLED,
                          lambda value: {"moduleType": 0, "operateType": "TCP", "params": {"id": 66, "xboost": value}}),

            EnabledEntity(client, "inv.acPassByAutoEn", const.AC_ALWAYS_ENABLED,
                          lambda value: {"moduleType": 0, "operateType": "TCP", "params": {"id": 84, "enabled": value}})
        ]

    def selects(self, client: EcoflowMQTTClient) -> list[BaseSelectEntity]:
        return [
            DictSelectEntity(client, "mppt.cfgDcChgCurrent", const.DC_CHARGE_CURRENT, const.DC_CHARGE_CURRENT_OPTIONS,
                            lambda value: {"moduleType": 0, "operateType": "TCP",
                                                 "params": {"currMa": value, "id": 71}}),

            DictSelectEntity(client, "pd.lcdOffSec", const.SCREEN_TIMEOUT, const.SCREEN_TIMEOUT_OPTIONS,
                                lambda value: {"moduleType": 0, "operateType": "TCP",
                                               "params": {"lcdTime": value, "id": 39}}),

            DictSelectEntity(client, "pd.standByMode", const.UNIT_TIMEOUT, const.UNIT_TIMEOUT_OPTIONS,
                                lambda value: {"moduleType": 0, "operateType": "TCP",
                                               "params": {"standByMode": value, "id": 33}}),

            DictSelectEntity(client, "inv.cfgStandbyMin", const.AC_TIMEOUT, const.AC_TIMEOUT_OPTIONS,
                                lambda value: {"moduleType": 0, "operateType": "TCP",
                                               "params": {"standByMins": value, "id": 153}}),

        ]