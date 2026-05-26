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
    OutWattsSensorEntity,
    RemainSensorEntity,
    TempSensorEntity,
    WattsSensorEntity,
)
from custom_components.ecoflow_cloud.select import DictSelectEntity
from custom_components.ecoflow_cloud.switch import EnabledEntity

_LOGGER = logging.getLogger(__name__)


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
            WattsSensorEntity(client, self, "gridConnectionPower", const.STREAM_POWER_AC),
            # "gridConnectionSta": "PANEL_GRID_IN",
            # "gridConnectionVol": 235.34576,
            MilliVoltSensorEntity(client, self, "gridConnectionVol", const.STREAM_POWER_VOL, False),
            # "gridSysDeviceCnt": 2,
            # "heatfilmNtcNum": 0,
            # "heatfilmTemp": [],
            # "hwVer": "V0.0.0",
            # "inputWatts": 900,
            InWattsSensorEntity(client, self, "inputWatts", const.STREAM_IN_POWER, False),
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
            OutWattsSensorEntity(client, self, "outputWatts", const.STREAM_OUT_POWER, False),
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
            WattsSensorEntity(client, self, "powGetBpCms", const.STREAM_POWER_BATTERY),
            # "powGetPv": 0.0,
            WattsSensorEntity(client, self, "powGetPv", const.STREAM_POWER_PV_1, False, True),
            # "powGetPv2": 0.0,
            WattsSensorEntity(client, self, "powGetPv2", const.STREAM_POWER_PV_2, False, True),
            # "powGetPv3": 0.0,
            WattsSensorEntity(client, self, "powGetPv3", const.STREAM_POWER_PV_3, False, True),
            # "powGetPv4": 0.0,
            WattsSensorEntity(client, self, "powGetPv4", const.STREAM_POWER_PV_4, False, True),
            # "powGetPvSum": 2051.3975,
            WattsSensorEntity(client, self, "powGetPvSum", const.STREAM_POWER_PV_SUM),
            # "powGetSchuko1": 0.0,
            WattsSensorEntity(client, self, "powGetSchuko1", const.STREAM_GET_SCHUKO1, False, True),
            # "powGetSchuko2": 18.654325,
            WattsSensorEntity(client, self, "powGetSchuko2", const.STREAM_GET_SCHUKO2, False, True),
            # "powGetSysGrid": -135.0,
            WattsSensorEntity(client, self, "powGetSysGrid", const.STREAM_POWER_GRID),
            # "powGetSysLoad": 0.0,
            WattsSensorEntity(client, self, "powGetSysLoad", const.STREAM_GET_SYS_LOAD),
            # "powGetSysLoadFromBp": 0.0,
            WattsSensorEntity(client, self, "powGetSysLoadFromBp", const.STREAM_GET_SYS_LOAD_FROM_BP),
            # "powGetSysLoadFromGrid": 0.0,
            WattsSensorEntity(
                client,
                self,
                "powGetSysLoadFromGrid",
                const.STREAM_GET_SYS_LOAD_FROM_GRID,
            ),
            # "powGetSysLoadFromPv": 0.0,
            WattsSensorEntity(client, self, "powGetSysLoadFromPv", const.STREAM_GET_SYS_LOAD_FROM_PV),
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
            WattsSensorEntity(client, self, "sysGridConnectionPower", const.STREAM_POWER_AC_SYS, False),
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
                3,
                95,
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
