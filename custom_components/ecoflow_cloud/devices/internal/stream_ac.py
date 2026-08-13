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
from custom_components.ecoflow_cloud.sensor import (
    AmpSensorEntity,
    BatteryLimitSensorEntity,
    CapacitySensorEntity,
    CumulativeCapacitySensorEntity,
    CyclesSensorEntity,
    EnergySensorEntity,
    InWattsSensorEntity,
    LevelSensorEntity,
    MilliVoltSensorEntity,
    OutWattsSensorEntity,
    RemainSensorEntity,
    StateOfHealthSensorEntity,
    StoredEnergyFromSocSensorEntity,
    TempSensorEntity,
    VoltSensorEntity,
    WattsSensorEntity,
)

_LOGGER = logging.getLogger(__name__)


class StreamAC(BaseInternalDevice):
    # StreamAC backs every Stream-family model (registry.py maps STREAM_AC,
    # STREAM_PRO, STREAM_ULTRA and STREAM_ULTRA_X all to this one class), so
    # any sensor added here applies to all of them unless explicitly gated.
    # The per-PV field numbers below (see _ultra_x_pv_sensors()) were
    # raw-decoded against one physical Stream Ultra X and are NOT verified to
    # mean the same thing -- or to be populated at all -- on Stream AC/PRO,
    # which are different products with (at minimum) fewer PV inputs. Gating
    # by device_type so this can't surface a wrong value mislabelled as PV
    # power on those models.
    #
    # Both "STREAM_ULTRA" and "STREAM_ULTRA_X" are included: the private/MQTT
    # API used by this class reports the former for what the public API and
    # the EcoFlow app call "Ultra X" (confirmed: the "BK61" serial prefix on
    # the physical unit the field mapping was decoded from matches units
    # reporting "STREAM_ULTRA" here) -- the "_X" suffix appears to be a
    # public-API-only distinction, not a different private-API device_type.
    _ULTRA_X_DEVICE_TYPES = {"STREAM_ULTRA", "STREAM_ULTRA_X"}

    def _ultra_x_pv_sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        """Per-PV power/voltage/current for Stream Ultra / Ultra X only.

        The previous powGetPv/powGetPv2/powGetPv3/powGetPv4 keys were never
        wired to any field in this class's protobuf schema
        (StreamACChamp_cmd21_3) -- pure dead code, always reading a missing
        dict key -- which is why these sensors sat at 0 while powGetPvSum (a
        real field, 517) worked. Field numbers raw-decoded and cross-checked
        against the app's per-panel display and against powGetPvSum (the
        four powers sum to it): see stream_ac.proto and
        https://github.com/tolwi/hassio-ecoflow-cloud/pull/846#issuecomment-5046026257
        """
        if self.device_data.device_type not in self._ULTRA_X_DEVICE_TYPES:
            # Not verified on this model -- fall back to the old dead-but-
            # harmless wiring so entity ids/behaviour are unchanged for
            # Stream AC / PRO.
            return [
                WattsSensorEntity(client, self, "powGetPv", const.STREAM_POWER_PV_1, False, True),
                WattsSensorEntity(client, self, "powGetPv2", const.STREAM_POWER_PV_2, False, True),
                WattsSensorEntity(client, self, "powGetPv3", const.STREAM_POWER_PV_3, False, True),
                WattsSensorEntity(client, self, "powGetPv4", const.STREAM_POWER_PV_4, False, True),
            ]
        return [
            WattsSensorEntity(client, self, "powGetPv", const.STREAM_POWER_PV_1),
            WattsSensorEntity(client, self, "powGetPv2", const.STREAM_POWER_PV_2),
            WattsSensorEntity(client, self, "powGetPv3", const.STREAM_POWER_PV_3),
            WattsSensorEntity(client, self, "powGetPv4", const.STREAM_POWER_PV_4),
            VoltSensorEntity(client, self, "inVolPv1", const.STREAM_IN_VOL_PV_1, False),
            VoltSensorEntity(client, self, "inVolPv2", const.STREAM_IN_VOL_PV_2, False),
            VoltSensorEntity(client, self, "inVolPv3", const.STREAM_IN_VOL_PV_3, False),
            VoltSensorEntity(client, self, "inVolPv4", const.STREAM_IN_VOL_PV_4, False),
            AmpSensorEntity(client, self, "inAmpPv1", const.STREAM_IN_AMPS_PV_1, False),
            AmpSensorEntity(client, self, "inAmpPv2", const.STREAM_IN_AMPS_PV_2, False),
            AmpSensorEntity(client, self, "inAmpPv3", const.STREAM_IN_AMPS_PV_3, False),
            AmpSensorEntity(client, self, "inAmpPv4", const.STREAM_IN_AMPS_PV_4, False),
        ]

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
            # Discharge remaining time (minutes). Stream AC emits this as a
            # top-level value; Stream Ultra / Ultra X carry it inside the nested
            # Champ_cmd21_2 message (field 13), normalised onto this key by
            # _normalize_champ_fields(). One sensor works for every variant.
            RemainSensorEntity(client, self, "bmsDsgRemTime", const.DISCHARGE_REMAINING_TIME),
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
            # cmsBattFullEnergy / cmsBattSoc are not emitted on the private API
            # for Stream Ultra / Ultra X (confirmed absent from both the private
            # dump and the Public API quota). auto_enable keeps this hidden where
            # the source fields never arrive, while still surfacing on Stream
            # models that do report them.
            StoredEnergyFromSocSensorEntity(
                client, self, "cmsBattFullEnergy", "cmsBattSoc", const.STREAM_STORED_ENERGY, False, True
            ),
            # "cmsBattSoh": 100.0,
            # "cmsBmsRunState": 1,
            # "cmsChgDsgState": 2,
            # "cmsChgRemTime": 88,
            # "cmsDsgRemTime": 5939,
            # "cmsMaxChgSoc": 100,
            # Charge/discharge SoC limits. Stream AC emits these top-level;
            # Stream Ultra / Ultra X carry them inside the nested Champ_cmd21_2
            # message (field 7 / field 21), normalised onto these keys by
            # _normalize_champ_fields().
            BatteryLimitSensorEntity(client, self, "cmsMaxChgSoc", const.MAX_CHARGE_LEVEL),
            # "cmsMinDsgSoc": 5,
            BatteryLimitSensorEntity(client, self, "cmsMinDsgSoc", const.MIN_DISCHARGE_LEVEL),
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
            # Precise battery SoC (float). Stream AC emits this top-level; Stream
            # Ultra / Ultra X carry it inside the nested Champ_cmd21_2 message
            # (field 15), normalised onto this key by _normalize_champ_fields().
            LevelSensorEntity(client, self, "f32ShowSoc", const.STREAM_POWER_BATTERY_SOC),
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
            # "powConsumptionMeasurement": 2,
            # "powGetBpCms": 1915.0862,
            WattsSensorEntity(client, self, "powGetBpCms", const.STREAM_POWER_BATTERY),
            # Per-PV power/voltage/current -- see _ultra_x_pv_sensors().
            *self._ultra_x_pv_sensors(client),
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
            StateOfHealthSensorEntity(client, self, "realSoh", const.REAL_SOH, False),
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
            # Integer battery level. Stream AC emits this top-level; Stream
            # Ultra / Ultra X carry it inside the nested Champ_cmd21_2 message
            # (field 9), normalised onto this key by _normalize_champ_fields().
            LevelSensorEntity(client, self, "soc", const.STREAM_BATTERY_LEVEL)
            .attr("designCap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("fullCap", const.ATTR_FULL_CAPACITY, 0)
            .attr("remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            # "socketMeasurePower": 0.0,
            # "soh": 100,
            StateOfHealthSensorEntity(client, self, "soh", const.SOH, False),
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

    # moduleWifiRssi
    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return []

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return []

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return []

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
        self._normalize_champ_fields(raw["params"])
        return raw

    # Newer Stream firmware / models (e.g. Stream Ultra / Ultra X) do not emit
    # certain battery values as top-level parameters; they only appear inside
    # the correctly-typed nested Champ_cmd21_2 message, flattened by
    # _store_fields() into "Champ_cmd21_2_fieldN" leaves. Map those leaves back
    # onto their canonical parameter names so a single set of sensors works
    # across every Stream variant. Field meanings verified against a live Public
    # API read and the on-device display from raw pdata captures:
    #   field 9  -> soc          (integer battery level)
    #   field 15 -> f32ShowSoc   (precise SoC, == cmsBattSoc)
    #   field 13 -> bmsDsgRemTime (discharge remaining time, minutes)
    #   field 7  -> cmsMaxChgSoc (max charge SoC limit)
    #   field 21 -> cmsMinDsgSoc (min discharge SoC limit)
    # Any top-level value emitted by the device always takes precedence.
    _CHAMP_FIELD_ALIASES = {
        "soc": "Champ_cmd21_2_field9",
        "f32ShowSoc": "Champ_cmd21_2_field15",
        "bmsDsgRemTime": "Champ_cmd21_2_field13",
        "cmsMaxChgSoc": "Champ_cmd21_2_field7",
        "cmsMinDsgSoc": "Champ_cmd21_2_field21",
    }

    def _normalize_champ_fields(self, params: dict[str, Any]) -> None:
        for canonical, nested in self._CHAMP_FIELD_ALIASES.items():
            if nested in params and params.get(canonical) is None:
                params[canonical] = params[nested]

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

                self._store_fields(content, raw)

        except Exception as error:
            _LOGGER.debug(error)
            _LOGGER.debug("Erreur parsing pour le flux : %s", str(packet.msg.pdata.hex()))

    def _store_fields(self, content, raw, depth: int = 0) -> None:
        """Store a parsed protobuf message's fields into ``raw["params"]``.

        Scalar fields are stored under their own name (existing behaviour).
        Nested sub-messages are stored as-is (backwards compatible) AND their
        scalar leaves are flattened one level deeper so that values only
        available inside correctly-typed nested messages (e.g. the battery
        ``soc`` carried by ``Champ_cmd21_2_field9``) become readable by
        sensors. Bounded recursion depth guards against pathological nesting.
        """
        for descriptor in content.DESCRIPTOR.fields:
            if not content.HasField(descriptor.name):
                continue

            value = getattr(content, descriptor.name)

            if descriptor.type == descriptor.TYPE_MESSAGE:
                raw["params"][descriptor.name] = value
                if depth < 3:
                    self._store_fields(value, raw, depth + 1)
            else:
                raw["params"][descriptor.name] = value
