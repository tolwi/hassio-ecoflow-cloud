from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class SmartMeterRuntimePropertyUpload(_message.Message):
    __slots__ = ("display_property_full_upload_period", "display_property_incremental_upload_period", "runtime_property_full_upload_period", "runtime_property_incremental_upload_period")
    DISPLAY_PROPERTY_FULL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_PROPERTY_INCREMENTAL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_PROPERTY_FULL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_PROPERTY_INCREMENTAL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    display_property_full_upload_period: int
    display_property_incremental_upload_period: int
    runtime_property_full_upload_period: int
    runtime_property_incremental_upload_period: int
    def __init__(self, display_property_full_upload_period: int | None = ..., display_property_incremental_upload_period: int | None = ..., runtime_property_full_upload_period: int | None = ..., runtime_property_incremental_upload_period: int | None = ...) -> None: ...

class SmartMeterDisplayPropertyUpload(_message.Message):
    __slots__ = ("currentL1", "currentL2", "currentL3", "energy", "powerL1", "powerL2", "powerL3", "totalPower", "unknown618", "unknown619", "unknown627", "unknown728", "unknown729", "unknown732", "unknown733", "unknown762", "unknown763", "unknown764", "utc_set_mode", "utc_timezone", "utc_timezone_id", "voltageL1", "voltageL2", "voltageL3")
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
    CURRENTL1_FIELD_NUMBER: _ClassVar[int]
    VOLTAGEL1_FIELD_NUMBER: _ClassVar[int]
    VOLTAGEL2_FIELD_NUMBER: _ClassVar[int]
    CURRENTL3_FIELD_NUMBER: _ClassVar[int]
    CURRENTL2_FIELD_NUMBER: _ClassVar[int]
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
    energy: SmartMeterEnergyArray
    currentL1: float
    voltageL1: float
    voltageL2: float
    currentL3: float
    currentL2: float
    powerL1: float
    powerL2: float
    def __init__(self, utc_timezone: int | None = ..., utc_timezone_id: str | None = ..., utc_set_mode: int | None = ..., totalPower: float | None = ..., unknown618: float | None = ..., unknown619: int | None = ..., unknown627: _Iterable[str] | None = ..., unknown728: _Iterable[str] | None = ..., unknown729: int | None = ..., unknown732: int | None = ..., unknown733: int | None = ..., unknown762: int | None = ..., unknown763: int | None = ..., unknown764: int | None = ..., voltageL3: float | None = ..., powerL3: float | None = ..., energy: SmartMeterEnergyArray | _Mapping | None = ..., currentL1: float | None = ..., voltageL1: float | None = ..., voltageL2: float | None = ..., currentL3: float | None = ..., currentL2: float | None = ..., powerL1: float | None = ..., powerL2: float | None = ...) -> None: ...

class SmartMeterEnergyArray(_message.Message):
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
    def __init__(self, energyL1daily: float | None = ..., energyL2daily: float | None = ..., energyL3daily: float | None = ..., lifeTimeEnergyConsumption: float | None = ..., lifeTimeEnergyDelivery: float | None = ..., netEnergyConsumption: float | None = ...) -> None: ...

class SmartMeterSetMessage(_message.Message):
    __slots__ = ("msg",)
    MSG_FIELD_NUMBER: _ClassVar[int]
    msg: _containers.RepeatedCompositeFieldContainer[SmartMeterSetHeader]
    def __init__(self, msg: _Iterable[SmartMeterSetHeader | _Mapping] | None = ...) -> None: ...

class SmartMeterSetValue(_message.Message):
    __slots__ = ("value", "value2")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    VALUE2_FIELD_NUMBER: _ClassVar[int]
    value: int
    value2: int
    def __init__(self, value: int | None = ..., value2: int | None = ...) -> None: ...

class SmartMeterSetHeader(_message.Message):
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

class SmartMeterSentDisplayPropertyUpload(_message.Message):
    __slots__ = ("header",)
    HEADER_FIELD_NUMBER: _ClassVar[int]
    header: SmartMeterSetHeader3
    def __init__(self, header: SmartMeterSetHeader3 | _Mapping | None = ...) -> None: ...

class SmartMeterSentRuntimePropertyUpload(_message.Message):
    __slots__ = ("header",)
    HEADER_FIELD_NUMBER: _ClassVar[int]
    header: SmartMeterSetHeader4
    def __init__(self, header: SmartMeterSetHeader4 | _Mapping | None = ...) -> None: ...

class SmartMeterSetHeader4(_message.Message):
    __slots__ = ("cmd_func", "cmd_id", "d_dest", "d_src", "data_len", "dest", "is_ack", "need_ack", "payload_ver", "pdata", "product_id", "seq", "src", "version")
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
    pdata: bytes
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
    def __init__(self, pdata: bytes | None = ..., src: int | None = ..., dest: int | None = ..., d_src: int | None = ..., d_dest: int | None = ..., cmd_func: int | None = ..., cmd_id: int | None = ..., data_len: int | None = ..., need_ack: int | None = ..., is_ack: int | None = ..., seq: int | None = ..., product_id: int | None = ..., version: int | None = ..., payload_ver: int | None = ...) -> None: ...

class SmartMeterSetHeader3(_message.Message):
    __slots__ = ("cmd_func", "cmd_id", "d_dest", "d_src", "data_len", "dest", "is_ack", "need_ack", "payload_ver", "pdata", "product_id", "seq", "src", "version")
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
    pdata: bytes
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
    def __init__(self, pdata: bytes | None = ..., src: int | None = ..., dest: int | None = ..., d_src: int | None = ..., d_dest: int | None = ..., cmd_func: int | None = ..., cmd_id: int | None = ..., data_len: int | None = ..., need_ack: int | None = ..., is_ack: int | None = ..., seq: int | None = ..., product_id: int | None = ..., version: int | None = ..., payload_ver: int | None = ...) -> None: ...
