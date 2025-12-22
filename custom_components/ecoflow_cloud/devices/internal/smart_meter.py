import enum
import logging
from typing import Any, NamedTuple, cast, override

from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message as ProtoMessageRaw
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity

# from homeassistant.components.sensor import SensorEntity  # pyright: ignore[reportMissingImports]
# from homeassistant.components.switch import SwitchEntity  # pyright: ignore[reportMissingImports]
# from homeassistant.components.number import NumberEntity  # pyright: ignore[reportMissingImports]
# from homeassistant.components.select import SelectEntity  # pyright: ignore[reportMissingImports]
from homeassistant.util import dt

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.api.message import JSONDict, Message, PrivateAPIMessageProtocol
from custom_components.ecoflow_cloud.devices import BaseInternalDevice, const
from custom_components.ecoflow_cloud.devices.internal import flatten_dict
from custom_components.ecoflow_cloud.devices.internal.proto import AddressId, ef_smartmeter_pb2
from custom_components.ecoflow_cloud.sensor import (
    EnergySensorEntity,
    InAmpSensorEntity,
    MiscSensorEntity,
    QuotaStatusSensorEntity,
    StatusSensorEntity,
    VoltSensorEntity,
    WattsSensorEntity,
)


class CommandFuncAndId(NamedTuple):
    func: int
    id: int


class Command(enum.Enum):
    @enum.property
    def func(self) -> int:
        return self.value.func

    @enum.property
    def id(self) -> int:
        return self.value.id

    HEARTBEAT = CommandFuncAndId(func=20, id=1)
    DISPLAY_PROPERTY_UPLOAD = CommandFuncAndId(func=254, id=21)
    RUNTIME_PROPERTY_UPLOAD = CommandFuncAndId(func=254, id=22)


def get_expected_payload_type(cmd: Command) -> type[ProtoMessageRaw]:
    _expected_payload_types = {
        Command.DISPLAY_PROPERTY_UPLOAD: ef_smartmeter_pb2.SmartMeterDisplayPropertyUpload,
        Command.RUNTIME_PROPERTY_UPLOAD: ef_smartmeter_pb2.SmartMeterRuntimePropertyUpload,
    }
    return _expected_payload_types[cmd]


_LOGGER = logging.getLogger(__name__)


class SmartMeterCommandMessage(PrivateAPIMessageProtocol):
    """Message wrapper for SmartMeter protobuf commands."""

    def __init__(self, device_sn: str, command: Command, payload: ProtoMessageRaw | None):
        self._packet = ef_smartmeter_pb2.SmartMeterSetMessage()
        self._payload = payload
        message = self._packet.msg.add()
        message.seq = Message.gen_seq()
        message.device_sn = device_sn
        message.from_ = "HomeAssistant"

        if command == Command.HEARTBEAT:
            message.src = AddressId.APP
            message.dest = AddressId.APP
            message.data_len = 0

        else:
            message.src = AddressId.APP
            message.dest = AddressId.MQTT
            message.d_src = 1
            message.d_dest = 1
            message.check_type = 3
            message.need_ack = 1
            message.version = 19
            message.payload_ver = 1
            if payload is not None:
                pdata = payload.SerializeToString()
                message.pdata = pdata
                message.data_len = len(pdata)

        message.cmd_func = command.func
        message.cmd_id = command.id

    @override
    def to_mqtt_payload(self):
        return self._packet.SerializeToString()

    @override
    def to_dict(self) -> dict:
        if self._payload is None:
            payload_dict = {}
        else:
            payload_dict = MessageToDict(self._payload, preserving_proto_field_name=True)

        result = MessageToDict(self._packet, preserving_proto_field_name=True)
        result["msg"][0]["pdata"] = {type(self._payload).__name__: payload_dict}
        result["msg"][0].pop("seq", None)
        return {type(self._packet).__name__: result}


class SmartMeter(BaseInternalDevice):
    @override
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        timezoneEntity = MiscSensorEntity(client, self, "254_21.utcTimezone", const.UTC_TIMEZONE, False)
        timezoneEntity.attr("254_21.utcTimezoneId", const.UTC_TIMEZONE_ID, "Unknown")
        return [
            WattsSensorEntity(
                client,
                self,
                "254_21.totalPower",
                const.SMART_METER_POWER_GLOBAL,
                diagnostic=False,
            ),
            WattsSensorEntity(
                client,
                self,
                "254_21.powerL1",
                const.SMART_METER_POWER_L1,
                False,
            ),
            WattsSensorEntity(
                client,
                self,
                "254_21.powerL2",
                const.SMART_METER_POWER_L2,
                False,
            ),
            WattsSensorEntity(
                client,
                self,
                "254_21.powerL3",
                const.SMART_METER_POWER_L3,
                False,
            ),
            InAmpSensorEntity(
                client,
                self,
                "254_21.currentL1",
                const.SMART_METER_IN_AMPS_L1,
                False,
            ),
            InAmpSensorEntity(
                client,
                self,
                "254_21.currentL2",
                const.SMART_METER_IN_AMPS_L2,
                False,
            ),
            InAmpSensorEntity(
                client,
                self,
                "254_21.currentL3",
                const.SMART_METER_IN_AMPS_L3,
                False,
            ),
            VoltSensorEntity(
                client,
                self,
                "254_21.voltageL1",
                const.SMART_METER_VOLT_L1,
                False,
            ),
            VoltSensorEntity(
                client,
                self,
                "254_21.voltageL2",
                const.SMART_METER_VOLT_L2,
                False,
            ),
            VoltSensorEntity(
                client,
                self,
                "254_21.voltageL3",
                const.SMART_METER_VOLT_L3,
                False,
            ),
            # MiscBinarySensorEntity(
            #     client,
            #     self,
            #     "254_21.gridConnectionFlagL1",
            #     const.SMART_METER_FLAG_L1,
            #     False,
            # ),
            # MiscBinarySensorEntity(
            #     client,
            #     self,
            #     "254_21.gridConnectionFlagL2",
            #     const.SMART_METER_FLAG_L2,
            #     False,
            # ),
            # MiscBinarySensorEntity(
            #     client,
            #     self,
            #     "254_21.gridConnectionFlagL3",
            #     const.SMART_METER_FLAG_L3,
            #     False,
            # ),
            EnergySensorEntity(
                client,
                self,
                "254_21.energy.energyL1daily",
                const.SMART_METER_RECORD_ENERGY_L1_DAILY,
                False,
            ),
            EnergySensorEntity(
                client,
                self,
                "254_21.energy.energyL2daily",
                const.SMART_METER_RECORD_ENERGY_L2_DAILY,
                False,
            ),
            EnergySensorEntity(
                client,
                self,
                "254_21.energy.energyL3daily",
                const.SMART_METER_RECORD_ENERGY_L3_DAILY,
                False,
            ),
            EnergySensorEntity(
                client,
                self,
                "254_21.energy.netEnergyConsumption",
                const.SMART_METER_RECORD_NET_ENERGY_CONSUMPTION,
            ),
            EnergySensorEntity(
                client,
                self,
                "254_21.energy.lifeTimeEnergyDelivery",
                const.SMART_METER_RECORD_LIFETIME_ENERGY_DELIVERY,
            ),
            EnergySensorEntity(
                client,
                self,
                "254_21.energy.lifeTimeEnergyConsumption",
                const.SMART_METER_RECORD_LIFETIME_ENERGY_CONSUMPTION,
            ),
            # Configurable?
            timezoneEntity,
            # Configurable?
            # MiscSensorEntity(
            #     client,
            #     self,
            #     "254_21.gridConnectionPowerFactor",
            #     const.SMART_METER_GRID_CONNECTION_POWER_FACTOR,
            #     False,
            # ),
            # MiscSensorEntity(
            #     client,
            #     self,
            #     "254_21.gridConnectionSta",
            #     const.SMART_METER_GRID_CONNECTION_STATE,
            #     False,
            # ),
            # Configurable?
            # MiscSensorEntity(
            #     client, self, "254_21.countryCode", const.COUNTRY_CODE, False
            # ),
            # Configurable?
            # MiscSensorEntity(client, self, "254_21.townCode", const.TOWN_CODE, False),
            # Configurable?
            # MiscSensorEntity(
            #     client, self, "254_21.systemGroupId", const.SYSTEM_GROUP_ID, False
            # ),
            # Configurable?
            # MiscBinarySensorEntity(
            #     client,
            #     self,
            #     "254_21.factoryModeEnable",
            #     const.FACTORY_MODE,
            #     False,
            #     diagnostic=True,
            # ),
            # Configurable?
            # MiscBinarySensorEntity(
            #     client,
            #     self,
            #     "254_21.debugModeEnable",
            #     const.DEBUG_MODE,
            #     False,
            #     diagnostic=True,
            # ),
            self._status_sensor(client),
        ]

    @override
    def _prepare_data(self, raw_data: bytes) -> dict[str, Any]:
        res: dict[str, Any] = {"params": {}}
        from google.protobuf.json_format import MessageToDict  # pyright: ignore[reportMissingModuleSource]

        from .proto.ef_smartmeter_pb2 import SmartMeterSetMessage

        try:
            packet = SmartMeterSetMessage()
            _ = packet.ParseFromString(raw_data)
            for message in packet.msg:
                cmd_func = message.cmd_func
                cmd_id = message.cmd_id
                _LOGGER.debug(
                    'cmd_func %u, cmd_id %u, payload "%s"',
                    cmd_func,
                    cmd_id,
                    message.pdata.hex(),
                )

                if message.HasField("device_sn") and message.device_sn != self.device_data.sn:
                    _LOGGER.info(
                        "Ignoring EcoPacket for SN %s on topic for SN %s",
                        message.device_sn,
                        self.device_data.sn,
                    )

                command_desc = CommandFuncAndId(func=cmd_func, id=cmd_id)

                try:
                    command = Command(command_desc)
                except ValueError:
                    _LOGGER.info(
                        "Unsupported EcoPacket cmd_func %u, cmd_id %u",
                        command_desc.func,
                        command_desc.id,
                    )
                    continue

                params = cast(JSONDict, res.setdefault("params", {}))
                if command in {Command.DISPLAY_PROPERTY_UPLOAD}:
                    payload = get_expected_payload_type(command)()
                    try:
                        if message.enc_type == 1:
                            message.pdata = bytes([byte ^ (message.seq % 256) for byte in message.pdata])

                        _ = payload.ParseFromString(message.pdata)
                        params.update(
                            (f"{command.func}_{command.id}.{key}", value)
                            for key, value in cast(
                                JSONDict,
                                flatten_dict(MessageToDict(payload, preserving_proto_field_name=False)),
                            ).items()
                        )
                    except Exception:
                        pass

                # Add cmd information to allow extraction in extract_quota_data
                res["cmdFunc"] = command_desc.func
                res["cmdId"] = command_desc.id
                res["timestamp"] = dt.utcnow()
        except Exception as error:
            _LOGGER.error(error)
            _LOGGER.info(raw_data.hex())
        return res

    # @override
    # def _prepare_data_get_reply_topic(self, raw_data: bytes) -> PreparedData:
    #     data = self._prepare_data(raw_data)
    #     if "cmdFunc" in data and "cmdId" in data:
    #         command_desc = CommandFuncAndId(func=data["cmdFunc"], id=data["cmdId"])

    #         try:
    #             command = Command(command_desc)
    #         except ValueError:
    #             pass

    #         # ???
    #         if command in [
    #             Command.DISPLAY_PROPERTY_UPLOAD,
    #             Command.RUNTIME_PROPERTY_UPLOAD,
    #         ]:
    #             return PreparedData(None, data, {"proto": raw_data.hex()})
    #     return PreparedData(None, None, {"proto": raw_data.hex()})

    @override
    def get_quota_message(self) -> SmartMeterCommandMessage:
        return SmartMeterCommandMessage(
            device_sn=self.device_info.sn,
            command=Command.HEARTBEAT,
            payload=None,
        )

    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return []

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return []

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return []

    def _status_sensor(self, client: EcoflowApiClient) -> StatusSensorEntity:
        return QuotaStatusSensorEntity(client, self)
