from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import const, BaseDevice
from custom_components.ecoflow_cloud.entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, BaseSelectEntity
from custom_components.ecoflow_cloud.number import MaxBatteryLevelEntity
from custom_components.ecoflow_cloud.select import DictSelectEntity
from custom_components.ecoflow_cloud.sensor import LevelSensorEntity, WattsSensorEntity, RemainSensorEntity, \
    TempSensorEntity, \
    CyclesSensorEntity, InWattsSensorEntity, OutWattsSensorEntity, InEnergySensorEntity, OutEnergySensorEntity, \
    MilliVoltSensorEntity, InMilliVoltSensorEntity, \
    OutMilliVoltSensorEntity, CapacitySensorEntity, QuotaStatusSensorEntity
from custom_components.ecoflow_cloud.switch import EnabledEntity, BeeperEntity, FanModeEntity


class RiverMax(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [
            LevelSensorEntity(client, self, "bmsMaster.soc", const.MAIN_BATTERY_LEVEL)
                .attr("bmsMaster.designCap", const.ATTR_DESIGN_CAPACITY, 0)
                .attr("bmsMaster.fullCap", const.ATTR_FULL_CAPACITY, 0)
                .attr("bmsMaster.remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, self, "bmsMaster.designCap", const.MAIN_DESIGN_CAPACITY, False),
            CapacitySensorEntity(client, self, "bmsMaster.fullCap", const.MAIN_FULL_CAPACITY, False),
            CapacitySensorEntity(client, self, "bmsMaster.remainCap", const.MAIN_REMAIN_CAPACITY, False),

            WattsSensorEntity(client, self, "pd.wattsInSum", const.TOTAL_IN_POWER),
            WattsSensorEntity(client, self, "pd.wattsOutSum", const.TOTAL_OUT_POWER),

            InWattsSensorEntity(client, self, "inv.inputWatts", const.AC_IN_POWER),
            OutWattsSensorEntity(client, self, "inv.outputWatts", const.AC_OUT_POWER),

            InMilliVoltSensorEntity(client, self, "inv.acInVol", const.AC_IN_VOLT),
            OutMilliVoltSensorEntity(client, self, "inv.invOutVol", const.AC_OUT_VOLT),

            OutWattsSensorEntity(client, self, "pd.carWatts", const.DC_OUT_POWER),

            OutWattsSensorEntity(client, self, "pd.typecWatts", const.TYPEC_OUT_POWER),

            OutWattsSensorEntity(client, self, "pd.usb1Watts", const.USB_1_OUT_POWER),
            OutWattsSensorEntity(client, self, "pd.usb2Watts", const.USB_2_OUT_POWER),
            OutWattsSensorEntity(client, self, "pd.usb3Watts", const.USB_3_OUT_POWER),

            RemainSensorEntity(client, self, "pd.remainTime", const.REMAINING_TIME),
            CyclesSensorEntity(client, self, "bmsMaster.cycles", const.CYCLES),

            TempSensorEntity(client, self, "bmsMaster.temp", const.BATTERY_TEMP)
                .attr("bmsMaster.minCellTemp", const.ATTR_MIN_CELL_TEMP, 0)
                .attr("bmsMaster.maxCellTemp", const.ATTR_MAX_CELL_TEMP, 0),
            TempSensorEntity(client, self, "bmsMaster.minCellTemp", const.MIN_CELL_TEMP, False),
            TempSensorEntity(client, self, "bmsMaster.maxCellTemp", const.MAX_CELL_TEMP, False),

            MilliVoltSensorEntity(client, self, "bmsMaster.vol", const.BATTERY_VOLT, False)
                .attr("bmsMaster.minCellVol", const.ATTR_MIN_CELL_VOLT, 0)
                .attr("bmsMaster.maxCellVol", const.ATTR_MAX_CELL_VOLT, 0),
            MilliVoltSensorEntity(client, self, "bmsMaster.minCellVol", const.MIN_CELL_VOLT, False),
            MilliVoltSensorEntity(client, self, "bmsMaster.maxCellVol", const.MAX_CELL_VOLT, False),

            # https://github.com/tolwi/hassio-ecoflow-cloud/discussions/87
            InEnergySensorEntity(client, self, "pd.chgSunPower", const.SOLAR_IN_ENERGY),
            InEnergySensorEntity(client, self, "pd.chgPowerAC", const.CHARGE_AC_ENERGY),
            InEnergySensorEntity(client, self, "pd.chgPowerDC", const.CHARGE_DC_ENERGY),
            OutEnergySensorEntity(client, self, "pd.dsgPowerAC", const.DISCHARGE_AC_ENERGY),
            OutEnergySensorEntity(client, self, "pd.dsgPowerDC", const.DISCHARGE_DC_ENERGY),

            LevelSensorEntity(client, self, "bmsSlave1.soc", const.SLAVE_BATTERY_LEVEL, False, True)
                .attr("bmsSlave1.designCap", const.ATTR_DESIGN_CAPACITY, 0)
                .attr("bmsSlave1.fullCap", const.ATTR_FULL_CAPACITY, 0)
                .attr("bmsSlave1.remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, self, "bmsSlave1.designCap", const.SLAVE_DESIGN_CAPACITY, False),
            CapacitySensorEntity(client, self, "bmsSlave1.fullCap", const.SLAVE_FULL_CAPACITY, False),
            CapacitySensorEntity(client, self, "bmsSlave1.remainCap", const.SLAVE_REMAIN_CAPACITY, False),

            TempSensorEntity(client, self, "bmsSlave1.temp", const.SLAVE_BATTERY_TEMP, False, True)
                .attr("bmsSlave1.minCellTemp", const.ATTR_MIN_CELL_TEMP, 0)
                .attr("bmsSlave1.maxCellTemp", const.ATTR_MAX_CELL_TEMP, 0),
            TempSensorEntity(client, self, "bmsSlave1.minCellTemp", const.SLAVE_MIN_CELL_TEMP, False),
            TempSensorEntity(client, self, "bmsSlave1.maxCellTemp", const.SLAVE_MAX_CELL_TEMP, False),

            MilliVoltSensorEntity(client, self, "bmsSlave1.vol", const.BATTERY_VOLT, False)
                .attr("bmsSlave1.minCellVol", const.ATTR_MIN_CELL_VOLT, 0)
                .attr("bmsSlave1.maxCellVol", const.ATTR_MAX_CELL_VOLT, 0),
            MilliVoltSensorEntity(client, self, "bmsSlave1.minCellVol", const.MIN_CELL_VOLT, False),
            MilliVoltSensorEntity(client, self, "bmsSlave1.maxCellVol", const.MAX_CELL_VOLT, False),

            CyclesSensorEntity(client, self, "bmsSlave1.cycles", const.SLAVE_CYCLES, False, True),
            QuotaStatusSensorEntity(client, self)
        ]

    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return [
            MaxBatteryLevelEntity(client, self, "bmsMaster.maxChargeSoc", const.MAX_CHARGE_LEVEL, 30, 100, None),
            # MinBatteryLevelEntity(client, self, "bmsMaster.minDsgSoc", const.MIN_DISCHARGE_LEVEL, 0, 30, None),
        ]

    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        return [
            BeeperEntity(client, self, "pd.beepState", const.BEEPER, lambda value: {"moduleType": 0, "operateType": "TCP", "params": {"id": 38, "enabled": value}}),
            EnabledEntity(client, self, "inv.cfgAcEnabled", const.AC_ENABLED, lambda value: {"moduleType": 0, "operateType": "TCP", "params": {"id": 66, "enabled": value}}),
            EnabledEntity(client, self, "pd.carSwitch", const.DC_ENABLED, lambda value: {"moduleType": 0, "operateType": "TCP", "params": {"id": 34, "enabled": value}}),
            EnabledEntity(client, self, "inv.cfgAcXboost", const.XBOOST_ENABLED, lambda value: {"moduleType": 0, "operateType": "TCP", "params": {"id": 66, "xboost": value}}),
            FanModeEntity(client, self, "inv.cfgFanMode", const.AUTO_FAN_SPEED, lambda value: {"moduleType": 0, "operateType": "TCP", "params": {"id": 73, "fanMode": value}})
        ]
    
    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return [

            DictSelectEntity(client, self, "pd.standByMode", const.UNIT_TIMEOUT, const.UNIT_TIMEOUT_OPTIONS, lambda value: {"moduleType": 0, "operateType": "TCP", "params": {"id": 33, "standByMode": value}}),
            DictSelectEntity(client, self, "inv.cfgStandbyMin", const.AC_TIMEOUT, const.AC_TIMEOUT_OPTIONS, lambda value: {"moduleType": 0, "operateType": "TCP", "params": {"id": 153, "standByMins": value}}),

        ]

