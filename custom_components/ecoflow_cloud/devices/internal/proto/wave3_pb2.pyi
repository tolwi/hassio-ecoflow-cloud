from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

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
    __slots__ = ("pack_sn", "app_to_bms_launch_date", "app_launch_date_set_type", "app_to_bms_reset_flag", "bms_data_upload_en")
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
    def __init__(self, pack_sn: _Optional[str] = ..., app_to_bms_launch_date: _Optional[int] = ..., app_launch_date_set_type: _Optional[int] = ..., app_to_bms_reset_flag: _Optional[int] = ..., bms_data_upload_en: _Optional[int] = ...) -> None: ...

class Wave3ConfigReadAck(_message.Message):
    __slots__ = ("cfg_utc_time", "cfg_utc_timezone", "get_time_task_list", "read_time_task_v2_list", "get_pd_firm_ver", "get_iot_firm_ver", "get_mppt_firm_ver", "get_llc_firm_ver", "get_inv_firm_ver", "get_bms_firm_ver")
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
    def __init__(self, cfg_utc_time: _Optional[int] = ..., cfg_utc_timezone: _Optional[int] = ..., get_time_task_list: _Optional[_Union[Wave3GetAllTimeTaskReadck, _Mapping]] = ..., read_time_task_v2_list: _Optional[_Union[Wave3TimeTaskItemV2List, _Mapping]] = ..., get_pd_firm_ver: _Optional[int] = ..., get_iot_firm_ver: _Optional[int] = ..., get_mppt_firm_ver: _Optional[int] = ..., get_llc_firm_ver: _Optional[int] = ..., get_inv_firm_ver: _Optional[int] = ..., get_bms_firm_ver: _Optional[int] = ...) -> None: ...

class Wave3ConfigRead(_message.Message):
    __slots__ = ("action_id",)
    ACTION_ID_FIELD_NUMBER: _ClassVar[int]
    action_id: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, action_id: _Optional[_Iterable[int]] = ...) -> None: ...

class Wave3ResvInfo(_message.Message):
    __slots__ = ("resv_info",)
    RESV_INFO_FIELD_NUMBER: _ClassVar[int]
    resv_info: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, resv_info: _Optional[_Iterable[int]] = ...) -> None: ...

class Wave3TimeTaskParamDetail(_message.Message):
    __slots__ = ("type", "val")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VAL_FIELD_NUMBER: _ClassVar[int]
    type: WAVE3_TIME_TASK_DETAIL_TYPE
    val: float
    def __init__(self, type: _Optional[_Union[WAVE3_TIME_TASK_DETAIL_TYPE, str]] = ..., val: _Optional[float] = ...) -> None: ...

class Wave3TimeTaskItemV2(_message.Message):
    __slots__ = ("task_index", "is_cfg", "is_enable", "conflict_flag", "time_mode", "time_param", "time_table", "task_type", "task_param", "task_param_detail")
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
    def __init__(self, task_index: _Optional[int] = ..., is_cfg: _Optional[bool] = ..., is_enable: _Optional[bool] = ..., conflict_flag: _Optional[int] = ..., time_mode: _Optional[_Union[WAVE3_TIME_TASK_MODE, str]] = ..., time_param: _Optional[int] = ..., time_table: _Optional[int] = ..., task_type: _Optional[_Union[WAVE3_TIME_TASK_TYPE, str]] = ..., task_param: _Optional[int] = ..., task_param_detail: _Optional[_Iterable[_Union[Wave3TimeTaskParamDetail, _Mapping]]] = ...) -> None: ...

class Wave3TimeTaskItemV2List(_message.Message):
    __slots__ = ("time_task",)
    TIME_TASK_FIELD_NUMBER: _ClassVar[int]
    time_task: _containers.RepeatedCompositeFieldContainer[Wave3TimeTaskItemV2]
    def __init__(self, time_task: _Optional[_Iterable[_Union[Wave3TimeTaskItemV2, _Mapping]]] = ...) -> None: ...

class Wave3RuntimePropertyUpload(_message.Message):
    __slots__ = ("temp_pcs_dc", "temp_pcs_ac", "plug_in_info_ac_in_vol", "plug_in_info_bms_vol", "pd_mppt_comm_err", "pd_llc_comm_err", "pd_bms_comm_err", "pd_iot_comm_err", "pd_firm_ver", "iot_firm_ver", "mppt_firm_ver", "llc_firm_ver", "plug_in_info_ac_in_amp", "bms_firm_ver", "bms_batt_vol", "bms_batt_amp", "bms_bal_state", "bms_full_cap", "bms_remain_cap", "bms_alm_state", "bms_pro_state", "bms_flt_state", "bms_err_code", "bms_min_cell_vol", "bms_max_cell_vol", "cms_batt_vol", "cms_batt_amp", "cms_chg_req_vol", "cms_chg_req_amp", "bms_overload_icon", "bms_warn_icon", "bms_high_temp_icon", "bms_low_temp_icon", "bms_limit_icon", "bms_alm_state_2", "bms_pro_state_2", "display_property_full_upload_period", "display_property_incremental_upload_period", "runtime_property_full_upload_period", "runtime_property_incremental_upload_period", "temp_pv", "plug_in_info_pv_vol", "plug_in_info_pv_amp", "plug_in_info_dcp_vol", "plug_in_info_dcp_amp", "temp_indoor_return_air", "temp_outdoor_ambient", "temp_condenser", "temp_evaporator", "temp_compressor_discharge")
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
    def __init__(self, temp_pcs_dc: _Optional[float] = ..., temp_pcs_ac: _Optional[float] = ..., plug_in_info_ac_in_vol: _Optional[float] = ..., plug_in_info_bms_vol: _Optional[float] = ..., pd_mppt_comm_err: _Optional[int] = ..., pd_llc_comm_err: _Optional[int] = ..., pd_bms_comm_err: _Optional[int] = ..., pd_iot_comm_err: _Optional[int] = ..., pd_firm_ver: _Optional[int] = ..., iot_firm_ver: _Optional[int] = ..., mppt_firm_ver: _Optional[int] = ..., llc_firm_ver: _Optional[int] = ..., plug_in_info_ac_in_amp: _Optional[float] = ..., bms_firm_ver: _Optional[int] = ..., bms_batt_vol: _Optional[float] = ..., bms_batt_amp: _Optional[float] = ..., bms_bal_state: _Optional[int] = ..., bms_full_cap: _Optional[int] = ..., bms_remain_cap: _Optional[int] = ..., bms_alm_state: _Optional[int] = ..., bms_pro_state: _Optional[int] = ..., bms_flt_state: _Optional[int] = ..., bms_err_code: _Optional[int] = ..., bms_min_cell_vol: _Optional[int] = ..., bms_max_cell_vol: _Optional[int] = ..., cms_batt_vol: _Optional[float] = ..., cms_batt_amp: _Optional[float] = ..., cms_chg_req_vol: _Optional[float] = ..., cms_chg_req_amp: _Optional[float] = ..., bms_overload_icon: _Optional[int] = ..., bms_warn_icon: _Optional[int] = ..., bms_high_temp_icon: _Optional[int] = ..., bms_low_temp_icon: _Optional[int] = ..., bms_limit_icon: _Optional[int] = ..., bms_alm_state_2: _Optional[int] = ..., bms_pro_state_2: _Optional[int] = ..., display_property_full_upload_period: _Optional[int] = ..., display_property_incremental_upload_period: _Optional[int] = ..., runtime_property_full_upload_period: _Optional[int] = ..., runtime_property_incremental_upload_period: _Optional[int] = ..., temp_pv: _Optional[float] = ..., plug_in_info_pv_vol: _Optional[float] = ..., plug_in_info_pv_amp: _Optional[float] = ..., plug_in_info_dcp_vol: _Optional[float] = ..., plug_in_info_dcp_amp: _Optional[float] = ..., temp_indoor_return_air: _Optional[float] = ..., temp_outdoor_ambient: _Optional[float] = ..., temp_condenser: _Optional[float] = ..., temp_evaporator: _Optional[float] = ..., temp_compressor_discharge: _Optional[float] = ...) -> None: ...

class Wave3DevErrcodeList(_message.Message):
    __slots__ = ("dev_errcode",)
    DEV_ERRCODE_FIELD_NUMBER: _ClassVar[int]
    dev_errcode: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, dev_errcode: _Optional[_Iterable[int]] = ...) -> None: ...

class Wave3WaveOperatingModeParamItem(_message.Message):
    __slots__ = ("submode", "airflow_speed", "temp_set", "humi_set", "temp_thermostatic_upper_limit", "temp_thermostatic_lower_limit")
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
    def __init__(self, submode: _Optional[int] = ..., airflow_speed: _Optional[int] = ..., temp_set: _Optional[float] = ..., humi_set: _Optional[float] = ..., temp_thermostatic_upper_limit: _Optional[float] = ..., temp_thermostatic_lower_limit: _Optional[float] = ...) -> None: ...

class Wave3WaveOperatingModeParamList(_message.Message):
    __slots__ = ("list_info",)
    LIST_INFO_FIELD_NUMBER: _ClassVar[int]
    list_info: _containers.RepeatedCompositeFieldContainer[Wave3WaveOperatingModeParamItem]
    def __init__(self, list_info: _Optional[_Iterable[_Union[Wave3WaveOperatingModeParamItem, _Mapping]]] = ...) -> None: ...

class Wave3DisplayPropertyUpload(_message.Message):
    __slots__ = ("errcode", "pow_in_sum_w", "pow_out_sum_w", "lcd_light", "pow_get_qcusb1", "pow_get_typec1", "flow_info_qcusb1", "flow_info_typec1", "dev_standby_time", "screen_off_time", "pcs_fan_level", "flow_info_ac2dc", "flow_info_ac_in", "pow_get_ac", "pow_get_ac_in", "plug_in_info_ac_in_flag", "plug_in_info_ac_in_feq", "current_time_task_v2_item", "utc_timezone", "utc_timezone_id", "utc_set_mode", "bms_err_code", "flow_info_bms_dsg", "flow_info_bms_chg", "pow_get_bms", "en_beep", "plug_in_info_ac_charger_flag", "plug_in_info_ac_in_chg_pow_max", "dev_sleep_state", "pd_err_code", "plug_in_info_ac_out_dsg_pow_max", "bms_batt_soc", "bms_batt_soh", "bms_design_cap", "bms_dsg_rem_time", "bms_chg_rem_time", "bms_min_cell_temp", "bms_max_cell_temp", "bms_min_mos_temp", "bms_max_mos_temp", "cms_batt_soc", "cms_batt_soh", "cms_dsg_rem_time", "cms_chg_rem_time", "cms_max_chg_soc", "cms_min_dsg_soc", "cms_bms_run_state", "bms_chg_dsg_state", "cms_chg_dsg_state", "time_task_conflict_flag", "time_task_change_cnt", "plug_in_info_pv_dc_amp_max", "flow_info_pv", "pow_get_pv", "plug_in_info_pv_type", "plug_in_info_pv_charger_flag", "plug_in_info_pv_chg_amp_max", "plug_in_info_pv_chg_vol_max", "bms_main_sn", "flow_info_dcp_in", "flow_info_dcp_out", "pow_get_dcp", "plug_in_info_dcp_in_flag", "plug_in_info_dcp_type", "plug_in_info_dcp_detail", "plug_in_info_dcp_dsg_chg_type", "plug_in_info_dcp_resv", "plug_in_info_dcp_sn", "plug_in_info_dcp_firm_ver", "plug_in_info_dcp_charger_flag", "plug_in_info_dcp_run_state", "plug_in_info_dcp_err_code", "plug_in_info_ac_in_chg_hal_pow_max", "temp_ambient", "humi_ambient", "wave_operating_mode", "temp_indoor_supply_air", "condensate_water_level", "in_drainage", "drainage_mode", "mood_light_mode", "lcd_show_temp_type", "en_pet_care", "temp_pet_care_warning", "user_temp_unit", "pet_care_warning", "wave_mode_info", "dev_errcode_list", "pow_get_self_consume", "power_off_delay_set", "power_off_delay_remaining")
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
    def __init__(self, errcode: _Optional[int] = ..., pow_in_sum_w: _Optional[float] = ..., pow_out_sum_w: _Optional[float] = ..., lcd_light: _Optional[int] = ..., pow_get_qcusb1: _Optional[float] = ..., pow_get_typec1: _Optional[float] = ..., flow_info_qcusb1: _Optional[int] = ..., flow_info_typec1: _Optional[int] = ..., dev_standby_time: _Optional[int] = ..., screen_off_time: _Optional[int] = ..., pcs_fan_level: _Optional[int] = ..., flow_info_ac2dc: _Optional[int] = ..., flow_info_ac_in: _Optional[int] = ..., pow_get_ac: _Optional[float] = ..., pow_get_ac_in: _Optional[float] = ..., plug_in_info_ac_in_flag: _Optional[int] = ..., plug_in_info_ac_in_feq: _Optional[int] = ..., current_time_task_v2_item: _Optional[_Union[Wave3TimeTaskItemV2, _Mapping]] = ..., utc_timezone: _Optional[int] = ..., utc_timezone_id: _Optional[str] = ..., utc_set_mode: _Optional[bool] = ..., bms_err_code: _Optional[int] = ..., flow_info_bms_dsg: _Optional[int] = ..., flow_info_bms_chg: _Optional[int] = ..., pow_get_bms: _Optional[float] = ..., en_beep: _Optional[bool] = ..., plug_in_info_ac_charger_flag: _Optional[bool] = ..., plug_in_info_ac_in_chg_pow_max: _Optional[int] = ..., dev_sleep_state: _Optional[int] = ..., pd_err_code: _Optional[int] = ..., plug_in_info_ac_out_dsg_pow_max: _Optional[int] = ..., bms_batt_soc: _Optional[float] = ..., bms_batt_soh: _Optional[float] = ..., bms_design_cap: _Optional[int] = ..., bms_dsg_rem_time: _Optional[int] = ..., bms_chg_rem_time: _Optional[int] = ..., bms_min_cell_temp: _Optional[int] = ..., bms_max_cell_temp: _Optional[int] = ..., bms_min_mos_temp: _Optional[int] = ..., bms_max_mos_temp: _Optional[int] = ..., cms_batt_soc: _Optional[float] = ..., cms_batt_soh: _Optional[float] = ..., cms_dsg_rem_time: _Optional[int] = ..., cms_chg_rem_time: _Optional[int] = ..., cms_max_chg_soc: _Optional[int] = ..., cms_min_dsg_soc: _Optional[int] = ..., cms_bms_run_state: _Optional[int] = ..., bms_chg_dsg_state: _Optional[int] = ..., cms_chg_dsg_state: _Optional[int] = ..., time_task_conflict_flag: _Optional[int] = ..., time_task_change_cnt: _Optional[int] = ..., plug_in_info_pv_dc_amp_max: _Optional[int] = ..., flow_info_pv: _Optional[int] = ..., pow_get_pv: _Optional[float] = ..., plug_in_info_pv_type: _Optional[int] = ..., plug_in_info_pv_charger_flag: _Optional[bool] = ..., plug_in_info_pv_chg_amp_max: _Optional[int] = ..., plug_in_info_pv_chg_vol_max: _Optional[int] = ..., bms_main_sn: _Optional[str] = ..., flow_info_dcp_in: _Optional[int] = ..., flow_info_dcp_out: _Optional[int] = ..., pow_get_dcp: _Optional[float] = ..., plug_in_info_dcp_in_flag: _Optional[bool] = ..., plug_in_info_dcp_type: _Optional[int] = ..., plug_in_info_dcp_detail: _Optional[int] = ..., plug_in_info_dcp_dsg_chg_type: _Optional[int] = ..., plug_in_info_dcp_resv: _Optional[_Union[Wave3ResvInfo, _Mapping]] = ..., plug_in_info_dcp_sn: _Optional[str] = ..., plug_in_info_dcp_firm_ver: _Optional[int] = ..., plug_in_info_dcp_charger_flag: _Optional[bool] = ..., plug_in_info_dcp_run_state: _Optional[int] = ..., plug_in_info_dcp_err_code: _Optional[int] = ..., plug_in_info_ac_in_chg_hal_pow_max: _Optional[int] = ..., temp_ambient: _Optional[float] = ..., humi_ambient: _Optional[float] = ..., wave_operating_mode: _Optional[int] = ..., temp_indoor_supply_air: _Optional[float] = ..., condensate_water_level: _Optional[float] = ..., in_drainage: _Optional[bool] = ..., drainage_mode: _Optional[int] = ..., mood_light_mode: _Optional[int] = ..., lcd_show_temp_type: _Optional[int] = ..., en_pet_care: _Optional[bool] = ..., temp_pet_care_warning: _Optional[float] = ..., user_temp_unit: _Optional[_Union[USER_TEMP_UNIT_TYPE, str]] = ..., pet_care_warning: _Optional[bool] = ..., wave_mode_info: _Optional[_Union[Wave3WaveOperatingModeParamList, _Mapping]] = ..., dev_errcode_list: _Optional[_Union[Wave3DevErrcodeList, _Mapping]] = ..., pow_get_self_consume: _Optional[float] = ..., power_off_delay_set: _Optional[int] = ..., power_off_delay_remaining: _Optional[int] = ...) -> None: ...

class Wave3SetTimeTaskWrite(_message.Message):
    __slots__ = ("task_index", "is_valid", "is_cfg", "is_enable", "conflict_flag", "type", "time_mode", "time_param", "time_table")
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
    def __init__(self, task_index: _Optional[int] = ..., is_valid: _Optional[bool] = ..., is_cfg: _Optional[bool] = ..., is_enable: _Optional[bool] = ..., conflict_flag: _Optional[int] = ..., type: _Optional[int] = ..., time_mode: _Optional[int] = ..., time_param: _Optional[int] = ..., time_table: _Optional[_Iterable[int]] = ...) -> None: ...

class Wave3SetTimeTaskWriteAck(_message.Message):
    __slots__ = ("task_index", "type", "sta")
    TASK_INDEX_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    STA_FIELD_NUMBER: _ClassVar[int]
    task_index: int
    type: int
    sta: int
    def __init__(self, task_index: _Optional[int] = ..., type: _Optional[int] = ..., sta: _Optional[int] = ...) -> None: ...

class Wave3GetAllTimeTaskReadck(_message.Message):
    __slots__ = ("time_task",)
    TIME_TASK_FIELD_NUMBER: _ClassVar[int]
    time_task: _containers.RepeatedCompositeFieldContainer[Wave3SetTimeTaskWrite]
    def __init__(self, time_task: _Optional[_Iterable[_Union[Wave3SetTimeTaskWrite, _Mapping]]] = ...) -> None: ...

class Wave3CfgBmsPushWrite(_message.Message):
    __slots__ = ("bms_heartbeap_open", "bms_health_open", "bms_heartbeap_freq", "bms_health_freq")
    BMS_HEARTBEAP_OPEN_FIELD_NUMBER: _ClassVar[int]
    BMS_HEALTH_OPEN_FIELD_NUMBER: _ClassVar[int]
    BMS_HEARTBEAP_FREQ_FIELD_NUMBER: _ClassVar[int]
    BMS_HEALTH_FREQ_FIELD_NUMBER: _ClassVar[int]
    bms_heartbeap_open: bool
    bms_health_open: bool
    bms_heartbeap_freq: int
    bms_health_freq: int
    def __init__(self, bms_heartbeap_open: _Optional[bool] = ..., bms_health_open: _Optional[bool] = ..., bms_heartbeap_freq: _Optional[int] = ..., bms_health_freq: _Optional[int] = ...) -> None: ...

class Wave3CfgBmsPushWriteAck(_message.Message):
    __slots__ = ("bms_heartbeap_open", "bms_health_open")
    BMS_HEARTBEAP_OPEN_FIELD_NUMBER: _ClassVar[int]
    BMS_HEALTH_OPEN_FIELD_NUMBER: _ClassVar[int]
    bms_heartbeap_open: bool
    bms_health_open: bool
    def __init__(self, bms_heartbeap_open: _Optional[bool] = ..., bms_health_open: _Optional[bool] = ...) -> None: ...

class Wave3ConfigWrite(_message.Message):
    __slots__ = ("cfgPowerOff", "cfg_main_power", "cfg_utc_time", "cfg_utc_timezone", "enBeep", "screenOffTime", "devStandbyTime", "lcdLight", "cmsMaxChgSoc", "cmsMinDsgSoc", "cfg_soc_cali", "cfg_bms_push", "set_time_task", "cfg_plug_in_info_ac_in_chg_pow_max", "cfg_display_property_full_upload_period", "cfg_display_property_incremental_upload_period", "cfg_runtime_property_full_upload_period", "cfg_runtime_property_incremental_upload_period", "active_display_property_full_upload", "active_runtime_property_full_upload", "cfg_plug_in_info_pv_dc_amp_max", "cfg_time_task_v2_item", "active_selected_time_task_v2", "cfg_utc_timezone_id", "cfg_utc_set_mode", "cfg_wave_operating_mode", "cfg_wave_operating_submode", "cfg_airflow_speed", "cfg_temp_set", "cfg_humi_set", "cfg_temp_thermostatic_upper_limit", "cfg_temp_thermostatic_lower_limit", "cfg_drainage_mode", "cfg_mood_light_mode", "cfg_lcd_show_temp_type", "cfg_en_pet_care", "cfg_temp_pet_care_warning", "cfg_user_temp_unit", "cfg_sys_pause", "cfg_power_off_delay_set")
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
    def __init__(self, cfgPowerOff: _Optional[int] = ..., cfg_main_power: _Optional[bool] = ..., cfg_utc_time: _Optional[int] = ..., cfg_utc_timezone: _Optional[int] = ..., enBeep: _Optional[int] = ..., screenOffTime: _Optional[int] = ..., devStandbyTime: _Optional[int] = ..., lcdLight: _Optional[int] = ..., cmsMaxChgSoc: _Optional[int] = ..., cmsMinDsgSoc: _Optional[int] = ..., cfg_soc_cali: _Optional[int] = ..., cfg_bms_push: _Optional[_Union[Wave3CfgBmsPushWrite, _Mapping]] = ..., set_time_task: _Optional[_Union[Wave3SetTimeTaskWrite, _Mapping]] = ..., cfg_plug_in_info_ac_in_chg_pow_max: _Optional[int] = ..., cfg_display_property_full_upload_period: _Optional[int] = ..., cfg_display_property_incremental_upload_period: _Optional[int] = ..., cfg_runtime_property_full_upload_period: _Optional[int] = ..., cfg_runtime_property_incremental_upload_period: _Optional[int] = ..., active_display_property_full_upload: _Optional[bool] = ..., active_runtime_property_full_upload: _Optional[bool] = ..., cfg_plug_in_info_pv_dc_amp_max: _Optional[int] = ..., cfg_time_task_v2_item: _Optional[_Union[Wave3TimeTaskItemV2, _Mapping]] = ..., active_selected_time_task_v2: _Optional[int] = ..., cfg_utc_timezone_id: _Optional[str] = ..., cfg_utc_set_mode: _Optional[bool] = ..., cfg_wave_operating_mode: _Optional[int] = ..., cfg_wave_operating_submode: _Optional[int] = ..., cfg_airflow_speed: _Optional[int] = ..., cfg_temp_set: _Optional[float] = ..., cfg_humi_set: _Optional[float] = ..., cfg_temp_thermostatic_upper_limit: _Optional[float] = ..., cfg_temp_thermostatic_lower_limit: _Optional[float] = ..., cfg_drainage_mode: _Optional[int] = ..., cfg_mood_light_mode: _Optional[int] = ..., cfg_lcd_show_temp_type: _Optional[int] = ..., cfg_en_pet_care: _Optional[bool] = ..., cfg_temp_pet_care_warning: _Optional[float] = ..., cfg_user_temp_unit: _Optional[_Union[USER_TEMP_UNIT_TYPE, str]] = ..., cfg_sys_pause: _Optional[bool] = ..., cfg_power_off_delay_set: _Optional[int] = ...) -> None: ...

class Wave3ConfigWriteAck(_message.Message):
    __slots__ = ("actionId", "configOk", "cfgPowerOff", "cfg_main_power", "cfg_utc_time", "cfg_utc_timezone", "enBeep", "screenOffTime", "devStandbyTime", "lcdLight", "cmsMaxChgSoc", "cmsMinDsgSoc", "cfg_soc_cali", "cfg_bms_push", "set_time_task", "cfg_plug_in_info_ac_in_chg_pow_max", "cfg_display_property_full_upload_period", "cfg_display_property_incremental_upload_period", "cfg_runtime_property_full_upload_period", "cfg_runtime_property_incremental_upload_period", "active_display_property_full_upload", "active_runtime_property_full_upload", "cfg_plug_in_info_pv_dc_amp_max", "cfg_time_task_v2_item", "active_selected_time_task_v2", "cfg_utc_timezone_id", "cfg_utc_set_mode", "cfg_wave_operating_mode", "cfg_wave_operating_submode", "cfg_airflow_speed", "cfg_temp_set", "cfg_humi_set", "cfg_temp_thermostatic_upper_limit", "cfg_temp_thermostatic_lower_limit", "cfg_drainage_mode", "cfg_mood_light_mode", "cfg_lcd_show_temp_type", "cfg_en_pet_care", "cfg_temp_pet_care_warning", "cfg_user_temp_unit", "cfg_sys_pause", "cfg_power_off_delay_set")
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
    def __init__(self, actionId: _Optional[int] = ..., configOk: _Optional[bool] = ..., cfgPowerOff: _Optional[int] = ..., cfg_main_power: _Optional[bool] = ..., cfg_utc_time: _Optional[int] = ..., cfg_utc_timezone: _Optional[int] = ..., enBeep: _Optional[int] = ..., screenOffTime: _Optional[int] = ..., devStandbyTime: _Optional[int] = ..., lcdLight: _Optional[int] = ..., cmsMaxChgSoc: _Optional[int] = ..., cmsMinDsgSoc: _Optional[int] = ..., cfg_soc_cali: _Optional[int] = ..., cfg_bms_push: _Optional[_Union[Wave3CfgBmsPushWriteAck, _Mapping]] = ..., set_time_task: _Optional[_Union[Wave3SetTimeTaskWriteAck, _Mapping]] = ..., cfg_plug_in_info_ac_in_chg_pow_max: _Optional[int] = ..., cfg_display_property_full_upload_period: _Optional[int] = ..., cfg_display_property_incremental_upload_period: _Optional[int] = ..., cfg_runtime_property_full_upload_period: _Optional[int] = ..., cfg_runtime_property_incremental_upload_period: _Optional[int] = ..., active_display_property_full_upload: _Optional[bool] = ..., active_runtime_property_full_upload: _Optional[bool] = ..., cfg_plug_in_info_pv_dc_amp_max: _Optional[int] = ..., cfg_time_task_v2_item: _Optional[_Union[Wave3TimeTaskItemV2, _Mapping]] = ..., active_selected_time_task_v2: _Optional[int] = ..., cfg_utc_timezone_id: _Optional[str] = ..., cfg_utc_set_mode: _Optional[bool] = ..., cfg_wave_operating_mode: _Optional[int] = ..., cfg_wave_operating_submode: _Optional[int] = ..., cfg_airflow_speed: _Optional[int] = ..., cfg_temp_set: _Optional[float] = ..., cfg_humi_set: _Optional[float] = ..., cfg_temp_thermostatic_upper_limit: _Optional[float] = ..., cfg_temp_thermostatic_lower_limit: _Optional[float] = ..., cfg_drainage_mode: _Optional[int] = ..., cfg_mood_light_mode: _Optional[int] = ..., cfg_lcd_show_temp_type: _Optional[int] = ..., cfg_en_pet_care: _Optional[bool] = ..., cfg_temp_pet_care_warning: _Optional[float] = ..., cfg_user_temp_unit: _Optional[_Union[USER_TEMP_UNIT_TYPE, str]] = ..., cfg_sys_pause: _Optional[bool] = ..., cfg_power_off_delay_set: _Optional[int] = ...) -> None: ...

class Wave3SetMessage(_message.Message):
    __slots__ = ("header",)
    HEADER_FIELD_NUMBER: _ClassVar[int]
    header: Wave3SetHeader
    def __init__(self, header: _Optional[_Union[Wave3SetHeader, _Mapping]] = ...) -> None: ...

class Wave3SetHeader(_message.Message):
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
