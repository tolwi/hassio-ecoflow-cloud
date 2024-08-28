from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import const, BaseDevice
from custom_components.ecoflow_cloud.entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, BaseSelectEntity
from custom_components.ecoflow_cloud.number import ChargingPowerEntity, MinBatteryLevelEntity, MaxBatteryLevelEntity, \
    MaxGenStopLevelEntity, MinGenStartLevelEntity
from custom_components.ecoflow_cloud.sensor import LevelSensorEntity, RemainSensorEntity, TempSensorEntity, \
    CyclesSensorEntity, \
    InWattsSensorEntity, OutWattsSensorEntity, MilliVoltSensorEntity, \
    InMilliVoltSensorEntity, OutMilliVoltSensorEntity, CapacitySensorEntity, InWattsSolarSensorEntity, \
    OutWattsDcSensorEntity, QuotaStatusSensorEntity
from custom_components.ecoflow_cloud.switch import BeeperEntity, EnabledEntity


class DeltaMax(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [
            LevelSensorEntity(client, self, "bmsMaster.soc", const.MAIN_BATTERY_LEVEL)
                .attr("bmsMaster.designCap", const.ATTR_DESIGN_CAPACITY, 0)
                .attr("bmsMaster.fullCap", const.ATTR_FULL_CAPACITY, 0)
                .attr("bmsMaster.remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, self, "bmsMaster.designCap", const.MAIN_DESIGN_CAPACITY, False),
            CapacitySensorEntity(client, self, "bmsMaster.fullCap", const.MAIN_FULL_CAPACITY, False),
            CapacitySensorEntity(client, self, "bmsMaster.remainCap", const.MAIN_REMAIN_CAPACITY, False),

            LevelSensorEntity(client, self, "ems.lcdShowSoc", const.COMBINED_BATTERY_LEVEL),
            InWattsSensorEntity(client, self, "pd.wattsInSum", const.TOTAL_IN_POWER),
            OutWattsSensorEntity(client, self, "pd.wattsOutSum", const.TOTAL_OUT_POWER),

            InWattsSensorEntity(client, self, "inv.inputWatts", const.AC_IN_POWER),
            OutWattsSensorEntity(client, self, "inv.outputWatts", const.AC_OUT_POWER),

            InMilliVoltSensorEntity(client, self, "inv.acInVol", const.AC_IN_VOLT),
            OutMilliVoltSensorEntity(client, self, "inv.invOutVol", const.AC_OUT_VOLT),

            InWattsSolarSensorEntity(client, self, "mppt.inWatts", const.SOLAR_IN_POWER),
            OutWattsDcSensorEntity(client, self, "mppt.outWatts", const.DC_OUT_POWER),

            OutWattsSensorEntity(client, self, "pd.typec1Watts", const.TYPEC_1_OUT_POWER),
            OutWattsSensorEntity(client, self, "pd.typec2Watts", const.TYPEC_2_OUT_POWER),

            OutWattsSensorEntity(client, self, "pd.usb1Watts", const.USB_1_OUT_POWER),
            OutWattsSensorEntity(client, self, "pd.usb2Watts", const.USB_2_OUT_POWER),

            OutWattsSensorEntity(client, self, "pd.qcUsb1Watts", const.USB_QC_1_OUT_POWER),
            OutWattsSensorEntity(client, self, "pd.qcUsb2Watts", const.USB_QC_2_OUT_POWER),

            RemainSensorEntity(client, self, "ems.chgRemainTime", const.CHARGE_REMAINING_TIME),
            RemainSensorEntity(client, self, "ems.dsgRemainTime", const.DISCHARGE_REMAINING_TIME),

            TempSensorEntity(client, self, "inv.outTemp", "Inv Out Temperature"),
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

            # Optional Slave Battery
            #LevelSensorEntity(client, self, "bms_slave.soc", const.SLAVE_BATTERY_LEVEL, False, True),
            #TempSensorEntity(client, self, "bms_slave.temp", const.SLAVE_BATTERY_TEMP, False, True),
            #TempSensorEntity(client, self, "bms_slave.minCellTemp", const.SLAVE_MIN_CELL_TEMP, False),
            #TempSensorEntity(client, self, "bms_slave.maxCellTemp", const.SLAVE_MAX_CELL_TEMP, False),

            #VoltSensorEntity(client, self, "bms_slave.vol", const.SLAVE_BATTERY_VOLT, False),
            #VoltSensorEntity(client, self, "bms_slave.minCellVol", const.SLAVE_MIN_CELL_VOLT, False),
            #VoltSensorEntity(client, self, "bms_slave.maxCellVol", const.SLAVE_MAX_CELL_VOLT, False),

            #CyclesSensorEntity(client, self, "bms_slave.cycles", const.SLAVE_CYCLES, False, True),
            #InWattsSensorEntity(client, self, "bms_slave.inputWatts", const.SLAVE_IN_POWER, False, True),
            #OutWattsSensorEntity(client, self, "bms_slave.outputWatts", const.SLAVE_OUT_POWER, False, True)
            QuotaStatusSensorEntity(client, self)
        ]

    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return [
            MaxBatteryLevelEntity(client, self, "ems.maxChargeSoc", const.MAX_CHARGE_LEVEL, 50, 100,
                                  lambda value: {"moduleType": 2, "operateType": "TCP",
                                                 "params": {"id": 49, "maxChgSoc": value}}),

            MinBatteryLevelEntity(client, self, "ems.minDsgSoc", const.MIN_DISCHARGE_LEVEL, 0, 30,
                                  lambda value: {"moduleType": 2, "operateType": "TCP",
                                                 "params": {"id": 51, "minDsgSoc": value}}),

            MinGenStartLevelEntity(client, self, "ems.minOpenOilEbSoc", const.GEN_AUTO_START_LEVEL, 0, 30,
                                   lambda value: {"moduleType": 2, "operateType": "TCP",
                                                  "params": {"id": 52, "openOilSoc": value}}),

            MaxGenStopLevelEntity(client, self, "ems.maxCloseOilEbSoc", const.GEN_AUTO_STOP_LEVEL, 50, 100,
                                  lambda value: {"moduleType": 2, "operateType": "TCP",
                                                 "params": {"id": 53, "closeOilSoc": value}}),

            ChargingPowerEntity(client, self, "inv.cfgFastChgWatt", const.AC_CHARGING_POWER, 200, 2000,
                                lambda value: {"moduleType": 0, "operateType": "TCP",
                                               "params": {"slowChgPower": value, "id": 69}}),

        ]

    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        return [
            BeeperEntity(client, self, "pd.beepState", const.BEEPER,
                         lambda value: {"moduleType": 5, "operateType": "TCP", "params": {"id": 38, "enabled": value}}),

            EnabledEntity(client, self, "pd.dcOutState", const.USB_ENABLED,
                          lambda value: {"moduleType": 0, "operateType": "TCP", "params": {"enabled": value, "id": 34  }}),

            EnabledEntity(client, self, "pd.acAutoOnCfg", const.AC_ALWAYS_ENABLED,
                          lambda value: {"moduleType": 1, "operateType": "acAutoOn", "params": {"cfg": value}}),

            EnabledEntity(client, self, "pd.pvChgPrioSet", const.PV_PRIO,
                          lambda value: {"moduleType": 1, "operateType": "pvChangePrio", "params": {"pvChangeSet": value}}),

            EnabledEntity(client, self, "inv.cfgAcEnabled", const.AC_ENABLED,
                          lambda value: {"moduleType": 0, "operateType": "TCP", "params": {"enabled": value, "id": 66  }}),

            EnabledEntity(client, self, "inv.cfgAcXboost", const.XBOOST_ENABLED,
                          lambda value: {"moduleType": 5, "operateType": "TCP", "params": {"id": 66, "xboost": value}}),

            EnabledEntity(client, self, "mppt.carState", const.DC_ENABLED,
                          lambda value: {"moduleType": 0, "operateType": "TCP", "params": {"enabled": value, "id": 81  }}),

        ]

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return [
            #DictSelectEntity(client, self, "mppt.cfgDcChgCurrent", const.DC_CHARGE_CURRENT, const.DC_CHARGE_CURRENT_OPTIONS,
            #                 lambda value: {"moduleType": 5, "operateType": "dcChgCfg",
            #                                "params": {"dcChgCfg": value}}),

            #TimeoutDictSelectEntity(client, self, "pd.lcdOffSec", const.SCREEN_TIMEOUT, const.SCREEN_TIMEOUT_OPTIONS,
            #                        lambda value: {"moduleType": 1, "operateType": "lcdCfg",
            #                                       "params": {"brighLevel": 255, "delayOff": value}}),

            #TimeoutDictSelectEntity(client, self, "inv.cfgStandbyMin", const.UNIT_TIMEOUT, const.UNIT_TIMEOUT_OPTIONS,
            #                        lambda value: {"moduleType": 1, "operateType": "standbyTime",
            #                                       "params": {"standbyMin": value}}),

            #TimeoutDictSelectEntity(client, self, "mppt.acStandbyMins", const.AC_TIMEOUT, const.AC_TIMEOUT_OPTIONS,
            #                        lambda value: {"moduleType": 5, "operateType": "standbyTime",
            #                                       "params": {"standbyMins": value}}),

            #TimeoutDictSelectEntity(client, self, "mppt.carStandbyMin", const.DC_TIMEOUT, const.DC_TIMEOUT_OPTIONS,
            #                        lambda value: {"moduleType": 5, "operateType": "carStandby",
            #                                       "params": {"standbyMins": value}})

        ]
