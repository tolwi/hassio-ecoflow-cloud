import logging

from homeassistant.util import utcnow

from custom_components.ecoflow_cloud.devices import BaseDevice
from custom_components.ecoflow_cloud.entities import (
    BaseSensorEntity, BaseNumberEntity, BaseSelectEntity, BaseSwitchEntity
)
from custom_components.ecoflow_cloud.sensor import (
    AmpSensorEntity, CentivoltSensorEntity, DeciampSensorEntity,
    DecicelsiusSensorEntity, DecihertzSensorEntity, DeciwattsSensorEntity,
    DecivoltSensorEntity, InWattsSolarSensorEntity, LevelSensorEntity,
    MiscSensorEntity, RemainSensorEntity, StatusSensorEntity,
)
from ...api import EcoflowApiClient

# from ..number import MinBatteryLevelEntity, MaxBatteryLevelEntity
# from ..select import DictSelectEntity
_LOGGER = logging.getLogger(__name__)

class PowerStream(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [
            InWattsSolarSensorEntity(client, "20_1.pv1InputWatts", "Solar 1 Watts"),
            DecivoltSensorEntity(client, "20_1.pv1InputVolt", "Solar 1 Input Potential"),
            CentivoltSensorEntity(client, "20_1.pv1OpVolt", "Solar 1 Op Potential"),
            DeciampSensorEntity(client, "20_1.pv1InputCur", "Solar 1 Currrent"),
            DecicelsiusSensorEntity(client, "20_1.pv1Temp", "Solar 1 Temperature"),
            MiscSensorEntity(client, "20_1.pv1RelayStatus", "Solar 1 Relay Status"),
            MiscSensorEntity(client, "20_1.pv1ErrCode", "Solar 1 Error Code", False),
            MiscSensorEntity(client, "20_1.pv1WarnCode", "Solar 1 Warning Code", False),
            MiscSensorEntity(client, "20_1.pv1Statue", "Solar 1 Status", False),

            InWattsSolarSensorEntity(client, "20_1.pv2InputWatts", "Solar 2 Watts"),
            DecivoltSensorEntity(client, "20_1.pv2InputVolt", "Solar 2 Input Potential"),
            CentivoltSensorEntity(client, "20_1.pv2OpVolt", "Solar 2 Op Potential"),
            DeciampSensorEntity(client, "20_1.pv2InputCur", "Solar 2 Current"),
            DecicelsiusSensorEntity(client, "20_1.pv2Temp", "Solar 2 Temperature"),
            MiscSensorEntity(client, "20_1.pv2RelayStatus", "Solar 2 Relay Status"),
            MiscSensorEntity(client, "20_1.pv2ErrCode", "Solar 2 Error Code", False),
            MiscSensorEntity(client, "20_1.pv2WarningCode", "Solar 2 Warning Code", False),
            MiscSensorEntity(client, "20_1.pv2Statue", "Solar 2 Status", False),

            MiscSensorEntity(client, "20_1.bpType", "Battery Type", False),
            LevelSensorEntity(client, "20_1.batSoc", "Battery Charge"),
            DeciwattsSensorEntity(client, "20_1.batInputWatts", "Battery Input Watts"),
            DecivoltSensorEntity(client, "20_1.batInputVolt", "Battery Input Potential"),
            DecivoltSensorEntity(client, "20_1.batOpVolt", "Battery Op Potential"),
            AmpSensorEntity(client, "20_1.batInputCur", "Battery Input Current"),
            DecicelsiusSensorEntity(client, "20_1.batTemp", "Battery Temperature"),
            RemainSensorEntity(client, "20_1.chgRemainTime", "Charge Time"),
            RemainSensorEntity(client, "20_1.dsgRemainTime", "Discharge Time"),
            MiscSensorEntity(client, "20_1.batErrCode", "Battery Error Code", False),
            MiscSensorEntity(client, "20_1.batWarningCode", "Battery Warning Code", False),
            MiscSensorEntity(client, "20_1.batStatue", "Battery Status", False),

            DecivoltSensorEntity(client, "20_1.llcInputVolt", "LLC Input Potential", False),
            DecivoltSensorEntity(client, "20_1.llcOpVolt", "LLC Op Potential", False),
            DecicelsiusSensorEntity(client, "20_1.llcTemp", "LLC Temperature"),
            MiscSensorEntity(client, "20_1.llcErrCode", "LLC Error Code", False),
            MiscSensorEntity(client, "20_1.llcWarningCode", "LLC Warning Code", False),
            MiscSensorEntity(client, "20_1.llcStatue", "LLC Status", False),

            MiscSensorEntity(client, "20_1.invOnOff", "Inverter On/Off Status"),
            DeciwattsSensorEntity(client, "20_1.invOutputWatts", "Inverter Output Watts"),
            DecivoltSensorEntity(client, "20_1.invInputVolt", "Inverter Output Potential", False),
            DecivoltSensorEntity(client, "20_1.invOpVolt", "Inverter Op Potential"),
            AmpSensorEntity(client, "20_1.invOutputCur", "Inverter Output Current"),
            #  AmpSensorEntity(client, "inv_dc_cur", "Inverter DC Current"),
            DecihertzSensorEntity(client, "20_1.invFreq", "Inverter Frequency"),
            DecicelsiusSensorEntity(client, "20_1.invTemp", "Inverter Temperature"),
            MiscSensorEntity(client, "20_1.invRelayStatus", "Inverter Relay Status"),
            MiscSensorEntity(client, "20_1.invErrCode", "Inverter Error Code", False),
            MiscSensorEntity(client, "20_1.invWarnCode", "Inverter Warning Code", False),
            MiscSensorEntity(client, "20_1.invStatue", "Inverter Status", False),

            DeciwattsSensorEntity(client, "20_1.permanentWatts", "Other Loads"),
            DeciwattsSensorEntity(client, "20_1.dynamicWatts", "Smart Plug Loads"),
            DeciwattsSensorEntity(client, "20_1.ratedPower", "Rated Power"),

            MiscSensorEntity(client, "20_1.lowerLimit", "Lower Battery Limit", False),
            MiscSensorEntity(client, "20_1.upperLimit", "Upper Battery Limit", False),
            MiscSensorEntity(client, "20_1.wirelessErrCode", "Wireless Error Code", False),
            MiscSensorEntity(client, "20_1.wirelessWarnCode", "Wireless Warning Code", False),
            MiscSensorEntity(client, "20_1.invBrightness", "LED Brightness", False),
            MiscSensorEntity(client, "20_1.heartbeatFrequency", "Heartbeat Frequency", False),

            StatusSensorEntity(client)
        ]


    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return [
            # These will likely be some form of serialised data rather than JSON will look into it later
            # MinBatteryLevelEntity(client, "lowerLimit", "Min Disharge Level", 50, 100,
            #                       lambda value: {"moduleType": 0, "operateType": "TCP",
            #                                      "params": {"id": 00, "lowerLimit": value}}),
            # MaxBatteryLevelEntity(client, "upperLimit", "Max Charge Level", 0, 30,
            #                       lambda value: {"moduleType": 0, "operateType": "TCP",
            #                                      "params": {"id": 00, "upperLimit": value}}),
        ]

    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        return []

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return [
            # DictSelectEntity(client, "supplyPriority", "Power supply mode", {"Prioritize power supply", "Prioritize power storage"},
            #         lambda value: {"moduleType": 00, "operateType": "supplyPriority",
            #                     "params": {"supplyPriority": value}}),
        ]
