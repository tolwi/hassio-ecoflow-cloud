from ...sensor import StatusSensorEntity
from homeassistant.components.sensor import SensorStateClass  # pyright: ignore[reportMissingImports]
from homeassistant.util import dt
from datetime import timedelta
from .data_bridge import to_plain
from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import const, BaseDevice
from custom_components.ecoflow_cloud.entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, \
    BaseSelectEntity
from custom_components.ecoflow_cloud.sensor import WattsSensorEntity,LevelSensorEntity,CapacitySensorEntity, \
    InWattsSensorEntity,OutWattsSensorEntity, RemainSensorEntity, MilliVoltSensorEntity, TempSensorEntity, \
    CyclesSensorEntity, EnergySensorEntity, CumulativeCapacitySensorEntity, VoltSensorEntity
from ...switch import EnabledEntity
from ...number import (
    BatteryBackupLevel
)

# Historical metric codes as per API docs
HIST_CODE_ENERGY_INDEPENDENCE = "BK621-App-HOME-INDEPENDENCE-PERCENT-FLOW-indep-progress_bar-NOTDISTINGUISH-MASTER_DATA"
HIST_CODE_ENV_IMPACT = "BK621-App-HOME-CO2-WEIGHT-FLOW-impact-progress_arc-NOTDISTINGUISH-MASTER_DATA"
HIST_CODE_SAVINGS_TOTAL = "BK621-App-HOME-SAVING-CURRENCY-FLOW-earnings-progress_arc-NOTDISTINGUISH-MASTER_DATA"
HIST_CODE_SOLAR_GENERATED = "BK621-App-HOME-SOLAR-ENERGY-FLOW-solor-line-NOTDISTINGUISH-MASTER_DATA"
HIST_CODE_ELECTRICITY_CONS = "BK621-App-HOME-LOAD-ENERGY-FLOW-consumption-prop_arc-NOTDISTINGUISH-MASTER_DATA"
HIST_CODE_GRID = "BK621-App-HOME-GRID-ENERGY-FLOW-grid_prop_bar-NOTDISTINGUISH-MASTER_DATA"
HIST_CODE_BATTERY = "BK621-App-HOME-SOC-ENERGY-FLOW-battery-prop_bar-NOTDISTINGUISH-MASTER_DATA"

class _HistoricalDataStatus(StatusSensorEntity):
    def __init__(self, client: EcoflowApiClient, device: BaseDevice):
        super().__init__(client, device, "Status (Historical)", "status.historical")
        self.offline_barrier_sec = 60
        self._last_fetch = dt.utcnow().replace(year=2000, month=1, day=1, hour=0)

    def _resolve_main_sn(self) -> str:
        # Helper to resolve the main device SN for historical queries.
        # Fallback to current device SN when system-level main SN is unavailable.
        try:
            # If the client exposes a main/master SN, prefer it.
            main_sn = getattr(self._client, "main_sn", None)
            if isinstance(main_sn, str) and main_sn:
                return main_sn
        except Exception:
            pass
        return self._device.device_info.sn

    async def async_added_to_hass(self) -> None:
        # Kick off an immediate fetch when the entity is added so
        # history units/values are present before other sensors render.
        try:
            self.hass.async_create_background_task(self._fetch_and_update(), "initial historical data fetch")
        except Exception:
            pass

    async def _fetch_and_update(self):
        # Prepare day range in UTC for day/hour level metrics
        now = dt.utcnow()
        begin_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_day = now.replace(hour=23, minute=59, second=59, microsecond=0)
        fmt = "%Y-%m-%d %H:%M:%S"
        sn = self._resolve_main_sn()

        params: dict[str, float | int] = {}

        try:
            # Energy independence — Today and Yearly

            # Daily (today-so-far, live)
            resp_td = await self._client.historical_data(
                sn, begin_day.strftime(fmt), end_day.strftime(fmt), HIST_CODE_ENERGY_INDEPENDENCE
            )
            items_td = resp_td.get("data", {}).get("data", [])
            if items_td:
                params["history.energyIndependenceDailyToday"] = float(items_td[0].get("indexValue", 0))
                params["history.energyIndependenceDailyToday.beginTime"] = begin_day.strftime(fmt)
                params["history.energyIndependenceDailyToday.endTime"] = end_day.strftime(fmt)

            # Remove weekly/monthly for declutter

            # Yearly (calendar year)
            begin_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_year = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=0)
            resp_y = await self._client.historical_data(
                sn, begin_year.strftime(fmt), end_year.strftime(fmt), HIST_CODE_ENERGY_INDEPENDENCE
            )
            items_y = resp_y.get("data", {}).get("data", [])
            if items_y:
                params["history.energyIndependenceYearly"] = float(items_y[0].get("indexValue", 0))
                params["history.energyIndependenceYearly.beginTime"] = begin_year.strftime(fmt)
                params["history.energyIndependenceYearly.endTime"] = end_year.strftime(fmt)

            # Environmental impact (today, grams)
            resp = await self._client.historical_data(
                sn, begin_day.strftime(fmt), end_day.strftime(fmt), HIST_CODE_ENV_IMPACT
            )
            items = resp.get("data", {}).get("data", [])
            if items:
                params["history.environmentalImpactDailyToday"] = float(items[0].get("indexValue", 0))
                params["history.environmentalImpactDailyToday.beginTime"] = begin_day.strftime(fmt)
                params["history.environmentalImpactDailyToday.endTime"] = end_day.strftime(fmt)

            # Environmental impact aggregates for yesterday, week, month, year
            try:
                # Yesterday
                begin_yesterday = (begin_day - timedelta(days=1))
                end_yesterday = (end_day - timedelta(days=1))
                resp_y = await self._client.historical_data(
                    sn, begin_yesterday.strftime(fmt), end_yesterday.strftime(fmt), HIST_CODE_ENV_IMPACT
                )
                items_y = resp_y.get("data", {}).get("data", [])
                if items_y:
                    params["history.environmentalImpactYesterday"] = float(items_y[0].get("indexValue", 0))

                # Week (last 7 days including today)
                begin_week = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=6)
                resp_w = await self._client.historical_data(
                    sn, begin_week.strftime(fmt), end_day.strftime(fmt), HIST_CODE_ENV_IMPACT
                )
                items_w = resp_w.get("data", {}).get("data", [])
                if items_w:
                    total_w = 0.0
                    for it in items_w:
                        try:
                            total_w += float(it.get("indexValue", 0))
                        except Exception:
                            pass
                    params["history.environmentalImpactWeek"] = total_w

                # Month (calendar month to date)
                begin_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                resp_m = await self._client.historical_data(
                    sn, begin_month.strftime(fmt), end_day.strftime(fmt), HIST_CODE_ENV_IMPACT
                )
                items_m = resp_m.get("data", {}).get("data", [])
                if items_m:
                    total_m = 0.0
                    for it in items_m:
                        try:
                            total_m += float(it.get("indexValue", 0))
                        except Exception:
                            pass
                    params["history.environmentalImpactMonth"] = total_m

                # Year (calendar year to date)
                begin_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                resp_ytd = await self._client.historical_data(
                    sn, begin_year.strftime(fmt), end_day.strftime(fmt), HIST_CODE_ENV_IMPACT
                )
                items_ytd = resp_ytd.get("data", {}).get("data", [])
                if items_ytd:
                    total_y = 0.0
                    for it in items_ytd:
                        try:
                            total_y += float(it.get("indexValue", 0))
                        except Exception:
                            pass
                    params["history.environmentalImpactYear"] = total_y
            except Exception:
                # Ignore aggregate errors
                pass

            # Environmental impact cumulative (grams) since May 2017
            try:
                begin_all = dt.utcnow().replace(year=2017, month=5, day=1, hour=0, minute=0, second=0, microsecond=0)
                resp_all = await self._client.historical_data(
                    sn, begin_all.strftime(fmt), end_day.strftime(fmt), HIST_CODE_ENV_IMPACT
                )
                all_items = resp_all.get("data", {}).get("data", [])
                if all_items:
                    total_g = 0.0
                    for it in all_items:
                        try:
                            total_g += float(it.get("indexValue", 0))
                        except Exception:
                            pass
                    params["history.environmentalImpactCumulative"] = total_g
                    params["history.environmentalImpactCumulative.beginTime"] = begin_all.strftime(fmt)
                    params["history.environmentalImpactCumulative.endTime"] = end_day.strftime(fmt)
                    # capture unit from last item if present
                    # unit attribute not required for environmental impact
            except Exception:
                # Ignore cumulative errors to not block other updates
                pass

            # Total solar energy savings (cumulative currency)
            try:
                begin_all = dt.utcnow().replace(year=2017, month=5, day=1, hour=0, minute=0, second=0, microsecond=0)
                resp_sav_all = await self._client.historical_data(
                    sn, begin_all.strftime(fmt), end_day.strftime(fmt), HIST_CODE_SAVINGS_TOTAL
                )
                items_sav_all = resp_sav_all.get("data", {}).get("data", [])
                if items_sav_all:
                    total_sav = 0.0
                    unit = None
                    for it in items_sav_all:
                        try:
                            total_sav += float(it.get("indexValue", 0))
                        except Exception:
                            pass
                        u = it.get("unit")
                        if isinstance(u, str) and u:
                            unit = u
                    params["history.solarEnergySavingsCumulative"] = total_sav
                    params["history.solarEnergySavingsCumulative.beginTime"] = begin_all.strftime(fmt)
                    params["history.solarEnergySavingsCumulative.endTime"] = end_day.strftime(fmt)
                    if unit:
                        params["history.solarEnergySavingsUnit"] = unit
            except Exception:
                pass

            # Total solar energy savings today (currency)
            try:
                resp_sav_today = await self._client.historical_data(
                    sn, begin_day.strftime(fmt), end_day.strftime(fmt), HIST_CODE_SAVINGS_TOTAL
                )
                items_sav_today = resp_sav_today.get("data", {}).get("data", [])
                if items_sav_today:
                    unit_td = None
                    val_td = 0.0
                    # API usually returns single item for the day
                    it0 = items_sav_today[0]
                    try:
                        val_td = float(it0.get("indexValue", 0))
                    except Exception:
                        val_td = 0.0
                    u = it0.get("unit")
                    if isinstance(u, str) and u:
                        unit_td = u
                    params["history.solarEnergySavingsDailyToday"] = val_td
                    params["history.solarEnergySavingsDailyToday.beginTime"] = begin_day.strftime(fmt)
                    params["history.solarEnergySavingsDailyToday.endTime"] = end_day.strftime(fmt)
                    if unit_td:
                        params["history.solarEnergySavingsUnit"] = unit_td
            except Exception:
                pass

            # Solar-Generated Energy today (Wh)
            resp = await self._client.historical_data(
                sn, begin_day.strftime(fmt), end_day.strftime(fmt), HIST_CODE_SOLAR_GENERATED
            )
            items = resp.get("data", {}).get("data", [])
            if items:
                params["history.solarGeneratedWhDailyToday"] = float(items[0].get("indexValue", 0))
                params["history.solarGeneratedWhDailyToday.beginTime"] = begin_day.strftime(fmt)
                params["history.solarGeneratedWhDailyToday.endTime"] = end_day.strftime(fmt)

            # Solar-Generated cumulative (Wh) since May 2017
            try:
                begin_all = dt.utcnow().replace(year=2017, month=5, day=1, hour=0, minute=0, second=0, microsecond=0)
                resp_all = await self._client.historical_data(
                    sn, begin_all.strftime(fmt), end_day.strftime(fmt), HIST_CODE_SOLAR_GENERATED
                )
                all_items = resp_all.get("data", {}).get("data", [])
                if all_items:
                    total_wh = 0.0
                    for it in all_items:
                        try:
                            total_wh += float(it.get("indexValue", 0))
                        except Exception:
                            pass
                    params["history.solarGeneratedWhCumulative"] = total_wh
                    params["history.solarGeneratedWhCumulative.beginTime"] = begin_all.strftime(fmt)
                    params["history.solarGeneratedWhCumulative.endTime"] = end_day.strftime(fmt)
            except Exception:
                # Ignore cumulative errors to not block other updates
                pass

            # Electricity consumption today (Wh)
            resp = await self._client.historical_data(
                sn, begin_day.strftime(fmt), end_day.strftime(fmt), HIST_CODE_ELECTRICITY_CONS
            )
            items = resp.get("data", {}).get("data", [])
            if items:
                params["history.electricityConsumptionWhDailyToday"] = float(items[0].get("indexValue", 0))
                params["history.electricityConsumptionWhDailyToday.beginTime"] = begin_day.strftime(fmt)
                params["history.electricityConsumptionWhDailyToday.endTime"] = end_day.strftime(fmt)

            # Electricity consumption cumulative (Wh) since May 2017
            try:
                begin_all = dt.utcnow().replace(year=2017, month=5, day=1, hour=0, minute=0, second=0, microsecond=0)
                resp_ec_all = await self._client.historical_data(
                    sn, begin_all.strftime(fmt), end_day.strftime(fmt), HIST_CODE_ELECTRICITY_CONS
                )
                items_ec_all = resp_ec_all.get("data", {}).get("data", [])
                if items_ec_all:
                    total_cons_wh = 0.0
                    for it in items_ec_all:
                        try:
                            total_cons_wh += float(it.get("indexValue", 0))
                        except Exception:
                            pass
                    params["history.electricityConsumptionWhCumulative"] = total_cons_wh
                    params["history.electricityConsumptionWhCumulative.beginTime"] = begin_all.strftime(fmt)
                    params["history.electricityConsumptionWhCumulative.endTime"] = end_day.strftime(fmt)
            except Exception:
                pass

            # Grid (Wh): extra 1/2
            resp = await self._client.historical_data(
                sn, begin_day.strftime(fmt), end_day.strftime(fmt), HIST_CODE_GRID
            )
            items = resp.get("data", {}).get("data", [])
            for it in items:
                extra = str(it.get("extra", ""))
                if extra == "1":
                    params["history.gridImportWh"] = float(it.get("indexValue", 0))
                    params["history.gridImportWh.beginTime"] = begin_day.strftime(fmt)
                    params["history.gridImportWh.endTime"] = end_day.strftime(fmt)
                elif extra == "2":
                    params["history.gridExportWh"] = float(it.get("indexValue", 0))
                    params["history.gridExportWh.beginTime"] = begin_day.strftime(fmt)
                    params["history.gridExportWh.endTime"] = end_day.strftime(fmt)

            # Grid cumulative (Wh) since May 2017: split import/export by extra
            try:
                begin_all = dt.utcnow().replace(year=2017, month=5, day=1, hour=0, minute=0, second=0, microsecond=0)
                resp_grid_all = await self._client.historical_data(
                    sn, begin_all.strftime(fmt), end_day.strftime(fmt), HIST_CODE_GRID
                )
                items_grid_all = resp_grid_all.get("data", {}).get("data", [])
                if items_grid_all:
                    total_import = 0.0
                    total_export = 0.0
                    for it in items_grid_all:
                        try:
                            val = float(it.get("indexValue", 0))
                        except Exception:
                            val = 0.0
                        extra = str(it.get("extra", ""))
                        if extra == "1":
                            total_import += val
                        elif extra == "2":
                            total_export += val
                    params["history.gridImportWhCumulative"] = total_import
                    params["history.gridImportWhCumulative.beginTime"] = begin_all.strftime(fmt)
                    params["history.gridImportWhCumulative.endTime"] = end_day.strftime(fmt)
                    params["history.gridExportWhCumulative"] = total_export
                    params["history.gridExportWhCumulative.beginTime"] = begin_all.strftime(fmt)
                    params["history.gridExportWhCumulative.endTime"] = end_day.strftime(fmt)
            except Exception:
                pass

            # Battery charge/discharge (Wh): extra 2=charge, 1=discharge
            resp = await self._client.historical_data(
                sn, begin_day.strftime(fmt), end_day.strftime(fmt), HIST_CODE_BATTERY
            )
            items = resp.get("data", {}).get("data", [])
            for it in items:
                extra = str(it.get("extra", ""))
                if extra == "2":
                    params["history.batteryChargeWh"] = float(it.get("indexValue", 0))
                    params["history.batteryChargeWh.beginTime"] = begin_day.strftime(fmt)
                    params["history.batteryChargeWh.endTime"] = end_day.strftime(fmt)
                elif extra == "1":
                    params["history.batteryDischargeWh"] = float(it.get("indexValue", 0))
                    params["history.batteryDischargeWh.beginTime"] = begin_day.strftime(fmt)
                    params["history.batteryDischargeWh.endTime"] = end_day.strftime(fmt)

            # Battery cumulative (Wh) since May 2017
            try:
                begin_all = dt.utcnow().replace(year=2017, month=5, day=1, hour=0, minute=0, second=0, microsecond=0)
                resp_batt_all = await self._client.historical_data(
                    sn, begin_all.strftime(fmt), end_day.strftime(fmt), HIST_CODE_BATTERY
                )
                items_batt_all = resp_batt_all.get("data", {}).get("data", [])
                if items_batt_all:
                    total_charge = 0.0
                    total_discharge = 0.0
                    for it in items_batt_all:
                        try:
                            val = float(it.get("indexValue", 0))
                        except Exception:
                            val = 0.0
                        extra = str(it.get("extra", ""))
                        if extra == "2":
                            total_charge += val
                        elif extra == "1":
                            total_discharge += val
                    params["history.batteryChargeWhCumulative"] = total_charge
                    params["history.batteryChargeWhCumulative.beginTime"] = begin_all.strftime(fmt)
                    params["history.batteryChargeWhCumulative.endTime"] = end_day.strftime(fmt)
                    params["history.batteryDischargeWhCumulative"] = total_discharge
                    params["history.batteryDischargeWhCumulative.beginTime"] = begin_all.strftime(fmt)
                    params["history.batteryDischargeWhCumulative.endTime"] = end_day.strftime(fmt)
            except Exception:
                pass
        except Exception as e:
            # Log but do not break entity updates
            from logging import getLogger

            getLogger(__name__).error("Failed to fetch historical data: %s", e, exc_info=True)

        if params:
            params["history.mainSn"] = sn
            self._device.data.update_data({"params": params})

    def _actualize_status(self) -> bool:
        changed = super()._actualize_status()
        elapsed = dt.as_timestamp(dt.utcnow()) - dt.as_timestamp(self._last_fetch)
        if elapsed > self.offline_barrier_sec:
            self._last_fetch = dt.utcnow()
            # Fire and forget background task
            self.hass.async_create_background_task(self._fetch_and_update(), "fetch historical data")
            changed = True
        return changed

class StreamAC(BaseDevice):

    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [
            # "accuChgCap": 198511,
            CumulativeCapacitySensorEntity(client, self, "accuChgCap", const.ACCU_CHARGE_CAP, False).with_icon("mdi:battery-arrow-up"),
            # "accuChgEnergy": 3992,
            EnergySensorEntity(client, self, "accuChgEnergy", const.ACCU_CHARGE_ENERGY).with_icon("mdi:battery-arrow-up"),
            # "accuDsgCap": 184094,
            CumulativeCapacitySensorEntity(client, self, "accuDsgCap", const.ACCU_DISCHARGE_CAP, False).with_icon("mdi:battery-arrow-down"),
            # "accuDsgEnergy": 3646,
            EnergySensorEntity(client, self, "accuDsgEnergy", const.ACCU_DISCHARGE_ENERGY).with_icon("mdi:battery-arrow-down"),
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
            RemainSensorEntity(client, self, "bmsChgRemTime", const.CHARGE_REMAINING_TIME, False).with_icon("mdi:battery-clock"),
            # "bmsDesignCap": 1920,
            # "bmsDsgRemTime": 5939,
            RemainSensorEntity(client, self, "bmsDsgRemTime", const.DISCHARGE_REMAINING_TIME, False).with_icon("mdi:battery-clock"),
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
            CapacitySensorEntity(client, self, "designCap", const.STREAM_DESIGN_CAPACITY, False).with_icon("mdi:battery"),
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
            CapacitySensorEntity(client, self, "fullCap", const.STREAM_FULL_CAPACITY, False).with_icon("mdi:battery"),
            # "gridCodeSelection": "GRID_STD_CODE_UTE_MAINLAND",
            # "gridCodeVersion": 10001,
            # "gridConnectionFreq": 49.974655,
            # "gridConnectionPower": -967.2364,
            WattsSensorEntity(client, self, "gridConnectionPower", const.STREAM_POWER_AC).with_icon("mdi:current-ac"),
            # "gridConnectionSta": "PANEL_GRID_IN",
            # "gridConnectionVol": 235.34576,
            VoltSensorEntity(client, self, "gridConnectionVol", const.STREAM_POWER_VOL, False),
            # "gridSysDeviceCnt": 2,
            # "heatfilmNtcNum": 0,
            # "heatfilmTemp": [],
            # "hwVer": "V0.0.0",
            # "inputWatts": 900,
            InWattsSensorEntity(client, self, "inputWatts", const.STREAM_IN_POWER).with_icon("mdi:power-plug"),
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
            OutWattsSensorEntity(client, self, "outputWatts", const.STREAM_OUT_POWER).with_icon("mdi:power-plug"),
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
            WattsSensorEntity(client, self, "powGetBpCms", const.STREAM_POWER_BATTERY).with_icon("mdi:battery"),
            # "powGetPv": 0.0,
            WattsSensorEntity(client, self, "powGetPv", const.STREAM_POWER_PV_1, False, True).with_icon("mdi:solar-panel"),
            # "powGetPv2": 0.0,
            WattsSensorEntity(client, self, "powGetPv2", const.STREAM_POWER_PV_2, False, True).with_icon("mdi:solar-panel"),
            # "powGetPv3": 0.0,
            WattsSensorEntity(client, self, "powGetPv3", const.STREAM_POWER_PV_3, False, True).with_icon("mdi:solar-panel"),
            # "powGetPv4": 0.0,
            WattsSensorEntity(client, self, "powGetPv4", const.STREAM_POWER_PV_4, False, True).with_icon("mdi:solar-panel"),
            # "powGetPvSum": 2051.3975,
            WattsSensorEntity(client, self, "powGetPvSum", const.STREAM_POWER_PV_SUM).with_icon("mdi:solar-panel"),
            # "powGetSchuko1": 0.0,
            WattsSensorEntity(client, self, "powGetSchuko1", const.STREAM_GET_SCHUKO1, False, True).with_icon("mdi:power-socket"),
            # "powGetSchuko2": 18.654325,
            WattsSensorEntity(client, self, "powGetSchuko2", const.STREAM_GET_SCHUKO2, False, True).with_icon("mdi:power-socket"),
            # "powGetSysGrid": -135.0,
            WattsSensorEntity(client, self, "powGetSysGrid", const.STREAM_POWER_GRID).with_icon("mdi:transmission-tower"),
            # "powGetSysLoad": 0.0,
            WattsSensorEntity(client, self, "powGetSysLoad", const.STREAM_GET_SYS_LOAD).with_icon("mdi:power-plug"),
            # "powGetSysLoadFromBp": 0.0,
            WattsSensorEntity(client, self, "powGetSysLoadFromBp", const.STREAM_GET_SYS_LOAD_FROM_BP).with_icon("mdi:battery"),
            # "powGetSysLoadFromGrid": 0.0,
            WattsSensorEntity(client, self, "powGetSysLoadFromGrid", const.STREAM_GET_SYS_LOAD_FROM_GRID).with_icon("mdi:transmission-tower"),
            # "powGetSysLoadFromPv": 0.0,
            WattsSensorEntity(client, self, "powGetSysLoadFromPv", const.STREAM_GET_SYS_LOAD_FROM_PV).with_icon("mdi:solar-power"),
            # "powSysAcInMax": 4462,
            # "powSysAcOutMax": 800,
            # "productDetail": 5,
            # "productType": 58,
            # "realSoh": 100.0,
            LevelSensorEntity(client, self, "realSoh", const.REAL_SOH, False).with_icon("mdi:battery-heart"),
            # "relay1Onoff": true,
            # "relay2Onoff": true,
            # "relay3Onoff": true,
            # "relay4Onoff": true,
            # "remainCap": 46317,
            CapacitySensorEntity(client, self, "remainCap", const.STREAM_REMAIN_CAPACITY, False).with_unit_of_measurement("mAh").with_icon("mdi:battery-medium"),
            # "remainTime": 88,
            RemainSensorEntity(client, self, "remainTime", const.REMAINING_TIME).with_icon("mdi:battery-clock"),
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
            LevelSensorEntity(client, self, "soh", const.SOH).with_icon("mdi:battery-heart"),       
            # "stormPatternEnable": false,
            # "stormPatternEndTime": 0,
            # "stormPatternOpenFlag": false,
            # "sysGridConnectionPower": -2020.0437,
            WattsSensorEntity(client, self, "sysGridConnectionPower", const.STREAM_POWER_AC_SYS).with_icon("mdi:current-ac"),
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
            # Historical data sensors (HTTP)
            # Energy independence per period
            BaseSensorEntity(client, self, "history.energyIndependenceDailyToday", const.STREAM_HISTORY_ENERGY_INDEPENDENCE_TODAY)
            .with_unit_of_measurement("%")
            .with_icon("mdi:shield-check")
            .with_state_class(SensorStateClass.MEASUREMENT)
            .attr("history.energyIndependenceDailyToday.beginTime", "Begin Time", "")
            .attr("history.energyIndependenceDailyToday.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            BaseSensorEntity(client, self, "history.energyIndependenceYearly", const.STREAM_HISTORY_ENERGY_INDEPENDENCE_YEARLY)
            .with_unit_of_measurement("%")
            .with_icon("mdi:shield-check")
            .with_state_class(SensorStateClass.MEASUREMENT)
            .attr("history.energyIndependenceYearly.beginTime", "Begin Time", "")
            .attr("history.energyIndependenceYearly.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            # Environmental Impact (cumulative grams)
            BaseSensorEntity(
                client,
                self,
                "history.environmentalImpactDailyToday",
                const.STREAM_HISTORY_ENVIRONMENTAL_IMPACT_TODAY,
            )
            .with_unit_of_measurement("g")
            .with_icon("mdi:leaf")
            .with_state_class(SensorStateClass.MEASUREMENT)
            .attr("history.environmentalImpactDailyToday.beginTime", "Begin Time", "")
            .attr("history.environmentalImpactDailyToday.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            BaseSensorEntity(
                client,
                self,
                "history.environmentalImpactCumulative",
                const.STREAM_HISTORY_ENVIRONMENTAL_IMPACT_CUMULATIVE,
            )
            .with_unit_of_measurement("g")
            .with_icon("mdi:leaf")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.environmentalImpactCumulative.beginTime", "Begin Time", "")
            .attr("history.environmentalImpactCumulative.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            # Total solar energy savings (cumulative currency)
            DynamicCurrencySensorEntity(
                client,
                self,
                "history.solarEnergySavingsCumulative",
                const.STREAM_HISTORY_TOTAL_SOLAR_SAVINGS_CUMULATIVE,
                unit_param_key="history.solarEnergySavingsUnit",
            ).with_icon("mdi:cash")
             .with_state_class(SensorStateClass.TOTAL_INCREASING)
             .attr("history.solarEnergySavingsCumulative.beginTime", "Begin Time", "")
             .attr("history.solarEnergySavingsCumulative.endTime", "End Time", "")
             .attr("history.solarEnergySavingsUnit", "Currency Unit", "")
             .attr("history.mainSn", "Main Device SN", ""),
            # Total solar energy savings (today)
            DynamicCurrencySensorEntity(
                client,
                self,
                "history.solarEnergySavingsDailyToday",
                const.STREAM_HISTORY_TOTAL_SOLAR_SAVINGS_TODAY,
                unit_param_key="history.solarEnergySavingsUnit",
            ).with_icon("mdi:cash")
             .with_state_class(SensorStateClass.MEASUREMENT)
             .attr("history.solarEnergySavingsDailyToday.beginTime", "Begin Time", "")
             .attr("history.solarEnergySavingsDailyToday.endTime", "End Time", "")
             .attr("history.solarEnergySavingsUnit", "Currency Unit", "")
             .attr("history.mainSn", "Main Device SN", ""),
            # Solar-Generated Energy (today-so-far)
            BaseSensorEntity(
                client,
                self,
                "history.solarGeneratedWhDailyToday",
                const.STREAM_HISTORY_SOLAR_GENERATED_TODAY,
            )
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:solar-power")
            .with_state_class(SensorStateClass.MEASUREMENT)
            .attr("history.solarGeneratedWhDailyToday.beginTime", "Begin Time", "")
            .attr("history.solarGeneratedWhDailyToday.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            EnergySensorEntity(
                client,
                self,
                "history.solarGeneratedWhCumulative",
                const.STREAM_HISTORY_SOLAR_GENERATED_CUMULATIVE,
            )
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:solar-power")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.solarGeneratedWhCumulative.beginTime", "Begin Time", "")
            .attr("history.solarGeneratedWhCumulative.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            # Electricity consumption cumulative (Wh)
            EnergySensorEntity(
                client,
                self,
                "history.electricityConsumptionWhCumulative",
                const.STREAM_HISTORY_ELECTRICITY_CONSUMPTION_CUMULATIVE,
            ).with_unit_of_measurement("Wh")
            .with_icon("mdi:power-plug")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.electricityConsumptionWhCumulative.beginTime", "Begin Time", "")
            .attr("history.electricityConsumptionWhCumulative.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            # Electricity consumption today (live)
            BaseSensorEntity(
                client,
                self,
                "history.electricityConsumptionWhDailyToday",
                const.STREAM_HISTORY_ELECTRICITY_CONSUMPTION_TODAY,
            )
            .with_unit_of_measurement("Wh")
            .with_state_class(SensorStateClass.MEASUREMENT)
            .with_icon("mdi:power-plug")
            .attr("history.electricityConsumptionWhDailyToday.beginTime", "Begin Time", "")
            .attr("history.electricityConsumptionWhDailyToday.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            EnergySensorEntity(
                client,
                self,
                "history.gridImportWh",
                const.STREAM_HISTORY_GRID_IMPORT_TODAY,
            )
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:transmission-tower-import")
            .attr("history.gridImportWh.beginTime", "Begin Time", "")
            .attr("history.gridImportWh.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            EnergySensorEntity(
                client,
                self,
                "history.gridExportWh",
                const.STREAM_HISTORY_GRID_EXPORT_TODAY,
            )
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:transmission-tower-export")
            .attr("history.gridExportWh.beginTime", "Begin Time", "")
            .attr("history.gridExportWh.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            # Grid cumulative import/export (Wh)
            EnergySensorEntity(
                client,
                self,
                "history.gridImportWhCumulative",
                const.STREAM_HISTORY_GRID_IMPORT_CUMULATIVE,
            )
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:transmission-tower-import")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.gridImportWhCumulative.beginTime", "Begin Time", "")
            .attr("history.gridImportWhCumulative.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            EnergySensorEntity(
                client,
                self,
                "history.gridExportWhCumulative",
                const.STREAM_HISTORY_GRID_EXPORT_CUMULATIVE,
            )
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:transmission-tower-export")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.gridExportWhCumulative.beginTime", "Begin Time", "")
            .attr("history.gridExportWhCumulative.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            EnergySensorEntity(
                client,
                self,
                "history.batteryChargeWh",
                const.STREAM_HISTORY_BATTERY_CHARGE_TODAY,
            )
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:battery-arrow-up")
            .attr("history.batteryChargeWh.beginTime", "Begin Time", "")
            .attr("history.batteryChargeWh.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            EnergySensorEntity(
                client,
                self,
                "history.batteryDischargeWh",
                const.STREAM_HISTORY_BATTERY_DISCHARGE_TODAY,
            )
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:battery-arrow-down")
            .attr("history.batteryDischargeWh.beginTime", "Begin Time", "")
            .attr("history.batteryDischargeWh.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            # Battery cumulative charge/discharge (Wh)
            EnergySensorEntity(
                client,
                self,
                "history.batteryChargeWhCumulative",
                const.STREAM_HISTORY_BATTERY_CHARGE_CUMULATIVE,
            )
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:battery-arrow-up")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.batteryChargeWhCumulative.beginTime", "Begin Time", "")
            .attr("history.batteryChargeWhCumulative.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            EnergySensorEntity(
                client,
                self,
                "history.batteryDischargeWhCumulative",
                const.STREAM_HISTORY_BATTERY_DISCHARGE_CUMULATIVE,
            )
            .with_unit_of_measurement("Wh")
            .with_icon("mdi:battery-arrow-down")
            .with_state_class(SensorStateClass.TOTAL_INCREASING)
            .attr("history.batteryDischargeWhCumulative.beginTime", "Begin Time", "")
            .attr("history.batteryDischargeWhCumulative.endTime", "End Time", "")
            .attr("history.mainSn", "Main Device SN", ""),
            _HistoricalDataStatus(client, self),
        ]
    # moduleWifiRssi
    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
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

    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
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
                "params": {"cfgEnergyStrategyOperateMode": {"operateSelfPoweredOpen":value}},
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
                    "params": {"cfgEnergyStrategyOperateMode": {"operateIntelligentScheduleModeOpen":value}},
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

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return []

    def _prepare_data(self, raw_data) -> dict[str, any]:
        res = super()._prepare_data(raw_data)
        res = to_plain(res)
        return res

    def _status_sensor(self, client: EcoflowApiClient) -> StatusSensorEntity:
        # Status entity shows online/offline; use a connectivity icon
        return StatusSensorEntity(client, self).with_icon("mdi:lan-connect")

class DynamicCurrencySensorEntity(BaseSensorEntity):
    def __init__(self, client: EcoflowApiClient, device: BaseDevice, key: str, name: str, unit_param_key: str):
        super().__init__(client, device, key, name)
        self._unit_param_key = unit_param_key
        # For now, fix currency to euros; attribute will expose actual symbol
        self.with_unit_of_measurement("€")

    def _actualize_status(self) -> bool:
        # No dynamic unit updates; rely on fixed unit and attribute for symbol
        return super()._actualize_status()


