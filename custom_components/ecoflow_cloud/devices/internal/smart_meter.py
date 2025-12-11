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
    MiscBinarySensorEntity,
    QuotaStatusSensorEntity,
    StatusSensorEntity,
)

# from google.protobuf.message import Message as ProtoMessageRaw # pyright: ignore[reportMissingModuleSource]

from .proto.support.message import ProtoMessage

from ..internal.proto import AddressId

import enum
from typing import NamedTuple
from ..internal.proto import ef_smartmeter_pb2
from google.protobuf.message import Message as ProtoMessageRaw


# Local Constants
class CommandFunc(enum.IntEnum):
    SMART_METER = 254


class CommandFuncAndId(NamedTuple):
    func: int
    id: int


class Command(enum.Enum):
    @enum.property
    def func(self) -> CommandFunc | int:
        return self.value.func

    @enum.property
    def id(self) -> int:
        return self.value.id

    PRIVATE_API_SMART_METER_DISPLAY_PROPERTY_UPLOAD = CommandFuncAndId(
        func=CommandFunc.SMART_METER, id=21
    )
    PRIVATE_API_SMART_METER_RUNTIME_PROPERTY_UPLOAD = CommandFuncAndId(
        func=CommandFunc.SMART_METER, id=22
    )


def get_expected_payload_type(cmd: Command) -> type[ProtoMessageRaw]:
    _expected_payload_types = {
        Command.PRIVATE_API_SMART_METER_DISPLAY_PROPERTY_UPLOAD: ef_smartmeter_pb2.SmartMeterDisplayPropertyUpload,
        Command.PRIVATE_API_SMART_METER_RUNTIME_PROPERTY_UPLOAD: ef_smartmeter_pb2.SmartMeterRuntimePropertyUpload,
    }
    return _expected_payload_types[cmd]


_LOGGER = logging.getLogger(__name__)


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
                Command.PRIVATE_API_SMART_METER_DISPLAY_PROPERTY_UPLOAD,
                Command.PRIVATE_API_SMART_METER_RUNTIME_PROPERTY_UPLOAD,
            ]:
                return {"params": message["params"], "time": dt.utcnow()}
        raise ValueError("not a quota message")

    @override
    def private_api_get_quota(self) -> ProtoMessage:
        from .proto import ef_smartmeter_pb2

        return ProtoMessage(
            src=AddressId.APP,
            dest=AddressId.APP,
            from_="Android",
            command=CommandFuncAndId(20, 1),
            create_packet=ef_smartmeter_pb2.SmartMeterSendHeaderMsg,
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
                "254_21.powGetSysGrid",
                const.SMART_METER_POWER_GLOBAL,
                diagnostic=False,
            ),
            WattsSensorEntity(
                client,
                self,
                "254_21.gridConnectionPowerL1",
                const.SMART_METER_POWER_L1,
                False,
            ),
            WattsSensorEntity(
                client,
                self,
                "254_21.gridConnectionPowerL2",
                const.SMART_METER_POWER_L2,
                False,
            ),
            WattsSensorEntity(
                client,
                self,
                "254_21.gridConnectionPowerL3",
                const.SMART_METER_POWER_L3,
                False,
            ),
            InAmpSensorEntity(
                client,
                self,
                "254_21.gridConnectionAmpL1",
                const.SMART_METER_IN_AMPS_L1,
                False,
            ),
            InAmpSensorEntity(
                client,
                self,
                "254_21.gridConnectionAmpL2",
                const.SMART_METER_IN_AMPS_L2,
                False,
            ),
            InAmpSensorEntity(
                client,
                self,
                "254_21.gridConnectionAmpL3",
                const.SMART_METER_IN_AMPS_L3,
                False,
            ),
            VoltSensorEntity(
                client,
                self,
                "254_21.gridConnectionVolL1",
                const.SMART_METER_VOLT_L1,
                False,
            ),
            VoltSensorEntity(
                client,
                self,
                "254_21.gridConnectionVolL2",
                const.SMART_METER_VOLT_L2,
                False,
            ),
            VoltSensorEntity(
                client,
                self,
                "254_21.gridConnectionVolL3",
                const.SMART_METER_VOLT_L3,
                False,
            ),
            MiscBinarySensorEntity(
                client,
                self,
                "254_21.gridConnectionFlagL1",
                const.SMART_METER_FLAG_L1,
                False,
            ),
            MiscBinarySensorEntity(
                client,
                self,
                "254_21.gridConnectionFlagL2",
                const.SMART_METER_FLAG_L2,
                False,
            ),
            MiscBinarySensorEntity(
                client,
                self,
                "254_21.gridConnectionFlagL3",
                const.SMART_METER_FLAG_L3,
                False,
            ),
            EnergySensorEntity(
                client,
                self,
                "254_21.gridConnectionDataRecord.todayActiveL1",
                const.SMART_METER_RECORD_TODAY_ACTIVE_L1,
                False,
            ),
            EnergySensorEntity(
                client,
                self,
                "254_21.gridConnectionDataRecord.todayActiveL2",
                const.SMART_METER_RECORD_TODAY_ACTIVE_L2,
                False,
            ),
            EnergySensorEntity(
                client,
                self,
                "254_21.gridConnectionDataRecord.todayActiveL3",
                const.SMART_METER_RECORD_TODAY_ACTIVE_L3,
                False,
            ),
            EnergySensorEntity(
                client,
                self,
                "254_21.gridConnectionDataRecord.todayActive",
                const.SMART_METER_RECORD_ACTIVE_TODAY,
            ),
            EnergySensorEntity(
                client,
                self,
                "254_21.gridConnectionDataRecord.totalReactiveEnergy",
                const.SMART_METER_RECORD_LIFETIME_ENERGY_DELIVERY,
            ),
            EnergySensorEntity(
                client,
                self,
                "254_21.gridConnectionDataRecord.totalActiveEnergy",
                const.SMART_METER_RECORD_NET_ENERGY_CONSUMPTION,
            ),
            # Configurable?
            timezoneEntity,
            # Configurable?
            MiscSensorEntity(
                client,
                self,
                "254_21.gridConnectionPowerFactor",
                const.SMART_METER_GRID_CONNECTION_POWER_FACTOR,
                False,
            ),
            MiscSensorEntity(
                client,
                self,
                "254_21.gridConnectionSta",
                const.SMART_METER_GRID_CONNECTION_STATE,
                False,
            ),
            # Configurable?
            MiscSensorEntity(
                client, self, "254_21.countryCode", const.COUNTRY_CODE, False
            ),
            # Configurable?
            MiscSensorEntity(client, self, "254_21.townCode", const.TOWN_CODE, False),
            # Configurable?
            MiscSensorEntity(
                client, self, "254_21.systemGroupId", const.SYSTEM_GROUP_ID, False
            ),
            # Configurable?
            MiscBinarySensorEntity(
                client,
                self,
                "254_21.factoryModeEnable",
                const.FACTORY_MODE,
                False,
                diagnostic=True,
            ),
            # Configurable?
            MiscBinarySensorEntity(
                client,
                self,
                "254_21.debugModeEnable",
                const.DEBUG_MODE,
                False,
                diagnostic=True,
            ),
            self._status_sensor(client),
        ]

    def update_data(self, raw_data: bytes, data_type: str) -> bool:
        if data_type == self.device_info.data_topic:
            raw = self._prepare_data_data_topic(raw_data)
            self.data.update_data(raw)
        elif data_type == self.device_info.set_topic:
            # Commands send from HomeAssistant
            pass
        elif data_type == self.device_info.set_reply_topic:
            raw = self._prepare_data_set_reply_topic(raw_data)
            self.data.add_set_reply_message(raw)
        elif data_type == self.device_info.get_topic:
            # Commands send from HomeAssistant
            pass
        elif data_type == self.device_info.get_reply_topic:
            raw = self._prepare_data_get_reply_topic(raw_data)
            self.data.add_get_reply_message(raw)
        elif data_type == self.device_info.status_topic:
            raw = self._prepare_data_status_topic(raw_data)
            self.data.update_status(raw)
        else:
            return False
        return True

    @override
    def _prepare_data(self, raw_data: bytes) -> dict[str, Any]:
        res: dict[str, Any] = {"params": {}}
        from google.protobuf.json_format import MessageToDict  # pyright: ignore[reportMissingModuleSource]
        from .proto.support import flatten_dict

        from .proto.ef_smartmeter_pb2 import SmartMeterSendHeaderMsg

        try:
            packet = SmartMeterSendHeaderMsg()
            _ = packet.ParseFromString(raw_data)
            for message in packet.msg:
                _LOGGER.debug(
                    'cmd_func %u, cmd_id %u, payload "%s"',
                    message.cmd_func,
                    message.cmd_id,
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

                command_desc = CommandFuncAndId(
                    func=message.cmd_func, id=message.cmd_id
                )

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
                if command in {Command.PRIVATE_API_SMART_METER_DISPLAY_PROPERTY_UPLOAD}:
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
