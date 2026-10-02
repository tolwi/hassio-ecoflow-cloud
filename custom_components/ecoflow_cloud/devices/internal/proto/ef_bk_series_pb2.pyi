from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BK_SERIES_PANEL_GRID_STA(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PANEL_GRID_STA_NO_VALID: _ClassVar[BK_SERIES_PANEL_GRID_STA]
    PANEL_GRID_IN: _ClassVar[BK_SERIES_PANEL_GRID_STA]
    PANEL_GRID_NOT_ONLINE: _ClassVar[BK_SERIES_PANEL_GRID_STA]
    PANEL_FEED_GRID: _ClassVar[BK_SERIES_PANEL_GRID_STA]
PANEL_GRID_STA_NO_VALID: BK_SERIES_PANEL_GRID_STA
PANEL_GRID_IN: BK_SERIES_PANEL_GRID_STA
PANEL_GRID_NOT_ONLINE: BK_SERIES_PANEL_GRID_STA
PANEL_FEED_GRID: BK_SERIES_PANEL_GRID_STA

class BkSeriesDisplayPropertyUpload(_message.Message):
    __slots__ = ("pow_get_pv", "pow_get_pv2", "plug_in_info_pv_vol", "plug_in_info_pv_amp", "plug_in_info_pv2_vol", "plug_in_info_pv2_amp", "grid_connection_power", "grid_connection_vol", "grid_connection_amp", "grid_connection_freq", "grid_connection_sta", "module_wifi_rssi", "feed_grid_mode_pow_limit", "feed_grid_mode_pow_max")
    POW_GET_PV_FIELD_NUMBER: _ClassVar[int]
    POW_GET_PV2_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_PV_VOL_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_PV_AMP_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_PV2_VOL_FIELD_NUMBER: _ClassVar[int]
    PLUG_IN_INFO_PV2_AMP_FIELD_NUMBER: _ClassVar[int]
    GRID_CONNECTION_POWER_FIELD_NUMBER: _ClassVar[int]
    GRID_CONNECTION_VOL_FIELD_NUMBER: _ClassVar[int]
    GRID_CONNECTION_AMP_FIELD_NUMBER: _ClassVar[int]
    GRID_CONNECTION_FREQ_FIELD_NUMBER: _ClassVar[int]
    GRID_CONNECTION_STA_FIELD_NUMBER: _ClassVar[int]
    MODULE_WIFI_RSSI_FIELD_NUMBER: _ClassVar[int]
    FEED_GRID_MODE_POW_LIMIT_FIELD_NUMBER: _ClassVar[int]
    FEED_GRID_MODE_POW_MAX_FIELD_NUMBER: _ClassVar[int]
    pow_get_pv: float
    pow_get_pv2: float
    plug_in_info_pv_vol: float
    plug_in_info_pv_amp: float
    plug_in_info_pv2_vol: float
    plug_in_info_pv2_amp: float
    grid_connection_power: float
    grid_connection_vol: float
    grid_connection_amp: float
    grid_connection_freq: float
    grid_connection_sta: BK_SERIES_PANEL_GRID_STA
    module_wifi_rssi: float
    feed_grid_mode_pow_limit: int
    feed_grid_mode_pow_max: int
    def __init__(self, pow_get_pv: _Optional[float] = ..., pow_get_pv2: _Optional[float] = ..., plug_in_info_pv_vol: _Optional[float] = ..., plug_in_info_pv_amp: _Optional[float] = ..., plug_in_info_pv2_vol: _Optional[float] = ..., plug_in_info_pv2_amp: _Optional[float] = ..., grid_connection_power: _Optional[float] = ..., grid_connection_vol: _Optional[float] = ..., grid_connection_amp: _Optional[float] = ..., grid_connection_freq: _Optional[float] = ..., grid_connection_sta: _Optional[_Union[BK_SERIES_PANEL_GRID_STA, str]] = ..., module_wifi_rssi: _Optional[float] = ..., feed_grid_mode_pow_limit: _Optional[int] = ..., feed_grid_mode_pow_max: _Optional[int] = ...) -> None: ...

class BkSeriesRuntimePropertyUpload(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BkSeriesConfigWrite(_message.Message):
    __slots__ = ("cfg_utc_time", "cfg_inv_target_pwr", "cfg_feed_grid_mode_pow_limit")
    CFG_UTC_TIME_FIELD_NUMBER: _ClassVar[int]
    CFG_INV_TARGET_PWR_FIELD_NUMBER: _ClassVar[int]
    CFG_FEED_GRID_MODE_POW_LIMIT_FIELD_NUMBER: _ClassVar[int]
    cfg_utc_time: int
    cfg_inv_target_pwr: float
    cfg_feed_grid_mode_pow_limit: int
    def __init__(self, cfg_utc_time: _Optional[int] = ..., cfg_inv_target_pwr: _Optional[float] = ..., cfg_feed_grid_mode_pow_limit: _Optional[int] = ...) -> None: ...
