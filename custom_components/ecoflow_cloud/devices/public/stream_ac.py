from typing import cast
from custom_components.ecoflow_cloud.device_data import DeviceData
from custom_components.ecoflow_cloud.devices import EcoflowDeviceInfo
from datetime import timezone
from custom_components.ecoflow_cloud.api.public_api import EcoflowPublicApiClient
from datetime import datetime
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from typing import Any, NamedTuple
import asyncio

import jsonpath_ng.ext as jp

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.components.switch import SwitchEntity

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import BaseDevice, const
from custom_components.ecoflow_cloud.devices.public.data_bridge import to_plain
from custom_components.ecoflow_cloud.entities import BaseSensorEntity
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
    StatusSensorEntity,
    TempSensorEntity,
    VoltSensorEntity,
    WattsSensorEntity,
)
from homeassistant.util import dt
from custom_components.ecoflow_cloud.switch import EnabledEntity

import logging

_LOGGER = logging.getLogger(__name__)

# Historical metric codes
HIST_CODE_ENERGY_INDEPENDENCE = "BK621-App-HOME-INDEPENDENCE-PERCENT-FLOW-indep-progress_bar-NOTDISTINGUISH-MASTER_DATA"
HIST_CODE_ENV_IMPACT = "BK621-App-HOME-CO2-WEIGHT-FLOW-impact-progress_arc-NOTDISTINGUISH-MASTER_DATA"
HIST_CODE_SAVINGS_TOTAL = "BK621-App-HOME-SAVING-CURRENCY-FLOW-earnings-progress_arc-NOTDISTINGUISH-MASTER_DATA"
HIST_CODE_SOLAR_GENERATED = "BK621-App-HOME-SOLAR-ENERGY-FLOW-solor-line-NOTDISTINGUISH-MASTER_DATA"
HIST_CODE_ELECTRICITY_CONS = "BK621-App-HOME-LOAD-ENERGY-FLOW-consumption-prop_arc-NOTDISTINGUISH-MASTER_DATA"
HIST_CODE_GRID = "BK621-App-HOME-GRID-ENERGY-FLOW-grid_prop_bar-NOTDISTINGUISH-MASTER_DATA"
HIST_CODE_BATTERY = "BK621-App-HOME-SOC-ENERGY-FLOW-battery-prop_bar-NOTDISTINGUISH-MASTER_DATA"


# Historical data refresh period (seconds)
DEFAULT_STREAM_AC_HISTORY_PERIOD_SEC = 900  # 15 minutes

# Magic date for EcoFlow business start (used for cumulative queries)
ECOFLOW_BUSINESS_START = datetime(2017, 5, 1, 0, 0, 0, tzinfo=timezone.utc)


class MetrConfig(NamedTuple):
    code: str
    key: str
    mode: str


METRICS_CONFIG = [
    MetrConfig(HIST_CODE_ENERGY_INDEPENDENCE, "energyIndependenceToday", "today"),
    MetrConfig(HIST_CODE_ENERGY_INDEPENDENCE, "energyIndependenceYear", "year"),
    MetrConfig(HIST_CODE_ENV_IMPACT, "environmentalImpactToday", "today"),
    MetrConfig(HIST_CODE_ENV_IMPACT, "environmentalImpactCumulative", "cumulative"),
    MetrConfig(HIST_CODE_SAVINGS_TOTAL, "solarEnergySavingsToday", "today"),
    MetrConfig(HIST_CODE_SAVINGS_TOTAL, "solarEnergySavingsCumulative", "cumulative"),
    MetrConfig(HIST_CODE_SOLAR_GENERATED, "solarGeneratedToday", "today"),
    MetrConfig(HIST_CODE_SOLAR_GENERATED, "solarGeneratedCumulative", "cumulative"),
    MetrConfig(HIST_CODE_ELECTRICITY_CONS, "electricityConsumptionToday", "today"),
    MetrConfig(HIST_CODE_ELECTRICITY_CONS, "electricityConsumptionCumulative", "cumulative"),
    MetrConfig(HIST_CODE_GRID, "gridToday", "today"),
    MetrConfig(HIST_CODE_GRID, "gridCumulative", "cumulative"),
    MetrConfig(HIST_CODE_BATTERY, "batteryToday", "today"),
    MetrConfig(HIST_CODE_BATTERY, "batteryCumulative", "cumulative"),
]


class StreamACHistoryUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to fetch historical data for StreamAC devices."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: EcoflowPublicApiClient,
        device: BaseDevice,
        update_interval_seconds: int = DEFAULT_STREAM_AC_HISTORY_PERIOD_SEC,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"StreamAC History ({device.device_info.sn})",
            update_interval=timedelta(seconds=update_interval_seconds),
        )
        self._client = client
        self._device = device
        self.last_check: datetime | None = None

    def _get_time_ranges(self) -> dict[str, tuple[str, str]]:
        now = dt.utcnow()
        fmt = "%Y-%m-%d %H:%M:%S"

        begin_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_day = now.replace(hour=23, minute=59, second=59, microsecond=0)

        begin_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_year = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=0)

        begin_all = ECOFLOW_BUSINESS_START

        return {
            "today": (begin_day.strftime(fmt), end_day.strftime(fmt)),
            "year": (begin_year.strftime(fmt), end_year.strftime(fmt)),
            "cumulative": (begin_all.strftime(fmt), end_day.strftime(fmt)),
        }

    def _process_items(self, items: list[dict]) -> dict[str, Any]:
        result: dict[str, Any] = {}

        for it in items:
            val = float(it.get("indexValue", 0))
            extra = str(it.get("extra", ""))

            # Determine target key
            target_key = f"value_{extra}" if extra else "value"
            if target_key not in result:
                result[target_key] = 0.0

            # Aggregate
            result[target_key] += val

            # Extract unit from "first valid item" logic
            if "unit" not in result and (u := it.get("unit")):
                result["unit"] = u

        return result

    async def _call_historical_api(self, begin: str, end: str, code: str) -> dict:
        params: dict[str, Any] = {
            "sn": self._device.device_info.sn,
            "params": {
                "beginTime": begin,
                "endTime": end,
                "code": code,
            },
        }
        try:
            return await self._client.call_api("POST", "/device/quota/data", params)
        except Exception:
            # Return empty dict on error so we can proceed with other requests
            # The caller handles logging/retry if needed (though existing code just ignored errors)
            _LOGGER.debug(f"Failed to fetch historical data for code {code}", exc_info=True)
            return {}

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch historical data from the API."""
        self.last_check = dt.utcnow()
        # now = dt.utcnow()
        time_ranges = self._get_time_ranges()

        history: dict[str, Any] = {}
        last_check_iso = self.last_check.isoformat()

        # params["history.mainSn"] = self._device.device_info.sn
        history["last_history_check"] = last_check_iso

        _LOGGER.debug(
            "StreamACHistoryUpdateCoordinator: fetching historical data for sn=%s",
            self._device.device_info.sn,
        )

        # Prepare all API calls
        tasks = []
        for config in METRICS_CONFIG:
            begin, end = time_ranges[config.mode]
            tasks.append(self._call_historical_api(begin, end, config.code))

        # Execute all calls in parallel
        results = await asyncio.gather(*tasks)

        # Process results
        for config, resp in zip(METRICS_CONFIG, results):
            begin, end = time_ranges[config.mode]
            items = resp.get("data", {}).get("data", [])

            if items:
                processed = self._process_items(items)

                # Ensure the key exists in history
                if config.key not in history:
                    history[config.key] = {}

                metric_data = history[config.key]
                metric_data["beginTime"] = begin
                metric_data["endTime"] = end

                for internal_key, val in processed.items():
                    if internal_key == "unit":
                        # Store unit at the metric level or specific key if needed
                        # For now, we can store it in the metric dict
                        metric_data["unit"] = val
                        continue

                    metric_data[internal_key] = val

        try:
            self._device.data.params.update({"history": history})
        except Exception as exc:
            _LOGGER.error(
                "Failed to update device params for sn=%s: %s", self._device.device_info.sn, exc, exc_info=True
            )

        return history


class StreamACMonetarySensorEntity(BaseSensorEntity):
    def __init__(self, client: EcoflowApiClient, device: BaseDevice, mqtt_key: str, title: str, unit_key: str):
        super().__init__(client, device, mqtt_key, title)
        self._unit_key = unit_key
        self._unit_key_expr = jp.parse(unit_key)

    def _updated(self, data: dict[str, Any]):
        units = self._unit_key_expr.find(data)
        if len(units) == 1:
            self._attr_native_unit_of_measurement = units[0].value

        super()._updated(data)


class StreamAC(BaseDevice):
    def __init__(self, device_info: EcoflowDeviceInfo, device_data: DeviceData):
        super().__init__(device_info, device_data)
        self.history_coordinator: StreamACHistoryUpdateCoordinator | None = None

    def configure(self, hass: HomeAssistant, client: EcoflowApiClient):
        super().configure(hass, client)
        self.history_coordinator = StreamACHistoryUpdateCoordinator(hass, cast(EcoflowPublicApiClient, client), self)

    def flat_json(self) -> bool:
        return False

    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            # "accuChgCap": 198511,
            CumulativeCapacitySensorEntity(client, self, "accuChgCap", const.ACCU_CHARGE_CAP, False),
            # "accuChgEnergy": 3992,
            EnergySensorEntity(client, self, "accuChgEnergy", const.ACCU_CHARGE_ENERGY),
            # "accuDsgCap": 184094,
            CumulativeCapacitySensorEntity(client, self, "accuDsgCap", const.ACCU_DISCHARGE_CAP, False),
            # "accuDsgEnergy": 3646,
            EnergySensorEntity(client, self, "accuDsgEnergy", const.ACCU_DISCHARGE_ENERGY),
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
            LevelSensorEntity(client, self, "cmsMaxChgSoc", const.MAX_CHARGE_LEVEL),
            LevelSensorEntity(client, self, "cmsMinDsgSoc", const.MIN_DISCHARGE_LEVEL),
            # "curSensorNtcNum": 0,
            # "curSensorTemp": [],
            # "cycleSoh": 100.0,
            # "cycles": 1,
            CyclesSensorEntity(client, self, "cycles", const.CYCLES),
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
            VoltSensorEntity(client, self, "gridConnectionVol", const.STREAM_POWER_VOL, False),
            # "gridSysDeviceCnt": 2,
            # "heatfilmNtcNum": 0,
            # "heatfilmTemp": [],
            # "hwVer": "V0.0.0",
            # "inputWatts": 900,
            InWattsSensorEntity(client, self, "inputWatts", const.STREAM_IN_POWER),
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
            OutWattsSensorEntity(client, self, "outputWatts", const.STREAM_OUT_POWER),
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
            WattsSensorEntity(client, self, "powGetSysLoadFromGrid", const.STREAM_GET_SYS_LOAD_FROM_GRID),
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
            RemainSensorEntity(client, self, "remainTime", const.REMAINING_TIME),
            # "runtimePropertyFullUploadPeriod": 120000,
            # "runtimePropertyIncrementalUploadPeriod": 2000,
            # "seriesConnectDeviceId": 1,
            # "seriesConnectDeviceStatus": "MASTER",
            # "soc": 46,
            LevelSensorEntity(client, self, "soc", const.STREAM_POWER_BATTERY)
            .attr("designCap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("fullCap", const.ATTR_FULL_CAPACITY, 0)
            .attr("remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            # "socketMeasurePower": 0.0,
            # "soh": 100,
            LevelSensorEntity(client, self, "soh", const.SOH),
            # "stormPatternEnable": false,
            # "stormPatternEndTime": 0,
            # "stormPatternOpenFlag": false,
            # "sysGridConnectionPower": -2020.0437,
            WattsSensorEntity(client, self, "sysGridConnectionPower", const.STREAM_POWER_AC_SYS),
            # "sysLoaderVer": 4294967295,
            # "sysState": 3,
            # "sysVer": 33620026,
            # "systemGroupId": 12356789,
            # "systemMeshId": 1,
            # "tagChgAmp": 50000,
            # "targetSoc": 46.314102,
            # "temp": 35,
            TempSensorEntity(client, self, "temp", const.BATTERY_TEMP)
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
        ] + self._history_sensors(client)

    # moduleWifiRssi
    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return [
            BatteryBackupLevel(
                client,
                self,
                "backupReverseSoc",
                const.BACKUP_RESERVE_LEVEL,
                3,
                95,
                "cmsMinDsgSoc",
                "cmsMaxChgSoc",
                3,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdId": 17,
                    "cmdFunc": 254,
                    "dirDest": 1,
                    "dirSrc": 1,
                    "dest": 2,
                    "needAck": True,
                    "params": {
                        "cfgBackupReverseSoc": int(value),
                    },
                },
            ),
        ]

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return [
            EnabledEntity(
                client,
                self,
                "relay2Onoff",
                const.MODE_AC1_ON,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdId": 17,
                    "cmdFunc": 254,
                    "dirDest": 1,
                    "dirSrc": 1,
                    "dest": 2,
                    "needAck": True,
                    "params": {"cfgRelay2Onoff": value},
                },
                enableValue=True,
                disableValue=False,
            ),
            EnabledEntity(
                client,
                self,
                "relay3Onoff",
                const.MODE_AC2_ON,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdId": 17,
                    "cmdFunc": 254,
                    "dirDest": 1,
                    "dirSrc": 1,
                    "dest": 2,
                    "needAck": True,
                    "params": {"cfgRelay3Onoff": value},
                },
                enableValue=True,
                disableValue=False,
            ),
            EnabledEntity(
                client,
                self,
                "energyStrategyOperateMode.operateSelfPoweredOpen",
                const.STREAM_OPERATION_MODE_SELF_POWERED,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdId": 17,
                    "cmdFunc": 254,
                    "dirDest": 1,
                    "dirSrc": 1,
                    "dest": 2,
                    "needAck": True,
                    "params": {"cfgEnergyStrategyOperateMode": {"operateSelfPoweredOpen": value}},
                },
                enableValue=True,
                disableValue=False,
            ),
            EnabledEntity(
                client,
                self,
                "energyStrategyOperateMode.operateIntelligentScheduleModeOpen",
                const.STREAM_OPERATION_MODE_AI_MODE,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdId": 17,
                    "cmdFunc": 254,
                    "dirDest": 1,
                    "dirSrc": 1,
                    "dest": 2,
                    "needAck": True,
                    "params": {"cfgEnergyStrategyOperateMode": {"operateIntelligentScheduleModeOpen": value}},
                },
                enableValue=True,
                disableValue=False,
            ),
            EnabledEntity(
                client,
                self,
                "feedGridMode",
                const.STREAM_FEED_IN_CONTROL,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdId": 17,
                    "cmdFunc": 254,
                    "dirDest": 1,
                    "dirSrc": 1,
                    "dest": 2,
                    "needAck": True,
                    "params": {"cfgFeedGridMode": value},
                },
                enableValue=2,
                disableValue=1,
            ),
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return []

    def _prepare_data(self, raw_data) -> dict[str, Any]:
        res = super()._prepare_data(raw_data)
        res = to_plain(res)
        return res

    def _status_sensor(self, client: EcoflowApiClient) -> StatusSensorEntity:
        return StatusSensorEntity(client, self)

    def _history_sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            # Energy Independence (Today)
            EnergySensorEntity(
                client, self, "history.energyIndependenceToday.value", const.STREAM_HISTORY_ENERGY_INDEPENDENCE_TODAY
            )
            .with_unit_of_measurement("%")
            .with_icon("mdi:percent")
            .with_state_class(SensorStateClass.MEASUREMENT)
            .attr("history.energyIndependenceToday.beginTime", "Begin Time", "")
            .attr("history.energyIndependenceToday.endTime", "End Time", "")
            .attr("history.last_history_check", "Last Checked", ""),
            # Energy Independence (Year)
            EnergySensorEntity(
                client, self, "history.energyIndependenceYear.value", const.STREAM_HISTORY_ENERGY_INDEPENDENCE_YEAR
            )
            .with_unit_of_measurement("%")
            .with_icon("mdi:percent")
            .with_state_class(SensorStateClass.MEASUREMENT)
            .attr("history.energyIndependenceYear.beginTime", "Begin Time", "")
            .attr("history.energyIndependenceYear.endTime", "End Time", "")
            .attr("history.last_history_check", "Last Checked", ""),
            # Environmental Impact (Today)
            EnergySensorEntity(
                client, self, "history.environmentalImpactToday.value", const.STREAM_HISTORY_ENVIRONMENTAL_IMPACT_TODAY
            )
            .with_unit_of_measurement("kg")
            .with_icon("mdi:leaf")
            .with_state_class(SensorStateClass.TOTAL)
            .attr("history.environmentalImpactToday.beginTime", "Begin Time", "")
            .attr("history.environmentalImpactToday.endTime", "End Time", "")
            .attr("history.last_history_check", "Last Checked", ""),
            # Environmental Impact (Cumulative)
            EnergySensorEntity(
                client,
                self,
                "history.environmentalImpactCumulative.value",
                const.STREAM_HISTORY_ENVIRONMENTAL_IMPACT_CUMULATIVE,
            )
            .with_unit_of_measurement("kg")
            .with_icon("mdi:leaf")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.environmentalImpactCumulative.beginTime", "Begin Time", "")
            .attr("history.environmentalImpactCumulative.endTime", "End Time", "")
            .attr("history.last_history_check", "Last Checked", ""),
            # Solar Energy Savings (Today)
            StreamACMonetarySensorEntity(
                client,
                self,
                "history.solarEnergySavingsToday.value",
                const.STREAM_HISTORY_TOTAL_SOLAR_SAVINGS_TODAY,
                "history.solarEnergySavingsToday.unit",
            )
            .with_icon("mdi:cash")
            .with_state_class(SensorStateClass.TOTAL)
            .attr("history.solarEnergySavingsToday.beginTime", "Begin Time", "")
            .attr("history.solarEnergySavingsToday.endTime", "End Time", "")
            .attr("history.last_history_check", "Last Checked", ""),
            # Solar Energy Savings (Cumulative)
            StreamACMonetarySensorEntity(
                client,
                self,
                "history.solarEnergySavingsCumulative.value",
                const.STREAM_HISTORY_TOTAL_SOLAR_SAVINGS_CUMULATIVE,
                "history.solarEnergySavingsCumulative.unit",
            )
            .with_icon("mdi:cash")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.solarEnergySavingsCumulative.beginTime", "Begin Time", "")
            .attr("history.solarEnergySavingsCumulative.endTime", "End Time", "")
            .attr("history.last_history_check", "Last Checked", ""),
            # Solar Generated (Today)
            EnergySensorEntity(
                client, self, "history.solarGeneratedToday.value", const.STREAM_HISTORY_SOLAR_GENERATED_TODAY
            )
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:solar-power")
            .with_state_class(SensorStateClass.TOTAL)
            .attr("history.solarGeneratedToday.beginTime", "Begin Time", "")
            .attr("history.solarGeneratedToday.endTime", "End Time", "")
            .attr("history.last_history_check", "Last Checked", ""),
            # Solar Generated (Cumulative)
            EnergySensorEntity(
                client, self, "history.solarGeneratedCumulative.value", const.STREAM_HISTORY_SOLAR_GENERATED_CUMULATIVE
            )
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:solar-power")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.solarGeneratedCumulative.beginTime", "Begin Time", "")
            .attr("history.solarGeneratedCumulative.endTime", "End Time", "")
            .attr("history.last_history_check", "Last Checked", ""),
            # Electricity Consumption (Today)
            EnergySensorEntity(
                client,
                self,
                "history.electricityConsumptionToday.value",
                const.STREAM_HISTORY_ELECTRICITY_CONSUMPTION_TODAY,
            )
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:lightning-bolt")
            .with_state_class(SensorStateClass.TOTAL)
            .attr("history.electricityConsumptionToday.beginTime", "Begin Time", "")
            .attr("history.electricityConsumptionToday.endTime", "End Time", "")
            .attr("history.last_history_check", "Last Checked", ""),
            # Electricity Consumption (Cumulative)
            EnergySensorEntity(
                client,
                self,
                "history.electricityConsumptionCumulative.value",
                const.STREAM_HISTORY_ELECTRICITY_CONSUMPTION_CUMULATIVE,
            )
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:lightning-bolt")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.electricityConsumptionCumulative.beginTime", "Begin Time", "")
            .attr("history.electricityConsumptionCumulative.endTime", "End Time", "")
            .attr("history.last_history_check", "Last Checked", ""),
            # Grid Import (Today) (extra='1' -> value_1)
            EnergySensorEntity(client, self, "history.gridToday.value_1", const.STREAM_HISTORY_GRID_IMPORT_TODAY)
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:transmission-tower-import")
            .with_state_class(SensorStateClass.TOTAL)
            .attr("history.gridToday.beginTime", "Begin Time", "")
            .attr("history.gridToday.endTime", "End Time", "")
            .attr("history.last_history_check", "Last Checked", ""),
            # Grid Import (Cumulative)
            EnergySensorEntity(
                client, self, "history.gridCumulative.value_1", const.STREAM_HISTORY_GRID_IMPORT_CUMULATIVE
            )
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:transmission-tower-import")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.gridCumulative.beginTime", "Begin Time", "")
            .attr("history.gridCumulative.endTime", "End Time", "")
            .attr("history.last_history_check", "Last Checked", ""),
            # Grid Export (Today) (extra='2' -> value_2)
            EnergySensorEntity(client, self, "history.gridToday.value_2", const.STREAM_HISTORY_GRID_EXPORT_TODAY)
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:transmission-tower-export")
            .with_state_class(SensorStateClass.TOTAL)
            .attr("history.gridToday.beginTime", "Begin Time", "")
            .attr("history.gridToday.endTime", "End Time", "")
            .attr("history.last_history_check", "Last Checked", ""),
            # Grid Export (Cumulative)
            EnergySensorEntity(
                client, self, "history.gridCumulative.value_2", const.STREAM_HISTORY_GRID_EXPORT_CUMULATIVE
            )
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:transmission-tower-export")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.gridCumulative.beginTime", "Begin Time", "")
            .attr("history.gridCumulative.endTime", "End Time", "")
            .attr("history.last_history_check", "Last Checked", ""),
            # Battery Charge (Today) (extra='1' -> value_1)
            EnergySensorEntity(client, self, "history.batteryToday.value_1", const.STREAM_HISTORY_BATTERY_CHARGE_TODAY)
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:battery-arrow-up")
            .with_state_class(SensorStateClass.TOTAL)
            .attr("history.batteryToday.beginTime", "Begin Time", "")
            .attr("history.batteryToday.endTime", "End Time", "")
            .attr("history.last_history_check", "Last Checked", ""),
            # Battery Charge (Cumulative)
            EnergySensorEntity(
                client, self, "history.batteryCumulative.value_1", const.STREAM_HISTORY_BATTERY_CHARGE_CUMULATIVE
            )
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:battery-arrow-up")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.batteryCumulative.beginTime", "Begin Time", "")
            .attr("history.batteryCumulative.endTime", "End Time", "")
            .attr("history.last_history_check", "Last Checked", ""),
            # Battery Discharge (Today) (extra='2' -> value_2)
            EnergySensorEntity(
                client, self, "history.batteryToday.value_2", const.STREAM_HISTORY_BATTERY_DISCHARGE_TODAY
            )
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:battery-arrow-down")
            .with_state_class(SensorStateClass.TOTAL)
            .attr("history.batteryToday.beginTime", "Begin Time", "")
            .attr("history.batteryToday.endTime", "End Time", "")
            .attr("history.last_history_check", "Last Checked", ""),
            # Battery Discharge (Cumulative)
            EnergySensorEntity(
                client, self, "history.batteryCumulative.value_2", const.STREAM_HISTORY_BATTERY_DISCHARGE_CUMULATIVE
            )
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:battery-arrow-down")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.batteryCumulative.beginTime", "Begin Time", "")
            .attr("history.batteryCumulative.endTime", "End Time", "")
            .attr("history.last_history_check", "Last Checked", ""),
        ]
