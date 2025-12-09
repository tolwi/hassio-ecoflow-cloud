import enum
from typing import NamedTuple, cast

from google.protobuf.message import Message as ProtoMessageRaw

from .. import platform_pb2 as platform


# https://github.com/tomvd/local-powerstream/issues/4#issuecomment-2781354316
class AddressId(enum.Enum):
    IOT = 1
    IOT2 = 2
    APP = 32
    MQTT = 53


class DirectionId(enum.Enum):
    DEFAULT = 1


class CommandFunc(enum.IntEnum):
    DEFAULT = 0
    SMART_PLUG = 2
    POWERSTREAM = 20
    SMART_METER = 254
    PLATFORM = platform.PlCmdSets.PL_EXT_CMD_SETS


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

    PRIVATE_API_POWERSTREAM_HEARTBEAT = CommandFuncAndId(
        func=CommandFunc.POWERSTREAM, id=1
    )

    WN511_SET_PERMANENT_WATTS_PACK = CommandFuncAndId(
        func=CommandFunc.POWERSTREAM, id=129
    )
    WN511_SET_SUPPLY_PRIORITY_PACK = CommandFuncAndId(
        func=CommandFunc.POWERSTREAM, id=130
    )
    WN511_SET_BAT_LOWER_PACK = CommandFuncAndId(func=CommandFunc.POWERSTREAM, id=132)
    WN511_SET_BAT_UPPER_PACK = CommandFuncAndId(func=CommandFunc.POWERSTREAM, id=133)
    WN511_SET_BRIGHTNESS_PACK = CommandFuncAndId(func=CommandFunc.POWERSTREAM, id=135)

    PRIVATE_API_POWERSTREAM_SET_FEED_PROTECT = CommandFuncAndId(
        func=CommandFunc.POWERSTREAM, id=143
    )

    PRIVATE_API_SMART_METER_DISPLAY_PROPERTY_UPLOAD = CommandFuncAndId(func=CommandFunc.SMART_METER, id=21)
    PRIVATE_API_SMART_METER_RUNTIME_PROPERTY_UPLOAD = CommandFuncAndId(func=CommandFunc.SMART_METER, id=22)

    PRIVATE_API_PLATFORM_WATTH = CommandFuncAndId(
        func=CommandFunc.PLATFORM, id=platform.PlCmdId.PL_CMD_ID_WATTH
    )


# https://github.com/peuter/ecoflow/blob/04bb01fb3d6dcd845b0a896342b0d895f532cf85/model/ecoflow/constant.py#L9
class WatthType(enum.IntEnum):
    TO_SMART_PLUGS = 2  # ?
    TO_BATTERY = 3  # ?
    FROM_BATTERY = 4  # ?
    PV1 = 7  # ?
    PV2 = 8  # ?


_expected_payload_types = dict[Command, type[ProtoMessageRaw]]()


def get_expected_payload_type(cmd: Command) -> type[ProtoMessageRaw]:
    from .. import powerstream_pb2 as powerstream
    from .. import ef_dp3_iobroker_pb2 as dev_apl_comm

    global _expected_payload_types
    if not _expected_payload_types:
        _expected_payload_types.update(
            cast(
                dict[Command, type[ProtoMessageRaw]],
                {
                    Command.PRIVATE_API_POWERSTREAM_HEARTBEAT: powerstream.InverterHeartbeat,
                    Command.WN511_SET_PERMANENT_WATTS_PACK: powerstream.PermanentWattsPack,
                    Command.WN511_SET_SUPPLY_PRIORITY_PACK: powerstream.SupplyPriorityPack,
                    Command.WN511_SET_BAT_LOWER_PACK: powerstream.BatLowerPack,
                    Command.WN511_SET_BAT_UPPER_PACK: powerstream.BatUpperPack,
                    Command.WN511_SET_BRIGHTNESS_PACK: powerstream.BrightnessPack,
                    Command.PRIVATE_API_POWERSTREAM_SET_FEED_PROTECT: powerstream.PrivateAPIGenericSetValue,
                    Command.PRIVATE_API_PLATFORM_WATTH: platform.BatchEnergyTotalReport,
                    Command.PRIVATE_API_SMART_METER_DISPLAY_PROPERTY_UPLOAD: dev_apl_comm.DisplayPropertyUpload,
                    Command.PRIVATE_API_SMART_METER_RUNTIME_PROPERTY_UPLOAD: dev_apl_comm.RuntimePropertyUpload
                },
            )
        )

    return _expected_payload_types[cmd]
