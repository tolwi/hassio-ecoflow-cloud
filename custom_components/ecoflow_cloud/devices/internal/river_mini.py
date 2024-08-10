from custom_components.ecoflow_cloud import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import const, BaseDevice
from custom_components.ecoflow_cloud.entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, BaseSelectEntity
from custom_components.ecoflow_cloud.number import MaxBatteryLevelEntity
from custom_components.ecoflow_cloud.sensor import LevelSensorEntity, WattsSensorEntity, TempSensorEntity, \
    CyclesSensorEntity, InEnergySensorEntity, InWattsSensorEntity, OutEnergySensorEntity, OutWattsSensorEntity, \
    AmpSensorEntity, InMilliVoltSensorEntity, \
    BeMilliVoltSensorEntity
from custom_components.ecoflow_cloud.switch import EnabledEntity


class RiverMini(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [
            LevelSensorEntity(client, self, "inv.soc", const.MAIN_BATTERY_LEVEL)
                    .attr("inv.maxChargeSoc", const.ATTR_DESIGN_CAPACITY, 0),

            InWattsSensorEntity(client, self, "inv.inputWatts", const.AC_IN_POWER),
            OutWattsSensorEntity(client, self, "inv.outputWatts", const.AC_OUT_POWER),
            
            BeMilliVoltSensorEntity(client, self, "inv.invInVol", const.AC_IN_VOLT),
            BeMilliVoltSensorEntity(client, self, "inv.invOutVol", const.AC_OUT_VOLT),

            InMilliVoltSensorEntity(client, self, "inv.dcInVol", const.SOLAR_IN_VOLTAGE),
            AmpSensorEntity(client, self, "inv.dcInAmp", const.SOLAR_IN_CURRENT),
            
            TempSensorEntity(client, self, "inv.inTemp", const.INV_IN_TEMP),
            TempSensorEntity(client, self, "inv.outTemp", const.INV_OUT_TEMP),
            
            InEnergySensorEntity(client, self, "pd.chgSunPower", const.SOLAR_IN_ENERGY),
            InEnergySensorEntity(client, self, "pd.chgPowerAC", const.CHARGE_AC_ENERGY),
            InEnergySensorEntity(client, self, "pd.chgPowerDC", const.CHARGE_DC_ENERGY),
            OutEnergySensorEntity(client, self, "pd.dsgPowerAC", const.DISCHARGE_AC_ENERGY),
            OutEnergySensorEntity(client, self, "pd.dsgPowerDC", const.DISCHARGE_DC_ENERGY),
            
            WattsSensorEntity(client, self, "pd.wattsInSum", const.TOTAL_IN_POWER),
            WattsSensorEntity(client, self, "pd.wattsOutSum", const.TOTAL_OUT_POWER),

            
            CyclesSensorEntity(client, self, "inv.cycles", const.CYCLES),
        ]

    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return [
            MaxBatteryLevelEntity(client, self, "inv.maxChargeSoc", const.MAX_CHARGE_LEVEL, 30, 100,
                                  lambda value: {"moduleType": 0, "operateType": "TCP",
                                                 "params": {"id": 0, "maxChgSoc": value}}),
        ]
        
    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        return [
            EnabledEntity(client, self, "inv.cfgAcEnabled", const.AC_ENABLED, lambda value: {"moduleType": 0, "operateType": "TCP", "params": {"id": 66, "enabled": value}}),
            EnabledEntity(client, self, "inv.cfgAcXboost", const.XBOOST_ENABLED, lambda value: {"moduleType": 0, "operateType": "TCP", "params": {"id": 66, "xboost": value}}),
        ]
    
    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return []