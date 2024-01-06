from homeassistant.const import Platform

from . import const, BaseDevice, EntityMigration, MigrationAction
from .const import ATTR_DESIGN_CAPACITY, ATTR_FULL_CAPACITY, ATTR_REMAIN_CAPACITY
from ..entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, BaseSelectEntity
from ..mqtt.ecoflow_mqtt import EcoflowMQTTClient
from ..number import MaxBatteryLevelEntity
from ..select import DictSelectEntity
from ..sensor import LevelSensorEntity, WattsSensorEntity, RemainSensorEntity, TempSensorEntity, \
    CyclesSensorEntity, InWattsSensorEntity, OutWattsSensorEntity, VoltSensorEntity, InVoltSensorEntity, \
    InAmpSensorEntity, AmpSensorEntity, StatusSensorEntity, MilliVoltSensorEntity, InMilliVoltSensorEntity, \
    OutMilliVoltSensorEntity
from ..switch import EnabledEntity, BeeperEntity


class RiverPro(BaseDevice):
    def sensors(self, client: EcoflowMQTTClient) -> list[BaseSensorEntity]:
        return [
            LevelSensorEntity(client, "bmsMaster.soc", const.MAIN_BATTERY_LEVEL)
                .attr("bmsMaster.designCap", ATTR_DESIGN_CAPACITY, 0)
                .attr("bmsMaster.fullCap", ATTR_FULL_CAPACITY, 0)
                .attr("bmsMaster.remainCap", ATTR_REMAIN_CAPACITY, 0),

            WattsSensorEntity(client, "pd.wattsInSum", const.TOTAL_IN_POWER),
            WattsSensorEntity(client, "pd.wattsOutSum", const.TOTAL_OUT_POWER),

            InAmpSensorEntity(client, "inv.dcInAmp", const.SOLAR_IN_CURRENT),
            InVoltSensorEntity(client, "inv.dcInVol", const.SOLAR_IN_VOLTAGE),

            InWattsSensorEntity(client, "inv.inputWatts", const.AC_IN_POWER),
            OutWattsSensorEntity(client, "inv.outputWatts", const.AC_OUT_POWER),

            InMilliVoltSensorEntity(client, "inv.acInVol", const.AC_IN_VOLT),
            OutMilliVoltSensorEntity(client, "inv.invOutVol", const.AC_OUT_VOLT),

            OutWattsSensorEntity(client, "pd.carWatts", const.DC_OUT_POWER),
            OutWattsSensorEntity(client, "pd.typecWatts", const.TYPEC_OUT_POWER),

            OutWattsSensorEntity(client, "pd.usb1Watts", const.USB_1_OUT_POWER),
            OutWattsSensorEntity(client, "pd.usb2Watts", const.USB_2_OUT_POWER),
            OutWattsSensorEntity(client, "pd.usb3Watts", const.USB_3_OUT_POWER),

            RemainSensorEntity(client, "pd.remainTime", const.REMAINING_TIME),
            TempSensorEntity(client, "bmsMaster.temp", const.BATTERY_TEMP),
            TempSensorEntity(client, "bmsMaster.minCellTemp", const.MIN_CELL_TEMP, False),
            TempSensorEntity(client, "bmsMaster.maxCellTemp", const.MAX_CELL_TEMP, False),

            MilliVoltSensorEntity(client, "bmsMaster.vol", const.BATTERY_VOLT, False),
            AmpSensorEntity(client, "bmsMaster.amp", const.BATTERY_AMP, False),
            MilliVoltSensorEntity(client, "bmsMaster.minCellVol", const.MIN_CELL_VOLT, False),
            MilliVoltSensorEntity(client, "bmsMaster.maxCellVol", const.MAX_CELL_VOLT, False),

            CyclesSensorEntity(client, "bmsMaster.cycles", const.CYCLES),


            # Optional Slave Batteries
            LevelSensorEntity(client, "bmsSlave1.soc", const.SLAVE_BATTERY_LEVEL, False, True)
                .attr("bmsSlave1.designCap", ATTR_DESIGN_CAPACITY, 0)
                .attr("bmsSlave1.fullCap", ATTR_FULL_CAPACITY, 0)
                .attr("bmsSlave1.remainCap", ATTR_REMAIN_CAPACITY, 0),

            CyclesSensorEntity(client, "bmsSlave1.cycles", const.SLAVE_CYCLES, False, True),
            TempSensorEntity(client, "bmsSlave1.temp", const.SLAVE_BATTERY_TEMP, False, True),
            MilliVoltSensorEntity(client, "bmsSlave1.vol", const.SLAVE_BATTERY_VOLT, False),
            AmpSensorEntity(client, "bmsSlave1.amp", const.SLAVE_BATTERY_AMP, False),
            MilliVoltSensorEntity(client, "bmsSlave1.minCellVol", const.SLAVE_MIN_CELL_VOLT, False),
            MilliVoltSensorEntity(client, "bmsSlave1.maxCellVol", const.SLAVE_MAX_CELL_VOLT, False),


            StatusSensorEntity(client),

        ]

    def numbers(self, client: EcoflowMQTTClient) -> list[BaseNumberEntity]:
        return [
            MaxBatteryLevelEntity(client, "bmsMaster.maxChargeSoc", const.MAX_CHARGE_LEVEL, 50, 100, None),
            # MinBatteryLevelEntity(client, "bmsMaster.minDsgSoc", const.MIN_DISCHARGE_LEVEL, 0, 30, None),
        ]

    def switches(self, client: EcoflowMQTTClient) -> list[BaseSwitchEntity]:
        return [
            BeeperEntity(client, "pd.beepState", const.BEEPER, None),
            EnabledEntity(client, "inv.cfgAcEnabled", const.AC_ENABLED, None),
            EnabledEntity(client, "inv.cfgAcXboost", const.XBOOST_ENABLED, None)
        ]

    def selects(self, client: EcoflowMQTTClient) -> list[BaseSelectEntity]:
        return [

            DictSelectEntity(client, "pd.standByMode", const.UNIT_TIMEOUT, const.UNIT_TIMEOUT_OPTIONS, None),
            DictSelectEntity(client, "inv.cfgStandbyMin", const.AC_TIMEOUT, const.AC_TIMEOUT_OPTIONS, None),

        ]

    def migrate(self, version) -> list[EntityMigration]:
        if version == 2:
            return [
                EntityMigration("pd.soc", Platform.SENSOR, MigrationAction.REMOVE),
            ]
        return []
