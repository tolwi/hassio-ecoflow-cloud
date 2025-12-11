from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SmartMeterHeader(_message.Message):
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

class SmartMeterSendHeaderMsg(_message.Message):
    __slots__ = ("msg",)
    MSG_FIELD_NUMBER: _ClassVar[int]
    msg: _containers.RepeatedCompositeFieldContainer[SmartMeterHeader]
    def __init__(self, msg: _Optional[_Iterable[_Union[SmartMeterHeader, _Mapping]]] = ...) -> None: ...

class RuntimePropertyUpload(_message.Message):
    __slots__ = ("display_property_full_upload_period", "display_property_incremental_upload_period", "runtime_property_full_upload_period", "runtime_property_incremental_upload_period")
    DISPLAY_PROPERTY_FULL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_PROPERTY_INCREMENTAL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_PROPERTY_FULL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_PROPERTY_INCREMENTAL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    display_property_full_upload_period: int
    display_property_incremental_upload_period: int
    runtime_property_full_upload_period: int
    runtime_property_incremental_upload_period: int
    def __init__(self, display_property_full_upload_period: _Optional[int] = ..., display_property_incremental_upload_period: _Optional[int] = ..., runtime_property_full_upload_period: _Optional[int] = ..., runtime_property_incremental_upload_period: _Optional[int] = ...) -> None: ...

class DisplayPropertyUpload(_message.Message):
    __slots__ = ("utc_timezone", "utc_timezone_id", "utc_set_mode", "totalPower", "unknown618", "unknown619", "unknown627", "unknown728", "unknown729", "unknown732", "unknown733", "unknown762", "unknown763", "unknown764", "voltageL3", "powerL3", "energy", "voltageL1", "voltageL2", "powerL1", "powerL2")
    UTC_TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    UTC_TIMEZONE_ID_FIELD_NUMBER: _ClassVar[int]
    UTC_SET_MODE_FIELD_NUMBER: _ClassVar[int]
    TOTALPOWER_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN618_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN619_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN627_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN728_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN729_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN732_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN733_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN762_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN763_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN764_FIELD_NUMBER: _ClassVar[int]
    VOLTAGEL3_FIELD_NUMBER: _ClassVar[int]
    POWERL3_FIELD_NUMBER: _ClassVar[int]
    ENERGY_FIELD_NUMBER: _ClassVar[int]
    VOLTAGEL1_FIELD_NUMBER: _ClassVar[int]
    VOLTAGEL2_FIELD_NUMBER: _ClassVar[int]
    POWERL1_FIELD_NUMBER: _ClassVar[int]
    POWERL2_FIELD_NUMBER: _ClassVar[int]
    utc_timezone: int
    utc_timezone_id: str
    utc_set_mode: int
    totalPower: float
    unknown618: float
    unknown619: int
    unknown627: _containers.RepeatedScalarFieldContainer[str]
    unknown728: _containers.RepeatedScalarFieldContainer[str]
    unknown729: int
    unknown732: int
    unknown733: int
    unknown762: int
    unknown763: int
    unknown764: int
    voltageL3: float
    powerL3: float
    energy: EnergyArray
    voltageL1: float
    voltageL2: float
    powerL1: float
    powerL2: float
    def __init__(self, utc_timezone: _Optional[int] = ..., utc_timezone_id: _Optional[str] = ..., utc_set_mode: _Optional[int] = ..., totalPower: _Optional[float] = ..., unknown618: _Optional[float] = ..., unknown619: _Optional[int] = ..., unknown627: _Optional[_Iterable[str]] = ..., unknown728: _Optional[_Iterable[str]] = ..., unknown729: _Optional[int] = ..., unknown732: _Optional[int] = ..., unknown733: _Optional[int] = ..., unknown762: _Optional[int] = ..., unknown763: _Optional[int] = ..., unknown764: _Optional[int] = ..., voltageL3: _Optional[float] = ..., powerL3: _Optional[float] = ..., energy: _Optional[_Union[EnergyArray, _Mapping]] = ..., voltageL1: _Optional[float] = ..., voltageL2: _Optional[float] = ..., powerL1: _Optional[float] = ..., powerL2: _Optional[float] = ...) -> None: ...

class EnergyArray(_message.Message):
    __slots__ = ("energyL1daily", "energyL2daily", "energyL3daily", "lifeTimeEnergyConsumption", "lifeTimeEnergyDelivery", "netEnergyConsumption")
    ENERGYL1DAILY_FIELD_NUMBER: _ClassVar[int]
    ENERGYL2DAILY_FIELD_NUMBER: _ClassVar[int]
    ENERGYL3DAILY_FIELD_NUMBER: _ClassVar[int]
    LIFETIMEENERGYCONSUMPTION_FIELD_NUMBER: _ClassVar[int]
    LIFETIMEENERGYDELIVERY_FIELD_NUMBER: _ClassVar[int]
    NETENERGYCONSUMPTION_FIELD_NUMBER: _ClassVar[int]
    energyL1daily: float
    energyL2daily: float
    energyL3daily: float
    lifeTimeEnergyConsumption: float
    lifeTimeEnergyDelivery: float
    netEnergyConsumption: float
    def __init__(self, energyL1daily: _Optional[float] = ..., energyL2daily: _Optional[float] = ..., energyL3daily: _Optional[float] = ..., lifeTimeEnergyConsumption: _Optional[float] = ..., lifeTimeEnergyDelivery: _Optional[float] = ..., netEnergyConsumption: _Optional[float] = ...) -> None: ...

class setMessage(_message.Message):
    __slots__ = ("header",)
    HEADER_FIELD_NUMBER: _ClassVar[int]
    header: setHeader
    def __init__(self, header: _Optional[_Union[setHeader, _Mapping]] = ...) -> None: ...

class setValue(_message.Message):
    __slots__ = ("value", "value2")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    VALUE2_FIELD_NUMBER: _ClassVar[int]
    value: int
    value2: int
    def __init__(self, value: _Optional[int] = ..., value2: _Optional[int] = ...) -> None: ...

class setHeader(_message.Message):
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
    pdata: setValue
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
    def __init__(self, pdata: _Optional[_Union[setValue, _Mapping]] = ..., src: _Optional[int] = ..., dest: _Optional[int] = ..., d_src: _Optional[int] = ..., d_dest: _Optional[int] = ..., enc_type: _Optional[int] = ..., check_type: _Optional[int] = ..., cmd_func: _Optional[int] = ..., cmd_id: _Optional[int] = ..., data_len: _Optional[int] = ..., need_ack: _Optional[int] = ..., is_ack: _Optional[int] = ..., seq: _Optional[int] = ..., product_id: _Optional[int] = ..., version: _Optional[int] = ..., payload_ver: _Optional[int] = ..., time_snap: _Optional[int] = ..., is_rw_cmd: _Optional[int] = ..., is_queue: _Optional[int] = ..., ack_type: _Optional[int] = ..., code: _Optional[str] = ..., module_sn: _Optional[str] = ..., device_sn: _Optional[str] = ..., **kwargs) -> None: ...

class sentDisplayPropertyUpload(_message.Message):
    __slots__ = ("header",)
    HEADER_FIELD_NUMBER: _ClassVar[int]
    header: setHeader3
    def __init__(self, header: _Optional[_Union[setHeader3, _Mapping]] = ...) -> None: ...

class sentRuntimePropertyUpload(_message.Message):
    __slots__ = ("header",)
    HEADER_FIELD_NUMBER: _ClassVar[int]
    header: setHeader4
    def __init__(self, header: _Optional[_Union[setHeader4, _Mapping]] = ...) -> None: ...

class setHeader4(_message.Message):
    __slots__ = ("pdata", "src", "dest", "d_src", "d_dest", "cmd_func", "cmd_id", "data_len", "need_ack", "is_ack", "seq", "product_id", "version", "payload_ver")
    PDATA_FIELD_NUMBER: _ClassVar[int]
    SRC_FIELD_NUMBER: _ClassVar[int]
    DEST_FIELD_NUMBER: _ClassVar[int]
    D_SRC_FIELD_NUMBER: _ClassVar[int]
    D_DEST_FIELD_NUMBER: _ClassVar[int]
    CMD_FUNC_FIELD_NUMBER: _ClassVar[int]
    CMD_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_LEN_FIELD_NUMBER: _ClassVar[int]
    NEED_ACK_FIELD_NUMBER: _ClassVar[int]
    IS_ACK_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_VER_FIELD_NUMBER: _ClassVar[int]
    pdata: RuntimePropertyUpload
    src: int
    dest: int
    d_src: int
    d_dest: int
    cmd_func: int
    cmd_id: int
    data_len: int
    need_ack: int
    is_ack: int
    seq: int
    product_id: int
    version: int
    payload_ver: int
    def __init__(self, pdata: _Optional[_Union[RuntimePropertyUpload, _Mapping]] = ..., src: _Optional[int] = ..., dest: _Optional[int] = ..., d_src: _Optional[int] = ..., d_dest: _Optional[int] = ..., cmd_func: _Optional[int] = ..., cmd_id: _Optional[int] = ..., data_len: _Optional[int] = ..., need_ack: _Optional[int] = ..., is_ack: _Optional[int] = ..., seq: _Optional[int] = ..., product_id: _Optional[int] = ..., version: _Optional[int] = ..., payload_ver: _Optional[int] = ...) -> None: ...

class setHeader3(_message.Message):
    __slots__ = ("pdata", "src", "dest", "d_src", "d_dest", "cmd_func", "cmd_id", "data_len", "need_ack", "is_ack", "seq", "product_id", "version", "payload_ver")
    PDATA_FIELD_NUMBER: _ClassVar[int]
    SRC_FIELD_NUMBER: _ClassVar[int]
    DEST_FIELD_NUMBER: _ClassVar[int]
    D_SRC_FIELD_NUMBER: _ClassVar[int]
    D_DEST_FIELD_NUMBER: _ClassVar[int]
    CMD_FUNC_FIELD_NUMBER: _ClassVar[int]
    CMD_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_LEN_FIELD_NUMBER: _ClassVar[int]
    NEED_ACK_FIELD_NUMBER: _ClassVar[int]
    IS_ACK_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_VER_FIELD_NUMBER: _ClassVar[int]
    pdata: DisplayPropertyUpload
    src: int
    dest: int
    d_src: int
    d_dest: int
    cmd_func: int
    cmd_id: int
    data_len: int
    need_ack: int
    is_ack: int
    seq: int
    product_id: int
    version: int
    payload_ver: int
    def __init__(self, pdata: _Optional[_Union[DisplayPropertyUpload, _Mapping]] = ..., src: _Optional[int] = ..., dest: _Optional[int] = ..., d_src: _Optional[int] = ..., d_dest: _Optional[int] = ..., cmd_func: _Optional[int] = ..., cmd_id: _Optional[int] = ..., data_len: _Optional[int] = ..., need_ack: _Optional[int] = ..., is_ack: _Optional[int] = ..., seq: _Optional[int] = ..., product_id: _Optional[int] = ..., version: _Optional[int] = ..., payload_ver: _Optional[int] = ...) -> None: ...
