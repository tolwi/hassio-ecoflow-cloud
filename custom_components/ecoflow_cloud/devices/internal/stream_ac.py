from typing import override
from typing import Any
import logging

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import PERCENTAGE
from homeassistant.util import utcnow

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import BaseInternalDevice, const
from custom_components.ecoflow_cloud.number import BatteryBackupLevel, MinMaxLevelEntity
from custom_components.ecoflow_cloud.sensor import (
    CapacitySensorEntity,
    CumulativeCapacitySensorEntity,
    CyclesSensorEntity,
    EnergySensorEntity,
    InWattsSensorEntity,
    LevelSensorEntity,
    MilliVoltSensorEntity,
    MiscSensorEntity,
    OutWattsSensorEntity,
    RemainSensorEntity,
    TempSensorEntity,
    WattsSensorEntity,
)
from custom_components.ecoflow_cloud.select import DictSelectEntity
from custom_components.ecoflow_cloud.switch import EnabledEntity

_LOGGER = logging.getLogger(__name__)

# Power values for the Stream AC are decoded as floats. A field whose real
# value is 0 occasionally decodes to a denormalized-float artifact (e.g.
# -1.40129846432482e-45), which then surfaces verbatim on the power sensors.
# Clamp any such near-zero float to a clean 0 so every power sensor on this
# device reports 0 instead of the artifact.
_POWER_CLAMP_THRESHOLD = 0.01


def _clamp_small_watts(val: Any) -> Any:
    if isinstance(val, float) and abs(val) < _POWER_CLAMP_THRESHOLD:
        return 0
    return val


class StreamACWattsSensorEntity(WattsSensorEntity):
    @override
    def _update_value(self, val: Any) -> bool:
        return super()._update_value(_clamp_small_watts(val))


class StreamACInWattsSensorEntity(InWattsSensorEntity):
    @override
    def _update_value(self, val: Any) -> bool:
        return super()._update_value(_clamp_small_watts(val))


class StreamACOutWattsSensorEntity(OutWattsSensorEntity):
    @override
    def _update_value(self, val: Any) -> bool:
        return super()._update_value(_clamp_small_watts(val))


class StreamAC(BaseInternalDevice):
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            # "accuChgCap": 198511,
            CumulativeCapacitySensorEntity(client, self, "accuChgCap", const.ACCU_CHARGE_CAP, False),
            # "accuChgEnergy": 3992,
            EnergySensorEntity(client, self, "accuChgEnergy", const.ACCU_CHARGE_ENERGY, False),
            # "accuDsgCap": 184094,
            CumulativeCapacitySensorEntity(client, self, "accuDsgCap", const.ACCU_DISCHARGE_CAP, False),
            # "accuDsgEnergy": 3646,
            EnergySensorEntity(client, self, "accuDsgEnergy", const.ACCU_DISCHARGE_ENERGY, False),
            # "actSoc": 46.0,
            # "amp": 44671,
            # "backupReverseSoc": 5,
            # "balanceCmd": 0,
            # "balanceState": 0,
            # "bmsAlarmState1": 0,
            # "bmsAlarmState2": 0,
            # "bmsBattHeating": false,
            # "bmsBattSoc": 46.0,
            # "bmsBattSoh": 100.0,
            # "bmsChgDsgState": 2,
            # "bmsChgRemTime": 88,
            RemainSensorEntity(client, self, "bmsChgRemTime", const.CHARGE_REMAINING_TIME, False),
            # "bmsDesignCap": 1920,
            # "bmsDsgRemTime": 5939,
            RemainSensorEntity(client, self, "bmsDsgRemTime", const.DISCHARGE_REMAINING_TIME, False),
            # "bmsFault": 0,
            # "bmsFaultState": 0,
            # "bmsHeartbeatVer": 260,
            # "bmsMaxCellTemp": 35,
            # "bmsMaxMosTemp": 47,
            # "bmsMinCellTemp": 33,
            # "bmsMinMosTemp": 47,
            # "bmsProtectState1": 0,
            # "bmsProtectState2": 0,
            # "bmsSn": "BKxxxx",
            # "bqSysStatReg": 0,
            # "brightness": 100,
            # "busbarPowLimit": 2300,
            # "calendarSoh": 88.0,
            # "cellId": 2,
            # "cellNtcNum": 2,
            # "cellSeriesNum": 6,
            # "chgDsgState": 2,
            # "cloudMetter.hasMeter": true,
            # "cloudMetter.model": "CT_EF_01",
            # "cloudMetter.phaseAPower": -134,
            # "cloudMetter.phaseBPower": 0,
            # "cloudMetter.phaseCPower": 0,
            # "cloudMetter.sn": "BKxxxx",
            # "cmsBattFullEnergy": 3840,
            # "cmsBattPowInMax": 2114,
            # "cmsBattPowOutMax": 2400,
            # "cmsBattSoc": 43.0,
            # "cmsBattSoh": 100.0,
            # "cmsBmsRunState": 1,
            # "cmsChgDsgState": 2,
            # "cmsChgRemTime": 88,
            # "cmsDsgRemTime": 5939,
            # "cmsMaxChgSoc": 100,
            # "cmsMinDsgSoc": 5,
            # "curSensorNtcNum": 0,
            # "curSensorTemp": [],
            # "cycleSoh": 100.0,
            # "cycles": 1,
            CyclesSensorEntity(client, self, "cycles", const.CYCLES, False),
            # "designCap": 100000,
            CapacitySensorEntity(client, self, "designCap", const.STREAM_DESIGN_CAPACITY, False),
            # "devCtrlStatus": 1,
            # "devSleepState": 0,
            # "diffSoc": 0.2050476,
            # "displayPropertyFullUploadPeriod": 120000,
            # "displayPropertyIncrementalUploadPeriod": 2000,
            # "distributedDeviceStatus": "MASTER",
            # "ecloudOcv": 65535,
            # "energyBackupState": 0,
            # "energyStrategyOperateMode.operateIntelligentScheduleModeOpen": false,
            # "energyStrategyOperateMode.operateScheduledOpen": false,
            # "energyStrategyOperateMode.operateSelfPoweredOpen": true,
            # "energyStrategyOperateMode.operateTouModeOpen": false,
            # "f32ShowSoc": 46.317574,
            LevelSensorEntity(client, self, "f32ShowSoc", const.STREAM_POWER_BATTERY_SOC, False),
            # "feedGridMode": 2,
            # "feedGridModePowLimit": 800,
            # "feedGridModePowMax": 800,
            # "fullCap": 100000,
            CapacitySensorEntity(client, self, "fullCap", const.STREAM_FULL_CAPACITY, False),
            # "gridCodeSelection": "GRID_STD_CODE_UTE_MAINLAND",
            # "gridCodeVersion": 10001,
            # "gridConnectionFreq": 49.974655,
            # "gridConnectionPower": -967.2364,
            StreamACWattsSensorEntity(client, self, "gridConnectionPower", const.STREAM_POWER_AC),
            # "gridConnectionSta": "PANEL_GRID_IN",
            # "gridConnectionVol": 235.34576,
            MilliVoltSensorEntity(client, self, "gridConnectionVol", const.STREAM_POWER_VOL, False),
            # "gridSysDeviceCnt": 2,
            # "heatfilmNtcNum": 0,
            # "heatfilmTemp": [],
            # "hwVer": "V0.0.0",
            # "inputWatts": 900,
            StreamACInWattsSensorEntity(client, self, "inputWatts", const.STREAM_IN_POWER, False),
            # "invNtcTemp3": 49,
            # "maxBpInput": 1050,
            # "maxBpOutput": 1200,
            # "maxCellTemp": 35,
            TempSensorEntity(client, self, "maxCellTemp", const.MAX_CELL_TEMP, False),
            # "maxCellVol": 3362,
            MilliVoltSensorEntity(client, self, "maxCellVol", const.MAX_CELL_VOLT, False),
            # "maxCurSensorTemp": 0,
            # "maxEnvTemp": 0,
            # "maxHeatfilmTemp": 0,
            # "maxInvInput": 1200,
            # "maxInvOutput": 1200,
            # "maxMosTemp": 47,
            # "maxVolDiff": 5,
            # "mcuPinInStatus": 0,
            # "mcuPinOutStatus": 0,
            # "minCellTemp": 33,
            TempSensorEntity(client, self, "minCellTemp", const.MIN_CELL_TEMP, False),
            # "minCellVol": 3357,
            MilliVoltSensorEntity(client, self, "minCellVol", const.MIN_CELL_VOLT, False),
            # "minCurSensorTemp": 0,
            # "minEnvTemp": 0,
            # "minHeatfilmTemp": 0,
            # "minMosTemp": 47,
            # "moduleWifiRssi": -22.0,
            # "mosNtcNum": 1,
            # "mosState": 3,
            # "num": 0,
            # "openBmsFlag": 1,
            # "outputWatts": 0,
            StreamACOutWattsSensorEntity(client, self, "outputWatts", const.STREAM_OUT_POWER, False),
            # "packSn": "BKxxxxx",
            # "plugInInfoPv2Amp": 0.0,
            # "plugInInfoPv2Flag": false,
            # "plugInInfoPv2Vol": 0.0,
            # "plugInInfoPv3Amp": 0.0,
            # "plugInInfoPv3Flag": false,
            # "plugInInfoPv3Vol": 0.0,
            # "plugInInfoPv4Amp": 0.0,
            # "plugInInfoPv4Flag": false,
            # "plugInInfoPv4Vol": 0.0,
            # "plugInInfoPvAmp": 0.0,
            # "plugInInfoPvFlag": false,
            # "plugInInfoPvVol": 0.0,
            # "powConsumptionMeasurement": 2,
            # "powGetBpCms": 1915.0862,
            StreamACWattsSensorEntity(client, self, "powGetBpCms", const.STREAM_POWER_BATTERY),
            # "powGetPv": 0.0,
            StreamACWattsSensorEntity(client, self, "powGetPv", const.STREAM_POWER_PV_1, False, True),
            # "powGetPv2": 0.0,
            StreamACWattsSensorEntity(client, self, "powGetPv2", const.STREAM_POWER_PV_2, False, True),
            # "powGetPv3": 0.0,
            StreamACWattsSensorEntity(client, self, "powGetPv3", const.STREAM_POWER_PV_3, False, True),
            # "powGetPv4": 0.0,
            StreamACWattsSensorEntity(client, self, "powGetPv4", const.STREAM_POWER_PV_4, False, True),
            # "powGetPvSum": 2051.3975,
            StreamACWattsSensorEntity(client, self, "powGetPvSum", const.STREAM_POWER_PV_SUM),
            # "powGetSchuko1": 0.0,
            StreamACWattsSensorEntity(client, self, "powGetSchuko1", const.STREAM_GET_SCHUKO1, False, True),
            # "powGetSchuko2": 18.654325,
            StreamACWattsSensorEntity(client, self, "powGetSchuko2", const.STREAM_GET_SCHUKO2, False, True),
            # "powGetSysGrid": -135.0,
            StreamACWattsSensorEntity(client, self, "powGetSysGrid", const.STREAM_POWER_GRID),
            # "powGetSysLoad": 0.0,
            StreamACWattsSensorEntity(client, self, "powGetSysLoad", const.STREAM_GET_SYS_LOAD),
            # "powGetSysLoadFromBp": 0.0,
            StreamACWattsSensorEntity(client, self, "powGetSysLoadFromBp", const.STREAM_GET_SYS_LOAD_FROM_BP),
            # "powGetSysLoadFromGrid": 0.0,
            StreamACWattsSensorEntity(
                client,
                self,
                "powGetSysLoadFromGrid",
                const.STREAM_GET_SYS_LOAD_FROM_GRID,
            ),
            # "powGetSysLoadFromPv": 0.0,
            StreamACWattsSensorEntity(client, self, "powGetSysLoadFromPv", const.STREAM_GET_SYS_LOAD_FROM_PV),
            # "powSysAcInMax": 4462,
            # "powSysAcOutMax": 800,
            # "productDetail": 5,
            # "productType": 58,
            # "realSoh": 100.0,
            LevelSensorEntity(client, self, "realSoh", const.REAL_SOH, False),
            # "relay1Onoff": true,
            # "relay2Onoff": true,
            # "relay3Onoff": true,
            # "relay4Onoff": true,
            # "remainCap": 46317,
            CapacitySensorEntity(client, self, "remainCap", const.STREAM_REMAIN_CAPACITY, False),
            # "remainTime": 88,
            RemainSensorEntity(client, self, "remainTime", const.REMAINING_TIME, False),
            # "runtimePropertyFullUploadPeriod": 120000,
            # "runtimePropertyIncrementalUploadPeriod": 2000,
            # "seriesConnectDeviceId": 1,
            # "seriesConnectDeviceStatus": "MASTER",
            # "soc": 46,
            LevelSensorEntity(client, self, "soc", const.STREAM_POWER_BATTERY, False)
            .attr("designCap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("fullCap", const.ATTR_FULL_CAPACITY, 0)
            .attr("remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            # "socketMeasurePower": 0.0,
            # "soh": 100,
            LevelSensorEntity(client, self, "soh", const.SOH, False),
            # "stormPatternEnable": false,
            # "stormPatternEndTime": 0,
            # "stormPatternOpenFlag": false,
            # "sysGridConnectionPower": -2020.0437,
            StreamACWattsSensorEntity(client, self, "sysGridConnectionPower", const.STREAM_POWER_AC_SYS, False),
            # "sysLoaderVer": 4294967295,
            # "sysState": 3,
            # "sysVer": 33620026,
            # "systemGroupId": 12356789,
            # "systemMeshId": 1,
            # "tagChgAmp": 50000,
            # "targetSoc": 46.314102,
            # "temp": 35,
            TempSensorEntity(client, self, "temp", const.BATTERY_TEMP, False)
            .attr("minCellTemp", const.ATTR_MIN_CELL_TEMP, 0)
            .attr("maxCellTemp", const.ATTR_MAX_CELL_TEMP, 0),
            # "v1p0.bmsModel": 1,
            # "v1p0.bmsWarningState": 0,
            # "v1p0.chgAmp": 90000,
            # "v1p0.chgCmd": 1,
            # "v1p0.chgRemainTime": 88,
            # "v1p0.chgState": 2,
            # "v1p0.chgVol": 22158,
            # "v1p0.dsgCmd": 1,
            # "v1p0.dsgRemainTime": 5939,
            # "v1p0.emsIsNormalFlag": 1,
            # "v1p0.f32LcdShowSoc": 46.313,
            # "v1p0.fanLevel": 0,
            # "v1p0.lcdShowSoc": 46,
            # "v1p0.maxAvailableNum": 1,
            # "v1p0.maxChargeSoc": 100,
            # "v1p0.maxCloseOilEbSoc": 100,
            # "v1p0.minDsgSoc": 5,
            # "v1p0.minOpenOilEbSoc": 20,
            # "v1p0.openBmsIdx": 1,
            # "v1p0.openUpsFlag": 1,
            # "v1p0.paraVolMax": 0,
            # "v1p0.paraVolMin": 0,
            # "v1p3.chgDisableCond": 0,
            # "v1p3.chgLinePlugInFlag": 0,
            # "v1p3.dsgDisableCond": 0,
            # "v1p3.emsHeartbeatVer": 259,
            # "v1p3.sysChgDsgState": 2,
            # "vol": 20161,
            MilliVoltSensorEntity(client, self, "vol", const.BATTERY_VOLT, False)
            .attr("minCellVol", const.ATTR_MIN_CELL_VOLT, 0)
            .attr("maxCellVol", const.ATTR_MAX_CELL_VOLT, 0),
            # "waterInFlag": 0,
            # Schedule entry — _decode_schedule_entry surfaces the active
            # SetTimeTaskWrite-style entry from DisplayPropertyUpload field
            # 584 into raw["params"]["schedule.*"]. The summary string is
            # the entity state; the structured fields hang off as attrs.
            MiscSensorEntity(client, self, "schedule.summary", const.STREAM_SCHEDULE)
            .attr("schedule.enabled", "Enabled", False)
            .attr("schedule.power", "Power (W)", 0)
            .attr("schedule.startMin", "Start (min of day)", 0)
            .attr("schedule.endMin", "End (min of day)", 0)
            .attr("schedule.days", "Days bitmask", 0)
            .attr("schedule.timeMode", "Time mode", 0)
            .attr("schedule.taskIndex", "Task index", 0)
            .attr("schedule.isValid", "Is valid", False),
        ]

    def _build_proto_command(self, field_num: int, value: int) -> bytes:
        """Build a protobuf command payload for Stream AC internal API."""
        import time
        from .proto import stream_ac_pb2

        def encode_varint(n):
            result = bytearray()
            while True:
                bits = n & 0x7F
                n >>= 7
                if n:
                    result.append(0x80 | bits)
                else:
                    result.append(bits)
                    break
            return bytes(result)

        def encode_field(fnum, val):
            return encode_varint((fnum << 3) | 0) + encode_varint(val)

        pdata = encode_field(6, int(time.time())) + encode_field(field_num, value)

        import random
        header = stream_ac_pb2.StreamACHeader()
        header.src = 32
        header.dest = 2
        header.d_src = 1
        header.d_dest = 1
        header.cmd_func = 254
        header.cmd_id = 17
        header.data_len = len(pdata)
        header.need_ack = 1
        header.seq = random.randint(100000000, 999999999)
        header.product_id = 58
        header.version = 3
        header.payload_ver = 1
        setattr(header, "from", "Android")
        header.pdata = pdata

        msg = stream_ac_pb2.StreamACSendHeaderMsg()
        msg.msg.CopyFrom(header)
        return msg.SerializeToString()

    def _build_proto_schedule_command(
        self,
        *,
        task_index: int,
        enabled: bool,
        is_valid: bool,
        is_repeating: bool,
        time_mode: int,
        days: int,
        start_min: int,
        end_min: int,
        power: int,
    ) -> bytes:
        """Build a `SetTimeTaskWrite`-shaped write at outer field 595.

        Empirical field semantics (capture session 2026-05-26):
            inner f2  = taskIndex (slot number, observed=2)
            inner f3  = isValid (always 1 in valid entries)
            inner f4  = isEnable (elided when 0)
            inner f5  = isRepeating
            inner f8  = timeMode (1=daily, 2=weekly; device-specific enum)
            inner f9  = days bitmask (bit0=Mon … bit6=Sun; only meaningful
                        when time_mode >= 2)
            inner f10 = timeTable — packed varint with
                        `(end_min << 16) | start_min`
            inner f12 = power in watts

        Inner fields f6, f7, f11 are not used by this device generation
        despite the decompiled-proto's SetTimeTaskWrite schema listing
        them. The strategy doc's enum/field-mapping for the schedule was
        wrong for this device; mappings above are the live truth.

        There is no `type` (AC1 / AC2 / grid) field in the schedule
        entry — discharge routing is controlled by feedGridMode
        (field 168) at the device level, not per-schedule.
        """
        import time
        from .proto import stream_ac_pb2

        def encode_varint(n):
            result = bytearray()
            while True:
                bits = n & 0x7F
                n >>= 7
                if n:
                    result.append(0x80 | bits)
                else:
                    result.append(bits)
                    break
            return bytes(result)

        def encode_field(fnum, val):
            return encode_varint((fnum << 3) | 0) + encode_varint(val)

        def encode_bytes_field(fnum, payload):
            return (
                encode_varint((fnum << 3) | 2)
                + encode_varint(len(payload))
                + payload
            )

        # Build the inner SetTimeTaskWrite body. Field order and presence
        # match the EcoFlow app's captured wire layout exactly: f3 and f5
        # are always emitted (even when their value is 0 — proto3 would
        # normally elide that, but the device may rely on the explicit
        # presence, similar to how the cfgMaxChgSoc/cfgMinDsgSoc pair is
        # silently rejected when only one field is sent). f4 is the one
        # field the app does drop on disable — captured behavior.
        inner_parts = [
            encode_field(2, task_index),
            encode_field(3, 1 if is_valid else 0),
        ]
        if enabled:
            inner_parts.append(encode_field(4, 1))
        inner_parts.append(encode_field(5, 1 if is_repeating else 0))
        inner_parts.append(encode_field(8, time_mode))
        inner_parts.append(encode_field(9, days))
        time_table_value = ((end_min & 0xFFFF) << 16) | (start_min & 0xFFFF)
        inner_parts.append(encode_bytes_field(10, encode_varint(time_table_value)))
        inner_parts.append(encode_field(12, power))
        inner = b"".join(inner_parts)

        # The schedule field 595 wraps an inner field-1 sub-message
        # containing the actual SetTimeTaskWrite. If the device supported
        # multiple entries in one write, additional field-1 sub-messages
        # would appear here.
        wrapper = encode_bytes_field(1, inner)
        pdata = (
            encode_field(6, int(time.time()))
            + encode_bytes_field(595, wrapper)
        )

        import random
        header = stream_ac_pb2.StreamACHeader()
        header.src = 32
        header.dest = 2
        header.d_src = 1
        header.d_dest = 1
        header.cmd_func = 254
        header.cmd_id = 17
        header.data_len = len(pdata)
        header.need_ack = 1
        header.seq = random.randint(100000000, 999999999)
        header.product_id = 58
        header.version = 3
        header.payload_ver = 1
        setattr(header, "from", "Android")
        header.pdata = pdata

        msg = stream_ac_pb2.StreamACSendHeaderMsg()
        msg.msg.CopyFrom(header)
        return msg.SerializeToString()

    def _build_proto_paired_command(
        self,
        field_num_a: int,
        value_a: int,
        field_num_b: int,
        value_b: int,
    ) -> bytes:
        """Build a write that carries two varint fields in one pdata.

        Some cfg writes on this device must include multiple paired fields
        in a single message — e.g. the SOC limit pair cfgMaxChgSoc (33)
        and cfgMinDsgSoc (34): writing only one of them is silently
        rejected by the device. Captured from the EcoFlow mobile app
        2026-05-26 — the app always emits both fields together even when
        only one slider changed, and the device only honours the change
        when both arrive in the same pdata.
        """
        import time
        from .proto import stream_ac_pb2

        def encode_varint(n):
            result = bytearray()
            while True:
                bits = n & 0x7F
                n >>= 7
                if n:
                    result.append(0x80 | bits)
                else:
                    result.append(bits)
                    break
            return bytes(result)

        def encode_field(fnum, val):
            return encode_varint((fnum << 3) | 0) + encode_varint(val)

        pdata = (
            encode_field(6, int(time.time()))
            + encode_field(field_num_a, value_a)
            + encode_field(field_num_b, value_b)
        )

        import random
        header = stream_ac_pb2.StreamACHeader()
        header.src = 32
        header.dest = 2
        header.d_src = 1
        header.d_dest = 1
        header.cmd_func = 254
        header.cmd_id = 17
        header.data_len = len(pdata)
        header.need_ack = 1
        header.seq = random.randint(100000000, 999999999)
        header.product_id = 58
        header.version = 3
        header.payload_ver = 1
        setattr(header, "from", "Android")
        header.pdata = pdata

        msg = stream_ac_pb2.StreamACSendHeaderMsg()
        msg.msg.CopyFrom(header)
        return msg.SerializeToString()

    def _build_proto_nested_command(
        self,
        outer_field_num: int,
        inner_field_num: int,
        value: bool,
        trailing_empty_field: int | None = None,
    ) -> bytes:
        """Build a protobuf command with a nested length-delimited sub-message (wire type 2).

        Used for grouped boolean fields like cfgEnergyStrategyOperateMode, where the
        outer field is a sub-message containing one or more inner varint booleans.
        Optionally appends a trailing empty length-delimited field (observed in the
        EcoFlow mobile app's writes as field 546 — appears to act as a "commit"
        marker the device requires before applying the change).
        """
        import time
        from .proto import stream_ac_pb2

        def encode_varint(n):
            result = bytearray()
            while True:
                bits = n & 0x7F
                n >>= 7
                if n:
                    result.append(0x80 | bits)
                else:
                    result.append(bits)
                    break
            return bytes(result)

        def encode_field(fnum, val):
            return encode_varint((fnum << 3) | 0) + encode_varint(val)

        def encode_nested_field(outer_fnum, inner_fnum, val):
            inner = encode_field(inner_fnum, int(bool(val)))
            return (
                encode_varint((outer_fnum << 3) | 2)
                + encode_varint(len(inner))
                + inner
            )

        def encode_empty_field(fnum):
            return encode_varint((fnum << 3) | 2) + encode_varint(0)

        pdata = encode_field(6, int(time.time())) + encode_nested_field(
            outer_field_num, inner_field_num, value
        )
        if trailing_empty_field is not None:
            pdata += encode_empty_field(trailing_empty_field)

        import random
        header = stream_ac_pb2.StreamACHeader()
        header.src = 32
        header.dest = 2
        header.d_src = 1
        header.d_dest = 1
        header.cmd_func = 254
        header.cmd_id = 17
        header.data_len = len(pdata)
        header.need_ack = 1
        header.seq = random.randint(100000000, 999999999)
        header.product_id = 58
        header.version = 3
        header.payload_ver = 1
        setattr(header, "from", "Android")
        header.pdata = pdata

        msg = stream_ac_pb2.StreamACSendHeaderMsg()
        msg.msg.CopyFrom(header)
        _LOGGER.debug("NESTED_CMD hex=%s", msg.SerializeToString().hex())
        return msg.SerializeToString()

    # moduleWifiRssi
    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        outer_self = self

        class ProtoBackupReserveEntity(BatteryBackupLevel):
            async def async_set_native_value(self_, value: float):
                raw = outer_self._build_proto_command(102, int(value))
                client.mqtt_client.publish(outer_self.device_info.set_topic, raw)

            def _updated(self_, data):
                super()._updated(data)
                # Pin to a fixed 15-100 range (true hardware ceiling) rather than
                # BatteryBackupLevel's dynamic clamp to the SOC limits, which capped
                # max at cmsMaxChgSoc (e.g. 82). Lets 95 be set as a charge target.
                self_._attr_native_min_value = 15
                self_._attr_native_max_value = 100

        class PairedSocNumberEntity(MinMaxLevelEntity):
            """SOC limit number that always writes the paired companion too.

            cfgMaxChgSoc (33) and cfgMinDsgSoc (34) must arrive in the same
            pdata, otherwise the device silently rejects the write. Each
            entity holds its own (mqtt_key, field_num) plus the companion's
            field_num and the mqtt_key for its current value, looked up
            from the device's last-known telemetry at write time.
            """

            _attr_native_unit_of_measurement = PERCENTAGE

            def __init__(
                self_,
                *args,
                my_field_num: int,
                other_field_num: int,
                other_mqtt_key: str,
                other_fallback: int,
                **kwargs,
            ):
                self_._my_field_num = my_field_num
                self_._other_field_num = other_field_num
                self_._other_mqtt_key = other_mqtt_key
                self_._other_fallback = other_fallback
                super().__init__(*args, **kwargs)

            async def async_set_native_value(self_, value: float):
                other_val = outer_self.data.params.get(
                    self_._other_mqtt_key, self_._other_fallback
                )
                raw = outer_self._build_proto_paired_command(
                    self_._my_field_num, int(value),
                    self_._other_field_num, int(other_val),
                )
                client.mqtt_client.publish(outer_self.device_info.set_topic, raw)

        return [
            ProtoBackupReserveEntity(
                client,
                self,
                "backupReverseSoc",
                const.BACKUP_RESERVE_LEVEL,
                15,
                100,
                "cmsMinDsgSoc",
                "cmsMaxChgSoc",
                3,
                lambda value: {},
            ),
            # Max charge SOC — write field 33 paired with field 34; read at
            # field 270 (cmsMaxChgSoc). See _build_proto_paired_command for
            # why the pairing is mandatory.
            PairedSocNumberEntity(
                client, self, "cmsMaxChgSoc", const.MAX_CHARGE_LEVEL,
                50, 100, lambda value: {},
                my_field_num=33, other_field_num=34,
                other_mqtt_key="cmsMinDsgSoc", other_fallback=5,
            ),
            # Min discharge SOC — write field 34 paired with field 33; read
            # at field 271 (cmsMinDsgSoc).
            PairedSocNumberEntity(
                client, self, "cmsMinDsgSoc", const.MIN_DISCHARGE_LEVEL,
                0, 30, lambda value: {},
                my_field_num=34, other_field_num=33,
                other_mqtt_key="cmsMaxChgSoc", other_fallback=100,
            ),
        ]

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        from custom_components.ecoflow_cloud.switch import EnabledEntity
        outer_self = self

        class ScheduleEnabledSwitchEntity(EnabledEntity):
            """Toggle the active schedule entry on/off by re-sending the
            full SetTimeTaskWrite at field 595 with the new isEnable bit.

            All other parameters (taskIndex, time slot, power, days,
            timeMode, isValid, isRepeating) are read from the last-known
            telemetry surfaced by _decode_schedule_entry; this entity does
            not let the user edit them — use the EcoFlow mobile app for
            that and then gate the resulting schedule on/off from here.
            """

            def turn_on(self_, **kwargs):
                self_._send_schedule(True)
                self_._attr_is_on = True
                self_.schedule_update_ha_state()

            def turn_off(self_, **kwargs):
                self_._send_schedule(False)
                self_._attr_is_on = False
                self_.schedule_update_ha_state()

            def _send_schedule(self_, enabled: bool):
                params = outer_self.data.params
                raw = outer_self._build_proto_schedule_command(
                    task_index=int(params.get("schedule.taskIndex") or 2),
                    enabled=enabled,
                    is_valid=bool(params.get("schedule.isValid", True)),
                    is_repeating=bool(params.get("schedule.isRepeating", False)),
                    time_mode=int(params.get("schedule.timeMode") or 1),
                    days=int(params.get("schedule.days") or 0),
                    start_min=int(params.get("schedule.startMin") or 0),
                    end_min=int(params.get("schedule.endMin") or 0),
                    power=int(params.get("schedule.power") or 0),
                )
                client.mqtt_client.publish(outer_self.device_info.set_topic, raw)

        class ProtoEnabledEntity(EnabledEntity):
            def __init__(self_, *args, field_num, enable_val, disable_val, **kwargs):
                self_._field_num = field_num
                self_._enable_val = enable_val
                self_._disable_val = disable_val
                super().__init__(*args, **kwargs)

            def turn_on(self_, **kwargs):
                raw = self._build_proto_command(self_._field_num, self_._enable_val)
                client.mqtt_client.publish(self.device_info.set_topic, raw)
                self_._attr_is_on = True
                self_.schedule_update_ha_state()

            def turn_off(self_, **kwargs):
                raw = self._build_proto_command(self_._field_num, self_._disable_val)
                client.mqtt_client.publish(self.device_info.set_topic, raw)
                self_._attr_is_on = False
                self_.schedule_update_ha_state()

        class ProtoNestedEnabledEntity(EnabledEntity):
            def __init__(
                self_, *args,
                outer_field_num,
                enable_inner_field_num,
                disable_inner_field_num,
                trailing_empty_field=None,
                **kwargs,
            ):
                self_._outer_field_num = outer_field_num
                self_._enable_inner_field_num = enable_inner_field_num
                self_._disable_inner_field_num = disable_inner_field_num
                self_._trailing_empty_field = trailing_empty_field
                super().__init__(*args, **kwargs)

            def turn_on(self_, **kwargs):
                raw = self._build_proto_nested_command(
                    self_._outer_field_num,
                    self_._enable_inner_field_num,
                    True,
                    trailing_empty_field=self_._trailing_empty_field,
                )
                client.mqtt_client.publish(self.device_info.set_topic, raw)
                self_._attr_is_on = True
                self_.schedule_update_ha_state()

            def turn_off(self_, **kwargs):
                raw = self._build_proto_nested_command(
                    self_._outer_field_num,
                    self_._disable_inner_field_num,
                    True,
                    trailing_empty_field=self_._trailing_empty_field,
                )
                client.mqtt_client.publish(self.device_info.set_topic, raw)
                self_._attr_is_on = False
                self_.schedule_update_ha_state()

        return [
            ProtoEnabledEntity(
                client, self, "feedGridMode", const.STREAM_FEED_IN_CONTROL,
                lambda value: {}, field_num=168, enable_val=1, disable_val=2,
                enableValue=2, disableValue=1,
            ),
            # Field 380 is reused for two different things depending on direction:
            #   Write (cfgWrite, top-level varint 0/1): AC1 relay toggle
            #     (relay2Onoff). Empirically verified to click the relay in
            #     commit 218ad96.
            #   Read (DisplayPropertyUpload field 380): plugInInfoPvVol — PV1
            #     input voltage as a fixed32 float, nested two levels deep
            #     inside Champ_cmd21_3. Not surfaced by the current decoder
            #     (it's not declared in stream_ac.proto and
            #     _decode_manual_fields only walks the top level of pdata), so
            #     this switch's state stays "unknown" until the user toggles
            #     it. The _MANUAL_FIELD_MAP entry below is harmless but dead.
            ProtoEnabledEntity(
                client, self, "relay2Onoff", const.MODE_AC1_ON,
                lambda value: {}, field_num=380, enable_val=1, disable_val=0,
                enableValue=True, disableValue=False,
            ),
            # AC2 relay — write field 381 (adjacent to AC1's 380). Captured
            # from the EcoFlow app 2026-05-26: toggling AC2 in the app emits
            # a single-varint write at f381 with value 0/1, same encoding as
            # AC1. The strategy doc's cfgAc2OutOpen=377 was incorrect for
            # this device generation.
            ProtoEnabledEntity(
                client, self, "relay3Onoff", const.MODE_AC2_ON,
                lambda value: {}, field_num=381, enable_val=1, disable_val=0,
                enableValue=True, disableValue=False,
            ),
            # "Semi-automated monitoring" discharge-strategy enable (field 239).
            # Confirmed on hardware 2026-05-31 via this switch: enable_val=1
            # starts discharge (battery 0 -> -800W to AC output, read field 1628
            # 0->1->2); disable_val=2 stops it (1628 -> 0, battery -> 0). Note
            # f239=0 was also acked but did NOT stop discharge, so the enum is
            # 1=on / 2=off (same as feedGridMode field 168), not 1/0. This
            # switch's shown state is optimistic (no dedicated read field).
            ProtoEnabledEntity(
                client, self, "dischargeStrategy239", const.STREAM_SEMI_AUTO_DISCHARGE,
                lambda value: {}, field_num=239, enable_val=1, disable_val=2,
                enableValue=True, disableValue=False,
            ),
            # Schedule enable/disable. Class definition is above; this
            # instance re-emits the active SetTimeTask entry with the new
            # isEnable bit, preserving the other params from telemetry.
            ScheduleEnabledSwitchEntity(
                client, self,
                "schedule.enabled",
                const.STREAM_SCHEDULE_ENABLED,
                lambda value: {},
                enableValue=True, disableValue=False,
            ),
            # Legacy Self-Powered-only switch, superseded by the four-option
            # Operating mode select below. Disabled by default for new installs
            # but kept so existing users' automations don't break on upgrade.
            ProtoNestedEnabledEntity(
                client, self,
                "energyStrategyOperateMode.operateSelfPoweredOpen",
                const.STREAM_OPERATION_MODE_SELF_POWERED,
                lambda value: {},
                outer_field_num=106,
                enable_inner_field_num=1,
                disable_inner_field_num=2,
                trailing_empty_field=546,
                enabled=False,
                enableValue=True, disableValue=False,
            ),
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        outer_self = self

        class ProtoNestedRadioSelectEntity(DictSelectEntity):
            """Select for a mutually-exclusive radio-button proto field group.

            The ``value`` stored in ``options_dict`` is the inner-field number
            inside the outer nested write — selecting an option writes that
            inner field with value=1 (the "set this mode" signal). The device
            echoes back the chosen mode by emitting the matching inner field
            of the read sub-message; ``_decode_manual_fields`` translates that
            into the ``active_key`` int that this entity binds to.
            """

            def __init__(self_, *args, outer_field_num, trailing_empty_field=None, **kwargs):
                self_._outer_field_num = outer_field_num
                self_._trailing_empty_field = trailing_empty_field
                super().__init__(*args, **kwargs)

            def select_option(self_, option: str) -> None:
                inner_field_num = self_._options_dict[option]
                raw = outer_self._build_proto_nested_command(
                    self_._outer_field_num,
                    inner_field_num,
                    True,
                    trailing_empty_field=self_._trailing_empty_field,
                )
                client.mqtt_client.publish(outer_self.device_info.set_topic, raw)
                self_._current_option = option
                self_.schedule_update_ha_state()

        return [
            # Operating mode — cfgEnergyStrategyOperateMode (write field 106) /
            # energyStrategyOperateMode (read field 393). Four mutually
            # exclusive modes; selecting one writes its inner field number
            # with value=1, followed by an empty field 546 commit marker.
            # The device acks on /set_reply with is_ack=1, cmd_id=18.
            ProtoNestedRadioSelectEntity(
                client, self,
                "energyStrategyOperateMode.activeMode",
                const.STREAM_OPERATION_MODE,
                const.STREAM_OPERATION_MODE_OPTIONS,
                lambda value: {},
                outer_field_num=106,
                trailing_empty_field=546,
            ),
        ]

    _MANUAL_FIELD_MAP: dict = {
        6: ("f32ShowSoc", int),
        # Read mirrors of cfgMaxChgSoc (write 33) and cfgMinDsgSoc (write 34).
        # Empirically captured 2026-05-26 from a real device: moving the
        # Min discharge SOC slider in the EcoFlow app from 12 → 16 caused
        # f271 in the next DisplayPropertyUpload to flip from 12 → 16.
        # Both writes echo through these read fields within one telemetry
        # cycle. f730/f994 (the previous guesses) are unrelated.
        270: ("cmsMaxChgSoc", int),
        271: ("cmsMinDsgSoc", int),
        # See the field-380 note above ProtoEnabledEntity in switches(). This
        # entry is currently dead because incoming field 380 lives two levels
        # deep inside Champ_cmd21_3 (where the proto names it plugInInfoPvVol,
        # a float), not at the top level walked by _decode_manual_fields.
        380: ("relay2Onoff", bool),
        461: ("backupReverseSoc", int),
        1628: ("feedGridMode", int),
    }

    # Radio-button-group sub-messages: outer field number → group definition.
    # Inner fields in such a group are mutually exclusive; the device clears
    # the others when one is set to 1. For each group:
    #   active_key — synthetic top-level int key written into raw["params"],
    #                whose value is the inner field number of the active mode.
    #                Bind a select entity to this key.
    #   flags      — inner_field_num → (mirrored_bool_name, cast). When an
    #                inner field is observed with value=1, the matching flag
    #                is set True and all other tracked flags are cleared.
    _RADIO_GROUP_MAP: dict = {
        393: {
            "active_key": "energyStrategyOperateMode.activeMode",
            "flags": {
                1: ("energyStrategyOperateMode.operateSelfPoweredOpen", bool),
                2: ("energyStrategyOperateMode.operateScheduledOpen", bool),
                3: ("energyStrategyOperateMode.operateTouModeOpen", bool),
                4: ("energyStrategyOperateMode.operateIntelligentScheduleModeOpen", bool),
            },
        },
    }

    # Day bitmask labels in human order, bit0=Mon (per inner field 9 of the
    # schedule entry — see _build_proto_schedule_command). Used to render the
    # `schedule.days` raw int into a friendly summary.
    _SCHEDULE_DAY_LABELS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

    def _decode_schedule_entry(self, wrapper_bytes: bytes, raw: dict) -> None:
        """Decode the schedule entry at top-level field 584 (read mirror of
        the write at field 595). See _build_proto_schedule_command for the
        inner field mapping; this is the inverse.

        Surfaces the decoded values into ``raw["params"]`` under
        ``schedule.*`` keys so they can be bound to sensor attributes and
        re-used by the schedule_enabled switch when it re-sends the entry
        with one flag flipped.
        """

        def varint(b, p):
            r, s = 0, 0
            while p < len(b):
                x = b[p]; p += 1
                r |= (x & 0x7f) << s
                if not (x & 0x80): return r, p
                s += 7
            return r, p

        # Outer wrapper: a single field-1 sub-message holding the entry.
        try:
            p = 0
            tag, p = varint(wrapper_bytes, p)
            if (tag >> 3) != 1 or (tag & 7) != 2:
                return
            ln, p = varint(wrapper_bytes, p)
            inner = wrapper_bytes[p:p + ln]
        except Exception:
            return

        # Defaults reflect "no schedule configured" — proto3 elides
        # zero-value scalars on the wire, so any missing field implies 0.
        entry = {
            "taskIndex": 0,
            "isValid": False,
            "enabled": False,
            "isRepeating": False,
            "timeMode": 0,
            "days": 0,
            "startMin": 0,
            "endMin": 0,
            "power": 0,
        }
        p = 0
        while p < len(inner):
            try:
                tag, p = varint(inner, p)
            except Exception:
                break
            fn, wt = tag >> 3, tag & 7
            if wt == 0:
                v, p = varint(inner, p)
                if fn == 2: entry["taskIndex"] = v
                elif fn == 3: entry["isValid"] = bool(v)
                elif fn == 4: entry["enabled"] = bool(v)
                elif fn == 5: entry["isRepeating"] = bool(v)
                elif fn == 8: entry["timeMode"] = v
                elif fn == 9: entry["days"] = v
                elif fn == 12: entry["power"] = v
            elif wt == 2:
                sub_ln, p = varint(inner, p)
                val_bytes = inner[p:p + sub_ln]
                p += sub_ln
                if fn == 10 and val_bytes:
                    # timeTable is a `repeated uint32 packed` carrying one
                    # entry here: (end_min << 16) | start_min, varint-encoded.
                    try:
                        tt, _ = varint(val_bytes, 0)
                        entry["startMin"] = tt & 0xFFFF
                        entry["endMin"] = tt >> 16
                    except Exception:
                        pass
            else:
                break

        # Surface every field individually for the entity attribute view.
        for k, v in entry.items():
            raw["params"][f"schedule.{k}"] = v

        # Rendered one-line summary used as the sensor state. Examples:
        #   "disabled"
        #   "Mon|Wed|Fri 10:00-12:00 400W"
        #   "daily 08:00-20:00 600W"
        if not entry["isValid"]:
            summary = "invalid"
        elif not entry["enabled"]:
            summary = "disabled"
        else:
            start = entry["startMin"]
            end = entry["endMin"]
            time_str = f"{start//60:02d}:{start%60:02d}-{end//60:02d}:{end%60:02d}"
            if entry["timeMode"] >= 2 and entry["days"]:
                days_str = "|".join(
                    label
                    for bit, label in enumerate(self._SCHEDULE_DAY_LABELS)
                    if entry["days"] & (1 << bit)
                )
            else:
                days_str = "daily"
            summary = f"{days_str} {time_str} {entry['power']}W"
        raw["params"]["schedule.summary"] = summary

    def _decode_manual_fields(self, pdata: bytes, raw: dict) -> None:
        """Extract specific unmapped protobuf varint fields from raw pdata bytes."""

        def decode_varint(data, pos):
            result, shift = 0, 0
            while pos < len(data):
                b = data[pos]
                pos += 1
                result |= (b & 0x7F) << shift
                if not (b & 0x80):
                    return result, pos
                shift += 7
            return result, pos

        pos = 0
        while pos < len(pdata):
            try:
                tag, pos = decode_varint(pdata, pos)
                field_num = tag >> 3
                wire_type = tag & 0x7
                if wire_type == 0:
                    value, pos = decode_varint(pdata, pos)
                    if field_num in self._MANUAL_FIELD_MAP:
                        name, cast = self._MANUAL_FIELD_MAP[field_num]
                        raw["params"][name] = cast(value)
                elif wire_type == 2:
                    length, pos = decode_varint(pdata, pos)
                    sub_bytes = pdata[pos:pos + length]
                    if field_num in self._RADIO_GROUP_MAP:
                        group = self._RADIO_GROUP_MAP[field_num]
                        active_key = group["active_key"]
                        flags = group["flags"]
                        sub_pos = 0
                        while sub_pos < len(sub_bytes):
                            try:
                                inner_tag, sub_pos = decode_varint(sub_bytes, sub_pos)
                                inner_field_num = inner_tag >> 3
                                inner_wire_type = inner_tag & 0x7
                                if inner_wire_type == 0:
                                    inner_value, sub_pos = decode_varint(sub_bytes, sub_pos)
                                    if inner_field_num in flags and inner_value:
                                        # This is the active mode. Mirror all
                                        # flags (this one True, others False)
                                        # and record the active inner-field
                                        # number for the select entity.
                                        for fnum, (fname, fcast) in flags.items():
                                            raw["params"][fname] = fcast(1 if fnum == inner_field_num else 0)
                                        raw["params"][active_key] = inner_field_num
                                    elif inner_field_num in flags:
                                        # Explicit value=0: clear just this
                                        # flag. The device sometimes emits
                                        # 0-values alongside the new active
                                        # inner field within the same message.
                                        fname, fcast = flags[inner_field_num]
                                        raw["params"][fname] = fcast(0)
                                    elif inner_value:
                                        # An untracked inner field is set:
                                        # the device is in a mode we don't
                                        # model. Clear all tracked flags so
                                        # stale state doesn't linger; leave
                                        # active_key unchanged (the select
                                        # will keep its last known value).
                                        for fname, fcast in flags.values():
                                            raw["params"][fname] = fcast(0)
                                else:
                                    break
                            except Exception:
                                break
                    elif field_num == 584:
                        # Schedule entry (read mirror of write field 595).
                        # Empirically mapped — see _decode_schedule_entry.
                        self._decode_schedule_entry(sub_bytes, raw)
                    elif field_num not in self._MANUAL_FIELD_MAP:
                        _LOGGER.info(
                            "STREAM_AC_BOOL_GROUP field=%d len=%d hex=%s",
                            field_num,
                            length,
                            sub_bytes.hex(),
                        )
                    pos += length
                elif wire_type == 5:
                    pos += 4
                elif wire_type == 1:
                    pos += 8
                else:
                    break
            except Exception:
                break

    @override
    def _prepare_data(self, raw_data: bytes) -> dict[str, Any]:
        raw: dict[str, Any] = {"params": {}}
        from .proto import stream_ac_pb2 as stream_ac
        from .proto import stream_ac_pb2 as stream_ac2

        try:
            payload = raw_data

            while True:
                _LOGGER.debug('payload "%s"', payload.hex())
                packet = stream_ac.StreamACSendHeaderMsg()
                packet.ParseFromString(payload)

                if hasattr(packet.msg, "pdata"):
                    _LOGGER.debug(
                        'cmd id "%u" fct id "%u" content "%s" - pdata:"%s"',
                        packet.msg.cmd_id,
                        packet.msg.cmd_func,
                        str(packet),
                        str(packet.msg.pdata.hex()),
                    )
                else:
                    _LOGGER.debug(
                        'cmd id "%u" fct id "%u" content "%s"',
                        packet.msg.cmd_id,
                        str(packet),
                    )

                if (
                    packet.msg.cmd_id < 0
                ):  # packet.msg.cmd_id != 21 and packet.msg.cmd_id != 22 and packet.msg.cmd_id != 50:
                    _LOGGER.info("Unsupported EcoPacket cmd id %u", packet.msg.cmd_id)

                else:
                    _LOGGER.debug('new payload "%s"', str(packet.msg.pdata.hex()))
                    # paquet HeaderStream
                    if packet.msg.cmd_id > 0:
                        self._parsedata(packet, stream_ac2.StreamACHeader(), raw)

                    # paquet Champ_cmd21
                    if packet.msg.cmd_id > 0:
                        self._parsedata(packet, stream_ac2.StreamACChamp_cmd21(), raw)

                    # paquet Champ_cmd21_3
                    if packet.msg.cmd_id > 0:
                        self._parsedata(packet, stream_ac2.StreamACChamp_cmd21_3(), raw)

                    # paquet Champ_cmd50
                    if packet.msg.cmd_id > 0:
                        self._parsedata(packet, stream_ac2.StreamACChamp_cmd50(), raw)

                    # paquet Champ_cmd50_3
                    if packet.msg.cmd_id > 0:
                        self._parsedata(packet, stream_ac2.StreamACChamp_cmd50_3(), raw)

                    self._decode_manual_fields(packet.msg.pdata, raw)

                    _LOGGER.info("Found %u fields", len(raw["params"]))

                    raw["timestamp"] = utcnow()

                if packet.ByteSize() >= len(payload):
                    break

                _LOGGER.info("Found another frame in payload")

                packet_length = len(payload) - packet.ByteSize()
                payload = payload[:packet_length]

        except Exception as error:
            _LOGGER.error(error)
            _LOGGER.debug(
                'raw_data : "%s"  raw_data.hex() : "%s"',
                str(raw_data),
                str(raw_data.hex()),
            )
        return raw

    def _parsedata(self, packet, content, raw):
        try:
            if hasattr(packet.msg, "pdata") and len(packet.msg.pdata) > 0:
                content.ParseFromString(packet.msg.pdata)

                if len(str(content)) > 0:
                    _LOGGER.debug(
                        'initial cmd id "%u" fct id "%u" msg \n"%s"',
                        packet.msg.cmd_id,
                        packet.msg.cmd_func,
                        str(content),
                    )

                for descriptor in content.DESCRIPTOR.fields:
                    if not content.HasField(descriptor.name):
                        continue

                    raw["params"][descriptor.name] = getattr(content, descriptor.name)

        except Exception as error:
            _LOGGER.debug(error)
            _LOGGER.debug("Erreur parsing pour le flux : %s", str(packet.msg.pdata.hex()))
