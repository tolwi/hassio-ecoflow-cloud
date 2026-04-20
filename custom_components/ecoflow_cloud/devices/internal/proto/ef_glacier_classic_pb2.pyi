from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GlacierClassicHeader(_message.Message):
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

class GlacierClassicSendHeaderMsg(_message.Message):
    __slots__ = ("msg",)
    MSG_FIELD_NUMBER: _ClassVar[int]
    msg: _containers.RepeatedCompositeFieldContainer[GlacierClassicHeader]
    def __init__(self, msg: _Optional[_Iterable[_Union[GlacierClassicHeader, _Mapping]]] = ...) -> None: ...

class GlacierClassicBMSHeartBeatReport(_message.Message):
    __slots__ = ("num", "cell_id", "err_code", "sys_ver", "soc", "vol", "amp", "temp", "open_bms_flag", "design_cap", "remain_cap", "full_cap", "cycles", "soh", "max_cell_vol", "min_cell_vol", "max_cell_temp", "min_cell_temp", "max_mos_temp", "min_mos_temp", "bms_fault", "bq_sys_stat_reg", "tag_chg_amp", "f32_show_soc", "input_watts", "output_watts", "remain_time", "mos_state", "balance_state", "max_vol_diff", "cell_series_num", "cell_vol", "cell_temp", "hw_ver", "bms_sn", "act_soc", "diff_soc", "target_soc", "all_err_code", "all_bms_fault", "pack_sn", "water_in_flag")
    NUM_FIELD_NUMBER: _ClassVar[int]
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    ERR_CODE_FIELD_NUMBER: _ClassVar[int]
    SYS_VER_FIELD_NUMBER: _ClassVar[int]
    SOC_FIELD_NUMBER: _ClassVar[int]
    VOL_FIELD_NUMBER: _ClassVar[int]
    AMP_FIELD_NUMBER: _ClassVar[int]
    TEMP_FIELD_NUMBER: _ClassVar[int]
    OPEN_BMS_FLAG_FIELD_NUMBER: _ClassVar[int]
    DESIGN_CAP_FIELD_NUMBER: _ClassVar[int]
    REMAIN_CAP_FIELD_NUMBER: _ClassVar[int]
    FULL_CAP_FIELD_NUMBER: _ClassVar[int]
    CYCLES_FIELD_NUMBER: _ClassVar[int]
    SOH_FIELD_NUMBER: _ClassVar[int]
    MAX_CELL_VOL_FIELD_NUMBER: _ClassVar[int]
    MIN_CELL_VOL_FIELD_NUMBER: _ClassVar[int]
    MAX_CELL_TEMP_FIELD_NUMBER: _ClassVar[int]
    MIN_CELL_TEMP_FIELD_NUMBER: _ClassVar[int]
    MAX_MOS_TEMP_FIELD_NUMBER: _ClassVar[int]
    MIN_MOS_TEMP_FIELD_NUMBER: _ClassVar[int]
    BMS_FAULT_FIELD_NUMBER: _ClassVar[int]
    BQ_SYS_STAT_REG_FIELD_NUMBER: _ClassVar[int]
    TAG_CHG_AMP_FIELD_NUMBER: _ClassVar[int]
    F32_SHOW_SOC_FIELD_NUMBER: _ClassVar[int]
    INPUT_WATTS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_WATTS_FIELD_NUMBER: _ClassVar[int]
    REMAIN_TIME_FIELD_NUMBER: _ClassVar[int]
    MOS_STATE_FIELD_NUMBER: _ClassVar[int]
    BALANCE_STATE_FIELD_NUMBER: _ClassVar[int]
    MAX_VOL_DIFF_FIELD_NUMBER: _ClassVar[int]
    CELL_SERIES_NUM_FIELD_NUMBER: _ClassVar[int]
    CELL_VOL_FIELD_NUMBER: _ClassVar[int]
    CELL_TEMP_FIELD_NUMBER: _ClassVar[int]
    HW_VER_FIELD_NUMBER: _ClassVar[int]
    BMS_SN_FIELD_NUMBER: _ClassVar[int]
    ACT_SOC_FIELD_NUMBER: _ClassVar[int]
    DIFF_SOC_FIELD_NUMBER: _ClassVar[int]
    TARGET_SOC_FIELD_NUMBER: _ClassVar[int]
    ALL_ERR_CODE_FIELD_NUMBER: _ClassVar[int]
    ALL_BMS_FAULT_FIELD_NUMBER: _ClassVar[int]
    PACK_SN_FIELD_NUMBER: _ClassVar[int]
    WATER_IN_FLAG_FIELD_NUMBER: _ClassVar[int]
    num: int
    cell_id: int
    err_code: int
    sys_ver: int
    soc: int
    vol: int
    amp: int
    temp: int
    open_bms_flag: int
    design_cap: int
    remain_cap: int
    full_cap: int
    cycles: int
    soh: int
    max_cell_vol: int
    min_cell_vol: int
    max_cell_temp: int
    min_cell_temp: int
    max_mos_temp: int
    min_mos_temp: int
    bms_fault: int
    bq_sys_stat_reg: int
    tag_chg_amp: int
    f32_show_soc: float
    input_watts: int
    output_watts: int
    remain_time: int
    mos_state: int
    balance_state: int
    max_vol_diff: int
    cell_series_num: int
    cell_vol: _containers.RepeatedScalarFieldContainer[int]
    cell_temp: _containers.RepeatedScalarFieldContainer[int]
    hw_ver: str
    bms_sn: str
    act_soc: float
    diff_soc: float
    target_soc: float
    all_err_code: int
    all_bms_fault: int
    pack_sn: str
    water_in_flag: int
    def __init__(self, num: _Optional[int] = ..., cell_id: _Optional[int] = ..., err_code: _Optional[int] = ..., sys_ver: _Optional[int] = ..., soc: _Optional[int] = ..., vol: _Optional[int] = ..., amp: _Optional[int] = ..., temp: _Optional[int] = ..., open_bms_flag: _Optional[int] = ..., design_cap: _Optional[int] = ..., remain_cap: _Optional[int] = ..., full_cap: _Optional[int] = ..., cycles: _Optional[int] = ..., soh: _Optional[int] = ..., max_cell_vol: _Optional[int] = ..., min_cell_vol: _Optional[int] = ..., max_cell_temp: _Optional[int] = ..., min_cell_temp: _Optional[int] = ..., max_mos_temp: _Optional[int] = ..., min_mos_temp: _Optional[int] = ..., bms_fault: _Optional[int] = ..., bq_sys_stat_reg: _Optional[int] = ..., tag_chg_amp: _Optional[int] = ..., f32_show_soc: _Optional[float] = ..., input_watts: _Optional[int] = ..., output_watts: _Optional[int] = ..., remain_time: _Optional[int] = ..., mos_state: _Optional[int] = ..., balance_state: _Optional[int] = ..., max_vol_diff: _Optional[int] = ..., cell_series_num: _Optional[int] = ..., cell_vol: _Optional[_Iterable[int]] = ..., cell_temp: _Optional[_Iterable[int]] = ..., hw_ver: _Optional[str] = ..., bms_sn: _Optional[str] = ..., act_soc: _Optional[float] = ..., diff_soc: _Optional[float] = ..., target_soc: _Optional[float] = ..., all_err_code: _Optional[int] = ..., all_bms_fault: _Optional[int] = ..., pack_sn: _Optional[str] = ..., water_in_flag: _Optional[int] = ...) -> None: ...

class GlacierClassicCMSHeartBeatV1P0(_message.Message):
    __slots__ = ("chg_state", "chg_cmd", "dsg_cmd", "chg_amp", "fan_level", "max_charge_soc", "bms_model", "lcd_show_soc", "open_ups_flag", "bms_warning_state", "chg_remain_time", "dsg_remain_time", "ems_is_normal_flag", "f32_lcd_show_soc", "bms_is_connt", "max_available_num", "open_bms_idx", "para_vol_min", "para_vol_max", "min_dsg_soc", "min_open_oil_eb_soc", "max_close_oil_eb_soc")
    CHG_STATE_FIELD_NUMBER: _ClassVar[int]
    CHG_CMD_FIELD_NUMBER: _ClassVar[int]
    DSG_CMD_FIELD_NUMBER: _ClassVar[int]
    CHG_AMP_FIELD_NUMBER: _ClassVar[int]
    FAN_LEVEL_FIELD_NUMBER: _ClassVar[int]
    MAX_CHARGE_SOC_FIELD_NUMBER: _ClassVar[int]
    BMS_MODEL_FIELD_NUMBER: _ClassVar[int]
    LCD_SHOW_SOC_FIELD_NUMBER: _ClassVar[int]
    OPEN_UPS_FLAG_FIELD_NUMBER: _ClassVar[int]
    BMS_WARNING_STATE_FIELD_NUMBER: _ClassVar[int]
    CHG_REMAIN_TIME_FIELD_NUMBER: _ClassVar[int]
    DSG_REMAIN_TIME_FIELD_NUMBER: _ClassVar[int]
    EMS_IS_NORMAL_FLAG_FIELD_NUMBER: _ClassVar[int]
    F32_LCD_SHOW_SOC_FIELD_NUMBER: _ClassVar[int]
    BMS_IS_CONNT_FIELD_NUMBER: _ClassVar[int]
    MAX_AVAILABLE_NUM_FIELD_NUMBER: _ClassVar[int]
    OPEN_BMS_IDX_FIELD_NUMBER: _ClassVar[int]
    PARA_VOL_MIN_FIELD_NUMBER: _ClassVar[int]
    PARA_VOL_MAX_FIELD_NUMBER: _ClassVar[int]
    MIN_DSG_SOC_FIELD_NUMBER: _ClassVar[int]
    MIN_OPEN_OIL_EB_SOC_FIELD_NUMBER: _ClassVar[int]
    MAX_CLOSE_OIL_EB_SOC_FIELD_NUMBER: _ClassVar[int]
    chg_state: int
    chg_cmd: int
    dsg_cmd: int
    chg_amp: int
    fan_level: int
    max_charge_soc: int
    bms_model: int
    lcd_show_soc: int
    open_ups_flag: int
    bms_warning_state: int
    chg_remain_time: int
    dsg_remain_time: int
    ems_is_normal_flag: int
    f32_lcd_show_soc: float
    bms_is_connt: _containers.RepeatedScalarFieldContainer[int]
    max_available_num: int
    open_bms_idx: int
    para_vol_min: int
    para_vol_max: int
    min_dsg_soc: int
    min_open_oil_eb_soc: int
    max_close_oil_eb_soc: int
    def __init__(self, chg_state: _Optional[int] = ..., chg_cmd: _Optional[int] = ..., dsg_cmd: _Optional[int] = ..., chg_amp: _Optional[int] = ..., fan_level: _Optional[int] = ..., max_charge_soc: _Optional[int] = ..., bms_model: _Optional[int] = ..., lcd_show_soc: _Optional[int] = ..., open_ups_flag: _Optional[int] = ..., bms_warning_state: _Optional[int] = ..., chg_remain_time: _Optional[int] = ..., dsg_remain_time: _Optional[int] = ..., ems_is_normal_flag: _Optional[int] = ..., f32_lcd_show_soc: _Optional[float] = ..., bms_is_connt: _Optional[_Iterable[int]] = ..., max_available_num: _Optional[int] = ..., open_bms_idx: _Optional[int] = ..., para_vol_min: _Optional[int] = ..., para_vol_max: _Optional[int] = ..., min_dsg_soc: _Optional[int] = ..., min_open_oil_eb_soc: _Optional[int] = ..., max_close_oil_eb_soc: _Optional[int] = ...) -> None: ...

class GlacierClassicCMSHeartBeatV1P3(_message.Message):
    __slots__ = ("chg_disable_cond", "dsg_disable_cond", "chg_line_plug_in_flag", "sys_chg_dsg_state", "ems_heartbeat_ver")
    CHG_DISABLE_COND_FIELD_NUMBER: _ClassVar[int]
    DSG_DISABLE_COND_FIELD_NUMBER: _ClassVar[int]
    CHG_LINE_PLUG_IN_FLAG_FIELD_NUMBER: _ClassVar[int]
    SYS_CHG_DSG_STATE_FIELD_NUMBER: _ClassVar[int]
    EMS_HEARTBEAT_VER_FIELD_NUMBER: _ClassVar[int]
    chg_disable_cond: int
    dsg_disable_cond: int
    chg_line_plug_in_flag: int
    sys_chg_dsg_state: int
    ems_heartbeat_ver: int
    def __init__(self, chg_disable_cond: _Optional[int] = ..., dsg_disable_cond: _Optional[int] = ..., chg_line_plug_in_flag: _Optional[int] = ..., sys_chg_dsg_state: _Optional[int] = ..., ems_heartbeat_ver: _Optional[int] = ...) -> None: ...

class GlacierClassicCMSHeartBeatReport(_message.Message):
    __slots__ = ("v1p0", "v1p3")
    V1P0_FIELD_NUMBER: _ClassVar[int]
    V1P3_FIELD_NUMBER: _ClassVar[int]
    v1p0: GlacierClassicCMSHeartBeatV1P0
    v1p3: GlacierClassicCMSHeartBeatV1P3
    def __init__(self, v1p0: _Optional[_Union[GlacierClassicCMSHeartBeatV1P0, _Mapping]] = ..., v1p3: _Optional[_Union[GlacierClassicCMSHeartBeatV1P3, _Mapping]] = ...) -> None: ...

class GlacierClassicDisplayPropertyUpload(_message.Message):
    __slots__ = ("errcode", "sys_status", "pow_in_sum_w", "pow_out_sum_w", "dev_standby_time", "screen_off_time", "bat_temp102", "bms_err_code", "en_beep", "pd_err_code", "cms_batt_soc", "cms_dsg_rem_time", "cms_chg_rem_time", "cms_max_chg_soc", "cms_min_dsg_soc", "cms_chg_dsg_state", "cms_batt_design_cap", "plug_in_info_pv_flag", "plug_in_info_pv_type", "bms_main_sn", "plug_in_info_dcp_in_flag", "temp_unit", "set_point_left", "set_point_right", "child_lock", "simple_mode", "bat_protect", "cooling_mode", "temp_monitor_left", "temp_monitor_right", "lid_status", "zone_status", "temp_alert", "input_volt777")
    ERRCODE_FIELD_NUMBER: _ClassVar[int]
    SYS_STATUS_FIELD_NUMBER: _ClassVar[int]
    POW_IN_SUM_W_FIELD_NUMBER: _ClassVar[int]
    POW_OUT_SUM_W_FIELD_NUMBER: _ClassVar[int]
    DEV_STANDBY_TIME_FIELD_NUMBER: _ClassVar[int]
    SCREEN_OFF_TIME_FIELD_NUMBER: _ClassVar[int]
    BAT_TEMP102_FIELD_NUMBER: _ClassVar[int]
    BMS_ERR_CODE_FIELD_NUMBER: _ClassVar[int]
    EN_BEEP_FIELD_NUMBER: _ClassVar[int]
    PD_ERR_CODE_FIELD_NUMBER: _ClassVar[int]
    CMS_BATT_SOC_FIELD_NUMBER: _ClassVar[int]
    CMS_DSG_REM_TIME_FIELD_NUMBER: _ClassVar[int]
    CMS_CHG_REM_TIME_FIELD_NUMBER: _ClassVar[int]
    CMS_MAX_CHG_SOC_FIELD_NUMBER: _ClassVar[int]
    CMS_MIN_DSG_SOC_FIELD_NUMBER: _ClassVar[int]
    CMS_CHG_DSG_STATE_FIELD_NUMBER: _ClassVar[int]
    CMS_BATT_DESIGN_CAP_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_PV_FLAG_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_PV_TYPE_FIELD_NUMBER: _ClassVar[int]
    BMS_MAIN_SN_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_DCP_IN_FLAG_FIELD_NUMBER: _ClassVar[int]
    TEMP_UNIT_FIELD_NUMBER: _ClassVar[int]
    SET_POINT_LEFT_FIELD_NUMBER: _ClassVar[int]
    SET_POINT_RIGHT_FIELD_NUMBER: _ClassVar[int]
    CHILD_LOCK_FIELD_NUMBER: _ClassVar[int]
    SIMPLE_MODE_FIELD_NUMBER: _ClassVar[int]
    BAT_PROTECT_FIELD_NUMBER: _ClassVar[int]
    COOLING_MODE_FIELD_NUMBER: _ClassVar[int]
    TEMP_MONITOR_LEFT_FIELD_NUMBER: _ClassVar[int]
    TEMP_MONITOR_RIGHT_FIELD_NUMBER: _ClassVar[int]
    LID_STATUS_FIELD_NUMBER: _ClassVar[int]
    ZONE_STATUS_FIELD_NUMBER: _ClassVar[int]
    TEMP_ALERT_FIELD_NUMBER: _ClassVar[int]
    INPUT_VOLT777_FIELD_NUMBER: _ClassVar[int]
    errcode: int
    sys_status: int
    pow_in_sum_w: float
    pow_out_sum_w: float
    dev_standby_time: int
    screen_off_time: int
    bat_temp102: int
    bms_err_code: int
    en_beep: int
    pd_err_code: int
    cms_batt_soc: float
    cms_dsg_rem_time: int
    cms_chg_rem_time: int
    cms_max_chg_soc: int
    cms_min_dsg_soc: int
    cms_chg_dsg_state: int
    cms_batt_design_cap: int
    plug_in_info_pv_flag: int
    plug_in_info_pv_type: int
    bms_main_sn: str
    plug_in_info_dcp_in_flag: int
    temp_unit: int
    set_point_left: float
    set_point_right: float
    child_lock: int
    simple_mode: int
    bat_protect: int
    cooling_mode: int
    temp_monitor_left: float
    temp_monitor_right: float
    lid_status: int
    zone_status: int
    temp_alert: int
    input_volt777: float
    def __init__(self, errcode: _Optional[int] = ..., sys_status: _Optional[int] = ..., pow_in_sum_w: _Optional[float] = ..., pow_out_sum_w: _Optional[float] = ..., dev_standby_time: _Optional[int] = ..., screen_off_time: _Optional[int] = ..., bat_temp102: _Optional[int] = ..., bms_err_code: _Optional[int] = ..., en_beep: _Optional[int] = ..., pd_err_code: _Optional[int] = ..., cms_batt_soc: _Optional[float] = ..., cms_dsg_rem_time: _Optional[int] = ..., cms_chg_rem_time: _Optional[int] = ..., cms_max_chg_soc: _Optional[int] = ..., cms_min_dsg_soc: _Optional[int] = ..., cms_chg_dsg_state: _Optional[int] = ..., cms_batt_design_cap: _Optional[int] = ..., plug_in_info_pv_flag: _Optional[int] = ..., plug_in_info_pv_type: _Optional[int] = ..., bms_main_sn: _Optional[str] = ..., plug_in_info_dcp_in_flag: _Optional[int] = ..., temp_unit: _Optional[int] = ..., set_point_left: _Optional[float] = ..., set_point_right: _Optional[float] = ..., child_lock: _Optional[int] = ..., simple_mode: _Optional[int] = ..., bat_protect: _Optional[int] = ..., cooling_mode: _Optional[int] = ..., temp_monitor_left: _Optional[float] = ..., temp_monitor_right: _Optional[float] = ..., lid_status: _Optional[int] = ..., zone_status: _Optional[int] = ..., temp_alert: _Optional[int] = ..., input_volt777: _Optional[float] = ...) -> None: ...

class GlacierClassicRuntimePropertyUpload(_message.Message):
    __slots__ = ("plug_in_info_ac_in_vol", "display_property_full_upload_period", "display_property_incremental_upload_period", "runtime_property_full_upload_period", "runtime_property_incremental_upload_period")
    PLUG_IN_INFO_AC_IN_VOL_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_PROPERTY_FULL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_PROPERTY_INCREMENTAL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_PROPERTY_FULL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_PROPERTY_INCREMENTAL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    plug_in_info_ac_in_vol: float
    display_property_full_upload_period: int
    display_property_incremental_upload_period: int
    runtime_property_full_upload_period: int
    runtime_property_incremental_upload_period: int
    def __init__(self, plug_in_info_ac_in_vol: _Optional[float] = ..., display_property_full_upload_period: _Optional[int] = ..., display_property_incremental_upload_period: _Optional[int] = ..., runtime_property_full_upload_period: _Optional[int] = ..., runtime_property_incremental_upload_period: _Optional[int] = ...) -> None: ...

class GlacierClassicSetCommand(_message.Message):
    __slots__ = ("en_beep", "dev_standby_time", "cms_max_chg_soc", "cms_min_dsg_soc", "standby", "set_point_left", "set_point_right", "child_lock", "simple_mode", "bat_protect", "cooling_mode", "temp_alert")
    EN_BEEP_FIELD_NUMBER: _ClassVar[int]
    DEV_STANDBY_TIME_FIELD_NUMBER: _ClassVar[int]
    CMS_MAX_CHG_SOC_FIELD_NUMBER: _ClassVar[int]
    CMS_MIN_DSG_SOC_FIELD_NUMBER: _ClassVar[int]
    STANDBY_FIELD_NUMBER: _ClassVar[int]
    SET_POINT_LEFT_FIELD_NUMBER: _ClassVar[int]
    SET_POINT_RIGHT_FIELD_NUMBER: _ClassVar[int]
    CHILD_LOCK_FIELD_NUMBER: _ClassVar[int]
    SIMPLE_MODE_FIELD_NUMBER: _ClassVar[int]
    BAT_PROTECT_FIELD_NUMBER: _ClassVar[int]
    COOLING_MODE_FIELD_NUMBER: _ClassVar[int]
    TEMP_ALERT_FIELD_NUMBER: _ClassVar[int]
    en_beep: int
    dev_standby_time: int
    cms_max_chg_soc: int
    cms_min_dsg_soc: int
    standby: int
    set_point_left: float
    set_point_right: float
    child_lock: int
    simple_mode: int
    bat_protect: int
    cooling_mode: int
    temp_alert: int
    def __init__(self, en_beep: _Optional[int] = ..., dev_standby_time: _Optional[int] = ..., cms_max_chg_soc: _Optional[int] = ..., cms_min_dsg_soc: _Optional[int] = ..., standby: _Optional[int] = ..., set_point_left: _Optional[float] = ..., set_point_right: _Optional[float] = ..., child_lock: _Optional[int] = ..., simple_mode: _Optional[int] = ..., bat_protect: _Optional[int] = ..., cooling_mode: _Optional[int] = ..., temp_alert: _Optional[int] = ...) -> None: ...
