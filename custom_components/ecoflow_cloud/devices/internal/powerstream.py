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
    MiscSensorEntity, RemainSensorEntity, StatusSensorEntity, ReconnectStatusSensorEntity,
)
from ...api import EcoflowApiClient

# from ..number import MinBatteryLevelEntity, MaxBatteryLevelEntity
# from ..select import DictSelectEntity
_LOGGER = logging.getLogger(__name__)

class PowerStream(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [
            InWattsSolarSensorEntity(client, self,  "pv1_input_watts", "Solar 1 Watts"),
            DecivoltSensorEntity(client, self,  "pv1_input_volt", "Solar 1 Input Potential"),
            CentivoltSensorEntity(client, self,  "pv1_op_volt", "Solar 1 Op Potential"),
            DeciampSensorEntity(client, self,  "pv1_input_cur", "Solar 1 Currrent"),
            DecicelsiusSensorEntity(client, self,  "pv1_temp", "Solar 1 Temperature"),
            MiscSensorEntity(client, self,  "pv1_relay_status", "Solar 1 Relay Status"),
            MiscSensorEntity(client, self,  "pv1_error_code", "Solar 1 Error Code", False),
            MiscSensorEntity(client, self,  "pv1_warning_code", "Solar 1 Warning Code", False),
            MiscSensorEntity(client, self,  "pv1_status", "Solar 1 Status", False),

            InWattsSolarSensorEntity(client, self,  "pv2_input_watts", "Solar 2 Watts"),
            DecivoltSensorEntity(client, self,  "pv2_input_volt", "Solar 2 Input Potential"),
            CentivoltSensorEntity(client, self,  "pv2_op_volt", "Solar 2 Op Potential"),
            DeciampSensorEntity(client, self,  "pv2_input_cur", "Solar 2 Current"),
            DecicelsiusSensorEntity(client, self,  "pv2_temp", "Solar 2 Temperature"),
            MiscSensorEntity(client, self,  "pv2_relay_status", "Solar 2 Relay Status"),
            MiscSensorEntity(client, self,  "pv2_error_code", "Solar 2 Error Code", False),
            MiscSensorEntity(client, self,  "pv2_warning_code", "Solar 2 Warning Code", False),
            MiscSensorEntity(client, self,  "pv2_status", "Solar 2 Status", False),

            MiscSensorEntity(client, self,  "bp_type", "Battery Type", False),
            LevelSensorEntity(client, self,  "bat_soc", "Battery Charge"),
            DeciwattsSensorEntity(client, self,  "bat_input_watts", "Battery Input Watts"),
            DecivoltSensorEntity(client, self,  "bat_input_volt", "Battery Input Potential"),
            DecivoltSensorEntity(client, self,  "bat_op_volt", "Battery Op Potential"),
            AmpSensorEntity(client, self,  "bat_input_cur", "Battery Input Current"),
            DecicelsiusSensorEntity(client, self,  "bat_temp", "Battery Temperature"),
            RemainSensorEntity(client, self,  "battery_charge_remain", "Charge Time"),
            RemainSensorEntity(client, self,  "battery_discharge_remain", "Discharge Time"),
            MiscSensorEntity(client, self,  "bat_error_code", "Battery Error Code", False),
            MiscSensorEntity(client, self,  "bat_warning_code", "Battery Warning Code", False),
            MiscSensorEntity(client, self,  "bat_status", "Battery Status", False),

            DecivoltSensorEntity(client, self,  "llc_input_volt", "LLC Input Potential", False),
            DecivoltSensorEntity(client, self,  "llc_op_volt", "LLC Op Potential", False),
            MiscSensorEntity(client, self,  "llc_error_code", "LLC Error Code", False),
            MiscSensorEntity(client, self,  "llc_warning_code", "LLC Warning Code", False),
            MiscSensorEntity(client, self,  "llc_status", "LLC Status", False),

            MiscSensorEntity(client, self,  "inv_on_off", "Inverter On/Off Status"),
            DeciwattsSensorEntity(client, self,  "inv_output_watts", "Inverter Output Watts"),
            DecivoltSensorEntity(client, self,  "inv_input_volt", "Inverter Output Potential", False),
            DecivoltSensorEntity(client, self,  "inv_op_volt", "Inverter Op Potential"),
            AmpSensorEntity(client, self,  "inv_output_cur", "Inverter Output Current"),
            AmpSensorEntity(client, self,  "inv_dc_cur", "Inverter DC Current"),
            DecihertzSensorEntity(client, self,  "inv_freq", "Inverter Frequency"),
            DecicelsiusSensorEntity(client, self,  "inv_temp", "Inverter Temperature"),
            MiscSensorEntity(client, self,  "inv_relay_status", "Inverter Relay Status"),
            MiscSensorEntity(client, self,  "inv_error_code", "Inverter Error Code", False),
            MiscSensorEntity(client, self,  "inv_warning_code", "Inverter Warning Code", False),
            MiscSensorEntity(client, self,  "inv_status", "Inverter Status", False),

            DeciwattsSensorEntity(client, self,  "permanent_watts", "Other Loads"),
            DeciwattsSensorEntity(client, self,  "dynamic_watts", "Smart Plug Loads"),
            DeciwattsSensorEntity(client, self,  "rated_power", "Rated Power"),

            MiscSensorEntity(client, self,  "lower_limit", "Lower Battery Limit", False),
            MiscSensorEntity(client, self,  "upper_limit", "Upper Battery Limit", False),
            MiscSensorEntity(client, self,  "wireless_error_code", "Wireless Error Code", False),
            MiscSensorEntity(client, self,  "wireless_warning_code", "Wireless Warning Code", False),
            MiscSensorEntity(client, self,  "inv_brightness", "LED Brightness", False),
            MiscSensorEntity(client, self,  "heartbeat_frequency", "Heartbeat Frequency", False),

            ReconnectStatusSensorEntity(client, self)
        ]


    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return [
            # These will likely be some form of serialised data rather than JSON will look into it later
            # MinBatteryLevelEntity(client, self,  "lowerLimit", "Min Discharge Level", 50, 100,
            #                       lambda value: {"moduleType": 0, "operateType": "TCP",
            #                                      "params": {"id": 00, "lowerLimit": value}}),
            # MaxBatteryLevelEntity(client, self,  "upperLimit", "Max Charge Level", 0, 30,
            #                       lambda value: {"moduleType": 0, "operateType": "TCP",
            #                                      "params": {"id": 00, "upperLimit": value}}),
        ]

    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        return []

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return [
            # DictSelectEntity(client, self,  "supplyPriority", "Power supply mode", {"Prioritize power supply", "Prioritize power storage"},
            #         lambda value: {"moduleType": 00, "operateType": "supplyPriority",
            #                     "params": {"supplyPriority": value}}),
        ]

    def _prepare_data(self, raw_data) -> dict[str, any]:
        raw = {"params": {}}
        from .proto import ecopacket_pb2 as ecopacket, powerstream_pb2 as powerstream
        try:
            payload =raw_data

            while True:
                packet = ecopacket.SendHeaderMsg()
                packet.ParseFromString(payload)

                _LOGGER.debug("cmd id %u payload \"%s\"", packet.msg.cmd_id, payload.hex())

                if packet.msg.cmd_id != 1:
                    _LOGGER.info("Unsupported EcoPacket cmd id %u", packet.msg.cmd_id)

                else:
                    heartbeat = powerstream.InverterHeartbeat()
                    heartbeat.ParseFromString(packet.msg.pdata)

                    for descriptor in heartbeat.DESCRIPTOR.fields:
                        if not heartbeat.HasField(descriptor.name):
                            continue

                        raw["params"][descriptor.name] = getattr(heartbeat, descriptor.name)

                    _LOGGER.info("Found %u fields", len(raw["params"]))

                    raw["timestamp"] = utcnow()

                if packet.ByteSize() >= len(payload):
                    break

                _LOGGER.info("Found another frame in payload")

                packet_length = len(payload) - packet.ByteSize()
                payload = payload[:packet_length]

        except Exception as error:
            _LOGGER.error(error)
            _LOGGER.info(raw_data.hex())

        return raw

