from . import const, BaseDevice
from ..entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, BaseSelectEntity
from ..mqtt.ecoflow_mqtt import EcoflowMQTTClient
from ..number import LevelEntity, MinBatteryLevelEntity, MaxBatteryLevelEntity
from ..select import DictSelectEntity
from ..sensor import LevelSensorEntity, WattsSensorEntity, RemainSensorEntity, TempSensorEntity, \
    CyclesSensorEntity
from ..switch import EnabledEntity


class DeltaPro(BaseDevice):
    def sensors(self, client: EcoflowMQTTClient) -> list[BaseSensorEntity]:
        return [
            LevelSensorEntity(client, "pd.soc", const.MAIN_BATTERY_LEVEL),
            WattsSensorEntity(client, "pd.wattsInSum", const.TOTAL_IN_POWER),
            WattsSensorEntity(client, "pd.wattsOutSum", const.TOTAL_OUT_POWER),

            RemainSensorEntity(client, "pd.remainTime", const.REMAINING_TIME),
            TempSensorEntity(client, "bmsMaster.temp", const.BATTERY_TEMP),
            TempSensorEntity(client, "bmsSlave1.temp", const.SLAVE_BATTERY_TEMP),

            CyclesSensorEntity(client, "bmsMaster.cycles", const.CYCLES),
            CyclesSensorEntity(client, "bmsSlave1.cycles", const.SLAVE_CYCLES),
        ]

    def numbers(self, client: EcoflowMQTTClient) -> list[BaseNumberEntity]:
        return [
            MaxBatteryLevelEntity(client, "bmsMaster.maxChargeSoc", const.MAX_CHARGE_LEVEL, 50, 100, None),
            MinBatteryLevelEntity(client, "bmsMaster.minDsgSoc", const.MIN_DISCHARGE_LEVEL, 0, 30, None),
        ]

    def switches(self, client: EcoflowMQTTClient) -> list[BaseSwitchEntity]:
        return [
            EnabledEntity(client, "inv.cfgAcEnabled", const.AC_ENABLED, None),
            EnabledEntity(client, "inv.cfgAcXboost", const.XBOOST_ENABLED, None)
        ]

    def selects(self, client: EcoflowMQTTClient) -> list[BaseSelectEntity]:
        return [
            DictSelectEntity(client, "mppt.cfgDcChgCurrent", const.DC_CHARGE_CURRENT, const.DC_CHARGE_CURRENT_OPTIONS,
                             None),

            DictSelectEntity(client, "pd.lcdOffSec", const.SCREEN_TIMEOUT, const.SCREEN_TIMEOUT_OPTIONS, None),

            DictSelectEntity(client, "pd.standByMode", const.UNIT_TIMEOUT, const.UNIT_TIMEOUT_OPTIONS, None),

            DictSelectEntity(client, "inv.cfgStandbyMin", const.AC_TIMEOUT, const.AC_TIMEOUT_OPTIONS, None),

        ]
