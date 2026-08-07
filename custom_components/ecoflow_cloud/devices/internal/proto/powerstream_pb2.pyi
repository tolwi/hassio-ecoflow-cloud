from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper

DESCRIPTOR: _descriptor.FileDescriptor

class PlCmdSets(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PL_NONE_CMD_SETS: _ClassVar[PlCmdSets]
    PL_BASIC_CMD_SETS: _ClassVar[PlCmdSets]
    PL_EXT_CMD_SETS: _ClassVar[PlCmdSets]

class PlCmdId(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PL_CMD_ID_NONE: _ClassVar[PlCmdId]
    PL_CMD_ID_XLOG: _ClassVar[PlCmdId]
    PL_CMD_ID_WATTH: _ClassVar[PlCmdId]
PL_NONE_CMD_SETS: PlCmdSets
PL_BASIC_CMD_SETS: PlCmdSets
PL_EXT_CMD_SETS: PlCmdSets
PL_CMD_ID_NONE: PlCmdId
PL_CMD_ID_XLOG: PlCmdId
PL_CMD_ID_WATTH: PlCmdId

class PowerStreamHeader(_message.Message):
    __slots__ = ("ack_type", "check_type", "cmd_func", "cmd_id", "code", "d_dest", "d_src", "data_len", "dest", "device_sn", "enc_type", "from_", "is_ack", "is_queue", "is_rw_cmd", "module_sn", "need_ack", "payload_ver", "pdata", "product_id", "seq", "src", "time_snap", "version")
    PDATA_FIELD_NUMBER: _ClassVar[int]
    SRC_FIELD_NUMBER: _ClassVar[int]
    DEST_FIELD_NUMBER: _ClassVar[int]
    D_SRC_FIELD_NUMBER: _ClassVar[int]
    D_DEST_FIELD_NUMBER: _ClassVar[int]
    ENC_TYPE_FIELD_NUMBER: _ClassVar[int]
    CHECK_TYPE_FIELD_NUMBER: _ClassVar[int]
    CMD_FUNC_FIELD_NUMBER: _ClassVar[int]
    CMD_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_LEN_FIELD_NUMBER: _ClassVar[int]
    NEED_ACK_FIELD_NUMBER: _ClassVar[int]
    IS_ACK_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_VER_FIELD_NUMBER: _ClassVar[int]
    TIME_SNAP_FIELD_NUMBER: _ClassVar[int]
    IS_RW_CMD_FIELD_NUMBER: _ClassVar[int]
    IS_QUEUE_FIELD_NUMBER: _ClassVar[int]
    ACK_TYPE_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    FROM__FIELD_NUMBER: _ClassVar[int]
    MODULE_SN_FIELD_NUMBER: _ClassVar[int]
    DEVICE_SN_FIELD_NUMBER: _ClassVar[int]
    pdata: bytes
    src: int
    dest: int
    d_src: int
    d_dest: int
    enc_type: int
    check_type: int
    cmd_func: int
    cmd_id: int
    data_len: int
    need_ack: int
    is_ack: int
    seq: int
    product_id: int
    version: int
    payload_ver: int
    time_snap: int
    is_rw_cmd: int
    is_queue: int
    ack_type: int
    code: str
    from_: str
    module_sn: str
    device_sn: str
    def __init__(self, pdata: bytes | None = ..., src: int | None = ..., dest: int | None = ..., d_src: int | None = ..., d_dest: int | None = ..., enc_type: int | None = ..., check_type: int | None = ..., cmd_func: int | None = ..., cmd_id: int | None = ..., data_len: int | None = ..., need_ack: int | None = ..., is_ack: int | None = ..., seq: int | None = ..., product_id: int | None = ..., version: int | None = ..., payload_ver: int | None = ..., time_snap: int | None = ..., is_rw_cmd: int | None = ..., is_queue: int | None = ..., ack_type: int | None = ..., code: str | None = ..., from_: str | None = ..., module_sn: str | None = ..., device_sn: str | None = ...) -> None: ...

class PowerStreamSendHeaderMsg(_message.Message):
    __slots__ = ("msg",)
    MSG_FIELD_NUMBER: _ClassVar[int]
    msg: _containers.RepeatedCompositeFieldContainer[PowerStreamHeader]
    def __init__(self, msg: _Iterable[PowerStreamHeader | _Mapping] | None = ...) -> None: ...

class PowerStreamInverterHeartbeat(_message.Message):
    __slots__ = ("bat_error_code", "bat_input_cur", "bat_input_volt", "bat_input_watts", "bat_op_volt", "bat_soc", "bat_statue", "bat_temp", "bat_warning_code", "bp_type", "chg_remain_time", "dsg_remain_time", "dynamic_watts", "feed_protect", "heartbeat_frequency", "install_country", "install_town", "inv_brightness", "inv_dc_cur", "inv_error_code", "inv_freq", "inv_input_volt", "inv_on_off", "inv_op_volt", "inv_output_cur", "inv_output_watts", "inv_relay_status", "inv_statue", "inv_temp", "inv_warning_code", "llc_error_code", "llc_input_volt", "llc_op_volt", "llc_statue", "llc_temp", "llc_warning_code", "lower_limit", "permanent_watts", "pv1_error_code", "pv1_input_cur", "pv1_input_volt", "pv1_input_watts", "pv1_op_volt", "pv1_relay_status", "pv1_statue", "pv1_temp", "pv1_warning_code", "pv2_error_code", "pv2_input_cur", "pv2_input_volt", "pv2_input_watts", "pv2_op_volt", "pv2_relay_status", "pv2_statue", "pv2_temp", "pv2_warning_code", "rated_power", "supply_priority", "upper_limit", "wireless_error_code", "wireless_warning_code")
    INV_ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    INV_WARNING_CODE_FIELD_NUMBER: _ClassVar[int]
    PV1_ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    PV1_WARNING_CODE_FIELD_NUMBER: _ClassVar[int]
    PV2_ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    PV2_WARNING_CODE_FIELD_NUMBER: _ClassVar[int]
    BAT_ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    BAT_WARNING_CODE_FIELD_NUMBER: _ClassVar[int]
    LLC_ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    LLC_WARNING_CODE_FIELD_NUMBER: _ClassVar[int]
    PV1_STATUE_FIELD_NUMBER: _ClassVar[int]
    PV2_STATUE_FIELD_NUMBER: _ClassVar[int]
    BAT_STATUE_FIELD_NUMBER: _ClassVar[int]
    LLC_STATUE_FIELD_NUMBER: _ClassVar[int]
    INV_STATUE_FIELD_NUMBER: _ClassVar[int]
    PV1_INPUT_VOLT_FIELD_NUMBER: _ClassVar[int]
    PV1_OP_VOLT_FIELD_NUMBER: _ClassVar[int]
    PV1_INPUT_CUR_FIELD_NUMBER: _ClassVar[int]
    PV1_INPUT_WATTS_FIELD_NUMBER: _ClassVar[int]
    PV1_TEMP_FIELD_NUMBER: _ClassVar[int]
    PV2_INPUT_VOLT_FIELD_NUMBER: _ClassVar[int]
    PV2_OP_VOLT_FIELD_NUMBER: _ClassVar[int]
    PV2_INPUT_CUR_FIELD_NUMBER: _ClassVar[int]
    PV2_INPUT_WATTS_FIELD_NUMBER: _ClassVar[int]
    PV2_TEMP_FIELD_NUMBER: _ClassVar[int]
    BAT_INPUT_VOLT_FIELD_NUMBER: _ClassVar[int]
    BAT_OP_VOLT_FIELD_NUMBER: _ClassVar[int]
    BAT_INPUT_CUR_FIELD_NUMBER: _ClassVar[int]
    BAT_INPUT_WATTS_FIELD_NUMBER: _ClassVar[int]
    BAT_TEMP_FIELD_NUMBER: _ClassVar[int]
    BAT_SOC_FIELD_NUMBER: _ClassVar[int]
    LLC_INPUT_VOLT_FIELD_NUMBER: _ClassVar[int]
    LLC_OP_VOLT_FIELD_NUMBER: _ClassVar[int]
    LLC_TEMP_FIELD_NUMBER: _ClassVar[int]
    INV_INPUT_VOLT_FIELD_NUMBER: _ClassVar[int]
    INV_OP_VOLT_FIELD_NUMBER: _ClassVar[int]
    INV_OUTPUT_CUR_FIELD_NUMBER: _ClassVar[int]
    INV_OUTPUT_WATTS_FIELD_NUMBER: _ClassVar[int]
    INV_TEMP_FIELD_NUMBER: _ClassVar[int]
    INV_FREQ_FIELD_NUMBER: _ClassVar[int]
    INV_DC_CUR_FIELD_NUMBER: _ClassVar[int]
    BP_TYPE_FIELD_NUMBER: _ClassVar[int]
    INV_RELAY_STATUS_FIELD_NUMBER: _ClassVar[int]
    PV1_RELAY_STATUS_FIELD_NUMBER: _ClassVar[int]
    PV2_RELAY_STATUS_FIELD_NUMBER: _ClassVar[int]
    INSTALL_COUNTRY_FIELD_NUMBER: _ClassVar[int]
    INSTALL_TOWN_FIELD_NUMBER: _ClassVar[int]
    PERMANENT_WATTS_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_WATTS_FIELD_NUMBER: _ClassVar[int]
    SUPPLY_PRIORITY_FIELD_NUMBER: _ClassVar[int]
    LOWER_LIMIT_FIELD_NUMBER: _ClassVar[int]
    UPPER_LIMIT_FIELD_NUMBER: _ClassVar[int]
    INV_ON_OFF_FIELD_NUMBER: _ClassVar[int]
    WIRELESS_ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    WIRELESS_WARNING_CODE_FIELD_NUMBER: _ClassVar[int]
    INV_BRIGHTNESS_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    RATED_POWER_FIELD_NUMBER: _ClassVar[int]
    CHG_REMAIN_TIME_FIELD_NUMBER: _ClassVar[int]
    DSG_REMAIN_TIME_FIELD_NUMBER: _ClassVar[int]
    FEED_PROTECT_FIELD_NUMBER: _ClassVar[int]
    inv_error_code: int
    inv_warning_code: int
    pv1_error_code: int
    pv1_warning_code: int
    pv2_error_code: int
    pv2_warning_code: int
    bat_error_code: int
    bat_warning_code: int
    llc_error_code: int
    llc_warning_code: int
    pv1_statue: int
    pv2_statue: int
    bat_statue: int
    llc_statue: int
    inv_statue: int
    pv1_input_volt: int
    pv1_op_volt: int
    pv1_input_cur: int
    pv1_input_watts: int
    pv1_temp: int
    pv2_input_volt: int
    pv2_op_volt: int
    pv2_input_cur: int
    pv2_input_watts: int
    pv2_temp: int
    bat_input_volt: int
    bat_op_volt: int
    bat_input_cur: int
    bat_input_watts: int
    bat_temp: int
    bat_soc: int
    llc_input_volt: int
    llc_op_volt: int
    llc_temp: int
    inv_input_volt: int
    inv_op_volt: int
    inv_output_cur: int
    inv_output_watts: int
    inv_temp: int
    inv_freq: int
    inv_dc_cur: int
    bp_type: int
    inv_relay_status: int
    pv1_relay_status: int
    pv2_relay_status: int
    install_country: int
    install_town: int
    permanent_watts: int
    dynamic_watts: int
    supply_priority: int
    lower_limit: int
    upper_limit: int
    inv_on_off: int
    wireless_error_code: int
    wireless_warning_code: int
    inv_brightness: int
    heartbeat_frequency: int
    rated_power: int
    chg_remain_time: int
    dsg_remain_time: int
    feed_protect: int
    def __init__(self, inv_error_code: int | None = ..., inv_warning_code: int | None = ..., pv1_error_code: int | None = ..., pv1_warning_code: int | None = ..., pv2_error_code: int | None = ..., pv2_warning_code: int | None = ..., bat_error_code: int | None = ..., bat_warning_code: int | None = ..., llc_error_code: int | None = ..., llc_warning_code: int | None = ..., pv1_statue: int | None = ..., pv2_statue: int | None = ..., bat_statue: int | None = ..., llc_statue: int | None = ..., inv_statue: int | None = ..., pv1_input_volt: int | None = ..., pv1_op_volt: int | None = ..., pv1_input_cur: int | None = ..., pv1_input_watts: int | None = ..., pv1_temp: int | None = ..., pv2_input_volt: int | None = ..., pv2_op_volt: int | None = ..., pv2_input_cur: int | None = ..., pv2_input_watts: int | None = ..., pv2_temp: int | None = ..., bat_input_volt: int | None = ..., bat_op_volt: int | None = ..., bat_input_cur: int | None = ..., bat_input_watts: int | None = ..., bat_temp: int | None = ..., bat_soc: int | None = ..., llc_input_volt: int | None = ..., llc_op_volt: int | None = ..., llc_temp: int | None = ..., inv_input_volt: int | None = ..., inv_op_volt: int | None = ..., inv_output_cur: int | None = ..., inv_output_watts: int | None = ..., inv_temp: int | None = ..., inv_freq: int | None = ..., inv_dc_cur: int | None = ..., bp_type: int | None = ..., inv_relay_status: int | None = ..., pv1_relay_status: int | None = ..., pv2_relay_status: int | None = ..., install_country: int | None = ..., install_town: int | None = ..., permanent_watts: int | None = ..., dynamic_watts: int | None = ..., supply_priority: int | None = ..., lower_limit: int | None = ..., upper_limit: int | None = ..., inv_on_off: int | None = ..., wireless_error_code: int | None = ..., wireless_warning_code: int | None = ..., inv_brightness: int | None = ..., heartbeat_frequency: int | None = ..., rated_power: int | None = ..., chg_remain_time: int | None = ..., dsg_remain_time: int | None = ..., feed_protect: int | None = ...) -> None: ...

class PowerStreamPermanentWattsPack(_message.Message):
    __slots__ = ("permanent_watts",)
    PERMANENT_WATTS_FIELD_NUMBER: _ClassVar[int]
    permanent_watts: int
    def __init__(self, permanent_watts: int | None = ...) -> None: ...

class PowerStreamSupplyPriorityPack(_message.Message):
    __slots__ = ("supply_priority",)
    SUPPLY_PRIORITY_FIELD_NUMBER: _ClassVar[int]
    supply_priority: int
    def __init__(self, supply_priority: int | None = ...) -> None: ...

class PowerStreamBatLowerPack(_message.Message):
    __slots__ = ("lower_limit",)
    LOWER_LIMIT_FIELD_NUMBER: _ClassVar[int]
    lower_limit: int
    def __init__(self, lower_limit: int | None = ...) -> None: ...

class PowerStreamBatUpperPack(_message.Message):
    __slots__ = ("upper_limit",)
    UPPER_LIMIT_FIELD_NUMBER: _ClassVar[int]
    upper_limit: int
    def __init__(self, upper_limit: int | None = ...) -> None: ...

class PowerStreamBrightnessPack(_message.Message):
    __slots__ = ("brightness",)
    BRIGHTNESS_FIELD_NUMBER: _ClassVar[int]
    brightness: int
    def __init__(self, brightness: int | None = ...) -> None: ...

class PowerStreamPowerItem(_message.Message):
    __slots__ = ("battery_power", "inv_to_grid_power", "inv_to_plug_power", "pv1_output_power", "pv2_output_power", "timestamp", "timezone")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    INV_TO_GRID_POWER_FIELD_NUMBER: _ClassVar[int]
    INV_TO_PLUG_POWER_FIELD_NUMBER: _ClassVar[int]
    BATTERY_POWER_FIELD_NUMBER: _ClassVar[int]
    PV1_OUTPUT_POWER_FIELD_NUMBER: _ClassVar[int]
    PV2_OUTPUT_POWER_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    timezone: int
    inv_to_grid_power: int
    inv_to_plug_power: int
    battery_power: int
    pv1_output_power: int
    pv2_output_power: int
    def __init__(self, timestamp: int | None = ..., timezone: int | None = ..., inv_to_grid_power: int | None = ..., inv_to_plug_power: int | None = ..., battery_power: int | None = ..., pv1_output_power: int | None = ..., pv2_output_power: int | None = ...) -> None: ...

class PowerStreamPowerPack(_message.Message):
    __slots__ = ("sys_power_stream", "sys_seq")
    SYS_SEQ_FIELD_NUMBER: _ClassVar[int]
    SYS_POWER_STREAM_FIELD_NUMBER: _ClassVar[int]
    sys_seq: int
    sys_power_stream: _containers.RepeatedCompositeFieldContainer[PowerStreamPowerItem]
    def __init__(self, sys_seq: int | None = ..., sys_power_stream: _Iterable[PowerStreamPowerItem | _Mapping] | None = ...) -> None: ...

class PowerStreamPowerAckPack(_message.Message):
    __slots__ = ("sys_seq",)
    SYS_SEQ_FIELD_NUMBER: _ClassVar[int]
    sys_seq: int
    def __init__(self, sys_seq: int | None = ...) -> None: ...

class PowerStreamNodeMessage(_message.Message):
    __slots__ = ("mac", "sn")
    SN_FIELD_NUMBER: _ClassVar[int]
    MAC_FIELD_NUMBER: _ClassVar[int]
    sn: str
    mac: bytes
    def __init__(self, sn: str | None = ..., mac: bytes | None = ...) -> None: ...

class PowerStreamMeshChildNodeInfo(_message.Message):
    __slots__ = ("max_sub_device_num", "mesh_id", "mesh_protocol", "parent_mac_id", "sub_device_list", "topology_type")
    TOPOLOGY_TYPE_FIELD_NUMBER: _ClassVar[int]
    MESH_PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    MAX_SUB_DEVICE_NUM_FIELD_NUMBER: _ClassVar[int]
    PARENT_MAC_ID_FIELD_NUMBER: _ClassVar[int]
    MESH_ID_FIELD_NUMBER: _ClassVar[int]
    SUB_DEVICE_LIST_FIELD_NUMBER: _ClassVar[int]
    topology_type: int
    mesh_protocol: int
    max_sub_device_num: int
    parent_mac_id: bytes
    mesh_id: bytes
    sub_device_list: _containers.RepeatedCompositeFieldContainer[PowerStreamNodeMessage]
    def __init__(self, topology_type: int | None = ..., mesh_protocol: int | None = ..., max_sub_device_num: int | None = ..., parent_mac_id: bytes | None = ..., mesh_id: bytes | None = ..., sub_device_list: _Iterable[PowerStreamNodeMessage | _Mapping] | None = ...) -> None: ...

class PowerStreamSetValue(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: int | None = ...) -> None: ...

class PowerStreamEnergyItem(_message.Message):
    __slots__ = ("timestamp", "watth", "watth_type")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    WATTH_TYPE_FIELD_NUMBER: _ClassVar[int]
    WATTH_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    watth_type: int
    watth: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, timestamp: int | None = ..., watth_type: int | None = ..., watth: _Iterable[int] | None = ...) -> None: ...

class PowerStreamEnergyTotalReport(_message.Message):
    __slots__ = ("watth_item", "watth_seq")
    WATTH_SEQ_FIELD_NUMBER: _ClassVar[int]
    WATTH_ITEM_FIELD_NUMBER: _ClassVar[int]
    watth_seq: int
    watth_item: PowerStreamEnergyItem
    def __init__(self, watth_seq: int | None = ..., watth_item: PowerStreamEnergyItem | _Mapping | None = ...) -> None: ...

class PowerStreamBatchEnergyTotalReport(_message.Message):
    __slots__ = ("watth_item", "watth_seq")
    WATTH_SEQ_FIELD_NUMBER: _ClassVar[int]
    WATTH_ITEM_FIELD_NUMBER: _ClassVar[int]
    watth_seq: int
    watth_item: _containers.RepeatedCompositeFieldContainer[PowerStreamEnergyItem]
    def __init__(self, watth_seq: int | None = ..., watth_item: _Iterable[PowerStreamEnergyItem | _Mapping] | None = ...) -> None: ...

class PowerStreamEnergyTotalReportAck(_message.Message):
    __slots__ = ("result", "watth_seq", "watth_type")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    WATTH_SEQ_FIELD_NUMBER: _ClassVar[int]
    WATTH_TYPE_FIELD_NUMBER: _ClassVar[int]
    result: int
    watth_seq: int
    watth_type: int
    def __init__(self, result: int | None = ..., watth_seq: int | None = ..., watth_type: int | None = ...) -> None: ...

class PowerStreamEventRecordItem(_message.Message):
    __slots__ = ("event_detail", "event_no", "sys_ms", "timestamp")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SYS_MS_FIELD_NUMBER: _ClassVar[int]
    EVENT_NO_FIELD_NUMBER: _ClassVar[int]
    EVENT_DETAIL_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    sys_ms: int
    event_no: int
    event_detail: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, timestamp: int | None = ..., sys_ms: int | None = ..., event_no: int | None = ..., event_detail: _Iterable[float] | None = ...) -> None: ...

class PowerStreamEventRecordReport(_message.Message):
    __slots__ = ("event_item", "event_seq", "event_ver")
    EVENT_VER_FIELD_NUMBER: _ClassVar[int]
    EVENT_SEQ_FIELD_NUMBER: _ClassVar[int]
    EVENT_ITEM_FIELD_NUMBER: _ClassVar[int]
    event_ver: int
    event_seq: int
    event_item: _containers.RepeatedCompositeFieldContainer[PowerStreamEventRecordItem]
    def __init__(self, event_ver: int | None = ..., event_seq: int | None = ..., event_item: _Iterable[PowerStreamEventRecordItem | _Mapping] | None = ...) -> None: ...

class PowerStreamEventInfoReportAck(_message.Message):
    __slots__ = ("event_item_num", "event_seq", "result")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    EVENT_SEQ_FIELD_NUMBER: _ClassVar[int]
    EVENT_ITEM_NUM_FIELD_NUMBER: _ClassVar[int]
    result: int
    event_seq: int
    event_item_num: int
    def __init__(self, result: int | None = ..., event_seq: int | None = ..., event_item_num: int | None = ...) -> None: ...

class PowerStreamProductNameSet(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: str | None = ...) -> None: ...

class PowerStreamProductNameSetAck(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: int
    def __init__(self, result: int | None = ...) -> None: ...

class PowerStreamProductNameGet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PowerStreamProductNameGetAck(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: str | None = ...) -> None: ...

class PowerStreamRTCTimeGet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PowerStreamRTCTimeGetAck(_message.Message):
    __slots__ = ("timestamp", "timezone")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    timezone: int
    def __init__(self, timestamp: int | None = ..., timezone: int | None = ...) -> None: ...

class PowerStreamRTCTimeSet(_message.Message):
    __slots__ = ("timestamp", "timezone")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    timezone: int
    def __init__(self, timestamp: int | None = ..., timezone: int | None = ...) -> None: ...

class PowerStreamRTCTimeSetAck(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: int
    def __init__(self, result: int | None = ...) -> None: ...

class PowerStreamCountryTownMessage(_message.Message):
    __slots__ = ("country", "town")
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    TOWN_FIELD_NUMBER: _ClassVar[int]
    country: int
    town: int
    def __init__(self, country: int | None = ..., town: int | None = ...) -> None: ...
