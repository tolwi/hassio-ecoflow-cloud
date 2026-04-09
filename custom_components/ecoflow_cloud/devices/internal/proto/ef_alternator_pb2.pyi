from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AlternatorHeader(_message.Message):
    __slots__ = ("pdata", "src", "dest", "d_src", "d_dest", "enc_type", "check_type", "cmd_func", "cmd_id", "data_len", "need_ack", "is_ack", "seq", "product_id", "version", "payload_ver", "time_snap", "is_rw_cmd", "is_queue", "ack_type", "code", "from_", "module_sn", "device_sn")
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
    def __init__(self, pdata: _Optional[bytes] = ..., src: _Optional[int] = ..., dest: _Optional[int] = ..., d_src: _Optional[int] = ..., d_dest: _Optional[int] = ..., enc_type: _Optional[int] = ..., check_type: _Optional[int] = ..., cmd_func: _Optional[int] = ..., cmd_id: _Optional[int] = ..., data_len: _Optional[int] = ..., need_ack: _Optional[int] = ..., is_ack: _Optional[int] = ..., seq: _Optional[int] = ..., product_id: _Optional[int] = ..., version: _Optional[int] = ..., payload_ver: _Optional[int] = ..., time_snap: _Optional[int] = ..., is_rw_cmd: _Optional[int] = ..., is_queue: _Optional[int] = ..., ack_type: _Optional[int] = ..., code: _Optional[str] = ..., from_: _Optional[str] = ..., module_sn: _Optional[str] = ..., device_sn: _Optional[str] = ...) -> None: ...

class AlternatorMessage(_message.Message):
    __slots__ = ("msg",)
    MSG_FIELD_NUMBER: _ClassVar[int]
    msg: _containers.RepeatedCompositeFieldContainer[AlternatorHeader]
    def __init__(self, msg: _Optional[_Iterable[_Union[AlternatorHeader, _Mapping]]] = ...) -> None: ...

class AlternatorHeartbeat(_message.Message):
    __slots__ = ("status1", "temp", "alternator_power", "switch_off130", "start_voltage", "car_bat_volt", "bat_soc", "charge_to_full268", "unknown269", "station_power", "unknown427", "unknown428", "operation_mode", "start_stop", "permanent_watts", "wifi_rssi", "rated_power", "cable_length608", "unknown609", "sp_charger_car_batt_chg_amp_limit", "sp_charger_dev_batt_chg_amp_limit", "sp_charger_car_batt_chg_amp_max", "sp_charger_dev_batt_chg_amp_max")
    STATUS1_FIELD_NUMBER: _ClassVar[int]
    TEMP_FIELD_NUMBER: _ClassVar[int]
    ALTERNATOR_POWER_FIELD_NUMBER: _ClassVar[int]
    SWITCH_OFF130_FIELD_NUMBER: _ClassVar[int]
    START_VOLTAGE_FIELD_NUMBER: _ClassVar[int]
    CAR_BAT_VOLT_FIELD_NUMBER: _ClassVar[int]
    BAT_SOC_FIELD_NUMBER: _ClassVar[int]
    CHARGE_TO_FULL268_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN269_FIELD_NUMBER: _ClassVar[int]
    STATION_POWER_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN427_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN428_FIELD_NUMBER: _ClassVar[int]
    OPERATION_MODE_FIELD_NUMBER: _ClassVar[int]
    START_STOP_FIELD_NUMBER: _ClassVar[int]
    PERMANENT_WATTS_FIELD_NUMBER: _ClassVar[int]
    WIFI_RSSI_FIELD_NUMBER: _ClassVar[int]
    RATED_POWER_FIELD_NUMBER: _ClassVar[int]
    CABLE_LENGTH608_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN609_FIELD_NUMBER: _ClassVar[int]
    SP_CHARGER_CAR_BATT_CHG_AMP_LIMIT_FIELD_NUMBER: _ClassVar[int]
    SP_CHARGER_DEV_BATT_CHG_AMP_LIMIT_FIELD_NUMBER: _ClassVar[int]
    SP_CHARGER_CAR_BATT_CHG_AMP_MAX_FIELD_NUMBER: _ClassVar[int]
    SP_CHARGER_DEV_BATT_CHG_AMP_MAX_FIELD_NUMBER: _ClassVar[int]
    status1: int
    temp: int
    alternator_power: float
    switch_off130: int
    start_voltage: int
    car_bat_volt: float
    bat_soc: float
    charge_to_full268: int
    unknown269: int
    station_power: float
    unknown427: int
    unknown428: int
    operation_mode: int
    start_stop: int
    permanent_watts: float
    wifi_rssi: float
    rated_power: float
    cable_length608: float
    unknown609: float
    sp_charger_car_batt_chg_amp_limit: float
    sp_charger_dev_batt_chg_amp_limit: float
    sp_charger_car_batt_chg_amp_max: float
    sp_charger_dev_batt_chg_amp_max: float
    def __init__(self, status1: _Optional[int] = ..., temp: _Optional[int] = ..., alternator_power: _Optional[float] = ..., switch_off130: _Optional[int] = ..., start_voltage: _Optional[int] = ..., car_bat_volt: _Optional[float] = ..., bat_soc: _Optional[float] = ..., charge_to_full268: _Optional[int] = ..., unknown269: _Optional[int] = ..., station_power: _Optional[float] = ..., unknown427: _Optional[int] = ..., unknown428: _Optional[int] = ..., operation_mode: _Optional[int] = ..., start_stop: _Optional[int] = ..., permanent_watts: _Optional[float] = ..., wifi_rssi: _Optional[float] = ..., rated_power: _Optional[float] = ..., cable_length608: _Optional[float] = ..., unknown609: _Optional[float] = ..., sp_charger_car_batt_chg_amp_limit: _Optional[float] = ..., sp_charger_dev_batt_chg_amp_limit: _Optional[float] = ..., sp_charger_car_batt_chg_amp_max: _Optional[float] = ..., sp_charger_dev_batt_chg_amp_max: _Optional[float] = ...) -> None: ...

class AlternatorSet(_message.Message):
    __slots__ = ("switch_off", "operation_mode", "start_stop", "permanent_watts", "start_voltage", "cable_length", "cfg_sp_charger_car_batt_chg_amp_limit", "cfg_sp_charger_dev_batt_chg_amp_limit")
    SWITCH_OFF_FIELD_NUMBER: _ClassVar[int]
    OPERATION_MODE_FIELD_NUMBER: _ClassVar[int]
    START_STOP_FIELD_NUMBER: _ClassVar[int]
    PERMANENT_WATTS_FIELD_NUMBER: _ClassVar[int]
    START_VOLTAGE_FIELD_NUMBER: _ClassVar[int]
    CABLE_LENGTH_FIELD_NUMBER: _ClassVar[int]
    CFG_SP_CHARGER_CAR_BATT_CHG_AMP_LIMIT_FIELD_NUMBER: _ClassVar[int]
    CFG_SP_CHARGER_DEV_BATT_CHG_AMP_LIMIT_FIELD_NUMBER: _ClassVar[int]
    switch_off: int
    operation_mode: int
    start_stop: int
    permanent_watts: float
    start_voltage: int
    cable_length: float
    cfg_sp_charger_car_batt_chg_amp_limit: float
    cfg_sp_charger_dev_batt_chg_amp_limit: float
    def __init__(self, switch_off: _Optional[int] = ..., operation_mode: _Optional[int] = ..., start_stop: _Optional[int] = ..., permanent_watts: _Optional[float] = ..., start_voltage: _Optional[int] = ..., cable_length: _Optional[float] = ..., cfg_sp_charger_car_batt_chg_amp_limit: _Optional[float] = ..., cfg_sp_charger_dev_batt_chg_amp_limit: _Optional[float] = ...) -> None: ...
