from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import const, BaseDevice
from custom_components.ecoflow_cloud.entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, \
    BaseSelectEntity
from custom_components.ecoflow_cloud.number import ChargingPowerEntity, MaxBatteryLevelEntity, MinBatteryLevelEntity, \
    MinGenStartLevelEntity, \
    MaxGenStopLevelEntity
from custom_components.ecoflow_cloud.select import DictSelectEntity, TimeoutDictSelectEntity
from custom_components.ecoflow_cloud.sensor import LevelSensorEntity, WattsSensorEntity, RemainSensorEntity, \
    TempSensorEntity, \
    CyclesSensorEntity, InWattsSensorEntity, OutWattsSensorEntity, OutWattsDcSensorEntity, InWattsSolarSensorEntity, \
    InVoltSolarSensorEntity, InAmpSolarSensorEntity, OutVoltDcSensorEntity, \
    InEnergySensorEntity, OutEnergySensorEntity, MilliVoltSensorEntity, InMilliVoltSensorEntity, \
    OutMilliVoltSensorEntity, AmpSensorEntity, CapacitySensorEntity, QuotaStatusSensorEntity
from custom_components.ecoflow_cloud.switch import BeeperEntity, EnabledEntity


class DeltaPro(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [
            LevelSensorEntity(client, self, "bmsMaster.soc", const.MAIN_BATTERY_LEVEL)
            .attr("bmsMaster.designCap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("bmsMaster.fullCap", const.ATTR_FULL_CAPACITY, 0)
            .attr("bmsMaster.remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            LevelSensorEntity(client, self, "bmsMaster.f32ShowSoc", const.MAIN_BATTERY_LEVEL_F32, False)
            .attr("bmsMaster.designCap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("bmsMaster.fullCap", const.ATTR_FULL_CAPACITY, 0)
            .attr("bmsMaster.remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, self, "bmsMaster.designCap", const.MAIN_DESIGN_CAPACITY, False),
            CapacitySensorEntity(client, self, "bmsMaster.fullCap", const.MAIN_FULL_CAPACITY, False),
            CapacitySensorEntity(client, self, "bmsMaster.remainCap", const.MAIN_REMAIN_CAPACITY, False),
            LevelSensorEntity(client, self, "bmsMaster.soh", const.SOH),

            LevelSensorEntity(client, self, "ems.lcdShowSoc", const.COMBINED_BATTERY_LEVEL),
            LevelSensorEntity(client, self, "ems.f32LcdShowSoc", const.COMBINED_BATTERY_LEVEL_F32, False),
            WattsSensorEntity(client, self, "pd.wattsInSum", const.TOTAL_IN_POWER),
            WattsSensorEntity(client, self, "pd.wattsOutSum", const.TOTAL_OUT_POWER),
            AmpSensorEntity(client, self, "bmsMaster.amp", const.MAIN_BATTERY_CURRENT),

            InWattsSensorEntity(client, self, "inv.inputWatts", const.AC_IN_POWER),
            OutWattsSensorEntity(client, self, "inv.outputWatts", const.AC_OUT_POWER),

            InMilliVoltSensorEntity(client, self, "inv.acInVol", const.AC_IN_VOLT),
            OutMilliVoltSensorEntity(client, self, "inv.invOutVol", const.AC_OUT_VOLT),

            InWattsSolarSensorEntity(client, self, "mppt.inWatts", const.SOLAR_IN_POWER),
            InVoltSolarSensorEntity(client, self, "mppt.inVol", const.SOLAR_IN_VOLTAGE),
            InAmpSolarSensorEntity(client, self, "mppt.inAmp", const.SOLAR_IN_CURRENT),

            OutWattsDcSensorEntity(client, self, "mppt.outWatts", const.DC_OUT_POWER),
            OutVoltDcSensorEntity(client, self, "mppt.outVol", const.DC_OUT_VOLTAGE),

            OutWattsSensorEntity(client, self, "mppt.carOutWatts", const.DC_CAR_OUT_POWER),
            OutWattsSensorEntity(client, self, "mppt.dcdc12vWatts", const.DC_ANDERSON_OUT_POWER),

            OutWattsSensorEntity(client, self, "pd.typec1Watts", const.TYPEC_1_OUT_POWER),
            OutWattsSensorEntity(client, self, "pd.typec2Watts", const.TYPEC_2_OUT_POWER),

            OutWattsSensorEntity(client, self, "pd.usb1Watts", const.USB_1_OUT_POWER),
            OutWattsSensorEntity(client, self, "pd.usb2Watts", const.USB_2_OUT_POWER),

            OutWattsSensorEntity(client, self, "pd.qcUsb1Watts", const.USB_QC_1_OUT_POWER),
            OutWattsSensorEntity(client, self, "pd.qcUsb2Watts", const.USB_QC_2_OUT_POWER),

            RemainSensorEntity(client, self, "ems.chgRemainTime", const.CHARGE_REMAINING_TIME),
            RemainSensorEntity(client, self, "ems.dsgRemainTime", const.DISCHARGE_REMAINING_TIME),
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
            InEnergySensorEntity(client, self, "pd.chgPowerAc", const.CHARGE_AC_ENERGY),
            InEnergySensorEntity(client, self, "pd.chgPowerDc", const.CHARGE_DC_ENERGY),
            OutEnergySensorEntity(client, self, "pd.dsgPowerAc", const.DISCHARGE_AC_ENERGY),
            OutEnergySensorEntity(client, self, "pd.dsgPowerDc", const.DISCHARGE_DC_ENERGY),

            # Optional Slave Batteries
            LevelSensorEntity(client, self, "bmsSlave1.soc", const.SLAVE_N_BATTERY_LEVEL % 1, False, True)
            .attr("bmsSlave1.designCap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("bmsSlave1.fullCap", const.ATTR_FULL_CAPACITY, 0)
            .attr("bmsSlave1.remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            LevelSensorEntity(client, self, "bmsSlave1.f32ShowSoc", const.SLAVE_N_BATTERY_LEVEL_F32 % 1, False, False)
            .attr("bmsSlave1.designCap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("bmsSlave1.fullCap", const.ATTR_FULL_CAPACITY, 0)
            .attr("bmsSlave1.remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, self, "bmsSlave1.designCap", const.SLAVE_N_DESIGN_CAPACITY % 1, False),
            CapacitySensorEntity(client, self, "bmsSlave1.fullCap", const.SLAVE_N_FULL_CAPACITY % 1, False),
            CapacitySensorEntity(client, self, "bmsSlave1.remainCap", const.SLAVE_N_REMAIN_CAPACITY % 1, False),
            LevelSensorEntity(client, self, "bmsSlave1.soh", const.SLAVE_N_SOH % 1),

            TempSensorEntity(client, self, "bmsSlave1.temp", const.SLAVE_N_BATTERY_TEMP % 1, False, True)
            .attr("bmsSlave1.minCellTemp", const.ATTR_MIN_CELL_TEMP, 0)
            .attr("bmsSlave1.maxCellTemp", const.ATTR_MAX_CELL_TEMP, 0),
            WattsSensorEntity(client, self, "bmsSlave1.inputWatts", const.SLAVE_N_IN_POWER % 1, False, True),
            WattsSensorEntity(client, self, "bmsSlave1.outputWatts", const.SLAVE_N_OUT_POWER % 1, False, True),

            LevelSensorEntity(client, self, "bmsSlave2.soc", const.SLAVE_N_BATTERY_LEVEL % 2, False, True)
            .attr("bmsSlave2.designCap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("bmsSlave2.fullCap", const.ATTR_FULL_CAPACITY, 0)
            .attr("bmsSlave2.remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            LevelSensorEntity(client, self, "bmsSlave2.f32ShowSoc", const.SLAVE_N_BATTERY_LEVEL_F32 % 2, False, False)
            .attr("bmsSlave2.designCap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("bmsSlave2.fullCap", const.ATTR_FULL_CAPACITY, 0)
            .attr("bmsSlave2.remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, self, "bmsSlave2.designCap", const.SLAVE_N_DESIGN_CAPACITY % 2, False),
            CapacitySensorEntity(client, self, "bmsSlave2.fullCap", const.SLAVE_N_FULL_CAPACITY % 2, False),
            CapacitySensorEntity(client, self, "bmsSlave2.remainCap", const.SLAVE_N_REMAIN_CAPACITY % 2, False),
            LevelSensorEntity(client, self, "bmsSlave2.soh", const.SLAVE_N_SOH % 2),
            MilliVoltSensorEntity(client, self, "bmsSlave1.vol", const.SLAVE_N_BATTERY_VOLT % 1, False),
            MilliVoltSensorEntity(client, self, "bmsSlave1.minCellVol", const.SLAVE_N_MIN_CELL_VOLT % 1, False),
            MilliVoltSensorEntity(client, self, "bmsSlave1.maxCellVol", const.SLAVE_N_MAX_CELL_VOLT % 1, False),
            AmpSensorEntity(client, self, "bmsSlave1.amp", const.SLAVE_N_BATTERY_CURRENT % 1, False),
            MilliVoltSensorEntity(client, self, "bmsSlave2.vol", const.SLAVE_N_BATTERY_VOLT % 2, False),
            MilliVoltSensorEntity(client, self, "bmsSlave2.minCellVol", const.SLAVE_N_MIN_CELL_VOLT % 2, False),
            MilliVoltSensorEntity(client, self, "bmsSlave2.maxCellVol", const.SLAVE_N_MAX_CELL_VOLT % 2, False),
            AmpSensorEntity(client, self, "bmsSlave2.amp", const.SLAVE_N_BATTERY_CURRENT % 2, False),
            TempSensorEntity(client, self, "bmsSlave2.temp", const.SLAVE_N_BATTERY_TEMP % 2, False, True)
            .attr("bmsSlave2.minCellTemp", const.ATTR_MIN_CELL_TEMP, 0)
            .attr("bmsSlave2.maxCellTemp", const.ATTR_MAX_CELL_TEMP, 0),
            WattsSensorEntity(client, self, "bmsSlave2.inputWatts", const.SLAVE_N_IN_POWER % 2, False, True),
            WattsSensorEntity(client, self, "bmsSlave2.outputWatts", const.SLAVE_N_OUT_POWER % 2, False, True),
            CyclesSensorEntity(client, self, "bmsSlave1.cycles", const.SLAVE_N_CYCLES % 1, False),
            CyclesSensorEntity(client, self, "bmsSlave2.cycles", const.SLAVE_N_CYCLES % 2, False),
            QuotaStatusSensorEntity(client, self)
        ]

    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return [
            MaxBatteryLevelEntity(client, self, "ems.maxChargeSoc", const.MAX_CHARGE_LEVEL, 50, 100,
                                  lambda value: {"operateType": "TCP", "params": {"cmdSet": 32, "id": 49, "maxChgSoc": value}}),
            MinBatteryLevelEntity(client, self, "ems.minDsgSoc", const.MIN_DISCHARGE_LEVEL, 0, 30,
                                  lambda value: {"operateType": "TCP", "params": {"cmdSet": 32, "id": 51, "minDsgSoc": value}}),
            MaxBatteryLevelEntity(client, self, "pd.bpPowerSoc", const.BACKUP_RESERVE_LEVEL, 5, 100,
                                  lambda value: {"operateType": "TCP",
                                                 "params": {"cmdSet": 32, "isConfig": 1, "bpPowerSoc": int(value), "minDsgSoc": 0,
                                                            "maxChgSoc": 0, "id": 94}}),
            MinGenStartLevelEntity(client, self, "ems.minOpenOilEbSoc", const.GEN_AUTO_START_LEVEL, 0, 30,
                                   lambda value: {"operateType": "TCP", "params": {"cmdSet": 32, "openOilSoc": value, "id": 52}}),

            MaxGenStopLevelEntity(client, self, "ems.maxCloseOilEbSoc", const.GEN_AUTO_STOP_LEVEL, 50, 100,
                                  lambda value: {"operateType": "TCP", "params": {"cmdSet": 32, "closeOilSoc": value, "id": 53}}),

            ChargingPowerEntity(client, self, "inv.cfgSlowChgWatts", const.AC_CHARGING_POWER, 200, 2900,
                                lambda value: {"operateType": "TCP", "params": {"cmdSet": 32, "slowChgPower": value, "id": 69}}),

        ]

    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        return [
            BeeperEntity(client, self, "pd.beepState", const.BEEPER,
                         lambda value: {"operateType": "TCP", "params": {"cmdSet": 32, "id": 38, "enabled": value}}),
            EnabledEntity(client, self, "mppt.carState", const.DC_ENABLED,
                          lambda value: {"operateType": "TCP", "params": {"cmdSet": 32, "id": 81, "enabled": value}}),
            EnabledEntity(client, self, "inv.cfgAcEnabled", const.AC_ENABLED,
                          lambda value: {"operateType": "TCP", "params": {"cmdSet": 32, "id": 66, "enabled": value}}),

            EnabledEntity(client, self, "inv.cfgAcXboost", const.XBOOST_ENABLED,
                          lambda value: {"operateType": "TCP", "params": {"cmdSet": 32, "id": 66, "xboost": value}}),
            EnabledEntity(client, self, "pd.acautooutConfig", const.AC_ALWAYS_ENABLED,
                          lambda value: {"operateType": "TCP", "params": {"cmdSet": 32, "id": 95, "acautooutConfig": value}}),
            EnabledEntity(client, self, "pd.watthisconfig", const.BP_ENABLED,
                          lambda value, params: {"operateType": "TCP",
                                                 "params": {"cmdSet": 32, "id": 94, "isConfig": value,
                                                            "bpPowerSoc": value * 50,
                                                            "minDsgSoc": 0,
                                                            "maxChgSoc": 0}}),
        ]

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return [
            DictSelectEntity(client, self, "mppt.cfgDcChgCurrent", const.DC_CHARGE_CURRENT, const.DC_CHARGE_CURRENT_OPTIONS,
                             lambda value: {"operateType": "TCP", "params": {"cmdSet": 32, "currMa": value, "id": 71}}),

            TimeoutDictSelectEntity(client, self, "pd.lcdOffSec", const.SCREEN_TIMEOUT, const.SCREEN_TIMEOUT_OPTIONS,
                                    lambda value: {"operateType": "TCP", "params": {"cmdSet": 32, "lcdTime": value, "id": 39}}),

            TimeoutDictSelectEntity(client, self, "pd.standByMode", const.UNIT_TIMEOUT, const.UNIT_TIMEOUT_OPTIONS_LIMITED,
                                    lambda value: {"operateType": "TCP", "params": {"cmdSet": 32, "standByMode": value, "id": 33}}),

            TimeoutDictSelectEntity(client, self, "inv.cfgStandbyMin", const.AC_TIMEOUT, const.AC_TIMEOUT_OPTIONS,
                                    lambda value: {"operateType": "TCP", "params": {"cmdSet": 32, "standByMins": value, "id": 153}}),

        ]
