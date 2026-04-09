from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CmdFunc(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CMD_FUNC_NONE: _ClassVar[CmdFunc]
    CMD_FUNC_WN_SMART_PLUG: _ClassVar[CmdFunc]

class WnCmdId(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CMD_ID_NONE: _ClassVar[WnCmdId]
    CMD_ID_DATA: _ClassVar[WnCmdId]
    CMD_ID_TIMER_AUTOMATION_READ: _ClassVar[WnCmdId]
    CMD_ID_CHANGE_SWITCH_STATUS: _ClassVar[WnCmdId]
    CMD_ID_SET_BRIGHTNESS: _ClassVar[WnCmdId]
    CMD_ID_SET_MAX_WATTS: _ClassVar[WnCmdId]
CMD_FUNC_NONE: CmdFunc
CMD_FUNC_WN_SMART_PLUG: CmdFunc
CMD_ID_NONE: WnCmdId
CMD_ID_DATA: WnCmdId
CMD_ID_TIMER_AUTOMATION_READ: WnCmdId
CMD_ID_CHANGE_SWITCH_STATUS: WnCmdId
CMD_ID_SET_BRIGHTNESS: WnCmdId
CMD_ID_SET_MAX_WATTS: WnCmdId

class SmartPlugHeader(_message.Message):
    __slots__ = ("pdata", "src", "dest", "dSrc", "dDest", "encType", "checkType", "cmdFunc", "cmdId", "dataLen", "needAck", "isAck", "seq", "productId", "version", "payloadVer", "timeSnap", "isRwCmd", "isQueue", "ackType", "code", "moduleSn", "deviceSn", "srcSn", "destSn")
    PDATA_FIELD_NUMBER: _ClassVar[int]
    SRC_FIELD_NUMBER: _ClassVar[int]
    DEST_FIELD_NUMBER: _ClassVar[int]
    DSRC_FIELD_NUMBER: _ClassVar[int]
    DDEST_FIELD_NUMBER: _ClassVar[int]
    ENCTYPE_FIELD_NUMBER: _ClassVar[int]
    CHECKTYPE_FIELD_NUMBER: _ClassVar[int]
    CMDFUNC_FIELD_NUMBER: _ClassVar[int]
    CMDID_FIELD_NUMBER: _ClassVar[int]
    DATALEN_FIELD_NUMBER: _ClassVar[int]
    NEEDACK_FIELD_NUMBER: _ClassVar[int]
    ISACK_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    PRODUCTID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    PAYLOADVER_FIELD_NUMBER: _ClassVar[int]
    TIMESNAP_FIELD_NUMBER: _ClassVar[int]
    ISRWCMD_FIELD_NUMBER: _ClassVar[int]
    ISQUEUE_FIELD_NUMBER: _ClassVar[int]
    ACKTYPE_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    MODULESN_FIELD_NUMBER: _ClassVar[int]
    DEVICESN_FIELD_NUMBER: _ClassVar[int]
    SRCSN_FIELD_NUMBER: _ClassVar[int]
    DESTSN_FIELD_NUMBER: _ClassVar[int]
    pdata: bytes
    src: int
    dest: int
    dSrc: int
    dDest: int
    encType: int
    checkType: int
    cmdFunc: int
    cmdId: int
    dataLen: int
    needAck: int
    isAck: int
    seq: int
    productId: int
    version: int
    payloadVer: int
    timeSnap: int
    isRwCmd: int
    isQueue: int
    ackType: int
    code: str
    moduleSn: str
    deviceSn: str
    srcSn: str
    destSn: str
    def __init__(self, pdata: _Optional[bytes] = ..., src: _Optional[int] = ..., dest: _Optional[int] = ..., dSrc: _Optional[int] = ..., dDest: _Optional[int] = ..., encType: _Optional[int] = ..., checkType: _Optional[int] = ..., cmdFunc: _Optional[int] = ..., cmdId: _Optional[int] = ..., dataLen: _Optional[int] = ..., needAck: _Optional[int] = ..., isAck: _Optional[int] = ..., seq: _Optional[int] = ..., productId: _Optional[int] = ..., version: _Optional[int] = ..., payloadVer: _Optional[int] = ..., timeSnap: _Optional[int] = ..., isRwCmd: _Optional[int] = ..., isQueue: _Optional[int] = ..., ackType: _Optional[int] = ..., code: _Optional[str] = ..., moduleSn: _Optional[str] = ..., deviceSn: _Optional[str] = ..., srcSn: _Optional[str] = ..., destSn: _Optional[str] = ..., **kwargs) -> None: ...

class SendSmartPlugHeaderMsg(_message.Message):
    __slots__ = ("msg",)
    MSG_FIELD_NUMBER: _ClassVar[int]
    msg: _containers.RepeatedCompositeFieldContainer[SmartPlugHeader]
    def __init__(self, msg: _Optional[_Iterable[_Union[SmartPlugHeader, _Mapping]]] = ...) -> None: ...

class WnPlugHeartbeatPack(_message.Message):
    __slots__ = ("errCode", "warnCode", "country", "town", "maxCur", "temp", "freq", "current", "volt", "watts", "switchSta", "brightness", "maxWatts", "heartbeatFrequency", "meshEnable", "resetReason", "rtcResetReason", "resetCount", "runTime", "lanState", "stackFree", "stackMinFree", "meshId", "meshLevel", "selfMac", "parentMac", "otaDlErr", "otaDlTlsErr", "staIpAddr", "matterFabric", "geneNum", "consNum", "geneWatt", "consWatt", "wifiErr", "wifiErrTime", "mqttErr", "mqttErrTime", "selfEmsSwitch", "parentWifiRssi", "insightsSwitch", "rssiThreshold", "rssiVariance", "utcTime", "timeZone", "dstTime")
    ERRCODE_FIELD_NUMBER: _ClassVar[int]
    WARNCODE_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    TOWN_FIELD_NUMBER: _ClassVar[int]
    MAXCUR_FIELD_NUMBER: _ClassVar[int]
    TEMP_FIELD_NUMBER: _ClassVar[int]
    FREQ_FIELD_NUMBER: _ClassVar[int]
    CURRENT_FIELD_NUMBER: _ClassVar[int]
    VOLT_FIELD_NUMBER: _ClassVar[int]
    WATTS_FIELD_NUMBER: _ClassVar[int]
    SWITCHSTA_FIELD_NUMBER: _ClassVar[int]
    BRIGHTNESS_FIELD_NUMBER: _ClassVar[int]
    MAXWATTS_FIELD_NUMBER: _ClassVar[int]
    HEARTBEATFREQUENCY_FIELD_NUMBER: _ClassVar[int]
    MESHENABLE_FIELD_NUMBER: _ClassVar[int]
    RESETREASON_FIELD_NUMBER: _ClassVar[int]
    RTCRESETREASON_FIELD_NUMBER: _ClassVar[int]
    RESETCOUNT_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_FIELD_NUMBER: _ClassVar[int]
    LANSTATE_FIELD_NUMBER: _ClassVar[int]
    STACKFREE_FIELD_NUMBER: _ClassVar[int]
    STACKMINFREE_FIELD_NUMBER: _ClassVar[int]
    MESHID_FIELD_NUMBER: _ClassVar[int]
    MESHLEVEL_FIELD_NUMBER: _ClassVar[int]
    SELFMAC_FIELD_NUMBER: _ClassVar[int]
    PARENTMAC_FIELD_NUMBER: _ClassVar[int]
    OTADLERR_FIELD_NUMBER: _ClassVar[int]
    OTADLTLSERR_FIELD_NUMBER: _ClassVar[int]
    STAIPADDR_FIELD_NUMBER: _ClassVar[int]
    MATTERFABRIC_FIELD_NUMBER: _ClassVar[int]
    GENENUM_FIELD_NUMBER: _ClassVar[int]
    CONSNUM_FIELD_NUMBER: _ClassVar[int]
    GENEWATT_FIELD_NUMBER: _ClassVar[int]
    CONSWATT_FIELD_NUMBER: _ClassVar[int]
    WIFIERR_FIELD_NUMBER: _ClassVar[int]
    WIFIERRTIME_FIELD_NUMBER: _ClassVar[int]
    MQTTERR_FIELD_NUMBER: _ClassVar[int]
    MQTTERRTIME_FIELD_NUMBER: _ClassVar[int]
    SELFEMSSWITCH_FIELD_NUMBER: _ClassVar[int]
    PARENTWIFIRSSI_FIELD_NUMBER: _ClassVar[int]
    INSIGHTSSWITCH_FIELD_NUMBER: _ClassVar[int]
    RSSITHRESHOLD_FIELD_NUMBER: _ClassVar[int]
    RSSIVARIANCE_FIELD_NUMBER: _ClassVar[int]
    UTCTIME_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    DSTTIME_FIELD_NUMBER: _ClassVar[int]
    errCode: int
    warnCode: int
    country: int
    town: int
    maxCur: int
    temp: int
    freq: int
    current: int
    volt: int
    watts: int
    switchSta: bool
    brightness: int
    maxWatts: int
    heartbeatFrequency: int
    meshEnable: int
    resetReason: int
    rtcResetReason: int
    resetCount: int
    runTime: int
    lanState: int
    stackFree: int
    stackMinFree: int
    meshId: int
    meshLevel: int
    selfMac: int
    parentMac: int
    otaDlErr: int
    otaDlTlsErr: int
    staIpAddr: int
    matterFabric: int
    geneNum: int
    consNum: int
    geneWatt: int
    consWatt: int
    wifiErr: int
    wifiErrTime: int
    mqttErr: int
    mqttErrTime: int
    selfEmsSwitch: int
    parentWifiRssi: int
    insightsSwitch: int
    rssiThreshold: int
    rssiVariance: int
    utcTime: int
    timeZone: int
    dstTime: int
    def __init__(self, errCode: _Optional[int] = ..., warnCode: _Optional[int] = ..., country: _Optional[int] = ..., town: _Optional[int] = ..., maxCur: _Optional[int] = ..., temp: _Optional[int] = ..., freq: _Optional[int] = ..., current: _Optional[int] = ..., volt: _Optional[int] = ..., watts: _Optional[int] = ..., switchSta: _Optional[bool] = ..., brightness: _Optional[int] = ..., maxWatts: _Optional[int] = ..., heartbeatFrequency: _Optional[int] = ..., meshEnable: _Optional[int] = ..., resetReason: _Optional[int] = ..., rtcResetReason: _Optional[int] = ..., resetCount: _Optional[int] = ..., runTime: _Optional[int] = ..., lanState: _Optional[int] = ..., stackFree: _Optional[int] = ..., stackMinFree: _Optional[int] = ..., meshId: _Optional[int] = ..., meshLevel: _Optional[int] = ..., selfMac: _Optional[int] = ..., parentMac: _Optional[int] = ..., otaDlErr: _Optional[int] = ..., otaDlTlsErr: _Optional[int] = ..., staIpAddr: _Optional[int] = ..., matterFabric: _Optional[int] = ..., geneNum: _Optional[int] = ..., consNum: _Optional[int] = ..., geneWatt: _Optional[int] = ..., consWatt: _Optional[int] = ..., wifiErr: _Optional[int] = ..., wifiErrTime: _Optional[int] = ..., mqttErr: _Optional[int] = ..., mqttErrTime: _Optional[int] = ..., selfEmsSwitch: _Optional[int] = ..., parentWifiRssi: _Optional[int] = ..., insightsSwitch: _Optional[int] = ..., rssiThreshold: _Optional[int] = ..., rssiVariance: _Optional[int] = ..., utcTime: _Optional[int] = ..., timeZone: _Optional[int] = ..., dstTime: _Optional[int] = ...) -> None: ...

class WnPlugSwitchMessage(_message.Message):
    __slots__ = ("switchSta",)
    SWITCHSTA_FIELD_NUMBER: _ClassVar[int]
    switchSta: bool
    def __init__(self, switchSta: _Optional[bool] = ...) -> None: ...

class WnBrightnessPack(_message.Message):
    __slots__ = ("brightness",)
    BRIGHTNESS_FIELD_NUMBER: _ClassVar[int]
    brightness: int
    def __init__(self, brightness: _Optional[int] = ...) -> None: ...

class WnMaxWattsPack(_message.Message):
    __slots__ = ("maxWatts",)
    MAXWATTS_FIELD_NUMBER: _ClassVar[int]
    maxWatts: int
    def __init__(self, maxWatts: _Optional[int] = ...) -> None: ...

class WnTimetaskReadMessage(_message.Message):
    __slots__ = ("task1", "task2", "task3", "task4", "task5", "task6", "task7", "task8", "task9", "task10", "task11")
    TASK1_FIELD_NUMBER: _ClassVar[int]
    TASK2_FIELD_NUMBER: _ClassVar[int]
    TASK3_FIELD_NUMBER: _ClassVar[int]
    TASK4_FIELD_NUMBER: _ClassVar[int]
    TASK5_FIELD_NUMBER: _ClassVar[int]
    TASK6_FIELD_NUMBER: _ClassVar[int]
    TASK7_FIELD_NUMBER: _ClassVar[int]
    TASK8_FIELD_NUMBER: _ClassVar[int]
    TASK9_FIELD_NUMBER: _ClassVar[int]
    TASK10_FIELD_NUMBER: _ClassVar[int]
    TASK11_FIELD_NUMBER: _ClassVar[int]
    task1: WnTimetaskSetMessage
    task2: WnTimetaskSetMessage
    task3: WnTimetaskSetMessage
    task4: WnTimetaskSetMessage
    task5: WnTimetaskSetMessage
    task6: WnTimetaskSetMessage
    task7: WnTimetaskSetMessage
    task8: WnTimetaskSetMessage
    task9: WnTimetaskSetMessage
    task10: WnTimetaskSetMessage
    task11: WnTimetaskSetMessage
    def __init__(self, task1: _Optional[_Union[WnTimetaskSetMessage, _Mapping]] = ..., task2: _Optional[_Union[WnTimetaskSetMessage, _Mapping]] = ..., task3: _Optional[_Union[WnTimetaskSetMessage, _Mapping]] = ..., task4: _Optional[_Union[WnTimetaskSetMessage, _Mapping]] = ..., task5: _Optional[_Union[WnTimetaskSetMessage, _Mapping]] = ..., task6: _Optional[_Union[WnTimetaskSetMessage, _Mapping]] = ..., task7: _Optional[_Union[WnTimetaskSetMessage, _Mapping]] = ..., task8: _Optional[_Union[WnTimetaskSetMessage, _Mapping]] = ..., task9: _Optional[_Union[WnTimetaskSetMessage, _Mapping]] = ..., task10: _Optional[_Union[WnTimetaskSetMessage, _Mapping]] = ..., task11: _Optional[_Union[WnTimetaskSetMessage, _Mapping]] = ...) -> None: ...

class WnTimetaskSetMessage(_message.Message):
    __slots__ = ("taskIndex", "timeRange", "type", "dstTime")
    TASKINDEX_FIELD_NUMBER: _ClassVar[int]
    TIMERANGE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DSTTIME_FIELD_NUMBER: _ClassVar[int]
    taskIndex: int
    timeRange: WnTimeRangeStrategy
    type: int
    dstTime: int
    def __init__(self, taskIndex: _Optional[int] = ..., timeRange: _Optional[_Union[WnTimeRangeStrategy, _Mapping]] = ..., type: _Optional[int] = ..., dstTime: _Optional[int] = ...) -> None: ...

class WnTimetaskDelMessage(_message.Message):
    __slots__ = ("taskIndex",)
    TASKINDEX_FIELD_NUMBER: _ClassVar[int]
    taskIndex: int
    def __init__(self, taskIndex: _Optional[int] = ...) -> None: ...

class WnTimeRangeStrategy(_message.Message):
    __slots__ = ("isConfig", "isEnable", "timeMode", "timeData", "startTime", "stopTime")
    ISCONFIG_FIELD_NUMBER: _ClassVar[int]
    ISENABLE_FIELD_NUMBER: _ClassVar[int]
    TIMEMODE_FIELD_NUMBER: _ClassVar[int]
    TIMEDATA_FIELD_NUMBER: _ClassVar[int]
    STARTTIME_FIELD_NUMBER: _ClassVar[int]
    STOPTIME_FIELD_NUMBER: _ClassVar[int]
    isConfig: int
    isEnable: int
    timeMode: int
    timeData: int
    startTime: WnTimeRtcData
    stopTime: WnTimeRtcData
    def __init__(self, isConfig: _Optional[int] = ..., isEnable: _Optional[int] = ..., timeMode: _Optional[int] = ..., timeData: _Optional[int] = ..., startTime: _Optional[_Union[WnTimeRtcData, _Mapping]] = ..., stopTime: _Optional[_Union[WnTimeRtcData, _Mapping]] = ...) -> None: ...

class WnTimeRtcData(_message.Message):
    __slots__ = ("week", "sec", "min", "hour", "day", "month", "year")
    WEEK_FIELD_NUMBER: _ClassVar[int]
    SEC_FIELD_NUMBER: _ClassVar[int]
    MIN_FIELD_NUMBER: _ClassVar[int]
    HOUR_FIELD_NUMBER: _ClassVar[int]
    DAY_FIELD_NUMBER: _ClassVar[int]
    MONTH_FIELD_NUMBER: _ClassVar[int]
    YEAR_FIELD_NUMBER: _ClassVar[int]
    week: int
    sec: int
    min: int
    hour: int
    day: int
    month: int
    year: int
    def __init__(self, week: _Optional[int] = ..., sec: _Optional[int] = ..., min: _Optional[int] = ..., hour: _Optional[int] = ..., day: _Optional[int] = ..., month: _Optional[int] = ..., year: _Optional[int] = ...) -> None: ...
