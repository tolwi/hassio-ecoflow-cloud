import asyncio
import logging
from datetime import datetime, timedelta, timezone as _timezone
from typing import Any, Final

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import BaseDevice, const
from custom_components.ecoflow_cloud.devices.public.data_bridge import to_plain
from custom_components.ecoflow_cloud.entities import BaseSensorEntity
from custom_components.ecoflow_cloud.number import BatteryBackupLevel
from custom_components.ecoflow_cloud.sensor import (
    AmpSensorEntity,
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
from custom_components.ecoflow_cloud.devices.public.stream_pv_helpers import (
    StreamPvWattsSensorEntity,
)
from custom_components.ecoflow_cloud.switch import EnabledEntity

# Historical metric codes used by the EcoFlow /device/quota/data API
HIST_CODE_ENERGY_INDEPENDENCE = "BK621-App-HOME-INDEPENDENCE-PERCENT-FLOW-indep-progress_bar-NOTDISTINGUISH-MASTER_DATA"
HIST_CODE_ENV_IMPACT = "BK621-App-HOME-CO2-WEIGHT-FLOW-impact-progress_arc-NOTDISTINGUISH-MASTER_DATA"
HIST_CODE_SAVINGS_TOTAL = "BK621-App-HOME-SAVING-CURRENCY-FLOW-earnings-progress_arc-NOTDISTINGUISH-MASTER_DATA"
HIST_CODE_SOLAR_GENERATED = "BK621-App-HOME-SOLAR-ENERGY-FLOW-solor-line-NOTDISTINGUISH-MASTER_DATA"
HIST_CODE_ELECTRICITY_CONS = "BK621-App-HOME-LOAD-ENERGY-FLOW-consumption-prop_arc-NOTDISTINGUISH-MASTER_DATA"
HIST_CODE_GRID = "BK621-App-HOME-GRID-ENERGY-FLOW-grid_prop_bar-NOTDISTINGUISH-MASTER_DATA"
HIST_CODE_BATTERY = "BK621-App-HOME-SOC-ENERGY-FLOW-battery-prop_bar-NOTDISTINGUISH-MASTER_DATA"

# Historical data refresh period (seconds) — 15 minutes
DEFAULT_STREAM_AC_HISTORY_PERIOD_SEC = 900

# Magic date for EcoFlow business start (used for cumulative queries)
ECOFLOW_BUSINESS_START = datetime(2017, 5, 1, 0, 0, 0, tzinfo=_timezone.utc)

HISTORY_METRIC_BASE_KEYS: Final[tuple[str, ...]] = (
    "history.energyIndependenceToday",
    "history.energyIndependenceYear",
    "history.environmentalImpactToday",
    "history.environmentalImpactCumulative",
    "history.solarEnergySavingsToday",
    "history.solarEnergySavingsCumulative",
    "history.solarGeneratedToday",
    "history.solarGeneratedCumulative",
    "history.electricityConsumptionToday",
    "history.electricityConsumptionCumulative",
    "history.gridImport",
    "history.gridExport",
    "history.gridImportCumulative",
    "history.gridExportCumulative",
    "history.batteryCharge",
    "history.batteryDischarge",
    "history.batteryChargeCumulative",
    "history.batteryDischargeCumulative",
)

_LOGGER = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(_timezone.utc)


class StreamACHistoryUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to fetch historical data for StreamAC devices via the HTTP API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: EcoflowApiClient,
        device: "StreamAC",
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

    async def _async_update_data(self) -> dict[str, Any]:
        self.last_check = _utcnow()
        return await self._fetch_historical_data()

    async def _fetch_historical_data(self) -> dict[str, Any]:
        now = _utcnow()
        begin_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_day = now.replace(hour=23, minute=59, second=59, microsecond=0)
        fmt = "%Y-%m-%d %H:%M:%S"
        sn = self._device.device_info.sn

        params: dict[str, Any] = {}
        last_check_iso = (self.last_check or now).isoformat()
        params["history.mainSn"] = sn
        params["history.last_history_check"] = last_check_iso
        for base_key in HISTORY_METRIC_BASE_KEYS:
            params[f"{base_key}.last_history_check"] = last_check_iso

        _LOGGER.debug("StreamACHistoryUpdateCoordinator: fetching historical data for sn=%s", sn)

        def _sum_grid(items: list[dict]) -> tuple[float, float]:
            imp = exp = 0.0
            for it in items:
                try:
                    val = float(it.get("indexValue", 0))
                except Exception:
                    val = 0.0
                extra = str(it.get("extra", ""))
                if extra == "1":
                    imp += val
                elif extra == "2":
                    exp += val
            return imp, exp

        def _first_value_and_unit(items: list[dict]) -> tuple[float, str | None]:
            if not items:
                return 0.0, None
            it0 = items[0]
            try:
                val = float(it0.get("indexValue", 0))
            except Exception:
                val = 0.0
            u = it0.get("unit")
            unit = u if isinstance(u, str) and u else None
            return val, unit

        def _first_value(items: list[dict]) -> float:
            val, _ = _first_value_and_unit(items)
            return val

        def _sum_values(items: list[dict]) -> float:
            total = 0.0
            for it in items:
                try:
                    total += float(it.get("indexValue", 0))
                except Exception as exc:
                    _LOGGER.debug("Failed to convert indexValue to float: %s", exc)
            return total

        def _sum_battery(items: list[dict]) -> tuple[float, float]:
            chg = dsg = 0.0
            for it in items:
                try:
                    val = float(it.get("indexValue", 0))
                except Exception as exc:
                    _LOGGER.debug("Failed to convert indexValue to float: %s", exc)
                    val = 0.0
                extra = str(it.get("extra", ""))
                if extra == "1":
                    chg += val
                elif extra == "2":
                    dsg += val
            return chg, dsg

        async def _call_api(begin: str, end: str, code: str) -> dict:
            historical_data = getattr(self._client, "historical_data", None)
            if callable(historical_data):
                return await historical_data(sn, begin, end, code)
            post_api = getattr(self._client, "post_api", None)
            if callable(post_api):
                return await post_api(
                    "/device/quota/data",
                    {"sn": sn, "params": {"beginTime": begin, "endTime": end, "code": code}},
                )
            raise AttributeError("EcoFlow client does not support historical data")

        # Energy Independence — today and year-to-date
        try:
            resp = await _call_api(begin_day.strftime(fmt), end_day.strftime(fmt), HIST_CODE_ENERGY_INDEPENDENCE)
            items = resp.get("data", {}).get("data", [])
            if items:
                params["history.energyIndependenceToday"] = _first_value(items)
                params["history.energyIndependenceToday.beginTime"] = begin_day.strftime(fmt)
                params["history.energyIndependenceToday.endTime"] = end_day.strftime(fmt)
        except Exception:
            _LOGGER.debug("Failed to fetch energy independence (today)", exc_info=True)

        try:
            begin_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_year = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=0)
            resp = await _call_api(begin_year.strftime(fmt), end_year.strftime(fmt), HIST_CODE_ENERGY_INDEPENDENCE)
            items = resp.get("data", {}).get("data", [])
            if items:
                params["history.energyIndependenceYear"] = _first_value(items)
                params["history.energyIndependenceYear.beginTime"] = begin_year.strftime(fmt)
                params["history.energyIndependenceYear.endTime"] = end_year.strftime(fmt)
        except Exception:
            _LOGGER.debug("Failed to fetch energy independence (year)", exc_info=True)

        # Environmental Impact — today and cumulative
        try:
            resp = await _call_api(begin_day.strftime(fmt), end_day.strftime(fmt), HIST_CODE_ENV_IMPACT)
            items = resp.get("data", {}).get("data", [])
            if items:
                params["history.environmentalImpactToday"] = _first_value(items)
                params["history.environmentalImpactToday.beginTime"] = begin_day.strftime(fmt)
                params["history.environmentalImpactToday.endTime"] = end_day.strftime(fmt)
        except Exception:
            _LOGGER.debug("Failed to fetch environmental impact (today)", exc_info=True)

        try:
            begin_all = ECOFLOW_BUSINESS_START
            resp = await _call_api(begin_all.strftime(fmt), end_day.strftime(fmt), HIST_CODE_ENV_IMPACT)
            items = resp.get("data", {}).get("data", [])
            if items:
                params["history.environmentalImpactCumulative"] = _sum_values(items)
                params["history.environmentalImpactCumulative.beginTime"] = begin_all.strftime(fmt)
                params["history.environmentalImpactCumulative.endTime"] = end_day.strftime(fmt)
        except Exception:
            _LOGGER.debug("Failed to fetch environmental impact (cumulative)", exc_info=True)

        # Solar Energy Savings — today and cumulative
        try:
            resp = await _call_api(begin_day.strftime(fmt), end_day.strftime(fmt), HIST_CODE_SAVINGS_TOTAL)
            items = resp.get("data", {}).get("data", [])
            if items:
                val, unit = _first_value_and_unit(items)
                params["history.solarEnergySavingsToday"] = val
                params["history.solarEnergySavingsToday.beginTime"] = begin_day.strftime(fmt)
                params["history.solarEnergySavingsToday.endTime"] = end_day.strftime(fmt)
                if unit:
                    params["history.solarEnergySavingsUnit"] = unit
        except Exception:
            _LOGGER.debug("Failed to fetch solar energy savings (today)", exc_info=True)

        try:
            begin_all = ECOFLOW_BUSINESS_START
            resp = await _call_api(begin_all.strftime(fmt), end_day.strftime(fmt), HIST_CODE_SAVINGS_TOTAL)
            items = resp.get("data", {}).get("data", [])
            if items:
                unit = next((it.get("unit") for it in items if isinstance(it.get("unit"), str) and it.get("unit")), None)
                params["history.solarEnergySavingsCumulative"] = _sum_values(items)
                params["history.solarEnergySavingsCumulative.beginTime"] = begin_all.strftime(fmt)
                params["history.solarEnergySavingsCumulative.endTime"] = end_day.strftime(fmt)
                if unit:
                    params["history.solarEnergySavingsUnit"] = unit
        except Exception:
            _LOGGER.debug("Failed to fetch solar energy savings (cumulative)", exc_info=True)

        # Solar Generated — today and cumulative
        try:
            resp = await _call_api(begin_day.strftime(fmt), end_day.strftime(fmt), HIST_CODE_SOLAR_GENERATED)
            items = resp.get("data", {}).get("data", [])
            if items:
                params["history.solarGeneratedToday"] = _first_value(items)
                params["history.solarGeneratedToday.beginTime"] = begin_day.strftime(fmt)
                params["history.solarGeneratedToday.endTime"] = end_day.strftime(fmt)
        except Exception:
            _LOGGER.debug("Failed to fetch solar generated (today)", exc_info=True)

        try:
            begin_all = ECOFLOW_BUSINESS_START
            resp = await _call_api(begin_all.strftime(fmt), end_day.strftime(fmt), HIST_CODE_SOLAR_GENERATED)
            items = resp.get("data", {}).get("data", [])
            if items:
                params["history.solarGeneratedCumulative"] = _sum_values(items)
                params["history.solarGeneratedCumulative.beginTime"] = begin_all.strftime(fmt)
                params["history.solarGeneratedCumulative.endTime"] = end_day.strftime(fmt)
        except Exception:
            _LOGGER.debug("Failed to fetch solar generated (cumulative)", exc_info=True)

        # Electricity Consumption — today and cumulative
        try:
            resp = await _call_api(begin_day.strftime(fmt), end_day.strftime(fmt), HIST_CODE_ELECTRICITY_CONS)
            items = resp.get("data", {}).get("data", [])
            if items:
                params["history.electricityConsumptionToday"] = _first_value(items)
                params["history.electricityConsumptionToday.beginTime"] = begin_day.strftime(fmt)
                params["history.electricityConsumptionToday.endTime"] = end_day.strftime(fmt)
        except Exception:
            _LOGGER.debug("Failed to fetch electricity consumption (today)", exc_info=True)

        try:
            begin_all = ECOFLOW_BUSINESS_START
            resp = await _call_api(begin_all.strftime(fmt), end_day.strftime(fmt), HIST_CODE_ELECTRICITY_CONS)
            items = resp.get("data", {}).get("data", [])
            if items:
                params["history.electricityConsumptionCumulative"] = _sum_values(items)
                params["history.electricityConsumptionCumulative.beginTime"] = begin_all.strftime(fmt)
                params["history.electricityConsumptionCumulative.endTime"] = end_day.strftime(fmt)
        except Exception:
            _LOGGER.debug("Failed to fetch electricity consumption (cumulative)", exc_info=True)

        # Grid Import / Export — today and cumulative
        try:
            resp = await _call_api(begin_day.strftime(fmt), end_day.strftime(fmt), HIST_CODE_GRID)
            items = resp.get("data", {}).get("data", [])
            if items:
                imp, exp = _sum_grid(items)
                params["history.gridImport"] = imp
                params["history.gridImport.beginTime"] = begin_day.strftime(fmt)
                params["history.gridImport.endTime"] = end_day.strftime(fmt)
                params["history.gridExport"] = exp
                params["history.gridExport.beginTime"] = begin_day.strftime(fmt)
                params["history.gridExport.endTime"] = end_day.strftime(fmt)
        except Exception:
            _LOGGER.debug("Failed to fetch grid import/export (today)", exc_info=True)

        try:
            begin_all = ECOFLOW_BUSINESS_START
            resp = await _call_api(begin_all.strftime(fmt), end_day.strftime(fmt), HIST_CODE_GRID)
            items = resp.get("data", {}).get("data", [])
            if items:
                imp, exp = _sum_grid(items)
                params["history.gridImportCumulative"] = imp
                params["history.gridImportCumulative.beginTime"] = begin_all.strftime(fmt)
                params["history.gridImportCumulative.endTime"] = end_day.strftime(fmt)
                params["history.gridExportCumulative"] = exp
                params["history.gridExportCumulative.beginTime"] = begin_all.strftime(fmt)
                params["history.gridExportCumulative.endTime"] = end_day.strftime(fmt)
        except Exception:
            _LOGGER.debug("Failed to fetch grid import/export (cumulative)", exc_info=True)

        # Battery Charge / Discharge — today and cumulative
        try:
            resp = await _call_api(begin_day.strftime(fmt), end_day.strftime(fmt), HIST_CODE_BATTERY)
            items = resp.get("data", {}).get("data", [])
            if items:
                chg, dsg = _sum_battery(items)
                params["history.batteryCharge"] = chg
                params["history.batteryCharge.beginTime"] = begin_day.strftime(fmt)
                params["history.batteryCharge.endTime"] = end_day.strftime(fmt)
                params["history.batteryDischarge"] = dsg
                params["history.batteryDischarge.beginTime"] = begin_day.strftime(fmt)
                params["history.batteryDischarge.endTime"] = end_day.strftime(fmt)
        except Exception:
            _LOGGER.debug("Failed to fetch battery charge/discharge (today)", exc_info=True)

        try:
            begin_all = ECOFLOW_BUSINESS_START
            resp = await _call_api(begin_all.strftime(fmt), end_day.strftime(fmt), HIST_CODE_BATTERY)
            items = resp.get("data", {}).get("data", [])
            if items:
                chg, dsg = _sum_battery(items)
                params["history.batteryChargeCumulative"] = chg
                params["history.batteryChargeCumulative.beginTime"] = begin_all.strftime(fmt)
                params["history.batteryChargeCumulative.endTime"] = end_day.strftime(fmt)
                params["history.batteryDischargeCumulative"] = dsg
                params["history.batteryDischargeCumulative.beginTime"] = begin_all.strftime(fmt)
                params["history.batteryDischargeCumulative.endTime"] = end_day.strftime(fmt)
        except Exception:
            _LOGGER.debug("Failed to fetch battery charge/discharge (cumulative)", exc_info=True)

        try:
            self._device.data.params.update(params)
            self._device.data.set_params_time = _utcnow()
        except Exception as exc:
            _LOGGER.error("Failed to update device params for sn=%s: %s", sn, exc, exc_info=True)

        return params


class StreamACMonetarySensorEntity(BaseSensorEntity):
    """Sensor whose unit of measurement is read dynamically from a params key (e.g. currency)."""

    def __init__(self, client: EcoflowApiClient, device: BaseDevice, mqtt_key: str, title: str, unit_key: str):
        super().__init__(client, device, mqtt_key, title)
        self._unit_key = unit_key

    def _updated(self, data: dict[str, Any]):
        unit = data.get(self._unit_key)
        if unit:
            self._attr_native_unit_of_measurement = str(unit)
        super()._updated(data)


class StreamAC(BaseDevice):
    """StreamAC device with real-time MQTT sensors and periodic historical data."""

    history_coordinator: "StreamACHistoryUpdateCoordinator | None" = None

    async def async_cleanup(self) -> None:
        """Cancel background tasks on device unload."""
        tasks = getattr(self, "_background_tasks", None)
        if tasks:
            for task in list(tasks):
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            tasks.clear()

    def configure_history(self, hass: HomeAssistant, client: EcoflowApiClient) -> None:
        """Set up the periodic historical-data coordinator and trigger an initial refresh."""
        if not hasattr(self, "_background_tasks"):
            self._background_tasks: set[asyncio.Task[Any]] = set()
        try:
            if self.history_coordinator is None:
                self.history_coordinator = StreamACHistoryUpdateCoordinator(
                    hass, client, self, DEFAULT_STREAM_AC_HISTORY_PERIOD_SEC
                )

            def _on_task_done(t: asyncio.Task) -> None:
                try:
                    t.result()
                except Exception as exc:
                    _LOGGER.error("Background historical fetch task failed: %s", exc)
                finally:
                    self._background_tasks.discard(t)

            task = hass.async_create_task(self.history_coordinator.async_request_refresh())
            self._background_tasks.add(task)
            task.add_done_callback(_on_task_done)
            _LOGGER.info("Scheduled initial historical refresh for StreamAC %s", self.device_info.sn)
        except Exception as exc:
            _LOGGER.error("Failed to schedule historical refresh for StreamAC %s: %s", self.device_info.sn, exc, exc_info=True)

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
            # Per-PV power, voltage, current (Stream Ultra / Ultra X / AC Pro).
            # Per-PV reporting depends on the firmware version installed:
            #   - Firmware <  1.0.1.88: powGetPv / powGetPv2..4 emitted, per-PV
            #     watts are correct, plugInInfoPv*Amp returns 0.
            #   - Firmware >= 1.0.1.88: powGetPv* returns 0, per-PV data lives
            #     in plugInInfoPv{,2,3,4}Amp + plugInInfoPv{,2,3,4}Vol instead.
            # See issues #582, #584. To stay firmware-agnostic we register BOTH
            # mapping variants with auto_enable=True. HA enables whichever set
            # first sees a non-zero value.
            #
            # New-firmware path (computed amp x vol via StreamPvWattsSensorEntity)
            StreamPvWattsSensorEntity(client, self, "plugInInfoPvAmp", const.STREAM_POWER_PV_1, False, True),
            StreamPvWattsSensorEntity(client, self, "plugInInfoPv2Amp", const.STREAM_POWER_PV_2, False, True),
            StreamPvWattsSensorEntity(client, self, "plugInInfoPv3Amp", const.STREAM_POWER_PV_3, False, True),
            StreamPvWattsSensorEntity(client, self, "plugInInfoPv4Amp", const.STREAM_POWER_PV_4, False, True),
            # Legacy-firmware path (powGetPv* keys)
            # "powGetPv": 0.0,
            WattsSensorEntity(client, self, "powGetPv", const.STREAM_POWER_PV_1, False, True),
            # "powGetPv2": 0.0,
            WattsSensorEntity(client, self, "powGetPv2", const.STREAM_POWER_PV_2, False, True),
            # "powGetPv3": 0.0,
            WattsSensorEntity(client, self, "powGetPv3", const.STREAM_POWER_PV_3, False, True),
            # "powGetPv4": 0.0,
            WattsSensorEntity(client, self, "powGetPv4", const.STREAM_POWER_PV_4, False, True),
            # Per-PV voltage + current (emitted by all Stream firmware versions)
            VoltSensorEntity(client, self, "plugInInfoPvVol", const.STREAM_IN_VOL_PV_1, False, True),
            VoltSensorEntity(client, self, "plugInInfoPv2Vol", const.STREAM_IN_VOL_PV_2, False, True),
            VoltSensorEntity(client, self, "plugInInfoPv3Vol", const.STREAM_IN_VOL_PV_3, False, True),
            VoltSensorEntity(client, self, "plugInInfoPv4Vol", const.STREAM_IN_VOL_PV_4, False, True),
            AmpSensorEntity(client, self, "plugInInfoPvAmp", const.STREAM_IN_AMPS_PV_1, False, True),
            AmpSensorEntity(client, self, "plugInInfoPv2Amp", const.STREAM_IN_AMPS_PV_2, False, True),
            AmpSensorEntity(client, self, "plugInInfoPv3Amp", const.STREAM_IN_AMPS_PV_3, False, True),
            AmpSensorEntity(client, self, "plugInInfoPv4Amp", const.STREAM_IN_AMPS_PV_4, False, True),
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
            # Historical data sensors (fetched via HTTP API every 15 minutes)
            BaseSensorEntity(client, self, "history.energyIndependenceToday", const.STREAM_HISTORY_ENERGY_INDEPENDENCE_TODAY)
            .with_unit_of_measurement("%")
            .with_state_class(SensorStateClass.MEASUREMENT)
            .attr("history.energyIndependenceToday.beginTime", "Begin Time", "")
            .attr("history.energyIndependenceToday.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            BaseSensorEntity(client, self, "history.energyIndependenceYear", const.STREAM_HISTORY_ENERGY_INDEPENDENCE_YEAR)
            .with_unit_of_measurement("%")
            .with_state_class(SensorStateClass.MEASUREMENT)
            .attr("history.energyIndependenceYear.beginTime", "Begin Time", "")
            .attr("history.energyIndependenceYear.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            BaseSensorEntity(client, self, "history.environmentalImpactToday", const.STREAM_HISTORY_ENVIRONMENTAL_IMPACT_TODAY)
            .with_unit_of_measurement("kg")
            .with_state_class(SensorStateClass.TOTAL)
            .attr("history.environmentalImpactToday.beginTime", "Begin Time", "")
            .attr("history.environmentalImpactToday.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            BaseSensorEntity(client, self, "history.environmentalImpactCumulative", const.STREAM_HISTORY_ENVIRONMENTAL_IMPACT_CUMULATIVE)
            .with_unit_of_measurement("kg")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.environmentalImpactCumulative.beginTime", "Begin Time", "")
            .attr("history.environmentalImpactCumulative.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            StreamACMonetarySensorEntity(client, self, "history.solarEnergySavingsToday", const.STREAM_HISTORY_TOTAL_SOLAR_SAVINGS_TODAY, "history.solarEnergySavingsUnit")
            .with_state_class(SensorStateClass.TOTAL)
            .attr("history.solarEnergySavingsToday.beginTime", "Begin Time", "")
            .attr("history.solarEnergySavingsToday.endTime", "End Time", "")
            .attr("history.solarEnergySavingsUnit", "Currency Unit", "")
            .attr("history.mainSn", "Main Device SN", ""),
            StreamACMonetarySensorEntity(client, self, "history.solarEnergySavingsCumulative", const.STREAM_HISTORY_TOTAL_SOLAR_SAVINGS_CUMULATIVE, "history.solarEnergySavingsUnit")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.solarEnergySavingsCumulative.beginTime", "Begin Time", "")
            .attr("history.solarEnergySavingsCumulative.endTime", "End Time", "")
            .attr("history.solarEnergySavingsUnit", "Currency Unit", "")
            .attr("history.mainSn", "Main Device SN", ""),
            EnergySensorEntity(client, self, "history.solarGeneratedToday", const.STREAM_HISTORY_SOLAR_GENERATED_TODAY)
            .with_unit_of_measurement("Wh")
            .with_state_class(SensorStateClass.TOTAL)
            .attr("history.solarGeneratedToday.beginTime", "Begin Time", "")
            .attr("history.solarGeneratedToday.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            EnergySensorEntity(client, self, "history.solarGeneratedCumulative", const.STREAM_HISTORY_SOLAR_GENERATED_CUMULATIVE)
            .with_unit_of_measurement("Wh")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.solarGeneratedCumulative.beginTime", "Begin Time", "")
            .attr("history.solarGeneratedCumulative.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            EnergySensorEntity(client, self, "history.electricityConsumptionToday", const.STREAM_HISTORY_ELECTRICITY_CONSUMPTION_TODAY)
            .with_unit_of_measurement("Wh")
            .with_state_class(SensorStateClass.TOTAL)
            .attr("history.electricityConsumptionToday.beginTime", "Begin Time", "")
            .attr("history.electricityConsumptionToday.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            EnergySensorEntity(client, self, "history.electricityConsumptionCumulative", const.STREAM_HISTORY_ELECTRICITY_CONSUMPTION_CUMULATIVE)
            .with_unit_of_measurement("Wh")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.electricityConsumptionCumulative.beginTime", "Begin Time", "")
            .attr("history.electricityConsumptionCumulative.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            EnergySensorEntity(client, self, "history.gridImport", const.STREAM_HISTORY_GRID_IMPORT_TODAY)
            .with_unit_of_measurement("Wh")
            .with_state_class(SensorStateClass.TOTAL)
            .attr("history.gridImport.beginTime", "Begin Time", "")
            .attr("history.gridImport.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            EnergySensorEntity(client, self, "history.gridImportCumulative", const.STREAM_HISTORY_GRID_IMPORT_CUMULATIVE)
            .with_unit_of_measurement("Wh")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.gridImportCumulative.beginTime", "Begin Time", "")
            .attr("history.gridImportCumulative.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            EnergySensorEntity(client, self, "history.gridExport", const.STREAM_HISTORY_GRID_EXPORT_TODAY)
            .with_unit_of_measurement("Wh")
            .with_state_class(SensorStateClass.TOTAL)
            .attr("history.gridExport.beginTime", "Begin Time", "")
            .attr("history.gridExport.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            EnergySensorEntity(client, self, "history.gridExportCumulative", const.STREAM_HISTORY_GRID_EXPORT_CUMULATIVE)
            .with_unit_of_measurement("Wh")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.gridExportCumulative.beginTime", "Begin Time", "")
            .attr("history.gridExportCumulative.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            EnergySensorEntity(client, self, "history.batteryCharge", const.STREAM_HISTORY_BATTERY_CHARGE_TODAY)
            .with_unit_of_measurement("Wh")
            .with_state_class(SensorStateClass.TOTAL)
            .attr("history.batteryCharge.beginTime", "Begin Time", "")
            .attr("history.batteryCharge.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            EnergySensorEntity(client, self, "history.batteryChargeCumulative", const.STREAM_HISTORY_BATTERY_CHARGE_CUMULATIVE)
            .with_unit_of_measurement("Wh")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.batteryChargeCumulative.beginTime", "Begin Time", "")
            .attr("history.batteryChargeCumulative.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            EnergySensorEntity(client, self, "history.batteryDischarge", const.STREAM_HISTORY_BATTERY_DISCHARGE_TODAY)
            .with_unit_of_measurement("Wh")
            .with_state_class(SensorStateClass.TOTAL)
            .attr("history.batteryDischarge.beginTime", "Begin Time", "")
            .attr("history.batteryDischarge.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            EnergySensorEntity(client, self, "history.batteryDischargeCumulative", const.STREAM_HISTORY_BATTERY_DISCHARGE_CUMULATIVE)
            .with_unit_of_measurement("Wh")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.batteryDischargeCumulative.beginTime", "Begin Time", "")
            .attr("history.batteryDischargeCumulative.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
        ]

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
