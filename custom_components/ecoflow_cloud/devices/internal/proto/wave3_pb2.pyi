from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper

DESCRIPTOR: _descriptor.FileDescriptor

class WAVE3_TIME_TASK_MODE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TIME_TASK_MODE_RESV: _ClassVar[WAVE3_TIME_TASK_MODE]
    TIME_TASK_MODE_PER_WEEK: _ClassVar[WAVE3_TIME_TASK_MODE]
    TIME_TASK_MODE_ONCE: _ClassVar[WAVE3_TIME_TASK_MODE]

class WAVE3_TIME_TASK_TYPE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TIME_TASK_TYPE_AC_CHG: _ClassVar[WAVE3_TIME_TASK_TYPE]
    TIME_TASK_TYPE_AC_DSG: _ClassVar[WAVE3_TIME_TASK_TYPE]
    TIME_TASK_TYPE_AC2_DSG: _ClassVar[WAVE3_TIME_TASK_TYPE]
    TIME_TASK_TYPE_DC_CHG: _ClassVar[WAVE3_TIME_TASK_TYPE]
    TIME_TASK_TYPE_DC2_CHG: _ClassVar[WAVE3_TIME_TASK_TYPE]
    TIME_TASK_TYPE_DC_DSG: _ClassVar[WAVE3_TIME_TASK_TYPE]
    TIME_TASK_TYPE_OIL_ON: _ClassVar[WAVE3_TIME_TASK_TYPE]
    TIME_TASK_TYPE_OIL_OFF: _ClassVar[WAVE3_TIME_TASK_TYPE]
    TIME_TASK_TYPE_USB_CHG: _ClassVar[WAVE3_TIME_TASK_TYPE]
    TIME_TASK_TYPE_USB_DSG: _ClassVar[WAVE3_TIME_TASK_TYPE]

class WAVE3_TIME_TASK_DETAIL_TYPE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TIME_TASK_DETAIL_IDLE: _ClassVar[WAVE3_TIME_TASK_DETAIL_TYPE]
    TIME_TASK_DETAIL_POW: _ClassVar[WAVE3_TIME_TASK_DETAIL_TYPE]
    TIME_TASK_DETAIL_TEMP: _ClassVar[WAVE3_TIME_TASK_DETAIL_TYPE]
    TIME_TASK_DETAIL_LEVEL: _ClassVar[WAVE3_TIME_TASK_DETAIL_TYPE]

class USER_TEMP_UNIT_TYPE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    USER_TEMP_UNIT_NONE: _ClassVar[USER_TEMP_UNIT_TYPE]
    USER_TEMP_UNIT_C: _ClassVar[USER_TEMP_UNIT_TYPE]
    USER_TEMP_UNIT_F: _ClassVar[USER_TEMP_UNIT_TYPE]
TIME_TASK_MODE_RESV: WAVE3_TIME_TASK_MODE
TIME_TASK_MODE_PER_WEEK: WAVE3_TIME_TASK_MODE
TIME_TASK_MODE_ONCE: WAVE3_TIME_TASK_MODE
TIME_TASK_TYPE_AC_CHG: WAVE3_TIME_TASK_TYPE
TIME_TASK_TYPE_AC_DSG: WAVE3_TIME_TASK_TYPE
TIME_TASK_TYPE_AC2_DSG: WAVE3_TIME_TASK_TYPE
TIME_TASK_TYPE_DC_CHG: WAVE3_TIME_TASK_TYPE
TIME_TASK_TYPE_DC2_CHG: WAVE3_TIME_TASK_TYPE
TIME_TASK_TYPE_DC_DSG: WAVE3_TIME_TASK_TYPE
TIME_TASK_TYPE_OIL_ON: WAVE3_TIME_TASK_TYPE
TIME_TASK_TYPE_OIL_OFF: WAVE3_TIME_TASK_TYPE
TIME_TASK_TYPE_USB_CHG: WAVE3_TIME_TASK_TYPE
TIME_TASK_TYPE_USB_DSG: WAVE3_TIME_TASK_TYPE
TIME_TASK_DETAIL_IDLE: WAVE3_TIME_TASK_DETAIL_TYPE
TIME_TASK_DETAIL_POW: WAVE3_TIME_TASK_DETAIL_TYPE
TIME_TASK_DETAIL_TEMP: WAVE3_TIME_TASK_DETAIL_TYPE
TIME_TASK_DETAIL_LEVEL: WAVE3_TIME_TASK_DETAIL_TYPE
USER_TEMP_UNIT_NONE: USER_TEMP_UNIT_TYPE
USER_TEMP_UNIT_C: USER_TEMP_UNIT_TYPE
USER_TEMP_UNIT_F: USER_TEMP_UNIT_TYPE

class Wave3AppRuquestBpEuLawData(_message.Message):
    __slots__ = ("app_launch_date_set_type", "app_to_bms_launch_date", "app_to_bms_reset_flag", "bms_data_upload_en", "pack_sn")
    PACK_SN_FIELD_NUMBER: _ClassVar[int]
    APP_TO_BMS_LAUNCH_DATE_FIELD_NUMBER: _ClassVar[int]
    APP_LAUNCH_DATE_SET_TYPE_FIELD_NUMBER: _ClassVar[int]
    APP_TO_BMS_RESET_FLAG_FIELD_NUMBER: _ClassVar[int]
    BMS_DATA_UPLOAD_EN_FIELD_NUMBER: _ClassVar[int]
    pack_sn: str
    app_to_bms_launch_date: int
    app_launch_date_set_type: int
    app_to_bms_reset_flag: int
    bms_data_upload_en: int
    def __init__(self, pack_sn: str | None = ..., app_to_bms_launch_date: int | None = ..., app_launch_date_set_type: int | None = ..., app_to_bms_reset_flag: int | None = ..., bms_data_upload_en: int | None = ...) -> None: ...

class Wave3ConfigReadAck(_message.Message):
    __slots__ = ("cfg_utc_time", "cfg_utc_timezone", "get_bms_firm_ver", "get_inv_firm_ver", "get_iot_firm_ver", "get_llc_firm_ver", "get_mppt_firm_ver", "get_pd_firm_ver", "get_time_task_list", "read_time_task_v2_list")
    CFG_UTC_TIME_FIELD_NUMBER: _ClassVar[int]
    CFG_UTC_TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    GET_TIME_TASK_LIST_FIELD_NUMBER: _ClassVar[int]
    READ_TIME_TASK_V2_LIST_FIELD_NUMBER: _ClassVar[int]
    GET_PD_FIRM_VER_FIELD_NUMBER: _ClassVar[int]
    GET_IOT_FIRM_VER_FIELD_NUMBER: _ClassVar[int]
    GET_MPPT_FIRM_VER_FIELD_NUMBER: _ClassVar[int]
    GET_LLC_FIRM_VER_FIELD_NUMBER: _ClassVar[int]
    GET_INV_FIRM_VER_FIELD_NUMBER: _ClassVar[int]
    GET_BMS_FIRM_VER_FIELD_NUMBER: _ClassVar[int]
    cfg_utc_time: int
    cfg_utc_timezone: int
    get_time_task_list: Wave3GetAllTimeTaskReadck
    read_time_task_v2_list: Wave3TimeTaskItemV2List
    get_pd_firm_ver: int
    get_iot_firm_ver: int
    get_mppt_firm_ver: int
    get_llc_firm_ver: int
    get_inv_firm_ver: int
    get_bms_firm_ver: int
    def __init__(self, cfg_utc_time: int | None = ..., cfg_utc_timezone: int | None = ..., get_time_task_list: Wave3GetAllTimeTaskReadck | _Mapping | None = ..., read_time_task_v2_list: Wave3TimeTaskItemV2List | _Mapping | None = ..., get_pd_firm_ver: int | None = ..., get_iot_firm_ver: int | None = ..., get_mppt_firm_ver: int | None = ..., get_llc_firm_ver: int | None = ..., get_inv_firm_ver: int | None = ..., get_bms_firm_ver: int | None = ...) -> None: ...

class Wave3ConfigRead(_message.Message):
    __slots__ = ("action_id",)
    ACTION_ID_FIELD_NUMBER: _ClassVar[int]
    action_id: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, action_id: _Iterable[int] | None = ...) -> None: ...

class Wave3ResvInfo(_message.Message):
    __slots__ = ("resv_info",)
    RESV_INFO_FIELD_NUMBER: _ClassVar[int]
    resv_info: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, resv_info: _Iterable[int] | None = ...) -> None: ...

class Wave3TimeTaskParamDetail(_message.Message):
    __slots__ = ("type", "val")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VAL_FIELD_NUMBER: _ClassVar[int]
    type: WAVE3_TIME_TASK_DETAIL_TYPE
    val: float
    def __init__(self, type: WAVE3_TIME_TASK_DETAIL_TYPE | str | None = ..., val: float | None = ...) -> None: ...

class Wave3TimeTaskItemV2(_message.Message):
    __slots__ = ("conflict_flag", "is_cfg", "is_enable", "task_index", "task_param", "task_param_detail", "task_type", "time_mode", "time_param", "time_table")
    TASK_INDEX_FIELD_NUMBER: _ClassVar[int]
    IS_CFG_FIELD_NUMBER: _ClassVar[int]
    IS_ENABLE_FIELD_NUMBER: _ClassVar[int]
    CONFLICT_FLAG_FIELD_NUMBER: _ClassVar[int]
    TIME_MODE_FIELD_NUMBER: _ClassVar[int]
    TIME_PARAM_FIELD_NUMBER: _ClassVar[int]
    TIME_TABLE_FIELD_NUMBER: _ClassVar[int]
    TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    TASK_PARAM_FIELD_NUMBER: _ClassVar[int]
    TASK_PARAM_DETAIL_FIELD_NUMBER: _ClassVar[int]
    task_index: int
    is_cfg: bool
    is_enable: bool
    conflict_flag: int
    time_mode: WAVE3_TIME_TASK_MODE
    time_param: int
    time_table: int
    task_type: WAVE3_TIME_TASK_TYPE
    task_param: int
    task_param_detail: _containers.RepeatedCompositeFieldContainer[Wave3TimeTaskParamDetail]
    def __init__(self, task_index: int | None = ..., is_cfg: bool | None = ..., is_enable: bool | None = ..., conflict_flag: int | None = ..., time_mode: WAVE3_TIME_TASK_MODE | str | None = ..., time_param: int | None = ..., time_table: int | None = ..., task_type: WAVE3_TIME_TASK_TYPE | str | None = ..., task_param: int | None = ..., task_param_detail: _Iterable[Wave3TimeTaskParamDetail | _Mapping] | None = ...) -> None: ...

class Wave3TimeTaskItemV2List(_message.Message):
    __slots__ = ("time_task",)
    TIME_TASK_FIELD_NUMBER: _ClassVar[int]
    time_task: _containers.RepeatedCompositeFieldContainer[Wave3TimeTaskItemV2]
    def __init__(self, time_task: _Iterable[Wave3TimeTaskItemV2 | _Mapping] | None = ...) -> None: ...

class Wave3RuntimePropertyUpload(_message.Message):
    __slots__ = ("bms_alm_state", "bms_alm_state_2", "bms_bal_state", "bms_batt_amp", "bms_batt_vol", "bms_err_code", "bms_firm_ver", "bms_flt_state", "bms_full_cap", "bms_high_temp_icon", "bms_limit_icon", "bms_low_temp_icon", "bms_max_cell_vol", "bms_min_cell_vol", "bms_overload_icon", "bms_pro_state", "bms_pro_state_2", "bms_remain_cap", "bms_warn_icon", "cms_batt_amp", "cms_batt_vol", "cms_chg_req_amp", "cms_chg_req_vol", "display_property_full_upload_period", "display_property_incremental_upload_period", "iot_firm_ver", "llc_firm_ver", "mppt_firm_ver", "pd_bms_comm_err", "pd_firm_ver", "pd_iot_comm_err", "pd_llc_comm_err", "pd_mppt_comm_err", "plug_in_info_ac_in_amp", "plug_in_info_ac_in_vol", "plug_in_info_bms_vol", "plug_in_info_dcp_amp", "plug_in_info_dcp_vol", "plug_in_info_pv_amp", "plug_in_info_pv_vol", "runtime_property_full_upload_period", "runtime_property_incremental_upload_period", "temp_compressor_discharge", "temp_condenser", "temp_evaporator", "temp_indoor_return_air", "temp_outdoor_ambient", "temp_pcs_ac", "temp_pcs_dc", "temp_pv")
    TEMP_PCS_DC_FIELD_NUMBER: _ClassVar[int]
    TEMP_PCS_AC_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_AC_IN_VOL_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_BMS_VOL_FIELD_NUMBER: _ClassVar[int]
    PD_MPPT_COMM_ERR_FIELD_NUMBER: _ClassVar[int]
    PD_LLC_COMM_ERR_FIELD_NUMBER: _ClassVar[int]
    PD_BMS_COMM_ERR_FIELD_NUMBER: _ClassVar[int]
    PD_IOT_COMM_ERR_FIELD_NUMBER: _ClassVar[int]
    PD_FIRM_VER_FIELD_NUMBER: _ClassVar[int]
    IOT_FIRM_VER_FIELD_NUMBER: _ClassVar[int]
    MPPT_FIRM_VER_FIELD_NUMBER: _ClassVar[int]
    LLC_FIRM_VER_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_AC_IN_AMP_FIELD_NUMBER: _ClassVar[int]
    BMS_FIRM_VER_FIELD_NUMBER: _ClassVar[int]
    BMS_BATT_VOL_FIELD_NUMBER: _ClassVar[int]
    BMS_BATT_AMP_FIELD_NUMBER: _ClassVar[int]
    BMS_BAL_STATE_FIELD_NUMBER: _ClassVar[int]
    BMS_FULL_CAP_FIELD_NUMBER: _ClassVar[int]
    BMS_REMAIN_CAP_FIELD_NUMBER: _ClassVar[int]
    BMS_ALM_STATE_FIELD_NUMBER: _ClassVar[int]
    BMS_PRO_STATE_FIELD_NUMBER: _ClassVar[int]
    BMS_FLT_STATE_FIELD_NUMBER: _ClassVar[int]
    BMS_ERR_CODE_FIELD_NUMBER: _ClassVar[int]
    BMS_MIN_CELL_VOL_FIELD_NUMBER: _ClassVar[int]
    BMS_MAX_CELL_VOL_FIELD_NUMBER: _ClassVar[int]
    CMS_BATT_VOL_FIELD_NUMBER: _ClassVar[int]
    CMS_BATT_AMP_FIELD_NUMBER: _ClassVar[int]
    CMS_CHG_REQ_VOL_FIELD_NUMBER: _ClassVar[int]
    CMS_CHG_REQ_AMP_FIELD_NUMBER: _ClassVar[int]
    BMS_OVERLOAD_ICON_FIELD_NUMBER: _ClassVar[int]
    BMS_WARN_ICON_FIELD_NUMBER: _ClassVar[int]
    BMS_HIGH_TEMP_ICON_FIELD_NUMBER: _ClassVar[int]
    BMS_LOW_TEMP_ICON_FIELD_NUMBER: _ClassVar[int]
    BMS_LIMIT_ICON_FIELD_NUMBER: _ClassVar[int]
    BMS_ALM_STATE_2_FIELD_NUMBER: _ClassVar[int]
    BMS_PRO_STATE_2_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_PROPERTY_FULL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_PROPERTY_INCREMENTAL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_PROPERTY_FULL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_PROPERTY_INCREMENTAL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    TEMP_PV_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_PV_VOL_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_PV_AMP_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_DCP_VOL_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_DCP_AMP_FIELD_NUMBER: _ClassVar[int]
    TEMP_INDOOR_RETURN_AIR_FIELD_NUMBER: _ClassVar[int]
    TEMP_OUTDOOR_AMBIENT_FIELD_NUMBER: _ClassVar[int]
    TEMP_CONDENSER_FIELD_NUMBER: _ClassVar[int]
    TEMP_EVAPORATOR_FIELD_NUMBER: _ClassVar[int]
    TEMP_COMPRESSOR_DISCHARGE_FIELD_NUMBER: _ClassVar[int]
    temp_pcs_dc: float
    temp_pcs_ac: float
    plug_in_info_ac_in_vol: float
    plug_in_info_bms_vol: float
    pd_mppt_comm_err: int
    pd_llc_comm_err: int
    pd_bms_comm_err: int
    pd_iot_comm_err: int
    pd_firm_ver: int
    iot_firm_ver: int
    mppt_firm_ver: int
    llc_firm_ver: int
    plug_in_info_ac_in_amp: float
    bms_firm_ver: int
    bms_batt_vol: float
    bms_batt_amp: float
    bms_bal_state: int
    bms_full_cap: int
    bms_remain_cap: int
    bms_alm_state: int
    bms_pro_state: int
    bms_flt_state: int
    bms_err_code: int
    bms_min_cell_vol: int
    bms_max_cell_vol: int
    cms_batt_vol: float
    cms_batt_amp: float
    cms_chg_req_vol: float
    cms_chg_req_amp: float
    bms_overload_icon: int
    bms_warn_icon: int
    bms_high_temp_icon: int
    bms_low_temp_icon: int
    bms_limit_icon: int
    bms_alm_state_2: int
    bms_pro_state_2: int
    display_property_full_upload_period: int
    display_property_incremental_upload_period: int
    runtime_property_full_upload_period: int
    runtime_property_incremental_upload_period: int
    temp_pv: float
    plug_in_info_pv_vol: float
    plug_in_info_pv_amp: float
    plug_in_info_dcp_vol: float
    plug_in_info_dcp_amp: float
    temp_indoor_return_air: float
    temp_outdoor_ambient: float
    temp_condenser: float
    temp_evaporator: float
    temp_compressor_discharge: float
    def __init__(self, temp_pcs_dc: float | None = ..., temp_pcs_ac: float | None = ..., plug_in_info_ac_in_vol: float | None = ..., plug_in_info_bms_vol: float | None = ..., pd_mppt_comm_err: int | None = ..., pd_llc_comm_err: int | None = ..., pd_bms_comm_err: int | None = ..., pd_iot_comm_err: int | None = ..., pd_firm_ver: int | None = ..., iot_firm_ver: int | None = ..., mppt_firm_ver: int | None = ..., llc_firm_ver: int | None = ..., plug_in_info_ac_in_amp: float | None = ..., bms_firm_ver: int | None = ..., bms_batt_vol: float | None = ..., bms_batt_amp: float | None = ..., bms_bal_state: int | None = ..., bms_full_cap: int | None = ..., bms_remain_cap: int | None = ..., bms_alm_state: int | None = ..., bms_pro_state: int | None = ..., bms_flt_state: int | None = ..., bms_err_code: int | None = ..., bms_min_cell_vol: int | None = ..., bms_max_cell_vol: int | None = ..., cms_batt_vol: float | None = ..., cms_batt_amp: float | None = ..., cms_chg_req_vol: float | None = ..., cms_chg_req_amp: float | None = ..., bms_overload_icon: int | None = ..., bms_warn_icon: int | None = ..., bms_high_temp_icon: int | None = ..., bms_low_temp_icon: int | None = ..., bms_limit_icon: int | None = ..., bms_alm_state_2: int | None = ..., bms_pro_state_2: int | None = ..., display_property_full_upload_period: int | None = ..., display_property_incremental_upload_period: int | None = ..., runtime_property_full_upload_period: int | None = ..., runtime_property_incremental_upload_period: int | None = ..., temp_pv: float | None = ..., plug_in_info_pv_vol: float | None = ..., plug_in_info_pv_amp: float | None = ..., plug_in_info_dcp_vol: float | None = ..., plug_in_info_dcp_amp: float | None = ..., temp_indoor_return_air: float | None = ..., temp_outdoor_ambient: float | None = ..., temp_condenser: float | None = ..., temp_evaporator: float | None = ..., temp_compressor_discharge: float | None = ...) -> None: ...

class Wave3DevErrcodeList(_message.Message):
    __slots__ = ("dev_errcode",)
    DEV_ERRCODE_FIELD_NUMBER: _ClassVar[int]
    dev_errcode: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, dev_errcode: _Iterable[int] | None = ...) -> None: ...

class Wave3WaveOperatingModeParamItem(_message.Message):
    __slots__ = ("airflow_speed", "humi_set", "submode", "temp_set", "temp_thermostatic_lower_limit", "temp_thermostatic_upper_limit")
    SUBMODE_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_SPEED_FIELD_NUMBER: _ClassVar[int]
    TEMP_SET_FIELD_NUMBER: _ClassVar[int]
    HUMI_SET_FIELD_NUMBER: _ClassVar[int]
    TEMP_THERMOSTATIC_UPPER_LIMIT_FIELD_NUMBER: _ClassVar[int]
    TEMP_THERMOSTATIC_LOWER_LIMIT_FIELD_NUMBER: _ClassVar[int]
    submode: int
    airflow_speed: int
    temp_set: float
    humi_set: float
    temp_thermostatic_upper_limit: float
    temp_thermostatic_lower_limit: float
    def __init__(self, submode: int | None = ..., airflow_speed: int | None = ..., temp_set: float | None = ..., humi_set: float | None = ..., temp_thermostatic_upper_limit: float | None = ..., temp_thermostatic_lower_limit: float | None = ...) -> None: ...

class Wave3WaveOperatingModeParamList(_message.Message):
    __slots__ = ("list_info",)
    LIST_INFO_FIELD_NUMBER: _ClassVar[int]
    list_info: _containers.RepeatedCompositeFieldContainer[Wave3WaveOperatingModeParamItem]
    def __init__(self, list_info: _Iterable[Wave3WaveOperatingModeParamItem | _Mapping] | None = ...) -> None: ...

class Wave3DisplayPropertyUpload(_message.Message):
    __slots__ = ("bms_batt_soc", "bms_batt_soh", "bms_chg_dsg_state", "bms_chg_rem_time", "bms_design_cap", "bms_dsg_rem_time", "bms_err_code", "bms_main_sn", "bms_max_cell_temp", "bms_max_mos_temp", "bms_min_cell_temp", "bms_min_mos_temp", "cms_batt_soc", "cms_batt_soh", "cms_bms_run_state", "cms_chg_dsg_state", "cms_chg_rem_time", "cms_dsg_rem_time", "cms_max_chg_soc", "cms_min_dsg_soc", "condensate_water_level", "current_time_task_v2_item", "dev_errcode_list", "dev_sleep_state", "dev_standby_time", "drainage_mode", "en_beep", "en_pet_care", "errcode", "flow_info_ac2dc", "flow_info_ac_in", "flow_info_bms_chg", "flow_info_bms_dsg", "flow_info_dcp_in", "flow_info_dcp_out", "flow_info_pv", "flow_info_qcusb1", "flow_info_typec1", "humi_ambient", "in_drainage", "lcd_light", "lcd_show_temp_type", "mood_light_mode", "pcs_fan_level", "pd_err_code", "pet_care_warning", "plug_in_info_ac_charger_flag", "plug_in_info_ac_in_chg_hal_pow_max", "plug_in_info_ac_in_chg_pow_max", "plug_in_info_ac_in_feq", "plug_in_info_ac_in_flag", "plug_in_info_ac_out_dsg_pow_max", "plug_in_info_dcp_charger_flag", "plug_in_info_dcp_detail", "plug_in_info_dcp_dsg_chg_type", "plug_in_info_dcp_err_code", "plug_in_info_dcp_firm_ver", "plug_in_info_dcp_in_flag", "plug_in_info_dcp_resv", "plug_in_info_dcp_run_state", "plug_in_info_dcp_sn", "plug_in_info_dcp_type", "plug_in_info_pv_charger_flag", "plug_in_info_pv_chg_amp_max", "plug_in_info_pv_chg_vol_max", "plug_in_info_pv_dc_amp_max", "plug_in_info_pv_type", "pow_get_ac", "pow_get_ac_in", "pow_get_bms", "pow_get_dcp", "pow_get_pv", "pow_get_qcusb1", "pow_get_self_consume", "pow_get_typec1", "pow_in_sum_w", "pow_out_sum_w", "power_off_delay_remaining", "power_off_delay_set", "screen_off_time", "temp_ambient", "temp_indoor_supply_air", "temp_pet_care_warning", "time_task_change_cnt", "time_task_conflict_flag", "user_temp_unit", "utc_set_mode", "utc_timezone", "utc_timezone_id", "wave_mode_info", "wave_operating_mode")
    ERRCODE_FIELD_NUMBER: _ClassVar[int]
    POW_IN_SUM_W_FIELD_NUMBER: _ClassVar[int]
    POW_OUT_SUM_W_FIELD_NUMBER: _ClassVar[int]
    LCD_LIGHT_FIELD_NUMBER: _ClassVar[int]
    POW_GET_QCUSB1_FIELD_NUMBER: _ClassVar[int]
    POW_GET_TYPEC1_FIELD_NUMBER: _ClassVar[int]
    FLOW_INFO_QCUSB1_FIELD_NUMBER: _ClassVar[int]
    FLOW_INFO_TYPEC1_FIELD_NUMBER: _ClassVar[int]
    DEV_STANDBY_TIME_FIELD_NUMBER: _ClassVar[int]
    SCREEN_OFF_TIME_FIELD_NUMBER: _ClassVar[int]
    PCS_FAN_LEVEL_FIELD_NUMBER: _ClassVar[int]
    FLOW_INFO_AC2DC_FIELD_NUMBER: _ClassVar[int]
    FLOW_INFO_AC_IN_FIELD_NUMBER: _ClassVar[int]
    POW_GET_AC_FIELD_NUMBER: _ClassVar[int]
    POW_GET_AC_IN_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_AC_IN_FLAG_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_AC_IN_FEQ_FIELD_NUMBER: _ClassVar[int]
    CURRENT_TIME_TASK_V2_ITEM_FIELD_NUMBER: _ClassVar[int]
    UTC_TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    UTC_TIMEZONE_ID_FIELD_NUMBER: _ClassVar[int]
    UTC_SET_MODE_FIELD_NUMBER: _ClassVar[int]
    BMS_ERR_CODE_FIELD_NUMBER: _ClassVar[int]
    FLOW_INFO_BMS_DSG_FIELD_NUMBER: _ClassVar[int]
    FLOW_INFO_BMS_CHG_FIELD_NUMBER: _ClassVar[int]
    POW_GET_BMS_FIELD_NUMBER: _ClassVar[int]
    EN_BEEP_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_AC_CHARGER_FLAG_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_AC_IN_CHG_POW_MAX_FIELD_NUMBER: _ClassVar[int]
    DEV_SLEEP_STATE_FIELD_NUMBER: _ClassVar[int]
    PD_ERR_CODE_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_AC_OUT_DSG_POW_MAX_FIELD_NUMBER: _ClassVar[int]
    BMS_BATT_SOC_FIELD_NUMBER: _ClassVar[int]
    BMS_BATT_SOH_FIELD_NUMBER: _ClassVar[int]
    BMS_DESIGN_CAP_FIELD_NUMBER: _ClassVar[int]
    BMS_DSG_REM_TIME_FIELD_NUMBER: _ClassVar[int]
    BMS_CHG_REM_TIME_FIELD_NUMBER: _ClassVar[int]
    BMS_MIN_CELL_TEMP_FIELD_NUMBER: _ClassVar[int]
    BMS_MAX_CELL_TEMP_FIELD_NUMBER: _ClassVar[int]
    BMS_MIN_MOS_TEMP_FIELD_NUMBER: _ClassVar[int]
    BMS_MAX_MOS_TEMP_FIELD_NUMBER: _ClassVar[int]
    CMS_BATT_SOC_FIELD_NUMBER: _ClassVar[int]
    CMS_BATT_SOH_FIELD_NUMBER: _ClassVar[int]
    CMS_DSG_REM_TIME_FIELD_NUMBER: _ClassVar[int]
    CMS_CHG_REM_TIME_FIELD_NUMBER: _ClassVar[int]
    CMS_MAX_CHG_SOC_FIELD_NUMBER: _ClassVar[int]
    CMS_MIN_DSG_SOC_FIELD_NUMBER: _ClassVar[int]
    CMS_BMS_RUN_STATE_FIELD_NUMBER: _ClassVar[int]
    BMS_CHG_DSG_STATE_FIELD_NUMBER: _ClassVar[int]
    CMS_CHG_DSG_STATE_FIELD_NUMBER: _ClassVar[int]
    TIME_TASK_CONFLICT_FLAG_FIELD_NUMBER: _ClassVar[int]
    TIME_TASK_CHANGE_CNT_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_PV_DC_AMP_MAX_FIELD_NUMBER: _ClassVar[int]
    FLOW_INFO_PV_FIELD_NUMBER: _ClassVar[int]
    POW_GET_PV_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_PV_TYPE_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_PV_CHARGER_FLAG_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_PV_CHG_AMP_MAX_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_PV_CHG_VOL_MAX_FIELD_NUMBER: _ClassVar[int]
    BMS_MAIN_SN_FIELD_NUMBER: _ClassVar[int]
    FLOW_INFO_DCP_IN_FIELD_NUMBER: _ClassVar[int]
    FLOW_INFO_DCP_OUT_FIELD_NUMBER: _ClassVar[int]
    POW_GET_DCP_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_DCP_IN_FLAG_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_DCP_TYPE_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_DCP_DETAIL_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_DCP_DSG_CHG_TYPE_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_DCP_RESV_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_DCP_SN_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_DCP_FIRM_VER_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_DCP_CHARGER_FLAG_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_DCP_RUN_STATE_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_DCP_ERR_CODE_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_AC_IN_CHG_HAL_POW_MAX_FIELD_NUMBER: _ClassVar[int]
    TEMP_AMBIENT_FIELD_NUMBER: _ClassVar[int]
    HUMI_AMBIENT_FIELD_NUMBER: _ClassVar[int]
    WAVE_OPERATING_MODE_FIELD_NUMBER: _ClassVar[int]
    TEMP_INDOOR_SUPPLY_AIR_FIELD_NUMBER: _ClassVar[int]
    CONDENSATE_WATER_LEVEL_FIELD_NUMBER: _ClassVar[int]
    IN_DRAINAGE_FIELD_NUMBER: _ClassVar[int]
    DRAINAGE_MODE_FIELD_NUMBER: _ClassVar[int]
    MOOD_LIGHT_MODE_FIELD_NUMBER: _ClassVar[int]
    LCD_SHOW_TEMP_TYPE_FIELD_NUMBER: _ClassVar[int]
    EN_PET_CARE_FIELD_NUMBER: _ClassVar[int]
    TEMP_PET_CARE_WARNING_FIELD_NUMBER: _ClassVar[int]
    USER_TEMP_UNIT_FIELD_NUMBER: _ClassVar[int]
    PET_CARE_WARNING_FIELD_NUMBER: _ClassVar[int]
    WAVE_MODE_INFO_FIELD_NUMBER: _ClassVar[int]
    DEV_ERRCODE_LIST_FIELD_NUMBER: _ClassVar[int]
    POW_GET_SELF_CONSUME_FIELD_NUMBER: _ClassVar[int]
    POWER_OFF_DELAY_SET_FIELD_NUMBER: _ClassVar[int]
    POWER_OFF_DELAY_REMAINING_FIELD_NUMBER: _ClassVar[int]
    errcode: int
    pow_in_sum_w: float
    pow_out_sum_w: float
    lcd_light: int
    pow_get_qcusb1: float
    pow_get_typec1: float
    flow_info_qcusb1: int
    flow_info_typec1: int
    dev_standby_time: int
    screen_off_time: int
    pcs_fan_level: int
    flow_info_ac2dc: int
    flow_info_ac_in: int
    pow_get_ac: float
    pow_get_ac_in: float
    plug_in_info_ac_in_flag: int
    plug_in_info_ac_in_feq: int
    current_time_task_v2_item: Wave3TimeTaskItemV2
    utc_timezone: int
    utc_timezone_id: str
    utc_set_mode: bool
    bms_err_code: int
    flow_info_bms_dsg: int
    flow_info_bms_chg: int
    pow_get_bms: float
    en_beep: bool
    plug_in_info_ac_charger_flag: bool
    plug_in_info_ac_in_chg_pow_max: int
    dev_sleep_state: int
    pd_err_code: int
    plug_in_info_ac_out_dsg_pow_max: int
    bms_batt_soc: float
    bms_batt_soh: float
    bms_design_cap: int
    bms_dsg_rem_time: int
    bms_chg_rem_time: int
    bms_min_cell_temp: int
    bms_max_cell_temp: int
    bms_min_mos_temp: int
    bms_max_mos_temp: int
    cms_batt_soc: float
    cms_batt_soh: float
    cms_dsg_rem_time: int
    cms_chg_rem_time: int
    cms_max_chg_soc: int
    cms_min_dsg_soc: int
    cms_bms_run_state: int
    bms_chg_dsg_state: int
    cms_chg_dsg_state: int
    time_task_conflict_flag: int
    time_task_change_cnt: int
    plug_in_info_pv_dc_amp_max: int
    flow_info_pv: int
    pow_get_pv: float
    plug_in_info_pv_type: int
    plug_in_info_pv_charger_flag: bool
    plug_in_info_pv_chg_amp_max: int
    plug_in_info_pv_chg_vol_max: int
    bms_main_sn: str
    flow_info_dcp_in: int
    flow_info_dcp_out: int
    pow_get_dcp: float
    plug_in_info_dcp_in_flag: bool
    plug_in_info_dcp_type: int
    plug_in_info_dcp_detail: int
    plug_in_info_dcp_dsg_chg_type: int
    plug_in_info_dcp_resv: Wave3ResvInfo
    plug_in_info_dcp_sn: str
    plug_in_info_dcp_firm_ver: int
    plug_in_info_dcp_charger_flag: bool
    plug_in_info_dcp_run_state: int
    plug_in_info_dcp_err_code: int
    plug_in_info_ac_in_chg_hal_pow_max: int
    temp_ambient: float
    humi_ambient: float
    wave_operating_mode: int
    temp_indoor_supply_air: float
    condensate_water_level: float
    in_drainage: bool
    drainage_mode: int
    mood_light_mode: int
    lcd_show_temp_type: int
    en_pet_care: bool
    temp_pet_care_warning: float
    user_temp_unit: USER_TEMP_UNIT_TYPE
    pet_care_warning: bool
    wave_mode_info: Wave3WaveOperatingModeParamList
    dev_errcode_list: Wave3DevErrcodeList
    pow_get_self_consume: float
    power_off_delay_set: int
    power_off_delay_remaining: int
    def __init__(self, errcode: int | None = ..., pow_in_sum_w: float | None = ..., pow_out_sum_w: float | None = ..., lcd_light: int | None = ..., pow_get_qcusb1: float | None = ..., pow_get_typec1: float | None = ..., flow_info_qcusb1: int | None = ..., flow_info_typec1: int | None = ..., dev_standby_time: int | None = ..., screen_off_time: int | None = ..., pcs_fan_level: int | None = ..., flow_info_ac2dc: int | None = ..., flow_info_ac_in: int | None = ..., pow_get_ac: float | None = ..., pow_get_ac_in: float | None = ..., plug_in_info_ac_in_flag: int | None = ..., plug_in_info_ac_in_feq: int | None = ..., current_time_task_v2_item: Wave3TimeTaskItemV2 | _Mapping | None = ..., utc_timezone: int | None = ..., utc_timezone_id: str | None = ..., utc_set_mode: bool | None = ..., bms_err_code: int | None = ..., flow_info_bms_dsg: int | None = ..., flow_info_bms_chg: int | None = ..., pow_get_bms: float | None = ..., en_beep: bool | None = ..., plug_in_info_ac_charger_flag: bool | None = ..., plug_in_info_ac_in_chg_pow_max: int | None = ..., dev_sleep_state: int | None = ..., pd_err_code: int | None = ..., plug_in_info_ac_out_dsg_pow_max: int | None = ..., bms_batt_soc: float | None = ..., bms_batt_soh: float | None = ..., bms_design_cap: int | None = ..., bms_dsg_rem_time: int | None = ..., bms_chg_rem_time: int | None = ..., bms_min_cell_temp: int | None = ..., bms_max_cell_temp: int | None = ..., bms_min_mos_temp: int | None = ..., bms_max_mos_temp: int | None = ..., cms_batt_soc: float | None = ..., cms_batt_soh: float | None = ..., cms_dsg_rem_time: int | None = ..., cms_chg_rem_time: int | None = ..., cms_max_chg_soc: int | None = ..., cms_min_dsg_soc: int | None = ..., cms_bms_run_state: int | None = ..., bms_chg_dsg_state: int | None = ..., cms_chg_dsg_state: int | None = ..., time_task_conflict_flag: int | None = ..., time_task_change_cnt: int | None = ..., plug_in_info_pv_dc_amp_max: int | None = ..., flow_info_pv: int | None = ..., pow_get_pv: float | None = ..., plug_in_info_pv_type: int | None = ..., plug_in_info_pv_charger_flag: bool | None = ..., plug_in_info_pv_chg_amp_max: int | None = ..., plug_in_info_pv_chg_vol_max: int | None = ..., bms_main_sn: str | None = ..., flow_info_dcp_in: int | None = ..., flow_info_dcp_out: int | None = ..., pow_get_dcp: float | None = ..., plug_in_info_dcp_in_flag: bool | None = ..., plug_in_info_dcp_type: int | None = ..., plug_in_info_dcp_detail: int | None = ..., plug_in_info_dcp_dsg_chg_type: int | None = ..., plug_in_info_dcp_resv: Wave3ResvInfo | _Mapping | None = ..., plug_in_info_dcp_sn: str | None = ..., plug_in_info_dcp_firm_ver: int | None = ..., plug_in_info_dcp_charger_flag: bool | None = ..., plug_in_info_dcp_run_state: int | None = ..., plug_in_info_dcp_err_code: int | None = ..., plug_in_info_ac_in_chg_hal_pow_max: int | None = ..., temp_ambient: float | None = ..., humi_ambient: float | None = ..., wave_operating_mode: int | None = ..., temp_indoor_supply_air: float | None = ..., condensate_water_level: float | None = ..., in_drainage: bool | None = ..., drainage_mode: int | None = ..., mood_light_mode: int | None = ..., lcd_show_temp_type: int | None = ..., en_pet_care: bool | None = ..., temp_pet_care_warning: float | None = ..., user_temp_unit: USER_TEMP_UNIT_TYPE | str | None = ..., pet_care_warning: bool | None = ..., wave_mode_info: Wave3WaveOperatingModeParamList | _Mapping | None = ..., dev_errcode_list: Wave3DevErrcodeList | _Mapping | None = ..., pow_get_self_consume: float | None = ..., power_off_delay_set: int | None = ..., power_off_delay_remaining: int | None = ...) -> None: ...

class Wave3SetTimeTaskWrite(_message.Message):
    __slots__ = ("conflict_flag", "is_cfg", "is_enable", "is_valid", "task_index", "time_mode", "time_param", "time_table", "type")
    TASK_INDEX_FIELD_NUMBER: _ClassVar[int]
    IS_VALID_FIELD_NUMBER: _ClassVar[int]
    IS_CFG_FIELD_NUMBER: _ClassVar[int]
    IS_ENABLE_FIELD_NUMBER: _ClassVar[int]
    CONFLICT_FLAG_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TIME_MODE_FIELD_NUMBER: _ClassVar[int]
    TIME_PARAM_FIELD_NUMBER: _ClassVar[int]
    TIME_TABLE_FIELD_NUMBER: _ClassVar[int]
    task_index: int
    is_valid: bool
    is_cfg: bool
    is_enable: bool
    conflict_flag: int
    type: int
    time_mode: int
    time_param: int
    time_table: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, task_index: int | None = ..., is_valid: bool | None = ..., is_cfg: bool | None = ..., is_enable: bool | None = ..., conflict_flag: int | None = ..., type: int | None = ..., time_mode: int | None = ..., time_param: int | None = ..., time_table: _Iterable[int] | None = ...) -> None: ...

class Wave3SetTimeTaskWriteAck(_message.Message):
    __slots__ = ("sta", "task_index", "type")
    TASK_INDEX_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    STA_FIELD_NUMBER: _ClassVar[int]
    task_index: int
    type: int
    sta: int
    def __init__(self, task_index: int | None = ..., type: int | None = ..., sta: int | None = ...) -> None: ...

class Wave3GetAllTimeTaskReadck(_message.Message):
    __slots__ = ("time_task",)
    TIME_TASK_FIELD_NUMBER: _ClassVar[int]
    time_task: _containers.RepeatedCompositeFieldContainer[Wave3SetTimeTaskWrite]
    def __init__(self, time_task: _Iterable[Wave3SetTimeTaskWrite | _Mapping] | None = ...) -> None: ...

class Wave3CfgBmsPushWrite(_message.Message):
    __slots__ = ("bms_health_freq", "bms_health_open", "bms_heartbeap_freq", "bms_heartbeap_open")
    BMS_HEARTBEAP_OPEN_FIELD_NUMBER: _ClassVar[int]
    BMS_HEALTH_OPEN_FIELD_NUMBER: _ClassVar[int]
    BMS_HEARTBEAP_FREQ_FIELD_NUMBER: _ClassVar[int]
    BMS_HEALTH_FREQ_FIELD_NUMBER: _ClassVar[int]
    bms_heartbeap_open: bool
    bms_health_open: bool
    bms_heartbeap_freq: int
    bms_health_freq: int
    def __init__(self, bms_heartbeap_open: bool | None = ..., bms_health_open: bool | None = ..., bms_heartbeap_freq: int | None = ..., bms_health_freq: int | None = ...) -> None: ...

class Wave3CfgBmsPushWriteAck(_message.Message):
    __slots__ = ("bms_health_open", "bms_heartbeap_open")
    BMS_HEARTBEAP_OPEN_FIELD_NUMBER: _ClassVar[int]
    BMS_HEALTH_OPEN_FIELD_NUMBER: _ClassVar[int]
    bms_heartbeap_open: bool
    bms_health_open: bool
    def __init__(self, bms_heartbeap_open: bool | None = ..., bms_health_open: bool | None = ...) -> None: ...

class Wave3ConfigWrite(_message.Message):
    __slots__ = ("active_display_property_full_upload", "active_runtime_property_full_upload", "active_selected_time_task_v2", "cfgPowerOff", "cfg_airflow_speed", "cfg_bms_push", "cfg_display_property_full_upload_period", "cfg_display_property_incremental_upload_period", "cfg_drainage_mode", "cfg_en_pet_care", "cfg_humi_set", "cfg_lcd_show_temp_type", "cfg_main_power", "cfg_mood_light_mode", "cfg_plug_in_info_ac_in_chg_pow_max", "cfg_plug_in_info_pv_dc_amp_max", "cfg_power_off_delay_set", "cfg_runtime_property_full_upload_period", "cfg_runtime_property_incremental_upload_period", "cfg_soc_cali", "cfg_sys_pause", "cfg_temp_pet_care_warning", "cfg_temp_set", "cfg_temp_thermostatic_lower_limit", "cfg_temp_thermostatic_upper_limit", "cfg_time_task_v2_item", "cfg_user_temp_unit", "cfg_utc_set_mode", "cfg_utc_time", "cfg_utc_timezone", "cfg_utc_timezone_id", "cfg_wave_operating_mode", "cfg_wave_operating_submode", "cmsMaxChgSoc", "cmsMinDsgSoc", "devStandbyTime", "enBeep", "lcdLight", "screenOffTime", "set_time_task")
    CFGPOWEROFF_FIELD_NUMBER: _ClassVar[int]
    CFG_MAIN_POWER_FIELD_NUMBER: _ClassVar[int]
    CFG_UTC_TIME_FIELD_NUMBER: _ClassVar[int]
    CFG_UTC_TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    ENBEEP_FIELD_NUMBER: _ClassVar[int]
    SCREENOFFTIME_FIELD_NUMBER: _ClassVar[int]
    DEVSTANDBYTIME_FIELD_NUMBER: _ClassVar[int]
    LCDLIGHT_FIELD_NUMBER: _ClassVar[int]
    CMSMAXCHGSOC_FIELD_NUMBER: _ClassVar[int]
    CMSMINDSGSOC_FIELD_NUMBER: _ClassVar[int]
    CFG_SOC_CALI_FIELD_NUMBER: _ClassVar[int]
    CFG_BMS_PUSH_FIELD_NUMBER: _ClassVar[int]
    SET_TIME_TASK_FIELD_NUMBER: _ClassVar[int]
    CFG_PLUG_IN_INFO_AC_IN_CHG_POW_MAX_FIELD_NUMBER: _ClassVar[int]
    CFG_DISPLAY_PROPERTY_FULL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    CFG_DISPLAY_PROPERTY_INCREMENTAL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    CFG_RUNTIME_PROPERTY_FULL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    CFG_RUNTIME_PROPERTY_INCREMENTAL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_DISPLAY_PROPERTY_FULL_UPLOAD_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_RUNTIME_PROPERTY_FULL_UPLOAD_FIELD_NUMBER: _ClassVar[int]
    CFG_PLUG_IN_INFO_PV_DC_AMP_MAX_FIELD_NUMBER: _ClassVar[int]
    CFG_TIME_TASK_V2_ITEM_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_SELECTED_TIME_TASK_V2_FIELD_NUMBER: _ClassVar[int]
    CFG_UTC_TIMEZONE_ID_FIELD_NUMBER: _ClassVar[int]
    CFG_UTC_SET_MODE_FIELD_NUMBER: _ClassVar[int]
    CFG_WAVE_OPERATING_MODE_FIELD_NUMBER: _ClassVar[int]
    CFG_WAVE_OPERATING_SUBMODE_FIELD_NUMBER: _ClassVar[int]
    CFG_AIRFLOW_SPEED_FIELD_NUMBER: _ClassVar[int]
    CFG_TEMP_SET_FIELD_NUMBER: _ClassVar[int]
    CFG_HUMI_SET_FIELD_NUMBER: _ClassVar[int]
    CFG_TEMP_THERMOSTATIC_UPPER_LIMIT_FIELD_NUMBER: _ClassVar[int]
    CFG_TEMP_THERMOSTATIC_LOWER_LIMIT_FIELD_NUMBER: _ClassVar[int]
    CFG_DRAINAGE_MODE_FIELD_NUMBER: _ClassVar[int]
    CFG_MOOD_LIGHT_MODE_FIELD_NUMBER: _ClassVar[int]
    CFG_LCD_SHOW_TEMP_TYPE_FIELD_NUMBER: _ClassVar[int]
    CFG_EN_PET_CARE_FIELD_NUMBER: _ClassVar[int]
    CFG_TEMP_PET_CARE_WARNING_FIELD_NUMBER: _ClassVar[int]
    CFG_USER_TEMP_UNIT_FIELD_NUMBER: _ClassVar[int]
    CFG_SYS_PAUSE_FIELD_NUMBER: _ClassVar[int]
    CFG_POWER_OFF_DELAY_SET_FIELD_NUMBER: _ClassVar[int]
    cfgPowerOff: int
    cfg_main_power: bool
    cfg_utc_time: int
    cfg_utc_timezone: int
    enBeep: int
    screenOffTime: int
    devStandbyTime: int
    lcdLight: int
    cmsMaxChgSoc: int
    cmsMinDsgSoc: int
    cfg_soc_cali: int
    cfg_bms_push: Wave3CfgBmsPushWrite
    set_time_task: Wave3SetTimeTaskWrite
    cfg_plug_in_info_ac_in_chg_pow_max: int
    cfg_display_property_full_upload_period: int
    cfg_display_property_incremental_upload_period: int
    cfg_runtime_property_full_upload_period: int
    cfg_runtime_property_incremental_upload_period: int
    active_display_property_full_upload: bool
    active_runtime_property_full_upload: bool
    cfg_plug_in_info_pv_dc_amp_max: int
    cfg_time_task_v2_item: Wave3TimeTaskItemV2
    active_selected_time_task_v2: int
    cfg_utc_timezone_id: str
    cfg_utc_set_mode: bool
    cfg_wave_operating_mode: int
    cfg_wave_operating_submode: int
    cfg_airflow_speed: int
    cfg_temp_set: float
    cfg_humi_set: float
    cfg_temp_thermostatic_upper_limit: float
    cfg_temp_thermostatic_lower_limit: float
    cfg_drainage_mode: int
    cfg_mood_light_mode: int
    cfg_lcd_show_temp_type: int
    cfg_en_pet_care: bool
    cfg_temp_pet_care_warning: float
    cfg_user_temp_unit: USER_TEMP_UNIT_TYPE
    cfg_sys_pause: bool
    cfg_power_off_delay_set: int
    def __init__(self, cfgPowerOff: int | None = ..., cfg_main_power: bool | None = ..., cfg_utc_time: int | None = ..., cfg_utc_timezone: int | None = ..., enBeep: int | None = ..., screenOffTime: int | None = ..., devStandbyTime: int | None = ..., lcdLight: int | None = ..., cmsMaxChgSoc: int | None = ..., cmsMinDsgSoc: int | None = ..., cfg_soc_cali: int | None = ..., cfg_bms_push: Wave3CfgBmsPushWrite | _Mapping | None = ..., set_time_task: Wave3SetTimeTaskWrite | _Mapping | None = ..., cfg_plug_in_info_ac_in_chg_pow_max: int | None = ..., cfg_display_property_full_upload_period: int | None = ..., cfg_display_property_incremental_upload_period: int | None = ..., cfg_runtime_property_full_upload_period: int | None = ..., cfg_runtime_property_incremental_upload_period: int | None = ..., active_display_property_full_upload: bool | None = ..., active_runtime_property_full_upload: bool | None = ..., cfg_plug_in_info_pv_dc_amp_max: int | None = ..., cfg_time_task_v2_item: Wave3TimeTaskItemV2 | _Mapping | None = ..., active_selected_time_task_v2: int | None = ..., cfg_utc_timezone_id: str | None = ..., cfg_utc_set_mode: bool | None = ..., cfg_wave_operating_mode: int | None = ..., cfg_wave_operating_submode: int | None = ..., cfg_airflow_speed: int | None = ..., cfg_temp_set: float | None = ..., cfg_humi_set: float | None = ..., cfg_temp_thermostatic_upper_limit: float | None = ..., cfg_temp_thermostatic_lower_limit: float | None = ..., cfg_drainage_mode: int | None = ..., cfg_mood_light_mode: int | None = ..., cfg_lcd_show_temp_type: int | None = ..., cfg_en_pet_care: bool | None = ..., cfg_temp_pet_care_warning: float | None = ..., cfg_user_temp_unit: USER_TEMP_UNIT_TYPE | str | None = ..., cfg_sys_pause: bool | None = ..., cfg_power_off_delay_set: int | None = ...) -> None: ...

class Wave3ConfigWriteAck(_message.Message):
    __slots__ = ("actionId", "active_display_property_full_upload", "active_runtime_property_full_upload", "active_selected_time_task_v2", "cfgPowerOff", "cfg_airflow_speed", "cfg_bms_push", "cfg_display_property_full_upload_period", "cfg_display_property_incremental_upload_period", "cfg_drainage_mode", "cfg_en_pet_care", "cfg_humi_set", "cfg_lcd_show_temp_type", "cfg_main_power", "cfg_mood_light_mode", "cfg_plug_in_info_ac_in_chg_pow_max", "cfg_plug_in_info_pv_dc_amp_max", "cfg_power_off_delay_set", "cfg_runtime_property_full_upload_period", "cfg_runtime_property_incremental_upload_period", "cfg_soc_cali", "cfg_sys_pause", "cfg_temp_pet_care_warning", "cfg_temp_set", "cfg_temp_thermostatic_lower_limit", "cfg_temp_thermostatic_upper_limit", "cfg_time_task_v2_item", "cfg_user_temp_unit", "cfg_utc_set_mode", "cfg_utc_time", "cfg_utc_timezone", "cfg_utc_timezone_id", "cfg_wave_operating_mode", "cfg_wave_operating_submode", "cmsMaxChgSoc", "cmsMinDsgSoc", "configOk", "devStandbyTime", "enBeep", "lcdLight", "screenOffTime", "set_time_task")
    ACTIONID_FIELD_NUMBER: _ClassVar[int]
    CONFIGOK_FIELD_NUMBER: _ClassVar[int]
    CFGPOWEROFF_FIELD_NUMBER: _ClassVar[int]
    CFG_MAIN_POWER_FIELD_NUMBER: _ClassVar[int]
    CFG_UTC_TIME_FIELD_NUMBER: _ClassVar[int]
    CFG_UTC_TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    ENBEEP_FIELD_NUMBER: _ClassVar[int]
    SCREENOFFTIME_FIELD_NUMBER: _ClassVar[int]
    DEVSTANDBYTIME_FIELD_NUMBER: _ClassVar[int]
    LCDLIGHT_FIELD_NUMBER: _ClassVar[int]
    CMSMAXCHGSOC_FIELD_NUMBER: _ClassVar[int]
    CMSMINDSGSOC_FIELD_NUMBER: _ClassVar[int]
    CFG_SOC_CALI_FIELD_NUMBER: _ClassVar[int]
    CFG_BMS_PUSH_FIELD_NUMBER: _ClassVar[int]
    SET_TIME_TASK_FIELD_NUMBER: _ClassVar[int]
    CFG_PLUG_IN_INFO_AC_IN_CHG_POW_MAX_FIELD_NUMBER: _ClassVar[int]
    CFG_DISPLAY_PROPERTY_FULL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    CFG_DISPLAY_PROPERTY_INCREMENTAL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    CFG_RUNTIME_PROPERTY_FULL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    CFG_RUNTIME_PROPERTY_INCREMENTAL_UPLOAD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_DISPLAY_PROPERTY_FULL_UPLOAD_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_RUNTIME_PROPERTY_FULL_UPLOAD_FIELD_NUMBER: _ClassVar[int]
    CFG_PLUG_IN_INFO_PV_DC_AMP_MAX_FIELD_NUMBER: _ClassVar[int]
    CFG_TIME_TASK_V2_ITEM_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_SELECTED_TIME_TASK_V2_FIELD_NUMBER: _ClassVar[int]
    CFG_UTC_TIMEZONE_ID_FIELD_NUMBER: _ClassVar[int]
    CFG_UTC_SET_MODE_FIELD_NUMBER: _ClassVar[int]
    CFG_WAVE_OPERATING_MODE_FIELD_NUMBER: _ClassVar[int]
    CFG_WAVE_OPERATING_SUBMODE_FIELD_NUMBER: _ClassVar[int]
    CFG_AIRFLOW_SPEED_FIELD_NUMBER: _ClassVar[int]
    CFG_TEMP_SET_FIELD_NUMBER: _ClassVar[int]
    CFG_HUMI_SET_FIELD_NUMBER: _ClassVar[int]
    CFG_TEMP_THERMOSTATIC_UPPER_LIMIT_FIELD_NUMBER: _ClassVar[int]
    CFG_TEMP_THERMOSTATIC_LOWER_LIMIT_FIELD_NUMBER: _ClassVar[int]
    CFG_DRAINAGE_MODE_FIELD_NUMBER: _ClassVar[int]
    CFG_MOOD_LIGHT_MODE_FIELD_NUMBER: _ClassVar[int]
    CFG_LCD_SHOW_TEMP_TYPE_FIELD_NUMBER: _ClassVar[int]
    CFG_EN_PET_CARE_FIELD_NUMBER: _ClassVar[int]
    CFG_TEMP_PET_CARE_WARNING_FIELD_NUMBER: _ClassVar[int]
    CFG_USER_TEMP_UNIT_FIELD_NUMBER: _ClassVar[int]
    CFG_SYS_PAUSE_FIELD_NUMBER: _ClassVar[int]
    CFG_POWER_OFF_DELAY_SET_FIELD_NUMBER: _ClassVar[int]
    actionId: int
    configOk: bool
    cfgPowerOff: int
    cfg_main_power: bool
    cfg_utc_time: int
    cfg_utc_timezone: int
    enBeep: int
    screenOffTime: int
    devStandbyTime: int
    lcdLight: int
    cmsMaxChgSoc: int
    cmsMinDsgSoc: int
    cfg_soc_cali: int
    cfg_bms_push: Wave3CfgBmsPushWriteAck
    set_time_task: Wave3SetTimeTaskWriteAck
    cfg_plug_in_info_ac_in_chg_pow_max: int
    cfg_display_property_full_upload_period: int
    cfg_display_property_incremental_upload_period: int
    cfg_runtime_property_full_upload_period: int
    cfg_runtime_property_incremental_upload_period: int
    active_display_property_full_upload: bool
    active_runtime_property_full_upload: bool
    cfg_plug_in_info_pv_dc_amp_max: int
    cfg_time_task_v2_item: Wave3TimeTaskItemV2
    active_selected_time_task_v2: int
    cfg_utc_timezone_id: str
    cfg_utc_set_mode: bool
    cfg_wave_operating_mode: int
    cfg_wave_operating_submode: int
    cfg_airflow_speed: int
    cfg_temp_set: float
    cfg_humi_set: float
    cfg_temp_thermostatic_upper_limit: float
    cfg_temp_thermostatic_lower_limit: float
    cfg_drainage_mode: int
    cfg_mood_light_mode: int
    cfg_lcd_show_temp_type: int
    cfg_en_pet_care: bool
    cfg_temp_pet_care_warning: float
    cfg_user_temp_unit: USER_TEMP_UNIT_TYPE
    cfg_sys_pause: bool
    cfg_power_off_delay_set: int
    def __init__(self, actionId: int | None = ..., configOk: bool | None = ..., cfgPowerOff: int | None = ..., cfg_main_power: bool | None = ..., cfg_utc_time: int | None = ..., cfg_utc_timezone: int | None = ..., enBeep: int | None = ..., screenOffTime: int | None = ..., devStandbyTime: int | None = ..., lcdLight: int | None = ..., cmsMaxChgSoc: int | None = ..., cmsMinDsgSoc: int | None = ..., cfg_soc_cali: int | None = ..., cfg_bms_push: Wave3CfgBmsPushWriteAck | _Mapping | None = ..., set_time_task: Wave3SetTimeTaskWriteAck | _Mapping | None = ..., cfg_plug_in_info_ac_in_chg_pow_max: int | None = ..., cfg_display_property_full_upload_period: int | None = ..., cfg_display_property_incremental_upload_period: int | None = ..., cfg_runtime_property_full_upload_period: int | None = ..., cfg_runtime_property_incremental_upload_period: int | None = ..., active_display_property_full_upload: bool | None = ..., active_runtime_property_full_upload: bool | None = ..., cfg_plug_in_info_pv_dc_amp_max: int | None = ..., cfg_time_task_v2_item: Wave3TimeTaskItemV2 | _Mapping | None = ..., active_selected_time_task_v2: int | None = ..., cfg_utc_timezone_id: str | None = ..., cfg_utc_set_mode: bool | None = ..., cfg_wave_operating_mode: int | None = ..., cfg_wave_operating_submode: int | None = ..., cfg_airflow_speed: int | None = ..., cfg_temp_set: float | None = ..., cfg_humi_set: float | None = ..., cfg_temp_thermostatic_upper_limit: float | None = ..., cfg_temp_thermostatic_lower_limit: float | None = ..., cfg_drainage_mode: int | None = ..., cfg_mood_light_mode: int | None = ..., cfg_lcd_show_temp_type: int | None = ..., cfg_en_pet_care: bool | None = ..., cfg_temp_pet_care_warning: float | None = ..., cfg_user_temp_unit: USER_TEMP_UNIT_TYPE | str | None = ..., cfg_sys_pause: bool | None = ..., cfg_power_off_delay_set: int | None = ...) -> None: ...

class Wave3SetMessage(_message.Message):
    __slots__ = ("header",)
    HEADER_FIELD_NUMBER: _ClassVar[int]
    header: Wave3SetHeader
    def __init__(self, header: Wave3SetHeader | _Mapping | None = ...) -> None: ...

class Wave3SetHeader(_message.Message):
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
