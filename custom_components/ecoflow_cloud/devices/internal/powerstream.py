from google.protobuf.json_format import MessageToDict
from custom_components.ecoflow_cloud.devices.internal import to_lower_camel_case
from custom_components.ecoflow_cloud.api.private_api import PrivateAPIMessageProtocol
import logging
from collections.abc import Sequence
from typing import Any, cast, override

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.util import dt

from custom_components.ecoflow_cloud.devices import const, BaseDevice
from custom_components.ecoflow_cloud.select import PowerDictSelectEntity
from custom_components.ecoflow_cloud.number import (
    MaxBatteryLevelEntity,
    MinBatteryLevelEntity,
)


from ...api import EcoflowApiClient
from ...api.message import JSONDict, JSONMessage
from ...sensor import (
    CelsiusSensorEntity,
    CentivoltSensorEntity,
    DeciampSensorEntity,
    DecicelsiusSensorEntity,
    DecihertzSensorEntity,
    DecivoltSensorEntity,
    DeciwattsSensorEntity,
    InWattsSolarSensorEntity,
    LevelSensorEntity,
    MilliampSensorEntity,
    MiscSensorEntity,
    QuotaStatusSensorEntity,
    RemainSensorEntity,
    ResettingInEnergySensorEntity,
    ResettingInEnergySolarSensorEntity,
    ResettingOutEnergySensorEntity,
    StatusSensorEntity,
)

from google.protobuf.message import Message as ProtoMessageRaw

from ...switch import EnabledEntity
import enum
from typing import NamedTuple

from .proto import (
    AddressId,
    powerstream_pb2 as powerstream,
)

_LOGGER = logging.getLogger(__name__)


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

    INVERTER_HEARTBEAT = CommandFuncAndId(func=20, id=1)
    PERMANENT_WATTS_PACK = CommandFuncAndId(func=20, id=129)
    SET_SUPPLY_PRIORITY = CommandFuncAndId(func=20, id=130)
    SET_BAT_LOWER = CommandFuncAndId(func=20, id=132)
    SET_BAT_UPPER = CommandFuncAndId(func=20, id=133)
    SET_BRIGHTNESS = CommandFuncAndId(func=20, id=135)
    SET_FEED_PROTECT = CommandFuncAndId(func=20, id=143)
    RATED_POWER = CommandFuncAndId(func=20, id=146)

    PLATFORM_WATTH = CommandFuncAndId(func=254, id=32)


class WatthType(enum.IntEnum):
    TO_SMART_PLUGS = 2
    TO_BATTERY = 3
    FROM_BATTERY = 4
    PV1 = 7
    PV2 = 8


# Local payload mapping
def get_expected_payload_type(cmd: Command) -> type[ProtoMessageRaw]:
    _expected_payload_types = {
        Command.INVERTER_HEARTBEAT: powerstream.PowerStreamInverterHeartbeat,
        Command.PERMANENT_WATTS_PACK: powerstream.PowerStreamPermanentWattsPack,
        Command.PLATFORM_WATTH: powerstream.PowerStreamBatchEnergyTotalReport,
        Command.SET_SUPPLY_PRIORITY: powerstream.PowerStreamSupplyPriorityPack,
        Command.SET_BAT_LOWER: powerstream.PowerStreamBatLowerPack,
        Command.SET_BAT_UPPER: powerstream.PowerStreamBatUpperPack,
        Command.SET_BRIGHTNESS: powerstream.PowerStreamBrightnessPack,
        Command.SET_FEED_PROTECT: powerstream.PowerStreamSetValue,
    }
    return _expected_payload_types[cmd]


class PowerStreamCommandMessage(PrivateAPIMessageProtocol):
    """Message wrapper for PowerStream protobuf commands."""

    def __init__(
        self,
        device_sn: str,
        command: CommandFuncAndId,
        payload: ProtoMessageRaw | None,
    ):
        self._packet = powerstream.PowerStreamSendHeaderMsg()
        self._payload = payload
        message = self._packet.msg.add()
        message.seq = JSONMessage.gen_seq()
        message.device_sn = device_sn
        message.from_ = "HomeAssistant"

        if command == Command.INVERTER_HEARTBEAT:
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
        result = MessageToDict(self._packet, preserving_proto_field_name=True)
        result["msg"][0]["pdata"] = {
            type(self._payload).__name__: MessageToDict(
                self._payload, preserving_proto_field_name=True
            )
        }
        return {type(self._packet).__name__: result}


class PowerStream(BaseDevice):
    @override
    def sensors(self, client: EcoflowApiClient) -> Sequence[SensorEntity]:
        return [
            CelsiusSensorEntity(client, self, "20_1.espTempsensor", "ESP Temperature"),
            InWattsSolarSensorEntity(
                client, self, "20_1.pv1InputWatts", "Solar 1 Watts"
            ),
            DecivoltSensorEntity(
                client, self, "20_1.pv1InputVolt", "Solar 1 Input Potential"
            ),
            CentivoltSensorEntity(
                client, self, "20_1.pv1OpVolt", "Solar 1 Op Potential"
            ),
            DeciampSensorEntity(client, self, "20_1.pv1InputCur", "Solar 1 Current"),
            DecicelsiusSensorEntity(
                client, self, "20_1.pv1Temp", "Solar 1 Temperature"
            ),
            MiscSensorEntity(
                client, self, "20_1.pv1RelayStatus", "Solar 1 Relay Status"
            ),
            MiscSensorEntity(
                client, self, "20_1.pv1ErrCode", "Solar 1 Error Code", False
            ),
            MiscSensorEntity(
                client, self, "20_1.pv1WarnCode", "Solar 1 Warning Code", False
            ),
            MiscSensorEntity(client, self, "20_1.pv1Statue", "Solar 1 Status", False),
            InWattsSolarSensorEntity(
                client, self, "20_1.pv2InputWatts", "Solar 2 Watts"
            ),
            DecivoltSensorEntity(
                client, self, "20_1.pv2InputVolt", "Solar 2 Input Potential"
            ),
            CentivoltSensorEntity(
                client, self, "20_1.pv2OpVolt", "Solar 2 Op Potential"
            ),
            DeciampSensorEntity(client, self, "20_1.pv2InputCur", "Solar 2 Current"),
            DecicelsiusSensorEntity(
                client, self, "20_1.pv2Temp", "Solar 2 Temperature"
            ),
            MiscSensorEntity(
                client, self, "20_1.pv2RelayStatus", "Solar 2 Relay Status"
            ),
            MiscSensorEntity(
                client, self, "20_1.pv2ErrCode", "Solar 2 Error Code", False
            ),
            MiscSensorEntity(
                client, self, "20_1.pv2WarningCode", "Solar 2 Warning Code", False
            ),
            MiscSensorEntity(client, self, "20_1.pv2Statue", "Solar 2 Status", False),
            MiscSensorEntity(client, self, "20_1.bpType", "Battery Type", False),
            LevelSensorEntity(client, self, "20_1.batSoc", "Battery Charge"),
            DeciwattsSensorEntity(
                client, self, "20_1.batInputWatts", "Battery Input Watts"
            ),
            DecivoltSensorEntity(
                client, self, "20_1.batInputVolt", "Battery Input Potential"
            ),
            DecivoltSensorEntity(
                client, self, "20_1.batOpVolt", "Battery Op Potential"
            ),
            MilliampSensorEntity(
                client, self, "20_1.batInputCur", "Battery Input Current"
            ),
            DecicelsiusSensorEntity(
                client, self, "20_1.batTemp", "Battery Temperature"
            ),
            RemainSensorEntity(client, self, "20_1.chgRemainTime", "Charge Time"),
            RemainSensorEntity(client, self, "20_1.dsgRemainTime", "Discharge Time"),
            MiscSensorEntity(
                client, self, "20_1.batErrCode", "Battery Error Code", False
            ),
            MiscSensorEntity(
                client, self, "20_1.batWarningCode", "Battery Warning Code", False
            ),
            MiscSensorEntity(client, self, "20_1.batStatue", "Battery Status", False),
            DecivoltSensorEntity(
                client, self, "20_1.llcInputVolt", "LLC Input Potential", False
            ),
            DecivoltSensorEntity(
                client, self, "20_1.llcOpVolt", "LLC Op Potential", False
            ),
            DecicelsiusSensorEntity(client, self, "20_1.llcTemp", "LLC Temperature"),
            MiscSensorEntity(client, self, "20_1.llcErrCode", "LLC Error Code", False),
            MiscSensorEntity(
                client, self, "20_1.llcWarningCode", "LLC Warning Code", False
            ),
            MiscSensorEntity(client, self, "20_1.llcStatue", "LLC Status", False),
            MiscSensorEntity(client, self, "20_1.invOnOff", "Inverter On/Off Status"),
            DeciwattsSensorEntity(
                client, self, "20_1.invOutputWatts", "Inverter Output Watts"
            ),
            DecivoltSensorEntity(
                client, self, "20_1.invInputVolt", "Inverter Output Potential", False
            ),
            DecivoltSensorEntity(
                client, self, "20_1.invOpVolt", "Inverter Op Potential"
            ),
            MilliampSensorEntity(
                client, self, "20_1.invOutputCur", "Inverter Output Current"
            ),
            #  MilliampSensorEntity(client, self, "inv_dc_cur", "Inverter DC Current"),
            DecihertzSensorEntity(client, self, "20_1.invFreq", "Inverter Frequency"),
            DecicelsiusSensorEntity(
                client, self, "20_1.invTemp", "Inverter Temperature"
            ),
            MiscSensorEntity(
                client, self, "20_1.invRelayStatus", "Inverter Relay Status"
            ),
            MiscSensorEntity(
                client, self, "20_1.invErrCode", "Inverter Error Code", False
            ),
            MiscSensorEntity(
                client, self, "20_1.invWarnCode", "Inverter Warning Code", False
            ),
            MiscSensorEntity(client, self, "20_1.invStatue", "Inverter Status", False),
            DeciwattsSensorEntity(client, self, "20_1.permanentWatts", "Other Loads"),
            DeciwattsSensorEntity(
                client, self, "20_1.dynamicWatts", "Smart Plug Loads"
            ),
            DeciwattsSensorEntity(client, self, "20_1.ratedPower", "Rated Power"),
            MiscSensorEntity(
                client, self, "20_1.lowerLimit", "Lower Battery Limit", False
            ),
            MiscSensorEntity(
                client, self, "20_1.upperLimit", "Upper Battery Limit", False
            ),
            MiscSensorEntity(
                client, self, "20_1.wirelessErrCode", "Wireless Error Code", False
            ),
            MiscSensorEntity(
                client, self, "20_1.wirelessWarnCode", "Wireless Warning Code", False
            ),
            MiscSensorEntity(
                client, self, "20_1.invBrightness", "LED Brightness", False
            ),
            MiscSensorEntity(
                client, self, "20_1.heartbeatFrequency", "Heartbeat Frequency", False
            ),
            ResettingInEnergySolarSensorEntity(
                client,
                self,
                "254_32.watthPv1",
                "PV1 Today Energy Total",
                enabled=True,
            ),
            ResettingInEnergySolarSensorEntity(
                client,
                self,
                "254_32.watthPv2",
                "PV2 Today Energy Total",
                enabled=True,
            ),
            ResettingInEnergySensorEntity(
                client,
                self,
                "254_32.watthFromBattery",
                "From Battery Today Energy Total",
                enabled=True,
            ),
            ResettingOutEnergySensorEntity(
                client,
                self,
                "254_32.watthToBattery",
                "To Battery Today Energy Total",
                enabled=True,
            ),
            ResettingOutEnergySensorEntity(
                client,
                self,
                "254_32.watthToSmartPlugs",
                "To Smart Plugs Today Energy Total",
                enabled=True,
            ),
            self._status_sensor(client),
        ]

    @override
    def switches(self, client: EcoflowApiClient) -> Sequence[SwitchEntity]:
        return [
            EnabledEntity(
                client,
                self,
                "20_1.feedProtect",
                "Feed-in Control",
                lambda value: PowerStreamCommandMessage(
                    device_sn=self.device_info.sn,
                    command=Command.SET_FEED_PROTECT,
                    payload=powerstream.PowerStreamSetValue(value=value),
                ),
                enabled=True,
                enableValue=1,
            )
        ]

    @override
    def selects(self, client: EcoflowApiClient) -> Sequence[SelectEntity]:
        return [
            PowerDictSelectEntity(
                client,
                self,
                "20_1.supplyPriority",
                "Power supply mode",
                const.POWER_SUPPLY_PRIORITY_OPTIONS,
                lambda value: PowerStreamCommandMessage(
                    device_sn=self.device_info.sn,
                    command=Command.SET_SUPPLY_PRIORITY,
                    payload=powerstream.PowerStreamSupplyPriorityPack(
                        supply_priority=value
                    ),
                ),
            ),
        ]

    @override
    def numbers(self, client: EcoflowApiClient) -> Sequence[NumberEntity]:
        return [
            MaxBatteryLevelEntity(
                client,
                self,
                "20_1.upperLimit",
                const.MAX_CHARGE_LEVEL,
                50,
                100,
                lambda value: PowerStreamCommandMessage(
                    device_sn=self.device_info.sn,
                    command=Command.SET_BAT_UPPER,
                    payload=powerstream.PowerStreamBatUpperPack(upper_limit=value),
                ),
            ),
            MinBatteryLevelEntity(
                client,
                self,
                "20_1.lowerLimit",
                const.MIN_DISCHARGE_LEVEL,
                0,
                30,
                lambda value: PowerStreamCommandMessage(
                    device_sn=self.device_info.sn,
                    command=Command.SET_BAT_LOWER,
                    payload=powerstream.PowerStreamBatLowerPack(lower_limit=value),
                ),
            ),
        ]

    @override
    def _prepare_data(self, raw_data: bytes) -> dict[str, Any]:
        res: dict[str, Any] = {"params": {}}
        from google.protobuf.json_format import MessageToDict

        try:
            packet = powerstream.PowerStreamSendHeaderMsg()
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
                if command in {Command.INVERTER_HEARTBEAT}:
                    payload = get_expected_payload_type(command)()
                    _ = payload.ParseFromString(message.pdata)
                    params.update(
                        (f"{command.func}_{command.id}.{key}", value)
                        for key, value in cast(
                            JSONDict,
                            MessageToDict(payload, preserving_proto_field_name=False),
                        ).items()
                    )
                elif command in {Command.PLATFORM_WATTH}:
                    payload = get_expected_payload_type(command)()
                    _ = payload.ParseFromString(message.pdata)
                    for watth_item in payload.watth_item:
                        try:
                            watth_type_name = to_lower_camel_case(
                                WatthType(watth_item.watth_type).name
                            )
                        except ValueError:
                            continue

                        field_name = (
                            f"watth{watth_type_name[0].upper()}{watth_type_name[1:]}"
                        )
                        params.update(
                            {
                                f"{command.func}_{command.id}.{field_name}": sum(
                                    watth_item.watth
                                ),
                                f"{command.func}_{command.id}.{field_name}Timestamp": watth_item.timestamp,
                            }
                        )

                # Add cmd information to allow extraction in private_api_extract_quota_message
                res["cmdFunc"] = command_desc.func
                res["cmdId"] = command_desc.id
                res["timestamp"] = dt.utcnow()
                continue
        except Exception as error:
            _LOGGER.error(error)
            _LOGGER.info(raw_data.hex())
        return res

    def _status_sensor(self, client: EcoflowApiClient) -> StatusSensorEntity:
        return QuotaStatusSensorEntity(client, self)

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
                Command.INVERTER_HEARTBEAT,
                Command.PLATFORM_WATTH,
            ]:
                return {"params": message["params"], "time": dt.utcnow()}
        raise ValueError("not a quota message")

    @override
    def private_api_get_quota(self) -> PowerStreamCommandMessage:
        return PowerStreamCommandMessage(
            device_sn=self.device_info.sn,
            command=Command.INVERTER_HEARTBEAT,
            payload=None,
        )
