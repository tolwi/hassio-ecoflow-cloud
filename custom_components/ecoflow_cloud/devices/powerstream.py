from . import BaseDevice
from .. import EcoflowMQTTClient
from ..entities import BaseSensorEntity, BaseNumberEntity, BaseSelectEntity, BaseSwitchEntity
from ..sensor import LevelSensorEntity, DecihertzSensorEntity, \
    InWattsSolarSensorEntity, RemainSensorEntity, InVoltSensorEntity, \
    DeciwattsSensorEntity, DecicelsiusSensorEntity, AmpSensorEntity, VoltSensorEntity
# from ..number import MinBatteryLevelEntity, MaxBatteryLevelEntity
# from ..select import DictSelectEntity

class PowerStream(BaseDevice):
    def sensors(self, client: EcoflowMQTTClient) -> list[BaseSensorEntity]:
        return [
            InWattsSolarSensorEntity(client, "pv1_input_watts", "Solar 1 Watts"),
            InVoltSensorEntity(client, "pv1_input_volt", "Solar 1 Input Volts"),
            VoltSensorEntity(client, "pv1_op_volt", "Solar 1 Op Volts"),
            AmpSensorEntity(client, "pv1_input_cur", "Solar 1 Amps"),
            DecicelsiusSensorEntity(client, "pv1_temp", "Solar 1 Tempurature"),
            # pv1RelayStatus

            InWattsSolarSensorEntity(client, "pv2_input_watts", "Solar 2 Watts"),
            InVoltSensorEntity(client, "pv2_input_volt", "Solar 2 Input Volts"),
            VoltSensorEntity(client, "pv2_op_volt", "Solar 2 Op Volts"),
            AmpSensorEntity(client, "pv2_input_cur", "Solar 2 Current"),
            DecicelsiusSensorEntity(client, "pv2_temp", "Solar 2 Tempurature"),
            # pv2RelayStatus

            LevelSensorEntity(client, "bat_soc", "Battery Charge"),
            DeciwattsSensorEntity(client, "bat_input_watts", "Battery Input Watts"),
            InVoltSensorEntity(client, "bat_input_volt", "Battery Input Volts"),
            InVoltSensorEntity(client, "bat_op_volt", "Battery Op Volts"),
            AmpSensorEntity(client, "bat_input_cur", "Battery Input Current"),
            DecicelsiusSensorEntity(client, "bat_temp", "Battery Tempurature"),
            RemainSensorEntity(client, "battery_remain", "Battery Remains"),

            InVoltSensorEntity(client, "llc_input_volt", "AC Input Volts"),
            VoltSensorEntity(client, "llc_op_volt", "AC Op Volts"),

            # invOnOff
            DeciwattsSensorEntity(client, "inv_output_watts", "Inverter Output Watts"),
            InVoltSensorEntity(client, "inv_input_volt", "Inverter Output Volts"),
            VoltSensorEntity(client, "inv_op_volt", "Inverter Op Volts"),
            AmpSensorEntity(client, "inv_output_cur", "Inverter Output Current"),
            AmpSensorEntity(client, "inv_dc_cur", "Inverter DC Current"),
            DecihertzSensorEntity(client, "inv_freq", "Inverter Frequency"),
            DecicelsiusSensorEntity(client, "inv_temp", "Inverter Tempurature"),
            # invRelayStatus

            DeciwattsSensorEntity(client, "permanent_watts", "Other Loads"),
            DeciwattsSensorEntity(client, "dynamic_watts", "Smart Plug Loads"),
            DeciwattsSensorEntity(client, "rated_power", "Rated Power"),

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
