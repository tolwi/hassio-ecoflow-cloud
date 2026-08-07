from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class GlacierClassicHeader(_message.Message):
    __slots__ = ("ack_type", "check_type", "cmd_func", "cmd_id", "code", "d_dest", "d_src", "data_len", "dest", "device_sn", "enc_type", "is_ack", "is_queue", "is_rw_cmd", "module_sn", "need_ack", "payload_ver", "pdata", "product_id", "seq", "src", "time_snap", "version")
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
    def __init__(self, pdata: bytes | None = ..., src: int | None = ..., dest: int | None = ..., d_src: int | None = ..., d_dest: int | None = ..., enc_type: int | None = ..., check_type: int | None = ..., cmd_func: int | None = ..., cmd_id: int | None = ..., data_len: int | None = ..., need_ack: int | None = ..., is_ack: int | None = ..., seq: int | None = ..., product_id: int | None = ..., version: int | None = ..., payload_ver: int | None = ..., time_snap: int | None = ..., is_rw_cmd: int | None = ..., is_queue: int | None = ..., ack_type: int | None = ..., code: str | None = ..., module_sn: str | None = ..., device_sn: str | None = ..., **kwargs) -> None: ...

class GlacierClassicSendHeaderMsg(_message.Message):
    __slots__ = ("msg",)
    MSG_FIELD_NUMBER: _ClassVar[int]
    msg: _containers.RepeatedCompositeFieldContainer[GlacierClassicHeader]
    def __init__(self, msg: _Iterable[GlacierClassicHeader | _Mapping] | None = ...) -> None: ...

class GlacierClassicBMSHeartBeatReport(_message.Message):
    __slots__ = ("act_soc", "all_bms_fault", "all_err_code", "amp", "balance_state", "bms_fault", "bms_sn", "bq_sys_stat_reg", "cell_id", "cell_series_num", "cell_temp", "cell_vol", "cycles", "design_cap", "diff_soc", "err_code", "f32_show_soc", "full_cap", "hw_ver", "input_watts", "max_cell_temp", "max_cell_vol", "max_mos_temp", "max_vol_diff", "min_cell_temp", "min_cell_vol", "min_mos_temp", "mos_state", "num", "open_bms_flag", "output_watts", "pack_sn", "remain_cap", "remain_time", "soc", "soh", "sys_ver", "tag_chg_amp", "target_soc", "temp", "vol", "water_in_flag")
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
    def __init__(self, num: int | None = ..., cell_id: int | None = ..., err_code: int | None = ..., sys_ver: int | None = ..., soc: int | None = ..., vol: int | None = ..., amp: int | None = ..., temp: int | None = ..., open_bms_flag: int | None = ..., design_cap: int | None = ..., remain_cap: int | None = ..., full_cap: int | None = ..., cycles: int | None = ..., soh: int | None = ..., max_cell_vol: int | None = ..., min_cell_vol: int | None = ..., max_cell_temp: int | None = ..., min_cell_temp: int | None = ..., max_mos_temp: int | None = ..., min_mos_temp: int | None = ..., bms_fault: int | None = ..., bq_sys_stat_reg: int | None = ..., tag_chg_amp: int | None = ..., f32_show_soc: float | None = ..., input_watts: int | None = ..., output_watts: int | None = ..., remain_time: int | None = ..., mos_state: int | None = ..., balance_state: int | None = ..., max_vol_diff: int | None = ..., cell_series_num: int | None = ..., cell_vol: _Iterable[int] | None = ..., cell_temp: _Iterable[int] | None = ..., hw_ver: str | None = ..., bms_sn: str | None = ..., act_soc: float | None = ..., diff_soc: float | None = ..., target_soc: float | None = ..., all_err_code: int | None = ..., all_bms_fault: int | None = ..., pack_sn: str | None = ..., water_in_flag: int | None = ...) -> None: ...

class GlacierClassicCMSHeartBeatV1P0(_message.Message):
    __slots__ = ("bms_is_connt", "bms_model", "bms_warning_state", "chg_amp", "chg_cmd", "chg_remain_time", "chg_state", "dsg_cmd", "dsg_remain_time", "ems_is_normal_flag", "f32_lcd_show_soc", "fan_level", "lcd_show_soc", "max_available_num", "max_charge_soc", "max_close_oil_eb_soc", "min_dsg_soc", "min_open_oil_eb_soc", "open_bms_idx", "open_ups_flag", "para_vol_max", "para_vol_min")
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
    def __init__(self, chg_state: int | None = ..., chg_cmd: int | None = ..., dsg_cmd: int | None = ..., chg_amp: int | None = ..., fan_level: int | None = ..., max_charge_soc: int | None = ..., bms_model: int | None = ..., lcd_show_soc: int | None = ..., open_ups_flag: int | None = ..., bms_warning_state: int | None = ..., chg_remain_time: int | None = ..., dsg_remain_time: int | None = ..., ems_is_normal_flag: int | None = ..., f32_lcd_show_soc: float | None = ..., bms_is_connt: _Iterable[int] | None = ..., max_available_num: int | None = ..., open_bms_idx: int | None = ..., para_vol_min: int | None = ..., para_vol_max: int | None = ..., min_dsg_soc: int | None = ..., min_open_oil_eb_soc: int | None = ..., max_close_oil_eb_soc: int | None = ...) -> None: ...

class GlacierClassicCMSHeartBeatV1P3(_message.Message):
    __slots__ = ("chg_disable_cond", "chg_line_plug_in_flag", "dsg_disable_cond", "ems_heartbeat_ver", "sys_chg_dsg_state")
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
    def __init__(self, chg_disable_cond: int | None = ..., dsg_disable_cond: int | None = ..., chg_line_plug_in_flag: int | None = ..., sys_chg_dsg_state: int | None = ..., ems_heartbeat_ver: int | None = ...) -> None: ...

class GlacierClassicCMSHeartBeatReport(_message.Message):
    __slots__ = ("v1p0", "v1p3")
    V1P0_FIELD_NUMBER: _ClassVar[int]
    V1P3_FIELD_NUMBER: _ClassVar[int]
    v1p0: GlacierClassicCMSHeartBeatV1P0
    v1p3: GlacierClassicCMSHeartBeatV1P3
    def __init__(self, v1p0: GlacierClassicCMSHeartBeatV1P0 | _Mapping | None = ..., v1p3: GlacierClassicCMSHeartBeatV1P3 | _Mapping | None = ...) -> None: ...

class GlacierClassicDisplayPropertyUpload(_message.Message):
    __slots__ = ("bat_protect", "bat_temp102", "bms_err_code", "bms_main_sn", "child_lock", "cms_batt_design_cap", "cms_batt_soc", "cms_chg_dsg_state", "cms_chg_rem_time", "cms_dsg_rem_time", "cms_max_chg_soc", "cms_min_dsg_soc", "cooling_mode", "dev_standby_time", "en_beep", "errcode", "input_volt777", "lid_status", "pd_err_code", "plug_in_info_dcp_in_flag", "plug_in_info_pv_flag", "plug_in_info_pv_type", "pow_in_sum_w", "pow_out_sum_w", "screen_off_time", "set_point_left", "set_point_right", "simple_mode", "sys_status", "temp_alert", "temp_monitor_left", "temp_monitor_right", "temp_unit", "zone_status")
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
    def __init__(self, errcode: int | None = ..., sys_status: int | None = ..., pow_in_sum_w: float | None = ..., pow_out_sum_w: float | None = ..., dev_standby_time: int | None = ..., screen_off_time: int | None = ..., bat_temp102: int | None = ..., bms_err_code: int | None = ..., en_beep: int | None = ..., pd_err_code: int | None = ..., cms_batt_soc: float | None = ..., cms_dsg_rem_time: int | None = ..., cms_chg_rem_time: int | None = ..., cms_max_chg_soc: int | None = ..., cms_min_dsg_soc: int | None = ..., cms_chg_dsg_state: int | None = ..., cms_batt_design_cap: int | None = ..., plug_in_info_pv_flag: int | None = ..., plug_in_info_pv_type: int | None = ..., bms_main_sn: str | None = ..., plug_in_info_dcp_in_flag: int | None = ..., temp_unit: int | None = ..., set_point_left: float | None = ..., set_point_right: float | None = ..., child_lock: int | None = ..., simple_mode: int | None = ..., bat_protect: int | None = ..., cooling_mode: int | None = ..., temp_monitor_left: float | None = ..., temp_monitor_right: float | None = ..., lid_status: int | None = ..., zone_status: int | None = ..., temp_alert: int | None = ..., input_volt777: float | None = ...) -> None: ...

class GlacierClassicRuntimePropertyUpload(_message.Message):
    __slots__ = ("display_property_full_upload_period", "display_property_incremental_upload_period", "plug_in_info_ac_in_vol", "runtime_property_full_upload_period", "runtime_property_incremental_upload_period")
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
    def __init__(self, plug_in_info_ac_in_vol: float | None = ..., display_property_full_upload_period: int | None = ..., display_property_incremental_upload_period: int | None = ..., runtime_property_full_upload_period: int | None = ..., runtime_property_incremental_upload_period: int | None = ...) -> None: ...

class GlacierClassicSetCommand(_message.Message):
    __slots__ = ("bat_protect", "child_lock", "cms_max_chg_soc", "cms_min_dsg_soc", "cooling_mode", "dev_standby_time", "en_beep", "set_point_left", "set_point_right", "simple_mode", "standby", "temp_alert")
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
    def __init__(self, en_beep: int | None = ..., dev_standby_time: int | None = ..., cms_max_chg_soc: int | None = ..., cms_min_dsg_soc: int | None = ..., standby: int | None = ..., set_point_left: float | None = ..., set_point_right: float | None = ..., child_lock: int | None = ..., simple_mode: int | None = ..., bat_protect: int | None = ..., cooling_mode: int | None = ..., temp_alert: int | None = ...) -> None: ...
