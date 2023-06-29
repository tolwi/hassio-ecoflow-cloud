from . import BaseDevice
from .. import EcoflowMQTTClient
from ..entities import BaseSensorEntity, BaseNumberEntity, BaseSelectEntity, BaseSwitchEntity
from ..sensor import LevelSensorEntity, AmpSensorEntity, TempSensorEntity, \
    InWattsSensorEntity, OutWattsSensorEntity, VoltSensorEntity, \
    WattsSensorEntity, FrequencySensorEntity, SolarWattsSensorEntity
# from ..number import MinBatteryLevelEntity, MaxBatteryLevelEntity
# from ..select import DictSelectEntity

class PowerStream(BaseDevice):
    def sensors(self, client: EcoflowMQTTClient) -> list[BaseSensorEntity]:
        return [
            SolarWattsSensorEntity(client, "pv1InputWatts", "Solar 1 Watts"),
            VoltSensorEntity(client, "pv1InputVolt", "Solar 1 Input Volts", False),
            VoltSensorEntity(client, "pv1OpVolt", "Solar 1 Op Volts", False),
            AmpSensorEntity(client, "pv1InputCur", "Solar 1 Amps", False),
            TempSensorEntity(client, "pv1Temp", "Solar 1 Tempurature"),
            # pv1RelayStatus

            SolarWattsSensorEntity(client, "pv2InputWatts", "Solar 2 Watts"),
            VoltSensorEntity(client, "pv2OnputVolt", "Solar 2 Input Volts", False),
            VoltSensorEntity(client, "pv2OpVolt", "Solar 2 Op Volts", False),
            AmpSensorEntity(client, "pv2InputCur", "Solar 2 Current", False),
            TempSensorEntity(client, "pv2Temp", "Solar 2 Tempurature"),
            # pv2RelayStatus

            LevelSensorEntity(client, "batSoc", "Battery Charge"),
            InWattsSensorEntity(client, "batInputWatts", "Battery Input Watts"),
            VoltSensorEntity(client, "batInputVolt", "Battery Input Volts", False),
            VoltSensorEntity(client, "batOpVolt", "Battery Op Volts", False),
            AmpSensorEntity(client, "batInputCur", "Battery Input Current", False),
            TempSensorEntity(client, "batTemp", "Battery Tempurature"),

            VoltSensorEntity(client, "llcInputVolt", "AC Input Volts", False),
            VoltSensorEntity(client, "llcOpVolt", "AC Op Volts", False),

            # invOnOff
            OutWattsSensorEntity(client, "invOutputWatts", "Inverter Output Watts"),
            VoltSensorEntity(client, "invInputVolt", "Inverter Output Volts", False),
            VoltSensorEntity(client, "invOpVolt", "Inverter Op Volts", False),
            AmpSensorEntity(client, "invOutputCur", "Inverter Output Current", False),
            AmpSensorEntity(client, "invDcCur", "Inverter DC Current", False),
            FrequencySensorEntity(client, "invFreq", "Inverter DC Current", False),
            TempSensorEntity(client, "invTemp", "Inverter Tempurature"),
            # invRelayStatus

            WattsSensorEntity(client, "permanentWatts", "Other Loads"),
            WattsSensorEntity(client, "dynamicWatts", "Smart Plug Loads"),
            WattsSensorEntity(client, "ratedPower", "Rated Power"),

            # Unsure what this will be, assuming it will be an identifier for River/Delta devices
            # xxx(client, "bpType", "Battery Power Type"),
        ]


    def numbers(self, client: EcoflowMQTTClient) -> list[BaseNumberEntity]:
        return [
            # These will likely be some form of serialised data rather than JSON will look into it later
            # MinBatteryLevelEntity(client, "lowerLimit", "Min Disharge Level", 50, 100,
            #                       lambda value: {"moduleType": 0, "operateType": "TCP",
            #                                      "params": {"id": 00, "lowerLimit": value}}),
            # MaxBatteryLevelEntity(client, "upperLimit", "Max Charge Level", 0, 30,
            #                       lambda value: {"moduleType": 0, "operateType": "TCP",
            #                                      "params": {"id": 00, "upperLimit": value}}),
        ]

    def switches(self, client: EcoflowMQTTClient) -> list[BaseSwitchEntity]:
        return []

    def selects(self, client: EcoflowMQTTClient) -> list[BaseSelectEntity]:
        return [
            # DictSelectEntity(client, "supplyPriority", "Power supply mode", {"Prioritize power supply", "Prioritize power storage"},
            #         lambda value: {"moduleType": 00, "operateType": "supplyPriority",
            #                     "params": {"supplyPriority": value}}),
        ]