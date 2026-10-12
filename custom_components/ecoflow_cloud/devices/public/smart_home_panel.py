import asyncio
import json
import logging
import threading
from datetime import datetime

import jsonpath_ng.ext as jp
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.button import ButtonEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.binary_sensor import MiscBinarySensorEntity
from custom_components.ecoflow_cloud.button import EnabledButtonEntity
from custom_components.ecoflow_cloud.device_data import DeviceData
from custom_components.ecoflow_cloud.devices import BaseDevice, EcoflowDeviceInfo, const
from custom_components.ecoflow_cloud.devices.data_holder import PreparedData
from custom_components.ecoflow_cloud.entities import EcoFlowDictEntity
from custom_components.ecoflow_cloud.number import (
    ChargingPowerEntity,
    MaxBatteryLevelEntity,
    MinBatteryLevelEntity,
)
from custom_components.ecoflow_cloud.select import DictSelectEntity
from custom_components.ecoflow_cloud.sensor import (
    InEnergySensorEntity,
    InWattsSensorEntity,
    LevelSensorEntity,
    OutEnergySensorEntity,
    OutWattsSensorEntity,
    QuotaStatusSensorEntity,
    RemainSensorEntity,
    TempSensorEntity,
    VoltSensorEntity,
    FrequencySensorEntity,
    AmpSensorEntity,
    WattsSensorEntity,
)
from custom_components.ecoflow_cloud.switch import EnabledEntity

_LOGGER = logging.getLogger(__name__)


class ScheduledChargeChStaSelectEntity(DictSelectEntity):
    def _update_value(self, val) -> bool:
        if isinstance(val, list):
            default = SmartHomePanel.SCHEDULED_CHARGE_CH_STA_DEFAULT
            list_value = val if val in const.SCHEDULED_CHARGE_BATTERY_OPTIONS.values() else default
            return super()._update_value(list_value)
        return super()._update_value(val)


class CircuitModeSelectEntity(DictSelectEntity):
    """Select entity for circuit mode control (Auto/Grid/Battery/Off)."""

    def __init__(self, client: EcoflowApiClient, device: BaseDevice, ch_index: int) -> None:
        self._ch = ch_index
        key = f"heartbeat.loadCmdChCtrlInfos[{ch_index}].ctrlSta"
        title = f"Circuit {ch_index + 1} Mode"
        options = {"Auto": 0, "Grid": 0, "Battery": 1, "Off": 2}
        super().__init__(client, device, key, title, options, command=None)
        self._ctrl_mode_expr = jp.parse(
            self._adopt_json_key(f"heartbeat.loadCmdChCtrlInfos[{ch_index}].ctrlMode")
        )

    def _update_value(self, val):
        try:
            params = self._device.data.params
            mode_vals = self._ctrl_mode_expr.find(params)
            ctrl_mode = mode_vals[0].value if len(mode_vals) == 1 else None
            if ctrl_mode == 0:
                self._current_option = "Auto"
                return True
            elif ctrl_mode == 1:
                mapping = {0: "Grid", 1: "Battery", 2: "Off"}
                option = mapping.get(int(val))
                if option is not None:
                    self._current_option = option
                    return True
                return False
            return False
        except Exception:
            return False

    def select_option(self, option: str) -> None:
        if option == "Auto":
            sta, ctrl_mode, target = 0, 0, 0
        elif option == "Grid":
            sta, ctrl_mode, target = 0, 1, 0
        elif option == "Battery":
            sta, ctrl_mode, target = 1, 1, 1
        elif option == "Off":
            sta, ctrl_mode, target = 2, 1, 2
        else:
            return
        command = {
            "moduleType": 0,
            "operateType": "TCP",
            "params": {"sta": sta, "ctrlMode": ctrl_mode, "ch": self._ch, "cmdSet": 11, "id": 16},
        }
        self.send_set_message(target, command)


class AggregatedWattsSensorEntity(WattsSensorEntity):
    """Aggregated watts sensor that computes value from infoList array."""

    def __init__(self, client: EcoflowApiClient, device: BaseDevice, title: str, aggregator, unique_key: str = "infoList"):
        super().__init__(client, device, unique_key, title, enabled=True, auto_enable=True)
        self._aggregator = aggregator

    def _updated(self, data: dict):
        info = data.get("infoList")
        if isinstance(info, list) and len(info) >= 1:
            self._attr_available = True
            try:
                value = int(self._aggregator(info))
            except Exception:
                return
            if self._update_value(value):
                self.schedule_update_ha_state()


class AlternatingChargeAttrsMixin(EcoFlowDictEntity):
    """Port 2 state lives in attributes; the base class writes state only when the port 1 value changes."""

    def _updated(self, data: dict):
        before = dict(self.extra_state_attributes or {})
        super()._updated(data)
        if dict(self.extra_state_attributes or {}) != before:
            self.schedule_update_ha_state()


class AlternatingChargeSwitchEntity(AlternatingChargeAttrsMixin, EnabledEntity):
    """Enables/disables both alternating scheduled-charge tasks (port 1 / port 2) at once."""

    def __init__(self, client: EcoflowApiClient, device: SmartHomePanel, key: str, title: str) -> None:
        # The command builder only documents the port 1 task; turn_on/turn_off send both tasks.
        super().__init__(
            client, device, key, title,
            command=lambda value, params: device._alternating_charge_commands(params, is_enable=value)[0][1],
        )
        self._panel = device

    def turn_on(self, **kwargs) -> None:
        self._panel.send_alternating_charge(self._client, is_enable=1)

    def turn_off(self, **kwargs) -> None:
        self._panel.send_alternating_charge(self._client, is_enable=0)


class AlternatingChargePowerEntity(AlternatingChargeAttrsMixin, ChargingPowerEntity):
    """Charge power shared by both alternating scheduled-charge tasks."""

    def __init__(self, client: EcoflowApiClient, device: SmartHomePanel, key: str, title: str, min_value: int, max_value: int) -> None:
        super().__init__(
            client, device, key, title, min_value, max_value,
            command=lambda value, params: device._alternating_charge_commands(params, charge_watt=value)[0][1],
        )
        self._panel = device

    async def async_set_native_value(self, value: float) -> None:
        self._panel.send_alternating_charge(self._client, charge_watt=int(value))


class AlternatingChargeLevelEntity(AlternatingChargeAttrsMixin, MaxBatteryLevelEntity):
    """Charge limit shared by both alternating scheduled-charge tasks."""

    def __init__(self, client: EcoflowApiClient, device: SmartHomePanel, key: str, title: str, min_value: int, max_value: int) -> None:
        super().__init__(
            client, device, key, title, min_value, max_value,
            command=lambda value, params: device._alternating_charge_commands(params, high_battery=value)[0][1],
        )
        self._panel = device

    async def async_set_native_value(self, value: float) -> None:
        self._panel.send_alternating_charge(self._client, high_battery=int(value))


class SmartHomePanel(BaseDevice):
    # Scheduled charge task slots (cfgIndex) on the panel. The panel has 20 slots
    # (0-19) and streams them round-robin, one per second, as params.timeTask
    # with an "index" field. The EcoFlow app allocates from 0 upwards.
    SCHEDULED_CHARGE_INDEX = 10
    # Alternating charge: two tasks that split every hour between the ports.
    # cfgIndex -> chSta (port 1, port 2)
    ALTERNATING_CHARGE_TASKS = {11: [1, 0], 12: [0, 1]}
    # cfgIndex -> active 10-minute slots within each hour
    ALTERNATING_CHARGE_SLOTS = {11: (0, 1, 2), 12: (3, 4, 5)}
    ALTERNATING_CHARGE_TIME_RANGE = {
        "isCfg": 1,
        "isEnable": 1,
        "timeMode": 0,
        "startTime": {"sec": 0, "min": 0, "week": 1, "hour": 0, "month": 1, "year": 2020, "day": 1},
        "endTime": {"sec": 59, "min": 59, "week": 1, "hour": 23, "month": 1, "year": 2040, "day": 1},
    }
    # The panel answers a cfg command that arrives while it is still applying the
    # previous one with a bare {"ack": 1} and drops it (observed with a 2 s gap;
    # 10 s apart both were applied), so the two task writes are spaced apart.
    ALTERNATING_CHARGE_COMMAND_GAP_SEC = 10.0
    # timeScale: 18 signed bytes = 144 bits = 24h in 10-minute slots, LSB first.
    TIME_SCALE_BYTES = 18
    TIME_SCALE_SLOTS_PER_HOUR = 6

    # Scheduled charge defaults and limits
    SCHEDULED_CHARGE_BATTERY_MIN = 50
    SCHEDULED_CHARGE_BATTERY_MAX = 100
    SCHEDULED_CHARGE_BATTERY_DEFAULT = 100
    SCHEDULED_CHARGE_POWER_MIN = 200
    SCHEDULED_CHARGE_POWER_MAX = 3400
    SCHEDULED_CHARGE_POWER_DEFAULT = 2000
    SCHEDULED_CHARGE_CH_STA_DEFAULT = [1, 1]

    def __init__(self, device_info: EcoflowDeviceInfo, device_data: DeviceData) -> None:
        super().__init__(device_info, device_data)
        self._time_tasks: dict[int, dict] = {}
        self._store: Store[dict] | None = None

    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        sensors = [
            LevelSensorEntity(client, self, "heartbeat.backupBatPer", const.COMBINED_BATTERY_LEVEL),
            LevelSensorEntity(client, self, "heartbeat.energyInfos[0].batteryPercentage", const.BATTERY_N_LEVEL % 1)
            .attr("heartbeat.energyInfos[0].stateBean.isConnect", "Connected", 0)
            .attr("heartbeat.energyInfos[0].stateBean.isEnable", "Enabled", 0)
            .attr("heartbeat.energyInfos[0].stateBean.isGridCharge", "Grid Charging", 0)
            .attr("heartbeat.energyInfos[0].dischargeTime", "Discharge Time (min)", 0)
            .attr("heartbeat.energyInfos[0].chargeTime", "Charge Time (min)", 0)
            .attr("heartbeat.energyInfos[0].outputPower", "Output Power (W)", 0),
            LevelSensorEntity(client, self, "heartbeat.energyInfos[1].batteryPercentage", const.BATTERY_N_LEVEL % 2, False)
            .attr("heartbeat.energyInfos[1].stateBean.isConnect", "Connected", 0)
            .attr("heartbeat.energyInfos[1].stateBean.isEnable", "Enabled", 0)
            .attr("heartbeat.energyInfos[1].stateBean.isGridCharge", "Grid Charging", 0)
            .attr("heartbeat.energyInfos[1].dischargeTime", "Discharge Time (min)", 0)
            .attr("heartbeat.energyInfos[1].chargeTime", "Charge Time (min)", 0)
            .attr("heartbeat.energyInfos[1].outputPower", "Output Power (W)", 0),
            RemainSensorEntity(client, self, "heartbeat.backupChaTime", const.REMAINING_TIME),
            RemainSensorEntity(client, self, "heartbeat.energyInfos[0].chargeTime", const.BATTERY_N_CHARGE_REMAINING_TIME % 1, False),
            RemainSensorEntity(client, self, "heartbeat.energyInfos[1].chargeTime", const.BATTERY_N_CHARGE_REMAINING_TIME % 2, False),
            RemainSensorEntity(client, self, "heartbeat.energyInfos[0].dischargeTime", const.BATTERY_N_DISCHARGE_REMAINING_TIME % 1, False),
            RemainSensorEntity(client, self, "heartbeat.energyInfos[1].dischargeTime", const.BATTERY_N_DISCHARGE_REMAINING_TIME % 2, False),
            TempSensorEntity(client, self, "heartbeat.energyInfos[0].emsBatTemp", const.BATTERY_N_TEMP % 1),
            TempSensorEntity(client, self, "heartbeat.energyInfos[1].emsBatTemp", const.BATTERY_N_TEMP % 2, False),
            InWattsSensorEntity(client, self, "heartbeat.energyInfos[0].lcdInputWatts", const.BATTERY_N_IN_POWER % 1)
            .with_energy().with_icon("mdi:transmission-tower"),
            InWattsSensorEntity(client, self, "heartbeat.energyInfos[1].lcdInputWatts", const.BATTERY_N_IN_POWER % 2, False)
            .with_energy().with_icon("mdi:transmission-tower"),
            OutWattsSensorEntity(client, self, "heartbeat.energyInfos[0].outputPower", const.BATTERY_N_OUT_POWER % 1)
            .with_energy().with_icon("mdi:home-battery"),
            OutWattsSensorEntity(client, self, "heartbeat.energyInfos[1].outputPower", const.BATTERY_N_OUT_POWER % 2, False)
            .with_energy().with_icon("mdi:home-battery"),
            InEnergySensorEntity(client, self, "heartbeat.gridDayWatth", const.POWER_GRID_TODAY),
            OutEnergySensorEntity(client, self, "heartbeat.backupDayWatth", const.BATTERY_TODAY),
            VoltSensorEntity(client, self, "'gridInfo.gridVol'", const.POWER_GRID_VOLTAGE, diagnostic=True),
            FrequencySensorEntity(client, self, "'gridInfo.gridFreq'", const.POWER_GRID_FREQUENCY, diagnostic=True),
            *[
                AmpSensorEntity(client, self, f"'loadChCurInfo.cur'[{x+10}]", const.BATTERY_N_CURRENT % (x+1), False, diagnostic=True)
                for x in range(2)
            ],
            *[
                AmpSensorEntity(client, self, f"'loadChCurInfo.cur'[{x}]", const.CIRCUIT_N_CURRENT % (x+1), False, diagnostic=True)
                for x in range(10)
            ],
        ]

        # Circuit/Breaker power sensors (10 circuits)
        for i in range(10):
            sensors.append(
                OutWattsSensorEntity(client, self, f"'infoList'[{i}].chWatt", const.BREAKER_N_POWER % (i + 1))
                .with_energy()
                .attr(f"'infoList'[{i}].powType", "Power Source (0=Grid,1=Battery)", 0)
                .attr(f"heartbeat.loadCmdChCtrlInfos[{i}].ctrlSta", "Circuit State", 0)
                .attr(f"heartbeat.loadCmdChCtrlInfos[{i}].ctrlMode", "Control Mode (0=Auto,1=Manual)", 0)
            )

        # Per-circuit Battery/Grid power sensors
        for i in range(10):
            sensors.append(
                AggregatedWattsSensorEntity(
                    client, self, f"Breaker {i + 1} Battery Power",
                    lambda info, idx=i: float(info[idx].get("chWatt", 0)) if (idx < len(info) and int(info[idx].get("powType", 0)) == 1) else 0.0,
                    unique_key=f"infoList.breaker{i + 1}.battery",
                ).with_energy()
            )
            sensors.append(
                AggregatedWattsSensorEntity(
                    client, self, f"Breaker {i + 1} Grid Power",
                    lambda info, idx=i: float(info[idx].get("chWatt", 0)) if (idx < len(info) and int(info[idx].get("powType", 0)) == 0) else 0.0,
                    unique_key=f"infoList.breaker{i + 1}.grid",
                ).with_energy()
            )

        # Battery power at indices 10, 11. On the battery ports powType is the
        # flow direction, not the circuits' grid/battery source.
        sensors.append(
            WattsSensorEntity(client, self, "'infoList'[10].chWatt", const.BATTERY_N_POWER % 1)
            .with_energy().attr("'infoList'[10].powType", "Direction (0=Idle,1=Discharging,2=Charging)", 0)
        )
        sensors.append(
            WattsSensorEntity(client, self, "'infoList'[11].chWatt", const.BATTERY_N_POWER % 2)
            .with_energy().attr("'infoList'[11].powType", "Direction (0=Idle,1=Discharging,2=Charging)", 0)
        )

        # Aggregated power sensors
        sensors.append(
            AggregatedWattsSensorEntity(
                client, self, "Circuits Combined Power",
                lambda info: sum(float(item.get("chWatt", 0)) for item in info[:10]),
                unique_key="infoList.total_circuits",
            ).with_energy()
        )
        sensors.append(
            AggregatedWattsSensorEntity(
                client, self, "Circuits Battery Demand Power",
                lambda info: sum(float(item.get("chWatt", 0)) for item in info[:10] if int(item.get("powType", 0)) == 1),
                unique_key="infoList.total_circuits_battery",
            ).with_energy()
        )
        sensors.append(
            AggregatedWattsSensorEntity(
                client, self, "Circuits Grid Demand Power",
                lambda info: sum(float(item.get("chWatt", 0)) for item in info[:10] if int(item.get("powType", 0)) == 0),
                unique_key="infoList.total_circuits_grid",
            ).with_energy()
        )
        sensors.append(
            AggregatedWattsSensorEntity(
                client, self, "Battery Combined Power",
                lambda info: sum(float(info[i].get("chWatt", 0)) for i in (10, 11) if i < len(info)),
                unique_key="infoList.total_battery_combined",
            ).with_energy()
        )

        # Status sensor
        sensors.append(QuotaStatusSensorEntity(client, self))

        return sensors

    def binary_sensors(self, client: EcoflowApiClient) -> list[BinarySensorEntity]:
        return [
            MiscBinarySensorEntity(client, self, "heartbeat.gridSta", const.POWER_GRID)
            .with_icon("mdi:transmission-tower"),
        ]

    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return [
            MinBatteryLevelEntity(
                client,
                self,
                "'backupChaDiscCfg.discLower'",
                const.MIN_DISCHARGE_LEVEL,
                0,
                30,
                lambda value, params: {
                    "operateType": "TCP",
                    "params": {
                        "cmdSet": 11,
                        "id": 29,
                        "discLower": value,
                        "forceChargeHigh": int(params.get("heartbeat.backupChaDiscCfg.forceChargeHigh", 100)),
                    },
                },
            ),
            MaxBatteryLevelEntity(
                client,
                self,
                "'backupChaDiscCfg.forceChargeHigh'",
                const.MAX_CHARGE_LEVEL,
                50,
                100,
                lambda value, params: {
                    "operateType": "TCP",
                    "params": {
                        "cmdSet": 11,
                        "id": 29,
                        "forceChargeHigh": value,
                        "discLower": int(params.get("backupChaDiscCfg.discLower", 0)),
                    },
                },
            ),
            MaxBatteryLevelEntity(
                client,
                self,
                "timeTask.cfg.param.hightBattery",
                const.SCHEDULED_CHARGE_BATTERY_LEVEL,
                self.SCHEDULED_CHARGE_BATTERY_MIN,
                self.SCHEDULED_CHARGE_BATTERY_MAX,
                lambda value, params: self._scheduled_charge_command(params, high_battery=value),
            ),
            ChargingPowerEntity(
                client,
                self,
                "timeTask.cfg.param.chChargeWatt",
                const.SCHEDULED_CHARGE_POWER,
                self.SCHEDULED_CHARGE_POWER_MIN,
                self.SCHEDULED_CHARGE_POWER_MAX,
                lambda value, params: self._scheduled_charge_command(params, charge_watt=value),
            ),
            AlternatingChargeLevelEntity(
                client,
                self,
                "timeTask11.cfg.param.hightBattery",
                const.ALTERNATING_CHARGE_BATTERY_LEVEL,
                self.SCHEDULED_CHARGE_BATTERY_MIN,
                self.SCHEDULED_CHARGE_BATTERY_MAX,
            ).attr("timeTask12.cfg.param.hightBattery", "Port 2 task level", 0),
            AlternatingChargePowerEntity(
                client,
                self,
                "timeTask11.cfg.param.chChargeWatt",
                const.ALTERNATING_CHARGE_POWER,
                self.SCHEDULED_CHARGE_POWER_MIN,
                self.SCHEDULED_CHARGE_POWER_MAX,
            ).attr("timeTask12.cfg.param.chChargeWatt", "Port 2 task power", 0),
        ]

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return [
            EnabledEntity(
                client,
                self,
                "'epsModeInfo.eps'",
                const.EPS_MODE,
                lambda value: {
                    "operateType": "TCP",
                    "params": {"cmdSet": 11, "id": 24, "eps": int(value)},
                },
            )
            .with_category(EntityCategory.CONFIG)
            .with_icon("mdi:power-plug-battery"),
            EnabledEntity(
                client,
                self,
                "timeTask.cfg.comCfg.isEnable",
                const.SCHEDULED_CHARGE,
                lambda value, params: self._scheduled_charge_enable_command(params, int(value)),
            )
            .with_category(EntityCategory.CONFIG)
            .with_icon("mdi:battery-clock"),
            AlternatingChargeSwitchEntity(client, self, "timeTask11.cfg.comCfg.isEnable", const.ALTERNATING_CHARGE)
            .attr("timeTask12.cfg.comCfg.isEnable", "Port 2 task enabled", 0)
            .attr("timeTask11.cfg.comCfg.isCfg", "Port 1 task configured", 0)
            .attr("timeTask12.cfg.comCfg.isCfg", "Port 2 task configured", 0)
            .with_category(EntityCategory.CONFIG)
            .with_icon("mdi:battery-sync"),
            self._batteryChargeSwitch(client, 1, True),
            self._batteryChargeSwitch(client, 2, False),
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return [
            *[CircuitModeSelectEntity(client, self, i) for i in range(10)],
            ScheduledChargeChStaSelectEntity(
                client,
                self,
                "timeTask.cfg.param.chSta",
                const.SCHEDULED_CHARGE_BATTERY,
                const.SCHEDULED_CHARGE_BATTERY_OPTIONS,
                lambda value, params: self._scheduled_charge_command(params, ch_sta=value),
            ),
        ]

    def buttons(self, client: EcoflowApiClient) -> list[ButtonEntity]:
        return [
            EnabledButtonEntity(
                client, self, "'rtcUpdate'", "Update Real-Time Clock",
                lambda value: {
                    "moduleType": 0, "operateType": "TCP",
                    "params": {
                        "cmdSet": 11, "id": 3,
                        "week": datetime.now().isoweekday(), "sec": datetime.now().second,
                        "min": datetime.now().minute, "hour": datetime.now().hour,
                        "day": datetime.now().day, "month": datetime.now().month, "year": datetime.now().year,
                    },
                },
                enabled=False,
            ),
        ]

    def flat_json(self):
        return False

    def configure(self, hass: HomeAssistant):
        super().configure(hass)
        self._hass = hass
        self._store = Store(hass, 1, f"ecoflow_cloud.{self.device_info.sn}.timetask")

    @classmethod
    def _time_task_key(cls, index: int) -> str:
        return f"timeTask{index}"

    async def async_restore_state(self):
        if self._store is None:
            return
        data = await self._store.async_load()
        if not data:
            return
        tasks = data.get("timeTasks")
        if isinstance(tasks, dict):
            for key, task in tasks.items():
                if isinstance(task, dict):
                    self._time_tasks[int(key)] = task
        elif isinstance(data.get("timeTask"), dict):
            # Legacy single-task store (last reported task, whatever its index).
            task = data["timeTask"]
            self._time_tasks[int(task.get("index", self.SCHEDULED_CHARGE_INDEX))] = task
        for index, task in self._time_tasks.items():
            self.data.params[self._time_task_key(index)] = task
            if index == self.SCHEDULED_CHARGE_INDEX:
                self.data.params["timeTask"] = task

    def update_data(self, raw_data: bytes, data_type: str) -> bool:
        if data_type in (self.device_info.set_topic, self.device_info.set_reply_topic) and _LOGGER.isEnabledFor(logging.DEBUG):
            _LOGGER.debug("%s: %s", "set" if data_type == self.device_info.set_topic else "set_reply", raw_data.decode("utf-8", errors="ignore"))
        return super().update_data(raw_data, data_type)

    def _prepare_data_data_topic(self, raw_data: bytes) -> PreparedData:
        data = self._prepare_data(raw_data)
        self._absorb_time_task(data)
        return PreparedData(None, data, data)

    def _absorb_time_task(self, data: dict) -> None:
        """Re-key the round-robin timeTask report by its slot index.

        The panel streams all 20 task slots one per second under the same
        params.timeTask key, so a plain params.update() would make every
        timeTask entity flap between slots. Each report is stored under
        timeTask<index>; the legacy timeTask key is kept only for the
        integration's own slot so existing entity keys stay valid.
        """
        try:
            params = data.get("params") if isinstance(data, dict) else None
            if not isinstance(params, dict):
                return
            task = params.get("timeTask")
            if not isinstance(task, dict) or "index" not in task:
                return
            index = int(task["index"])
            params[self._time_task_key(index)] = task
            if index != self.SCHEDULED_CHARGE_INDEX:
                del params["timeTask"]
            if self._time_tasks.get(index) != task:
                self._time_tasks[index] = task
                _LOGGER.debug("timeTask[%s] changed: %s", index, json.dumps(task, separators=(",", ":")))
                self._save_time_tasks()
        except Exception:
            _LOGGER.exception("Failed to process timeTask report")

    def _save_time_tasks(self) -> None:
        if self._store is None or self._hass.is_stopping or not self._hass.loop.is_running():
            # Reports still arrive on the MQTT thread while HA shuts down; a coroutine
            # scheduled onto a closing loop would only raise "never awaited".
            return
        snapshot = {"timeTasks": {str(k): v for k, v in self._time_tasks.items()}}
        asyncio.run_coroutine_threadsafe(self._store.async_save(snapshot), self._hass.loop)

    @classmethod
    def _time_scale(cls, slots_in_hour: tuple[int, ...]) -> list[int]:
        """Build a timeScale bitmap: 144 ten-minute slots, 8 per signed byte, LSB first."""
        bits = [0] * (cls.TIME_SCALE_BYTES * 8)
        for hour in range(24):
            for slot in slots_in_hour:
                bits[hour * cls.TIME_SCALE_SLOTS_PER_HOUR + slot] = 1
        result = []
        for byte in range(cls.TIME_SCALE_BYTES):
            value = sum(bits[byte * 8 + bit] << bit for bit in range(8))
            result.append(value - 256 if value > 127 else value)
        return result

    def send_alternating_charge(
        self,
        client: EcoflowApiClient,
        high_battery: int | None = None,
        charge_watt: int | None = None,
        is_enable: int | None = None,
    ) -> None:
        now = dt_util.now()
        set_time = {
            "sec": now.second, "min": now.minute, "hour": now.hour,
            "day": now.day, "month": now.month, "year": now.year, "week": now.isoweekday(),
        }
        commands = self._alternating_charge_commands(
            self.data.params, high_battery=high_battery, charge_watt=charge_watt, is_enable=is_enable, set_time=set_time
        )
        for i, (state, command) in enumerate(commands):
            _LOGGER.debug("alternating charge: cfgIndex %s %s", command["params"]["cfgIndex"], json.dumps(command, separators=(",", ":")))
            if i == 0:
                client.send_set_message(self.device_info.sn, state, command)
            else:
                threading.Timer(
                    i * self.ALTERNATING_CHARGE_COMMAND_GAP_SEC,
                    client.send_set_message,
                    args=(self.device_info.sn, state, command),
                ).start()

    def _alternating_charge_commands(
        self,
        params: dict,
        high_battery: int | None = None,
        charge_watt: int | None = None,
        is_enable: int | None = None,
        set_time: dict | None = None,
    ) -> list[tuple[dict, dict]]:
        """One (optimistic state, command) pair per alternating task; overrides apply to both.

        set_time None uses the builder's fixed default, which keeps the generated docs stable.
        """
        result = []
        for index, ch_sta in self.ALTERNATING_CHARGE_TASKS.items():
            p = self._get_scheduled_charge_params(params, index)
            high = high_battery if high_battery is not None else p["hightBattery"]
            watt = charge_watt if charge_watt is not None else p["chChargeWatt"]
            enable = is_enable if is_enable is not None else p["isEnable"]
            command = self._build_scheduled_charge_command(
                high, max(high - 5, 0), watt, ch_sta, enable,
                cfg_index=index,
                time_scale=self._time_scale(self.ALTERNATING_CHARGE_SLOTS[index]),
                time_range=self.ALTERNATING_CHARGE_TIME_RANGE,
                set_time=set_time,
            )
            key = self._time_task_key(index)
            state = {
                f"{key}.cfg.param.hightBattery": high,
                f"{key}.cfg.param.lowBattery": max(high - 5, 0),
                f"{key}.cfg.param.chChargeWatt": watt,
                f"{key}.cfg.comCfg.isEnable": enable,
            }
            result.append((state, command))
        return result

    @classmethod
    def _get_scheduled_charge_params(cls, params: dict, cfg_index: int = SCHEDULED_CHARGE_INDEX) -> dict:
        """Extract current scheduled charge param values for one task slot (defaults if unconfigured)."""
        time_task = None
        if params:
            time_task = params.get(cls._time_task_key(cfg_index))
            if time_task is None and cfg_index == cls.SCHEDULED_CHARGE_INDEX:
                time_task = params.get("timeTask")
        if not isinstance(time_task, dict):
            time_task = {}
        cfg = time_task.get("cfg", {})
        cfg_param = cfg.get("param", {})
        cfg_com = cfg.get("comCfg", {})
        if int(cfg_com.get("isCfg", 0)) != 1:
            # Empty slot: the panel reports all-zero fields, which must not be preserved.
            cfg_param = {}
            cfg_com = {}

        high = cfg_param.get("hightBattery", cls.SCHEDULED_CHARGE_BATTERY_DEFAULT)
        return {
            "hightBattery": high,
            "lowBattery": cfg_param.get("lowBattery", max(high - 5, 0)),
            "chChargeWatt": cfg_param.get("chChargeWatt", cls.SCHEDULED_CHARGE_POWER_DEFAULT),
            "chSta": cfg_param.get("chSta", cls.SCHEDULED_CHARGE_CH_STA_DEFAULT.copy()),
            "isEnable": cfg_com.get("isEnable", 0),
        }

    @staticmethod
    def _build_scheduled_charge_command(
        high_battery: int,
        low_battery: int,
        charge_watt: int,
        ch_sta: list,
        is_enable: int,
        cfg_index: int = SCHEDULED_CHARGE_INDEX,
        time_scale: list[int] | None = None,
        time_range: dict | None = None,
        set_time: dict | None = None,
    ) -> dict:
        """Build the scheduled charge command structure."""
        if time_range is None:
            time_range = {
                "isCfg": 1,
                "isEnable": 1,
                "timeMode": 0,
                "startTime": {"sec": 0, "min": 0, "week": 1, "hour": 0, "month": 1, "year": 2020, "day": 1},
                "endTime": {"sec": 0, "min": 0, "week": 1, "hour": 0, "month": 1, "year": 2030, "day": 1},
            }
        if set_time is None:
            set_time = {"sec": 0, "min": 0, "week": 1, "hour": 0, "month": 1, "year": 2020, "day": 1}
        return {
            "operateType": "TCP",
            "params": {
                "cfg": {
                    "param": {
                        "lowBattery": low_battery,
                        "hightBattery": high_battery,
                        "chChargeWatt": charge_watt,
                        "chSta": ch_sta,
                    },
                    "comCfg": {
                        "timeScale": list(time_scale) if time_scale is not None else [-1] * 18,
                        "isCfg": 1,
                        "type": 1,
                        "timeRange": dict(time_range),
                        "setTime": dict(set_time),
                        "isEnable": is_enable,
                    },
                },
                "cfgIndex": cfg_index,
                "cmdSet": 11,
                "id": 81,
            },
        }

    def _scheduled_charge_enable_command(self, params: dict, is_enable: int) -> dict:
        """Toggle scheduled charge on/off - preserves all other param values."""
        p = self._get_scheduled_charge_params(params)
        return self._build_scheduled_charge_command(
            p["hightBattery"], p["lowBattery"], p["chChargeWatt"], p["chSta"], is_enable
        )

    def _scheduled_charge_command(
        self,
        params: dict,
        high_battery: int | None = None,
        charge_watt: int | None = None,
        ch_sta: list | None = None,
        is_enable: int | None = None,
    ) -> dict:
        """Update scheduled charge settings - overrides specified values, preserves others."""
        p = self._get_scheduled_charge_params(params)
        return self._build_scheduled_charge_command(
            high_battery if high_battery is not None else p["hightBattery"],
            p["lowBattery"] if high_battery is None else max(high_battery - 5, 0),
            charge_watt if charge_watt is not None else p["chChargeWatt"],
            ch_sta if ch_sta is not None else p["chSta"],
            is_enable if is_enable is not None else p["isEnable"],
        )
    
    def _batteryChargeSwitch(self, client: EcoflowApiClient, index: int, enabled: bool = True) -> SwitchEntity:
        return (
            EnabledEntity(
                client,
                self,
                f"heartbeat.backupCmdChCtrlInfos[{index - 1}].ctrlSta",
                f"{const.BATTERY_N_CHARGE % index}",
                lambda value: {
                    "operateType": "TCP",
                    "params": {
                        "cmdSet": 11,
                        "id": 17,
                        "sta": 2 if value else 0,
                        "ctrlMode": 1 if value else 0,
                        "ch": 9 + index,
                    },
                },
                enabled,
                enableValue=2,
                disableValue=0,
            )
            .with_category(EntityCategory.CONFIG)
            .with_icon("mdi:battery-charging")
        )
