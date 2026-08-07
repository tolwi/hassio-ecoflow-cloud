from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper

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
    __slots__ = ("ackType", "checkType", "cmdFunc", "cmdId", "code", "dDest", "dSrc", "dataLen", "dest", "destSn", "deviceSn", "encType", "isAck", "isQueue", "isRwCmd", "moduleSn", "needAck", "payloadVer", "pdata", "productId", "seq", "src", "srcSn", "timeSnap", "version")
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
    def __init__(self, pdata: bytes | None = ..., src: int | None = ..., dest: int | None = ..., dSrc: int | None = ..., dDest: int | None = ..., encType: int | None = ..., checkType: int | None = ..., cmdFunc: int | None = ..., cmdId: int | None = ..., dataLen: int | None = ..., needAck: int | None = ..., isAck: int | None = ..., seq: int | None = ..., productId: int | None = ..., version: int | None = ..., payloadVer: int | None = ..., timeSnap: int | None = ..., isRwCmd: int | None = ..., isQueue: int | None = ..., ackType: int | None = ..., code: str | None = ..., moduleSn: str | None = ..., deviceSn: str | None = ..., srcSn: str | None = ..., destSn: str | None = ..., **kwargs) -> None: ...

class SendSmartPlugHeaderMsg(_message.Message):
    __slots__ = ("msg",)
    MSG_FIELD_NUMBER: _ClassVar[int]
    msg: _containers.RepeatedCompositeFieldContainer[SmartPlugHeader]
    def __init__(self, msg: _Iterable[SmartPlugHeader | _Mapping] | None = ...) -> None: ...

class WnPlugHeartbeatPack(_message.Message):
    __slots__ = ("brightness", "consNum", "consWatt", "country", "current", "dstTime", "errCode", "freq", "geneNum", "geneWatt", "heartbeatFrequency", "insightsSwitch", "lanState", "matterFabric", "maxCur", "maxWatts", "meshEnable", "meshId", "meshLevel", "mqttErr", "mqttErrTime", "otaDlErr", "otaDlTlsErr", "parentMac", "parentWifiRssi", "resetCount", "resetReason", "rssiThreshold", "rssiVariance", "rtcResetReason", "runTime", "selfEmsSwitch", "selfMac", "staIpAddr", "stackFree", "stackMinFree", "switchSta", "temp", "timeZone", "town", "utcTime", "volt", "warnCode", "watts", "wifiErr", "wifiErrTime")
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
    def __init__(self, errCode: int | None = ..., warnCode: int | None = ..., country: int | None = ..., town: int | None = ..., maxCur: int | None = ..., temp: int | None = ..., freq: int | None = ..., current: int | None = ..., volt: int | None = ..., watts: int | None = ..., switchSta: bool | None = ..., brightness: int | None = ..., maxWatts: int | None = ..., heartbeatFrequency: int | None = ..., meshEnable: int | None = ..., resetReason: int | None = ..., rtcResetReason: int | None = ..., resetCount: int | None = ..., runTime: int | None = ..., lanState: int | None = ..., stackFree: int | None = ..., stackMinFree: int | None = ..., meshId: int | None = ..., meshLevel: int | None = ..., selfMac: int | None = ..., parentMac: int | None = ..., otaDlErr: int | None = ..., otaDlTlsErr: int | None = ..., staIpAddr: int | None = ..., matterFabric: int | None = ..., geneNum: int | None = ..., consNum: int | None = ..., geneWatt: int | None = ..., consWatt: int | None = ..., wifiErr: int | None = ..., wifiErrTime: int | None = ..., mqttErr: int | None = ..., mqttErrTime: int | None = ..., selfEmsSwitch: int | None = ..., parentWifiRssi: int | None = ..., insightsSwitch: int | None = ..., rssiThreshold: int | None = ..., rssiVariance: int | None = ..., utcTime: int | None = ..., timeZone: int | None = ..., dstTime: int | None = ...) -> None: ...

class WnPlugSwitchMessage(_message.Message):
    __slots__ = ("switchSta",)
    SWITCHSTA_FIELD_NUMBER: _ClassVar[int]
    switchSta: bool
    def __init__(self, switchSta: bool | None = ...) -> None: ...

class WnBrightnessPack(_message.Message):
    __slots__ = ("brightness",)
    BRIGHTNESS_FIELD_NUMBER: _ClassVar[int]
    brightness: int
    def __init__(self, brightness: int | None = ...) -> None: ...

class WnMaxWattsPack(_message.Message):
    __slots__ = ("maxWatts",)
    MAXWATTS_FIELD_NUMBER: _ClassVar[int]
    maxWatts: int
    def __init__(self, maxWatts: int | None = ...) -> None: ...

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
    def __init__(self, task1: WnTimetaskSetMessage | _Mapping | None = ..., task2: WnTimetaskSetMessage | _Mapping | None = ..., task3: WnTimetaskSetMessage | _Mapping | None = ..., task4: WnTimetaskSetMessage | _Mapping | None = ..., task5: WnTimetaskSetMessage | _Mapping | None = ..., task6: WnTimetaskSetMessage | _Mapping | None = ..., task7: WnTimetaskSetMessage | _Mapping | None = ..., task8: WnTimetaskSetMessage | _Mapping | None = ..., task9: WnTimetaskSetMessage | _Mapping | None = ..., task10: WnTimetaskSetMessage | _Mapping | None = ..., task11: WnTimetaskSetMessage | _Mapping | None = ...) -> None: ...

class WnTimetaskSetMessage(_message.Message):
    __slots__ = ("dstTime", "taskIndex", "timeRange", "type")
    TASKINDEX_FIELD_NUMBER: _ClassVar[int]
    TIMERANGE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DSTTIME_FIELD_NUMBER: _ClassVar[int]
    taskIndex: int
    timeRange: WnTimeRangeStrategy
    type: int
    dstTime: int
    def __init__(self, taskIndex: int | None = ..., timeRange: WnTimeRangeStrategy | _Mapping | None = ..., type: int | None = ..., dstTime: int | None = ...) -> None: ...

class WnTimetaskDelMessage(_message.Message):
    __slots__ = ("taskIndex",)
    TASKINDEX_FIELD_NUMBER: _ClassVar[int]
    taskIndex: int
    def __init__(self, taskIndex: int | None = ...) -> None: ...

class WnTimeRangeStrategy(_message.Message):
    __slots__ = ("isConfig", "isEnable", "startTime", "stopTime", "timeData", "timeMode")
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
    def __init__(self, isConfig: int | None = ..., isEnable: int | None = ..., timeMode: int | None = ..., timeData: int | None = ..., startTime: WnTimeRtcData | _Mapping | None = ..., stopTime: WnTimeRtcData | _Mapping | None = ...) -> None: ...

class WnTimeRtcData(_message.Message):
    __slots__ = ("day", "hour", "min", "month", "sec", "week", "year")
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
    def __init__(self, week: int | None = ..., sec: int | None = ..., min: int | None = ..., hour: int | None = ..., day: int | None = ..., month: int | None = ..., year: int | None = ...) -> None: ...
