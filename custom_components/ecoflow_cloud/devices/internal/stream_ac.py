from typing import override
from typing import Any
import logging

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.util import utcnow

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import BaseInternalDevice, const
from custom_components.ecoflow_cloud.number import BatteryBackupLevel
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

    # moduleWifiRssi
    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        outer_self = self

        class ProtoBackupReserveEntity(BatteryBackupLevel):
            async def async_set_native_value(self_, value: float):
                raw = outer_self._build_proto_command(102, int(value))
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

            def turn_off(self_, **kwargs):
                raw = self._build_proto_command(self_._field_num, self_._disable_val)
                client.mqtt_client.publish(self.device_info.set_topic, raw)

        return [
            ProtoEnabledEntity(
                client, self, "feedGridMode", const.STREAM_FEED_IN_CONTROL,
                lambda value: {}, field_num=168, enable_val=1, disable_val=2,
                enableValue=2, disableValue=1,
            ),
            ProtoEnabledEntity(
                client, self, "relay2Onoff", const.MODE_AC1_ON,
                lambda value: {}, field_num=380, enable_val=1, disable_val=0,
                enableValue=True, disableValue=False,
            ),
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return []

    _MANUAL_FIELD_MAP: dict = {
        380: ("relay2Onoff", bool),
        461: ("backupReverseSoc", int),
        1628: ("feedGridMode", int),
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
