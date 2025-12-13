from google.protobuf.json_format import MessageToDict
from custom_components.ecoflow_cloud.devices.internal import flatten_dict
from custom_components.ecoflow_cloud.api.private_api import PrivateAPIMessageProtocol
from custom_components.ecoflow_cloud.api.message import JSONMessage
import logging
from typing import Any, cast, override


# from homeassistant.components.sensor import SensorEntity  # pyright: ignore[reportMissingImports]
# from homeassistant.components.switch import SwitchEntity  # pyright: ignore[reportMissingImports]
# from homeassistant.components.number import NumberEntity  # pyright: ignore[reportMissingImports]
# from homeassistant.components.select import SelectEntity  # pyright: ignore[reportMissingImports]
from homeassistant.util import dt

from ...api import EcoflowApiClient
from ...api.message import JSONDict
from ...devices import const, BaseDevice
from ...entities import (
    BaseSensorEntity,
    BaseNumberEntity,
    BaseSwitchEntity,
    BaseSelectEntity,
)
from ...sensor import (
    MiscSensorEntity,
    VoltSensorEntity,
    WattsSensorEntity,
    InAmpSensorEntity,
    EnergySensorEntity,
    QuotaStatusSensorEntity,
    StatusSensorEntity,
)


from ..internal.proto import AddressId

import enum
from typing import NamedTuple
from ..internal.proto import ef_smartmeter_pb2
from google.protobuf.message import Message as ProtoMessageRaw


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

    def __init__(
        self, device_sn: str, command: CommandFuncAndId, payload: ProtoMessageRaw | None
    ):
        self._packet = ef_smartmeter_pb2.SmartMeterSetMessage()
        self._payload = payload
        message = self._packet.msg.add()
        message.seq = JSONMessage.gen_seq()
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
        payload_dict = MessageToDict(self._payload, preserving_proto_field_name=True)

        result = MessageToDict(self._packet, preserving_proto_field_name=True)
        result["msg"][0]["pdata"] = {type(self._payload).__name__: payload_dict}
        result["msg"][0].pop("seq", None)
        return {type(self._packet).__name__: result}


class SmartMeter(BaseDevice):
    @override
    def private_api_extract_quota_message(self, message: JSONDict) -> dict[str, Any]:
        if "cmdFunc" in message and "cmdId" in message:
            command_desc = CommandFuncAndId(
                func=message["cmdFunc"], id=message["cmdId"]
            )

            try:
                command = Command(command_desc)
            except ValueError:
                pass
            if command in [
                Command.DISPLAY_PROPERTY_UPLOAD,
                Command.RUNTIME_PROPERTY_UPLOAD,
            ]:
                return {"params": message["params"], "time": dt.utcnow()}
        raise ValueError("not a quota message")

    @override
    def private_api_get_quota(self) -> SmartMeterCommandMessage:
        return SmartMeterCommandMessage(
            device_sn=self.device_info.sn,
            command=Command.HEARTBEAT,
            payload=None,
        )

    @override
    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        timezoneEntity = MiscSensorEntity(
            client, self, "254_21.utcTimezone", const.UTC_TIMEZONE, False
        )
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

    def update_data(self, raw_data: bytes, data_type: str) -> bool:
        if data_type not in [
            self.device_info.data_topic,
            self.device_info.set_reply_topic,
            self.device_info.get_reply_topic,
            self.device_info.status_topic,
        ]:
            super().update_data(raw_data, data_type)
        return True

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

                if (
                    message.HasField("device_sn")
                    and message.device_sn != self.device_data.sn
                ):
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
                            message.pdata = bytes(
                                [byte ^ (message.seq % 256) for byte in message.pdata]
                            )

                        _ = payload.ParseFromString(message.pdata)
                        params.update(
                            (f"{command.func}_{command.id}.{key}", value)
                            for key, value in cast(
                                JSONDict,
                                flatten_dict(
                                    MessageToDict(
                                        payload, preserving_proto_field_name=False
                                    )
                                ),
                            ).items()
                        )
                    except Exception:
                        pass

                # Add cmd information to allow extraction in private_api_extract_quota_message
                res["cmdFunc"] = command_desc.func
                res["cmdId"] = command_desc.id
                res["timestamp"] = dt.utcnow()
        except Exception as error:
            _LOGGER.error(error)
            _LOGGER.info(raw_data.hex())
        return res

    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return []

    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        return []

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return []

    def _status_sensor(self, client: EcoflowApiClient) -> StatusSensorEntity:
        return QuotaStatusSensorEntity(client, self)
