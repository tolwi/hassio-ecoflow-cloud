from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import EntityCategory

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.binary_sensor import MiscBinarySensorEntity
from custom_components.ecoflow_cloud.devices import BaseDevice, const
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
    RemainSensorEntity,
    TempSensorEntity,
    VoltSensorEntity,
    FrequencySensorEntity,
    AmpSensorEntity,
)
from custom_components.ecoflow_cloud.switch import EnabledEntity


class ScheduledChargeChStaSelectEntity(DictSelectEntity):
    def _update_value(self, val) -> bool:
        if isinstance(val, list):
            default = SmartHomePanel.SCHEDULED_CHARGE_CH_STA_DEFAULT
            list_value = val if val in const.SCHEDULED_CHARGE_BATTERY_OPTIONS.values() else default
            return super()._update_value(list_value)
        return super()._update_value(val)


class SmartHomePanel(BaseDevice):
    # Scheduled charge defaults and limits
    SCHEDULED_CHARGE_BATTERY_MIN = 50
    SCHEDULED_CHARGE_BATTERY_MAX = 100
    SCHEDULED_CHARGE_BATTERY_DEFAULT = 100
    SCHEDULED_CHARGE_POWER_MIN = 200
    SCHEDULED_CHARGE_POWER_MAX = 3400
    SCHEDULED_CHARGE_POWER_DEFAULT = 2000
    SCHEDULED_CHARGE_CH_STA_DEFAULT = [1, 1]

    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            LevelSensorEntity(client, self, "heartbeat.backupBatPer", const.COMBINED_BATTERY_LEVEL),
            LevelSensorEntity(client, self, "heartbeat.energyInfos[0].batteryPercentage", const.BATTERY_N_LEVEL % 1),
            LevelSensorEntity(client, self, "heartbeat.energyInfos[1].batteryPercentage", const.BATTERY_N_LEVEL % 2, False),
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
            self._batteryChargeSwitch(client, 1, True),
            self._batteryChargeSwitch(client, 2, False),
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return [
            ScheduledChargeChStaSelectEntity(
                client,
                self,
                "timeTask.cfg.param.chSta",
                const.SCHEDULED_CHARGE_BATTERY,
                const.SCHEDULED_CHARGE_BATTERY_OPTIONS,
                lambda value, params: self._scheduled_charge_command(params, ch_sta=value),
            ),
        ]

    def flat_json(self):
        return False

    @classmethod
    def _get_scheduled_charge_params(cls, params: dict) -> dict:
        """Extract current scheduled charge param values from timeTask structure."""
        time_task = params.get("timeTask", {}) if params else {}
        cfg = time_task.get("cfg", {})
        cfg_param = cfg.get("param", {})
        cfg_com = cfg.get("comCfg", {})

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
    ) -> dict:
        """Build the scheduled charge command structure."""
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
                        "timeScale": [-1] * 18,
                        "isCfg": 1,
                        "type": 1,
                        "timeRange": {
                            "isCfg": 1,
                            "isEnable": 1,
                            "timeMode": 0,
                            "startTime": {"sec": 0, "min": 0, "week": 1, "hour": 0, "month": 1, "year": 2020, "day": 1},
                            "endTime": {"sec": 0, "min": 0, "week": 1, "hour": 0, "month": 1, "year": 2030, "day": 1},
                        },
                        "setTime": {"sec": 0, "min": 0, "week": 1, "hour": 0, "month": 1, "year": 2020, "day": 1},
                        "isEnable": is_enable,
                    },
                },
                "cfgIndex": 10,
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
