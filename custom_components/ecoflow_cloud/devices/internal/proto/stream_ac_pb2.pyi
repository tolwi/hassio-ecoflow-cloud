from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StreamACHeader(_message.Message):
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

class StreamACSendHeaderMsg(_message.Message):
    __slots__ = ("msg",)
    MSG_FIELD_NUMBER: _ClassVar[int]
    msg: StreamACHeader
    def __init__(self, msg: _Optional[_Union[StreamACHeader, _Mapping]] = ...) -> None: ...

class StreamACChamp_cmd50_4(_message.Message):
    __slots__ = ("Champ_cmd50_4_field1",)
    CHAMP_CMD50_4_FIELD1_FIELD_NUMBER: _ClassVar[int]
    Champ_cmd50_4_field1: int
    def __init__(self, Champ_cmd50_4_field1: _Optional[int] = ...) -> None: ...

class StreamACChamp_cmd50_3(_message.Message):
    __slots__ = ("Champ_cmd50_3_field1", "Champ_cmd50_3_field2", "Champ_cmd50_3_field3", "Champ_cmd50_3_field4", "Champ_cmd50_3_field5", "Champ_cmd50_3_field6", "Champ_cmd50_3_field7", "Champ_cmd50_3_field8", "Champ_cmd50_3_field9", "Champ_cmd50_3_field10", "Champ_cmd50_3_field11", "Champ_cmd50_3_field12", "Champ_cmd50_3_field13", "Champ_cmd50_3_field14", "Champ_cmd50_3_field15", "Champ_cmd50_3_field16", "Champ_cmd50_3_field17", "Champ_cmd50_3_field18", "Champ_cmd50_3_field19", "Champ_cmd50_3_field20", "Champ_cmd50_3_field21", "Champ_cmd50_3_field22", "Champ_cmd50_3_field23", "Champ_cmd50_3_field24", "Champ_cmd50_3_field25", "Champ_cmd50_3_field26", "Champ_cmd50_3_field27", "Champ_cmd50_3_field28", "Champ_cmd50_3_field29", "Champ_cmd50_3_field30", "Champ_cmd50_3_field31", "Champ_cmd50_3_field32", "Champ_cmd50_3_field33", "Champ_cmd50_3_field34", "Champ_cmd50_3_filed35", "version", "Champ_cmd50_3_field37", "Champ_cmd50_3_field38", "sn1", "Champ_cmd50_3_field40", "Champ_cmd50_3_field41", "Champ_cmd50_3_field42", "Champ_cmd50_3_field43", "Champ_cmd50_3_field44", "Champ_cmd50_3_field45", "Champ_cmd50_3_field46", "Champ_cmd50_3_field47", "Champ_cmd50_3_field48", "Champ_cmd50_3_field49", "Champ_cmd50_3_field50", "Champ_cmd50_3_field51", "Champ_cmd50_3_field52", "Champ_cmd50_3_field53", "Champ_cmd50_3_field54", "Champ_cmd50_3_field55", "Champ_cmd50_3_field56", "Champ_cmd50_3_field57", "Champ_cmd50_3_field58", "Champ_cmd50_3_field59", "Champ_cmd50_3_field60", "Champ_cmd50_3_field61", "Champ_cmd50_3_field65", "Champ_cmd50_3_field66", "Champ_cmd50_3_field67", "Champ_cmd50_3_field68", "Champ_cmd50_3_field69", "Champ_cmd50_3_sn", "Champ_cmd50_3_field71", "Champ_cmd50_3_field72", "Champ_cmd50_3_field73", "Champ_cmd50_3_field74", "Champ_cmd50_3_field75", "Champ_cmd50_3_field76", "Champ_cmd50_3_field77", "Champ_cmd50_3_field78", "Champ_cmd50_3_field79", "Champ_cmd50_3_field80", "sn2", "Champ_cmd50_3_field82")
    CHAMP_CMD50_3_FIELD1_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD2_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD3_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD4_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD5_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD6_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD7_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD8_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD9_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD10_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD11_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD12_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD13_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD14_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD15_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD16_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD17_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD18_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD19_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD20_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD21_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD22_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD23_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD24_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD25_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD26_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD27_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD28_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD29_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD30_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD31_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD32_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD33_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD34_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FILED35_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD37_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD38_FIELD_NUMBER: _ClassVar[int]
    SN1_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD40_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD41_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD42_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD43_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD44_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD45_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD46_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD47_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD48_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD49_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD50_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD51_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD52_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD53_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD54_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD55_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD56_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD57_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD58_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD59_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD60_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD61_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD65_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD66_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD67_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD68_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD69_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_SN_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD71_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD72_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD73_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD74_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD75_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD76_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD77_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD78_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD79_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD80_FIELD_NUMBER: _ClassVar[int]
    SN2_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_3_FIELD82_FIELD_NUMBER: _ClassVar[int]
    Champ_cmd50_3_field1: int
    Champ_cmd50_3_field2: int
    Champ_cmd50_3_field3: int
    Champ_cmd50_3_field4: int
    Champ_cmd50_3_field5: int
    Champ_cmd50_3_field6: int
    Champ_cmd50_3_field7: int
    Champ_cmd50_3_field8: int
    Champ_cmd50_3_field9: int
    Champ_cmd50_3_field10: int
    Champ_cmd50_3_field11: int
    Champ_cmd50_3_field12: int
    Champ_cmd50_3_field13: int
    Champ_cmd50_3_field14: int
    Champ_cmd50_3_field15: int
    Champ_cmd50_3_field16: int
    Champ_cmd50_3_field17: int
    Champ_cmd50_3_field18: int
    Champ_cmd50_3_field19: int
    Champ_cmd50_3_field20: int
    Champ_cmd50_3_field21: int
    Champ_cmd50_3_field22: int
    Champ_cmd50_3_field23: int
    Champ_cmd50_3_field24: int
    Champ_cmd50_3_field25: float
    Champ_cmd50_3_field26: int
    Champ_cmd50_3_field27: int
    Champ_cmd50_3_field28: int
    Champ_cmd50_3_field29: int
    Champ_cmd50_3_field30: int
    Champ_cmd50_3_field31: int
    Champ_cmd50_3_field32: int
    Champ_cmd50_3_field33: str
    Champ_cmd50_3_field34: int
    Champ_cmd50_3_filed35: StreamACChamp_cmd50_4
    version: str
    Champ_cmd50_3_field37: int
    Champ_cmd50_3_field38: int
    sn1: str
    Champ_cmd50_3_field40: int
    Champ_cmd50_3_field41: int
    Champ_cmd50_3_field42: float
    Champ_cmd50_3_field43: float
    Champ_cmd50_3_field44: float
    Champ_cmd50_3_field45: int
    Champ_cmd50_3_field46: int
    Champ_cmd50_3_field47: int
    Champ_cmd50_3_field48: int
    Champ_cmd50_3_field49: int
    Champ_cmd50_3_field50: int
    Champ_cmd50_3_field51: int
    Champ_cmd50_3_field52: float
    Champ_cmd50_3_field53: float
    Champ_cmd50_3_field54: float
    Champ_cmd50_3_field55: int
    Champ_cmd50_3_field56: str
    Champ_cmd50_3_field57: int
    Champ_cmd50_3_field58: int
    Champ_cmd50_3_field59: int
    Champ_cmd50_3_field60: int
    Champ_cmd50_3_field61: int
    Champ_cmd50_3_field65: int
    Champ_cmd50_3_field66: int
    Champ_cmd50_3_field67: int
    Champ_cmd50_3_field68: int
    Champ_cmd50_3_field69: int
    Champ_cmd50_3_sn: str
    Champ_cmd50_3_field71: int
    Champ_cmd50_3_field72: int
    Champ_cmd50_3_field73: int
    Champ_cmd50_3_field74: int
    Champ_cmd50_3_field75: int
    Champ_cmd50_3_field76: int
    Champ_cmd50_3_field77: int
    Champ_cmd50_3_field78: int
    Champ_cmd50_3_field79: int
    Champ_cmd50_3_field80: int
    sn2: str
    Champ_cmd50_3_field82: int
    def __init__(self, Champ_cmd50_3_field1: _Optional[int] = ..., Champ_cmd50_3_field2: _Optional[int] = ..., Champ_cmd50_3_field3: _Optional[int] = ..., Champ_cmd50_3_field4: _Optional[int] = ..., Champ_cmd50_3_field5: _Optional[int] = ..., Champ_cmd50_3_field6: _Optional[int] = ..., Champ_cmd50_3_field7: _Optional[int] = ..., Champ_cmd50_3_field8: _Optional[int] = ..., Champ_cmd50_3_field9: _Optional[int] = ..., Champ_cmd50_3_field10: _Optional[int] = ..., Champ_cmd50_3_field11: _Optional[int] = ..., Champ_cmd50_3_field12: _Optional[int] = ..., Champ_cmd50_3_field13: _Optional[int] = ..., Champ_cmd50_3_field14: _Optional[int] = ..., Champ_cmd50_3_field15: _Optional[int] = ..., Champ_cmd50_3_field16: _Optional[int] = ..., Champ_cmd50_3_field17: _Optional[int] = ..., Champ_cmd50_3_field18: _Optional[int] = ..., Champ_cmd50_3_field19: _Optional[int] = ..., Champ_cmd50_3_field20: _Optional[int] = ..., Champ_cmd50_3_field21: _Optional[int] = ..., Champ_cmd50_3_field22: _Optional[int] = ..., Champ_cmd50_3_field23: _Optional[int] = ..., Champ_cmd50_3_field24: _Optional[int] = ..., Champ_cmd50_3_field25: _Optional[float] = ..., Champ_cmd50_3_field26: _Optional[int] = ..., Champ_cmd50_3_field27: _Optional[int] = ..., Champ_cmd50_3_field28: _Optional[int] = ..., Champ_cmd50_3_field29: _Optional[int] = ..., Champ_cmd50_3_field30: _Optional[int] = ..., Champ_cmd50_3_field31: _Optional[int] = ..., Champ_cmd50_3_field32: _Optional[int] = ..., Champ_cmd50_3_field33: _Optional[str] = ..., Champ_cmd50_3_field34: _Optional[int] = ..., Champ_cmd50_3_filed35: _Optional[_Union[StreamACChamp_cmd50_4, _Mapping]] = ..., version: _Optional[str] = ..., Champ_cmd50_3_field37: _Optional[int] = ..., Champ_cmd50_3_field38: _Optional[int] = ..., sn1: _Optional[str] = ..., Champ_cmd50_3_field40: _Optional[int] = ..., Champ_cmd50_3_field41: _Optional[int] = ..., Champ_cmd50_3_field42: _Optional[float] = ..., Champ_cmd50_3_field43: _Optional[float] = ..., Champ_cmd50_3_field44: _Optional[float] = ..., Champ_cmd50_3_field45: _Optional[int] = ..., Champ_cmd50_3_field46: _Optional[int] = ..., Champ_cmd50_3_field47: _Optional[int] = ..., Champ_cmd50_3_field48: _Optional[int] = ..., Champ_cmd50_3_field49: _Optional[int] = ..., Champ_cmd50_3_field50: _Optional[int] = ..., Champ_cmd50_3_field51: _Optional[int] = ..., Champ_cmd50_3_field52: _Optional[float] = ..., Champ_cmd50_3_field53: _Optional[float] = ..., Champ_cmd50_3_field54: _Optional[float] = ..., Champ_cmd50_3_field55: _Optional[int] = ..., Champ_cmd50_3_field56: _Optional[str] = ..., Champ_cmd50_3_field57: _Optional[int] = ..., Champ_cmd50_3_field58: _Optional[int] = ..., Champ_cmd50_3_field59: _Optional[int] = ..., Champ_cmd50_3_field60: _Optional[int] = ..., Champ_cmd50_3_field61: _Optional[int] = ..., Champ_cmd50_3_field65: _Optional[int] = ..., Champ_cmd50_3_field66: _Optional[int] = ..., Champ_cmd50_3_field67: _Optional[int] = ..., Champ_cmd50_3_field68: _Optional[int] = ..., Champ_cmd50_3_field69: _Optional[int] = ..., Champ_cmd50_3_sn: _Optional[str] = ..., Champ_cmd50_3_field71: _Optional[int] = ..., Champ_cmd50_3_field72: _Optional[int] = ..., Champ_cmd50_3_field73: _Optional[int] = ..., Champ_cmd50_3_field74: _Optional[int] = ..., Champ_cmd50_3_field75: _Optional[int] = ..., Champ_cmd50_3_field76: _Optional[int] = ..., Champ_cmd50_3_field77: _Optional[int] = ..., Champ_cmd50_3_field78: _Optional[int] = ..., Champ_cmd50_3_field79: _Optional[int] = ..., Champ_cmd50_3_field80: _Optional[int] = ..., sn2: _Optional[str] = ..., Champ_cmd50_3_field82: _Optional[int] = ...) -> None: ...

class StreamACChamp_cmd50_2(_message.Message):
    __slots__ = ("Champ_cmd50_2champ3", "Champ_cmd50_2_field1", "Champ_cmd50_2_field2", "Champ_cmd50_2_field3", "Champ_cmd50_2_field4", "Champ_cmd50_2_field5", "Champ_cmd50_2_field6", "Champ_cmd50_2_field7", "Champ_cmd50_2_field8", "Champ_cmd50_2_field9")
    CHAMP_CMD50_2CHAMP3_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_2_FIELD1_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_2_FIELD2_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_2_FIELD3_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_2_FIELD4_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_2_FIELD5_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_2_FIELD6_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_2_FIELD7_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_2_FIELD8_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD50_2_FIELD9_FIELD_NUMBER: _ClassVar[int]
    Champ_cmd50_2champ3: StreamACChamp_cmd50_3
    Champ_cmd50_2_field1: bytes
    Champ_cmd50_2_field2: int
    Champ_cmd50_2_field3: int
    Champ_cmd50_2_field4: int
    Champ_cmd50_2_field5: int
    Champ_cmd50_2_field6: int
    Champ_cmd50_2_field7: int
    Champ_cmd50_2_field8: int
    Champ_cmd50_2_field9: int
    def __init__(self, Champ_cmd50_2champ3: _Optional[_Union[StreamACChamp_cmd50_3, _Mapping]] = ..., Champ_cmd50_2_field1: _Optional[bytes] = ..., Champ_cmd50_2_field2: _Optional[int] = ..., Champ_cmd50_2_field3: _Optional[int] = ..., Champ_cmd50_2_field4: _Optional[int] = ..., Champ_cmd50_2_field5: _Optional[int] = ..., Champ_cmd50_2_field6: _Optional[int] = ..., Champ_cmd50_2_field7: _Optional[int] = ..., Champ_cmd50_2_field8: _Optional[int] = ..., Champ_cmd50_2_field9: _Optional[int] = ...) -> None: ...

class StreamACChamp_cmd50(_message.Message):
    __slots__ = ("Champ_cmd50_champ2",)
    CHAMP_CMD50_CHAMP2_FIELD_NUMBER: _ClassVar[int]
    Champ_cmd50_champ2: StreamACChamp_cmd50_2
    def __init__(self, Champ_cmd50_champ2: _Optional[_Union[StreamACChamp_cmd50_2, _Mapping]] = ...) -> None: ...

class StreamACCloudMeter(_message.Message):
    __slots__ = ("Champ_cmd21_4_field1", "Champ_cmd21_4_field2", "sn_metter", "Champ_cmd21_4_field4")
    CHAMP_CMD21_4_FIELD1_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD21_4_FIELD2_FIELD_NUMBER: _ClassVar[int]
    SN_METTER_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD21_4_FIELD4_FIELD_NUMBER: _ClassVar[int]
    Champ_cmd21_4_field1: int
    Champ_cmd21_4_field2: int
    sn_metter: str
    Champ_cmd21_4_field4: int
    def __init__(self, Champ_cmd21_4_field1: _Optional[int] = ..., Champ_cmd21_4_field2: _Optional[int] = ..., sn_metter: _Optional[str] = ..., Champ_cmd21_4_field4: _Optional[int] = ...) -> None: ...

class StreamACChamp_cmd21_3(_message.Message):
    __slots__ = ("Champ_cmd21_3_field282", "Champ_cmd21_3_field460", "powGetSysGrid", "powGetSysLoad", "powGetPvSum", "powGetBpCms", "Champ_cmd21_3_field602", "gridConnectionPower", "cloudMetter", "sysGridConnectionPower", "powGetSysLoadFromBp", "powGetSysLoadFromGrid", "powGetSchuko1")
    CHAMP_CMD21_3_FIELD282_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD21_3_FIELD460_FIELD_NUMBER: _ClassVar[int]
    POWGETSYSGRID_FIELD_NUMBER: _ClassVar[int]
    POWGETSYSLOAD_FIELD_NUMBER: _ClassVar[int]
    POWGETPVSUM_FIELD_NUMBER: _ClassVar[int]
    POWGETBPCMS_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD21_3_FIELD602_FIELD_NUMBER: _ClassVar[int]
    GRIDCONNECTIONPOWER_FIELD_NUMBER: _ClassVar[int]
    CLOUDMETTER_FIELD_NUMBER: _ClassVar[int]
    SYSGRIDCONNECTIONPOWER_FIELD_NUMBER: _ClassVar[int]
    POWGETSYSLOADFROMBP_FIELD_NUMBER: _ClassVar[int]
    POWGETSYSLOADFROMGRID_FIELD_NUMBER: _ClassVar[int]
    POWGETSCHUKO1_FIELD_NUMBER: _ClassVar[int]
    Champ_cmd21_3_field282: int
    Champ_cmd21_3_field460: int
    powGetSysGrid: float
    powGetSysLoad: float
    powGetPvSum: float
    powGetBpCms: float
    Champ_cmd21_3_field602: float
    gridConnectionPower: float
    cloudMetter: StreamACCloudMeter
    sysGridConnectionPower: float
    powGetSysLoadFromBp: float
    powGetSysLoadFromGrid: float
    powGetSchuko1: float
    def __init__(self, Champ_cmd21_3_field282: _Optional[int] = ..., Champ_cmd21_3_field460: _Optional[int] = ..., powGetSysGrid: _Optional[float] = ..., powGetSysLoad: _Optional[float] = ..., powGetPvSum: _Optional[float] = ..., powGetBpCms: _Optional[float] = ..., Champ_cmd21_3_field602: _Optional[float] = ..., gridConnectionPower: _Optional[float] = ..., cloudMetter: _Optional[_Union[StreamACCloudMeter, _Mapping]] = ..., sysGridConnectionPower: _Optional[float] = ..., powGetSysLoadFromBp: _Optional[float] = ..., powGetSysLoadFromGrid: _Optional[float] = ..., powGetSchuko1: _Optional[float] = ...) -> None: ...

class StreamACChamp_cmd21_2(_message.Message):
    __slots__ = ("Champ_cmd21_2_champ_cmd21_3", "Champ_cmd21_2_field2", "Champ_cmd21_2_field3", "Champ_cmd21_2_field4", "Champ_cmd21_2_field5", "Champ_cmd21_2_field8", "Champ_cmd21_2_field9", "Champ_cmd21_2_field10", "Champ_cmd21_2_field11", "Champ_cmd21_2_field16", "Champ_cmd21_2_field17")
    CHAMP_CMD21_2_CHAMP_CMD21_3_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD21_2_FIELD2_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD21_2_FIELD3_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD21_2_FIELD4_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD21_2_FIELD5_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD21_2_FIELD8_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD21_2_FIELD9_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD21_2_FIELD10_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD21_2_FIELD11_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD21_2_FIELD16_FIELD_NUMBER: _ClassVar[int]
    CHAMP_CMD21_2_FIELD17_FIELD_NUMBER: _ClassVar[int]
    Champ_cmd21_2_champ_cmd21_3: StreamACChamp_cmd21_3
    Champ_cmd21_2_field2: int
    Champ_cmd21_2_field3: int
    Champ_cmd21_2_field4: int
    Champ_cmd21_2_field5: int
    Champ_cmd21_2_field8: int
    Champ_cmd21_2_field9: int
    Champ_cmd21_2_field10: int
    Champ_cmd21_2_field11: int
    Champ_cmd21_2_field16: int
    Champ_cmd21_2_field17: int
    def __init__(self, Champ_cmd21_2_champ_cmd21_3: _Optional[_Union[StreamACChamp_cmd21_3, _Mapping]] = ..., Champ_cmd21_2_field2: _Optional[int] = ..., Champ_cmd21_2_field3: _Optional[int] = ..., Champ_cmd21_2_field4: _Optional[int] = ..., Champ_cmd21_2_field5: _Optional[int] = ..., Champ_cmd21_2_field8: _Optional[int] = ..., Champ_cmd21_2_field9: _Optional[int] = ..., Champ_cmd21_2_field10: _Optional[int] = ..., Champ_cmd21_2_field11: _Optional[int] = ..., Champ_cmd21_2_field16: _Optional[int] = ..., Champ_cmd21_2_field17: _Optional[int] = ...) -> None: ...

class StreamACChamp_cmd21(_message.Message):
    __slots__ = ("Champ_cmd21_champ_cmd21_2",)
    CHAMP_CMD21_CHAMP_CMD21_2_FIELD_NUMBER: _ClassVar[int]
    Champ_cmd21_champ_cmd21_2: StreamACChamp_cmd21_2
    def __init__(self, Champ_cmd21_champ_cmd21_2: _Optional[_Union[StreamACChamp_cmd21_2, _Mapping]] = ...) -> None: ...
