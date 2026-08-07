from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class AlternatorHeader(_message.Message):
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

class AlternatorMessage(_message.Message):
    __slots__ = ("msg",)
    MSG_FIELD_NUMBER: _ClassVar[int]
    msg: _containers.RepeatedCompositeFieldContainer[AlternatorHeader]
    def __init__(self, msg: _Iterable[AlternatorHeader | _Mapping] | None = ...) -> None: ...

class AlternatorHeartbeat(_message.Message):
    __slots__ = ("alternator_power", "bat_soc", "cable_length608", "car_bat_volt", "charge_to_full268", "operation_mode", "permanent_watts", "rated_power", "sp_charger_car_batt_chg_amp_limit", "sp_charger_car_batt_chg_amp_max", "sp_charger_dev_batt_chg_amp_limit", "sp_charger_dev_batt_chg_amp_max", "start_stop", "start_voltage", "station_power", "status1", "switch_off130", "temp", "unknown269", "unknown427", "unknown428", "unknown609", "wifi_rssi")
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
    def __init__(self, status1: int | None = ..., temp: int | None = ..., alternator_power: float | None = ..., switch_off130: int | None = ..., start_voltage: int | None = ..., car_bat_volt: float | None = ..., bat_soc: float | None = ..., charge_to_full268: int | None = ..., unknown269: int | None = ..., station_power: float | None = ..., unknown427: int | None = ..., unknown428: int | None = ..., operation_mode: int | None = ..., start_stop: int | None = ..., permanent_watts: float | None = ..., wifi_rssi: float | None = ..., rated_power: float | None = ..., cable_length608: float | None = ..., unknown609: float | None = ..., sp_charger_car_batt_chg_amp_limit: float | None = ..., sp_charger_dev_batt_chg_amp_limit: float | None = ..., sp_charger_car_batt_chg_amp_max: float | None = ..., sp_charger_dev_batt_chg_amp_max: float | None = ...) -> None: ...

class AlternatorSet(_message.Message):
    __slots__ = ("cable_length", "cfg_sp_charger_car_batt_chg_amp_limit", "cfg_sp_charger_dev_batt_chg_amp_limit", "operation_mode", "permanent_watts", "start_stop", "start_voltage", "switch_off")
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
    def __init__(self, switch_off: int | None = ..., operation_mode: int | None = ..., start_stop: int | None = ..., permanent_watts: float | None = ..., start_voltage: int | None = ..., cable_length: float | None = ..., cfg_sp_charger_car_batt_chg_amp_limit: float | None = ..., cfg_sp_charger_dev_batt_chg_amp_limit: float | None = ...) -> None: ...
