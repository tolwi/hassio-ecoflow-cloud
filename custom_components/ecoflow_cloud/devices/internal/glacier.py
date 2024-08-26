from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.button import EnabledButtonEntity
from custom_components.ecoflow_cloud.devices import const, BaseDevice
from custom_components.ecoflow_cloud.entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, \
    BaseSelectEntity, BaseButtonEntity
from custom_components.ecoflow_cloud.number import SetTempEntity
from custom_components.ecoflow_cloud.sensor import LevelSensorEntity, RemainSensorEntity, SecondsRemainSensorEntity, \
    TempSensorEntity, \
    CyclesSensorEntity, InWattsSensorEntity, OutWattsSensorEntity, VoltSensorEntity, MilliVoltSensorEntity, \
    ChargingStateSensorEntity, \
    FanSensorEntity, MiscBinarySensorEntity, DecicelsiusSensorEntity, MiscSensorEntity, CapacitySensorEntity, \
    QuotaStatusSensorEntity
from custom_components.ecoflow_cloud.switch import EnabledEntity, InvertedBeeperEntity


class Glacier(BaseDevice):

    @staticmethod
    def default_charging_power_step() -> int:
        return 50

    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [
            # Power and Battery Entities
            LevelSensorEntity(client, self, "bms_bmsStatus.soc", const.MAIN_BATTERY_LEVEL)
                .attr("bms_bmsStatus.designCap", const.ATTR_DESIGN_CAPACITY, 0)
                .attr("bms_bmsStatus.fullCap", const.ATTR_FULL_CAPACITY, 0)
                .attr("bms_bmsStatus.remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, self, "bms_bmsStatus.designCap", const.MAIN_DESIGN_CAPACITY, False),
            CapacitySensorEntity(client, self, "bms_bmsStatus.fullCap", const.MAIN_FULL_CAPACITY, False),
            CapacitySensorEntity(client, self, "bms_bmsStatus.remainCap", const.MAIN_REMAIN_CAPACITY, False),

            LevelSensorEntity(client, self, "bms_emsStatus.f32LcdSoc", const.COMBINED_BATTERY_LEVEL),

            ChargingStateSensorEntity(client, self, "bms_emsStatus.chgState", const.BATTERY_CHARGING_STATE),

            InWattsSensorEntity(client, self, "bms_bmsStatus.inWatts", const.TOTAL_IN_POWER),
            OutWattsSensorEntity(client, self, "bms_bmsStatus.outWatts", const.TOTAL_OUT_POWER),

            OutWattsSensorEntity(client, self, "pd.motorWat", "Motor Power"),

            RemainSensorEntity(client, self, "bms_emsStatus.chgRemain", const.CHARGE_REMAINING_TIME),
            RemainSensorEntity(client, self, "bms_emsStatus.dsgRemain", const.DISCHARGE_REMAINING_TIME),

            CyclesSensorEntity(client, self, "bms_bmsStatus.cycles", const.CYCLES),

            TempSensorEntity(client, self, "bms_bmsStatus.tmp", const.BATTERY_TEMP)
                .attr("bms_bmsStatus.minCellTemp", const.ATTR_MIN_CELL_TEMP, 0)
                .attr("bms_bmsStatus.maxCellTemp", const.ATTR_MAX_CELL_TEMP, 0),
            TempSensorEntity(client, self, "bms_bmsStatus.minCellTmp", const.MIN_CELL_TEMP, False),
            TempSensorEntity(client, self, "bms_bmsStatus.maxCellTmp", const.MAX_CELL_TEMP, False),

            VoltSensorEntity(client, self, "bms_bmsStatus.vol", const.BATTERY_VOLT, False)
                .attr("bms_bmsStatus.minCellVol", const.ATTR_MIN_CELL_VOLT, 0)
                .attr("bms_bmsStatus.maxCellVol", const.ATTR_MAX_CELL_VOLT, 0),
            MilliVoltSensorEntity(client, self, "bms_bmsStatus.minCellVol", const.MIN_CELL_VOLT, False),
            MilliVoltSensorEntity(client, self, "bms_bmsStatus.maxCellVol", const.MAX_CELL_VOLT, False),

            MiscBinarySensorEntity(client,self,"pd.batFlag", "Battery Present"),

            MiscSensorEntity(client, self, "pd.xt60InState", "XT60 State"),  

            #Fridge Entities
            FanSensorEntity(client, self, "bms_emsStatus.fanLvl", "Fan Level"),

            DecicelsiusSensorEntity(client, self, "pd.ambientTmp", "Ambient Temperature"),
            DecicelsiusSensorEntity(client, self, "pd.exhaustTmp", "Exhaust Temperature"),
            DecicelsiusSensorEntity(client, self, "pd.tempWater", "Water Temperature"),
            DecicelsiusSensorEntity(client, self, "pd.tmpL", "Left Temperature"),            
            DecicelsiusSensorEntity(client, self, "pd.tmpR", "Right Temperature"),            

            MiscBinarySensorEntity(client, self,"pd.flagTwoZone","Dual Zone Mode"),

            SecondsRemainSensorEntity(client, self, "pd.iceTm", "Ice Time Remain"),
            LevelSensorEntity(client, self, "pd.icePercent", "Ice Percentage"),

            MiscSensorEntity(client, self, "pd.iceMkMode", "Ice Make Mode"), 

            MiscBinarySensorEntity(client, self,"pd.iceAlert","Ice Alert"),
            MiscBinarySensorEntity(client,self, "pd.waterLine","Ice Water Level OK"),

            QuotaStatusSensorEntity(client, self)

        ]

    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return [
            SetTempEntity(client, self,"pd.tmpLSet", "Left Set Temperature",-25, 10,
                                  lambda value, params: {"moduleType": 1, "operateType": "temp",
                                                 "params": {"tmpM": int(params.get("pd.tmpMSet", 0)),
                                                            "tmpL": int(value),
                                                            "tmpR": int(params.get("pd.tmpRSet", 0))}}),
            
            SetTempEntity(client, self, "pd.tmpMSet", "Combined Set Temperature",-25, 10,
                                  lambda value, params: {"moduleType": 1, "operateType": "temp",
                                                 "params": {"tmpM": int(value),
                                                            "tmpL": int(params.get("pd.tmpLSet", 0)),
                                                            "tmpR": int(params.get("pd.tmpRSet", 0))}}),

            SetTempEntity(client, self,"pd.tmpRSet", "Right Set Temperature",-25, 10,
                                  lambda value, params: {"moduleType": 1, "operateType": "temp",
                                                 "params": {"tmpM": int(params.get("pd.tmpMSet", 0)),
                                                            "tmpL": int(params.get("pd.tmpLSet", 0)),
                                                            "tmpR": int(value)}}),                                                                                                                        

        ]

    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        return [
            InvertedBeeperEntity(client, self, "pd.beepEn", const.BEEPER,
                         lambda value: {"moduleType": 1, "operateType": "beepEn", "params": {"flag": value}}),

            EnabledEntity(client, self, "pd.coolMode", "Eco Mode",
                          lambda value: {"moduleType": 1, "operateType": "ecoMode", "params": {"mode": value}}),                         

            #power parameter is inverted for some reason
            EnabledEntity(client, self, "pd.pwrState", "Power",
                          lambda value: {"moduleType": 1, "operateType": "powerOff", "params": {"enable": value}}),                         

        ]
    
    def buttons(self, client: EcoflowApiClient) -> list[BaseButtonEntity]:
        return [
            EnabledButtonEntity(client, self, "smlice", "Make Small Ice", lambda value: {"moduleType": 1, "operateType": "iceMake", "params": {"enable": 1, "iceShape": 0}}),
            EnabledButtonEntity(client, self, "lrgice", "Make Large Ice", lambda value: {"moduleType": 1, "operateType": "iceMake", "params": {"enable": 1, "iceShape": 1}}),
            EnabledButtonEntity(client, self, "deice", "Detach Ice", lambda value: {"moduleType": 1, "operateType": "deIce", "params": {"enable": 1}})

        ]    
        

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return [

        ]
