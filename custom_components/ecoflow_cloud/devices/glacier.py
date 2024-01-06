from homeassistant.const import Platform

from . import const, BaseDevice, EntityMigration, MigrationAction
from .const import ATTR_DESIGN_CAPACITY, ATTR_FULL_CAPACITY, ATTR_REMAIN_CAPACITY, BATTERY_CHARGING_STATE
from ..entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, BaseSelectEntity, BaseButtonEntity
from ..mqtt.ecoflow_mqtt import EcoflowMQTTClient
from ..number import ChargingPowerEntity, MaxBatteryLevelEntity, MinBatteryLevelEntity, SetTempEntity
from ..select import DictSelectEntity, TimeoutDictSelectEntity
from ..sensor import LevelSensorEntity, RemainSensorEntity, SecondsRemainSensorEntity, TempSensorEntity, \
    CyclesSensorEntity, InWattsSensorEntity, OutWattsSensorEntity, VoltSensorEntity, QuotasStatusSensorEntity, \
    MilliVoltSensorEntity, InMilliVoltSensorEntity, OutMilliVoltSensorEntity, ChargingStateSensorEntity, \
    FanSensorEntity, MiscBinarySensorEntity, DecicelsiusSensorEntity, MiscSensorEntity, PowerBinarySensorEntity
from ..switch import EnabledEntity, InvertedBeeperEntity
from ..button import EnabledButtonEntity


class Glacier(BaseDevice):
    def charging_power_step(self) -> int:
        return 50

    def sensors(self, client: EcoflowMQTTClient) -> list[BaseSensorEntity]:
        return [
            # Power and Battery Entities
            LevelSensorEntity(client, "bms_bmsStatus.soc", const.MAIN_BATTERY_LEVEL)
                .attr("bms_bmsStatus.designCap", ATTR_DESIGN_CAPACITY, 0)
                .attr("bms_bmsStatus.fullCap", ATTR_FULL_CAPACITY, 0)
                .attr("bms_bmsStatus.remainCap", ATTR_REMAIN_CAPACITY, 0),

            LevelSensorEntity(client, "bms_emsStatus.f32LcdSoc", const.COMBINED_BATTERY_LEVEL),

            ChargingStateSensorEntity(client, "bms_emsStatus.chgState", BATTERY_CHARGING_STATE),

            InWattsSensorEntity(client, "bms_bmsStatus.inWatts", const.TOTAL_IN_POWER),
            OutWattsSensorEntity(client, "bms_bmsStatus.outWatts", const.TOTAL_OUT_POWER),

            OutWattsSensorEntity(client, "pd.motorWat", "Motor Power"),

            RemainSensorEntity(client, "bms_emsStatus.chgRemain", const.CHARGE_REMAINING_TIME),
            RemainSensorEntity(client, "bms_emsStatus.dsgRemain", const.DISCHARGE_REMAINING_TIME),

            CyclesSensorEntity(client, "bms_bmsStatus.cycles", const.CYCLES),

            TempSensorEntity(client, "bms_bmsStatus.tmp", const.BATTERY_TEMP),
            TempSensorEntity(client, "bms_bmsStatus.minCellTmp", const.MIN_CELL_TEMP, False),
            TempSensorEntity(client, "bms_bmsStatus.maxCellTmp", const.MAX_CELL_TEMP, False),

            VoltSensorEntity(client, "bms_bmsStatus.vol", const.BATTERY_VOLT, False),
            MilliVoltSensorEntity(client, "bms_bmsStatus.minCellVol", const.MIN_CELL_VOLT, False),
            MilliVoltSensorEntity(client, "bms_bmsStatus.maxCellVol", const.MAX_CELL_VOLT, False),

            MiscBinarySensorEntity(client,"pd.batFlag","Battery Present"),

            MiscSensorEntity(client, "pd.xt60InState", "XT60 State"),  

            #Fridge Entities
            FanSensorEntity(client, "bms_emsStatus.fanLvl", "Fan Level"),

            DecicelsiusSensorEntity(client, "pd.ambientTmp", "Ambient Temperature"),
            DecicelsiusSensorEntity(client, "pd.exhaustTmp", "Exhaust Temperature"),
            DecicelsiusSensorEntity(client, "pd.tempWater", "Water Temperature"),
            DecicelsiusSensorEntity(client, "pd.tmpL", "Left Temperature"),            
            DecicelsiusSensorEntity(client, "pd.tmpR", "Right Temperature"),            

            MiscBinarySensorEntity(client,"pd.flagTwoZone","Dual Zone Mode"),

            SecondsRemainSensorEntity(client, "pd.iceTm", "Ice Time Remain"),
            LevelSensorEntity(client, "pd.icePercent", "Ice Percentage"),

            MiscSensorEntity(client, "pd.iceMkMode", "Ice Make Mode"),  

            MiscBinarySensorEntity(client,"pd.iceAlert","Ice Alert"),          
            MiscBinarySensorEntity(client,"pd.waterLine","Ice Water Level OK"),   

            QuotasStatusSensorEntity(client)      

        ]

    def numbers(self, client: EcoflowMQTTClient) -> list[BaseNumberEntity]:
        return [
            SetTempEntity(client,"pd.tmpLSet", "Left Set Temperature",-25, 10,
                                  lambda value, params: {"moduleType": 1, "operateType": "temp",
                                                 "params": {"tmpM": int(params.get("pd.tmpMSet", 0)),
                                                            "tmpL": int(value),
                                                            "tmpR": int(params.get("pd.tmpRSet", 0))}}),
            
            SetTempEntity(client,"pd.tmpMSet", "Combined Set Temperature",-25, 10,
                                  lambda value, params: {"moduleType": 1, "operateType": "temp",
                                                 "params": {"tmpM": int(value),
                                                            "tmpL": int(params.get("pd.tmpLSet", 0)),
                                                            "tmpR": int(params.get("pd.tmpRSet", 0))}}),

            SetTempEntity(client,"pd.tmpRSet", "Right Set Temperature",-25, 10,
                                  lambda value, params: {"moduleType": 1, "operateType": "temp",
                                                 "params": {"tmpM": int(params.get("pd.tmpMSet", 0)),
                                                            "tmpL": int(params.get("pd.tmpLSet", 0)),
                                                            "tmpR": int(value)}}),                                                                                                                        

        ]

    def switches(self, client: EcoflowMQTTClient) -> list[BaseSwitchEntity]:
        return [
            InvertedBeeperEntity(client, "pd.beepEn", const.BEEPER,
                         lambda value: {"moduleType": 1, "operateType": "beepEn", "params": {"flag": value}}),

            EnabledEntity(client, "pd.coolMode", "Eco Mode",
                          lambda value: {"moduleType": 1, "operateType": "ecoMode", "params": {"mode": value}}),                         

            #power parameter is inverted for some reason
            EnabledEntity(client, "pd.pwrState", "Power",
                          lambda value: {"moduleType": 1, "operateType": "powerOff", "params": {"enable": value}}),                         

        ]
    
    def buttons(self, client: EcoflowMQTTClient) -> list[BaseButtonEntity]:
        return [
            EnabledButtonEntity(client, "smlice", "Make Small Ice", lambda value: {"moduleType": 1, "operateType": "iceMake", "params": {"enable": 1, "iceShape": 0}}),
            EnabledButtonEntity(client, "lrgice", "Make Large Ice", lambda value: {"moduleType": 1, "operateType": "iceMake", "params": {"enable": 1, "iceShape": 1}}),
            EnabledButtonEntity(client, "deice", "Detach Ice", lambda value: {"moduleType": 1, "operateType": "deIce", "params": {"enable": 1}})

        ]    
        

    def selects(self, client: EcoflowMQTTClient) -> list[BaseSelectEntity]:
        return [

        ]

    def migrate(self, version) -> list[EntityMigration]:
        if version == 2:
            return [
                EntityMigration("pd.soc", Platform.SENSOR, MigrationAction.REMOVE),
            ]
        return []
