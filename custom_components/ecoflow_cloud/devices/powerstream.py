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
            SolarWattsSensorEntity(client, "pv1_input_watts", "Solar 1 Watts"),
            VoltSensorEntity(client, "pv1_input_volt", "Solar 1 Input Volts", False),
            VoltSensorEntity(client, "pv1_op_volt", "Solar 1 Op Volts", False),
            AmpSensorEntity(client, "pv1_input_cur", "Solar 1 Amps", False),
            TempSensorEntity(client, "pv1_temp", "Solar 1 Tempurature"),
            # pv1RelayStatus

            SolarWattsSensorEntity(client, "pv2_input_watts", "Solar 2 Watts"),
            VoltSensorEntity(client, "pv2_input_volt", "Solar 2 Input Volts", False),
            VoltSensorEntity(client, "pv2_op_volt", "Solar 2 Op Volts", False),
            AmpSensorEntity(client, "pv2_input_cur", "Solar 2 Current", False),
            TempSensorEntity(client, "pv2_temp", "Solar 2 Tempurature"),
            # pv2RelayStatus

            LevelSensorEntity(client, "bat_soc", "Battery Charge"),
            InWattsSensorEntity(client, "bat_input_watts", "Battery Input Watts"),
            VoltSensorEntity(client, "bat_input_volt", "Battery Input Volts", False),
            VoltSensorEntity(client, "bat_op_volt", "Battery Op Volts", False),
            AmpSensorEntity(client, "bat_input_cur", "Battery Input Current", False),
            TempSensorEntity(client, "bat_temp", "Battery Tempurature"),

            VoltSensorEntity(client, "llc_input_volt", "AC Input Volts", False),
            VoltSensorEntity(client, "llc_op_volt", "AC Op Volts", False),

            # invOnOff
            OutWattsSensorEntity(client, "inv_output_watts", "Inverter Output Watts"),
            VoltSensorEntity(client, "inv_input_volt", "Inverter Output Volts", False),
            VoltSensorEntity(client, "inv_op_volt", "Inverter Op Volts", False),
            AmpSensorEntity(client, "inv_output_cur", "Inverter Output Current", False),
            AmpSensorEntity(client, "inv_dc_cur", "Inverter DC Current", False),
            FrequencySensorEntity(client, "inv_freq", "Inverter DC Current", False),
            TempSensorEntity(client, "inv_temp", "Inverter Tempurature"),
            # invRelayStatus

            WattsSensorEntity(client, "permanent_watts", "Other Loads"),
            WattsSensorEntity(client, "dynamic_watts", "Smart Plug Loads"),
            WattsSensorEntity(client, "rated_power", "Rated Power"),

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