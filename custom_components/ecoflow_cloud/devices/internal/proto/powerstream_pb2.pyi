from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

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
    __slots__ = ("pdata", "src", "dest", "d_src", "d_dest", "enc_type", "check_type", "cmd_func", "cmd_id", "data_len", "need_ack", "is_ack", "seq", "product_id", "version", "payload_ver", "time_snap", "is_rw_cmd", "is_queue", "ack_type", "code", "module_sn", "device_sn")
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
    FROM_FIELD_NUMBER: _ClassVar[int]
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
    module_sn: str
    device_sn: str
    def __init__(self, pdata: _Optional[bytes] = ..., src: _Optional[int] = ..., dest: _Optional[int] = ..., d_src: _Optional[int] = ..., d_dest: _Optional[int] = ..., enc_type: _Optional[int] = ..., check_type: _Optional[int] = ..., cmd_func: _Optional[int] = ..., cmd_id: _Optional[int] = ..., data_len: _Optional[int] = ..., need_ack: _Optional[int] = ..., is_ack: _Optional[int] = ..., seq: _Optional[int] = ..., product_id: _Optional[int] = ..., version: _Optional[int] = ..., payload_ver: _Optional[int] = ..., time_snap: _Optional[int] = ..., is_rw_cmd: _Optional[int] = ..., is_queue: _Optional[int] = ..., ack_type: _Optional[int] = ..., code: _Optional[str] = ..., module_sn: _Optional[str] = ..., device_sn: _Optional[str] = ..., **kwargs) -> None: ...

class PowerStreamSendHeaderMsg(_message.Message):
    __slots__ = ("msg",)
    MSG_FIELD_NUMBER: _ClassVar[int]
    msg: _containers.RepeatedCompositeFieldContainer[PowerStreamHeader]
    def __init__(self, msg: _Optional[_Iterable[_Union[PowerStreamHeader, _Mapping]]] = ...) -> None: ...

class PowerStreamInverterHeartbeat(_message.Message):
    __slots__ = ("inv_error_code", "inv_warning_code", "pv1_error_code", "pv1_warning_code", "pv2_error_code", "pv2_warning_code", "bat_error_code", "bat_warning_code", "llc_error_code", "llc_warning_code", "pv1_statue", "pv2_statue", "bat_statue", "llc_statue", "inv_statue", "pv1_input_volt", "pv1_op_volt", "pv1_input_cur", "pv1_input_watts", "pv1_temp", "pv2_input_volt", "pv2_op_volt", "pv2_input_cur", "pv2_input_watts", "pv2_temp", "bat_input_volt", "bat_op_volt", "bat_input_cur", "bat_input_watts", "bat_temp", "bat_soc", "llc_input_volt", "llc_op_volt", "llc_temp", "inv_input_volt", "inv_op_volt", "inv_output_cur", "inv_output_watts", "inv_temp", "inv_freq", "inv_dc_cur", "bp_type", "inv_relay_status", "pv1_relay_status", "pv2_relay_status", "install_country", "install_town", "permanent_watts", "dynamic_watts", "supply_priority", "lower_limit", "upper_limit", "inv_on_off", "wireless_error_code", "wireless_warning_code", "inv_brightness", "heartbeat_frequency", "rated_power", "chg_remain_time", "dsg_remain_time", "feed_protect")
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
    def __init__(self, inv_error_code: _Optional[int] = ..., inv_warning_code: _Optional[int] = ..., pv1_error_code: _Optional[int] = ..., pv1_warning_code: _Optional[int] = ..., pv2_error_code: _Optional[int] = ..., pv2_warning_code: _Optional[int] = ..., bat_error_code: _Optional[int] = ..., bat_warning_code: _Optional[int] = ..., llc_error_code: _Optional[int] = ..., llc_warning_code: _Optional[int] = ..., pv1_statue: _Optional[int] = ..., pv2_statue: _Optional[int] = ..., bat_statue: _Optional[int] = ..., llc_statue: _Optional[int] = ..., inv_statue: _Optional[int] = ..., pv1_input_volt: _Optional[int] = ..., pv1_op_volt: _Optional[int] = ..., pv1_input_cur: _Optional[int] = ..., pv1_input_watts: _Optional[int] = ..., pv1_temp: _Optional[int] = ..., pv2_input_volt: _Optional[int] = ..., pv2_op_volt: _Optional[int] = ..., pv2_input_cur: _Optional[int] = ..., pv2_input_watts: _Optional[int] = ..., pv2_temp: _Optional[int] = ..., bat_input_volt: _Optional[int] = ..., bat_op_volt: _Optional[int] = ..., bat_input_cur: _Optional[int] = ..., bat_input_watts: _Optional[int] = ..., bat_temp: _Optional[int] = ..., bat_soc: _Optional[int] = ..., llc_input_volt: _Optional[int] = ..., llc_op_volt: _Optional[int] = ..., llc_temp: _Optional[int] = ..., inv_input_volt: _Optional[int] = ..., inv_op_volt: _Optional[int] = ..., inv_output_cur: _Optional[int] = ..., inv_output_watts: _Optional[int] = ..., inv_temp: _Optional[int] = ..., inv_freq: _Optional[int] = ..., inv_dc_cur: _Optional[int] = ..., bp_type: _Optional[int] = ..., inv_relay_status: _Optional[int] = ..., pv1_relay_status: _Optional[int] = ..., pv2_relay_status: _Optional[int] = ..., install_country: _Optional[int] = ..., install_town: _Optional[int] = ..., permanent_watts: _Optional[int] = ..., dynamic_watts: _Optional[int] = ..., supply_priority: _Optional[int] = ..., lower_limit: _Optional[int] = ..., upper_limit: _Optional[int] = ..., inv_on_off: _Optional[int] = ..., wireless_error_code: _Optional[int] = ..., wireless_warning_code: _Optional[int] = ..., inv_brightness: _Optional[int] = ..., heartbeat_frequency: _Optional[int] = ..., rated_power: _Optional[int] = ..., chg_remain_time: _Optional[int] = ..., dsg_remain_time: _Optional[int] = ..., feed_protect: _Optional[int] = ...) -> None: ...

class PowerStreamPermanentWattsPack(_message.Message):
    __slots__ = ("permanent_watts",)
    PERMANENT_WATTS_FIELD_NUMBER: _ClassVar[int]
    permanent_watts: int
    def __init__(self, permanent_watts: _Optional[int] = ...) -> None: ...

class PowerStreamSupplyPriorityPack(_message.Message):
    __slots__ = ("supply_priority",)
    SUPPLY_PRIORITY_FIELD_NUMBER: _ClassVar[int]
    supply_priority: int
    def __init__(self, supply_priority: _Optional[int] = ...) -> None: ...

class PowerStreamBatLowerPack(_message.Message):
    __slots__ = ("lower_limit",)
    LOWER_LIMIT_FIELD_NUMBER: _ClassVar[int]
    lower_limit: int
    def __init__(self, lower_limit: _Optional[int] = ...) -> None: ...

class PowerStreamBatUpperPack(_message.Message):
    __slots__ = ("upper_limit",)
    UPPER_LIMIT_FIELD_NUMBER: _ClassVar[int]
    upper_limit: int
    def __init__(self, upper_limit: _Optional[int] = ...) -> None: ...

class PowerStreamBrightnessPack(_message.Message):
    __slots__ = ("brightness",)
    BRIGHTNESS_FIELD_NUMBER: _ClassVar[int]
    brightness: int
    def __init__(self, brightness: _Optional[int] = ...) -> None: ...

class PowerStreamPowerItem(_message.Message):
    __slots__ = ("timestamp", "timezone", "inv_to_grid_power", "inv_to_plug_power", "battery_power", "pv1_output_power", "pv2_output_power")
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
    def __init__(self, timestamp: _Optional[int] = ..., timezone: _Optional[int] = ..., inv_to_grid_power: _Optional[int] = ..., inv_to_plug_power: _Optional[int] = ..., battery_power: _Optional[int] = ..., pv1_output_power: _Optional[int] = ..., pv2_output_power: _Optional[int] = ...) -> None: ...

class PowerStreamPowerPack(_message.Message):
    __slots__ = ("sys_seq", "sys_power_stream")
    SYS_SEQ_FIELD_NUMBER: _ClassVar[int]
    SYS_POWER_STREAM_FIELD_NUMBER: _ClassVar[int]
    sys_seq: int
    sys_power_stream: _containers.RepeatedCompositeFieldContainer[PowerStreamPowerItem]
    def __init__(self, sys_seq: _Optional[int] = ..., sys_power_stream: _Optional[_Iterable[_Union[PowerStreamPowerItem, _Mapping]]] = ...) -> None: ...

class PowerStreamPowerAckPack(_message.Message):
    __slots__ = ("sys_seq",)
    SYS_SEQ_FIELD_NUMBER: _ClassVar[int]
    sys_seq: int
    def __init__(self, sys_seq: _Optional[int] = ...) -> None: ...

class PowerStreamNodeMessage(_message.Message):
    __slots__ = ("sn", "mac")
    SN_FIELD_NUMBER: _ClassVar[int]
    MAC_FIELD_NUMBER: _ClassVar[int]
    sn: str
    mac: bytes
    def __init__(self, sn: _Optional[str] = ..., mac: _Optional[bytes] = ...) -> None: ...

class PowerStreamMeshChildNodeInfo(_message.Message):
    __slots__ = ("topology_type", "mesh_protocol", "max_sub_device_num", "parent_mac_id", "mesh_id", "sub_device_list")
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
    def __init__(self, topology_type: _Optional[int] = ..., mesh_protocol: _Optional[int] = ..., max_sub_device_num: _Optional[int] = ..., parent_mac_id: _Optional[bytes] = ..., mesh_id: _Optional[bytes] = ..., sub_device_list: _Optional[_Iterable[_Union[PowerStreamNodeMessage, _Mapping]]] = ...) -> None: ...

class PowerStreamSetValue(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class PowerStreamEnergyItem(_message.Message):
    __slots__ = ("timestamp", "watth_type", "watth")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    WATTH_TYPE_FIELD_NUMBER: _ClassVar[int]
    WATTH_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    watth_type: int
    watth: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, timestamp: _Optional[int] = ..., watth_type: _Optional[int] = ..., watth: _Optional[_Iterable[int]] = ...) -> None: ...

class PowerStreamEnergyTotalReport(_message.Message):
    __slots__ = ("watth_seq", "watth_item")
    WATTH_SEQ_FIELD_NUMBER: _ClassVar[int]
    WATTH_ITEM_FIELD_NUMBER: _ClassVar[int]
    watth_seq: int
    watth_item: PowerStreamEnergyItem
    def __init__(self, watth_seq: _Optional[int] = ..., watth_item: _Optional[_Union[PowerStreamEnergyItem, _Mapping]] = ...) -> None: ...

class PowerStreamBatchEnergyTotalReport(_message.Message):
    __slots__ = ("watth_seq", "watth_item")
    WATTH_SEQ_FIELD_NUMBER: _ClassVar[int]
    WATTH_ITEM_FIELD_NUMBER: _ClassVar[int]
    watth_seq: int
    watth_item: _containers.RepeatedCompositeFieldContainer[PowerStreamEnergyItem]
    def __init__(self, watth_seq: _Optional[int] = ..., watth_item: _Optional[_Iterable[_Union[PowerStreamEnergyItem, _Mapping]]] = ...) -> None: ...

class PowerStreamEnergyTotalReportAck(_message.Message):
    __slots__ = ("result", "watth_seq", "watth_type")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    WATTH_SEQ_FIELD_NUMBER: _ClassVar[int]
    WATTH_TYPE_FIELD_NUMBER: _ClassVar[int]
    result: int
    watth_seq: int
    watth_type: int
    def __init__(self, result: _Optional[int] = ..., watth_seq: _Optional[int] = ..., watth_type: _Optional[int] = ...) -> None: ...

class PowerStreamEventRecordItem(_message.Message):
    __slots__ = ("timestamp", "sys_ms", "event_no", "event_detail")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SYS_MS_FIELD_NUMBER: _ClassVar[int]
    EVENT_NO_FIELD_NUMBER: _ClassVar[int]
    EVENT_DETAIL_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    sys_ms: int
    event_no: int
    event_detail: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, timestamp: _Optional[int] = ..., sys_ms: _Optional[int] = ..., event_no: _Optional[int] = ..., event_detail: _Optional[_Iterable[float]] = ...) -> None: ...

class PowerStreamEventRecordReport(_message.Message):
    __slots__ = ("event_ver", "event_seq", "event_item")
    EVENT_VER_FIELD_NUMBER: _ClassVar[int]
    EVENT_SEQ_FIELD_NUMBER: _ClassVar[int]
    EVENT_ITEM_FIELD_NUMBER: _ClassVar[int]
    event_ver: int
    event_seq: int
    event_item: _containers.RepeatedCompositeFieldContainer[PowerStreamEventRecordItem]
    def __init__(self, event_ver: _Optional[int] = ..., event_seq: _Optional[int] = ..., event_item: _Optional[_Iterable[_Union[PowerStreamEventRecordItem, _Mapping]]] = ...) -> None: ...

class PowerStreamEventInfoReportAck(_message.Message):
    __slots__ = ("result", "event_seq", "event_item_num")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    EVENT_SEQ_FIELD_NUMBER: _ClassVar[int]
    EVENT_ITEM_NUM_FIELD_NUMBER: _ClassVar[int]
    result: int
    event_seq: int
    event_item_num: int
    def __init__(self, result: _Optional[int] = ..., event_seq: _Optional[int] = ..., event_item_num: _Optional[int] = ...) -> None: ...

class PowerStreamProductNameSet(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class PowerStreamProductNameSetAck(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: int
    def __init__(self, result: _Optional[int] = ...) -> None: ...

class PowerStreamProductNameGet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PowerStreamProductNameGetAck(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class PowerStreamRTCTimeGet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PowerStreamRTCTimeGetAck(_message.Message):
    __slots__ = ("timestamp", "timezone")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    timezone: int
    def __init__(self, timestamp: _Optional[int] = ..., timezone: _Optional[int] = ...) -> None: ...

class PowerStreamRTCTimeSet(_message.Message):
    __slots__ = ("timestamp", "timezone")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    timezone: int
    def __init__(self, timestamp: _Optional[int] = ..., timezone: _Optional[int] = ...) -> None: ...

class PowerStreamRTCTimeSetAck(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: int
    def __init__(self, result: _Optional[int] = ...) -> None: ...

class PowerStreamCountryTownMessage(_message.Message):
    __slots__ = ("country", "town")
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    TOWN_FIELD_NUMBER: _ClassVar[int]
    country: int
    town: int
    def __init__(self, country: _Optional[int] = ..., town: _Optional[int] = ...) -> None: ...
