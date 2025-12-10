from homeassistant.helpers.entity import EntityCategory

from ...api import EcoflowApiClient
from ...entities import (
    BaseNumberEntity,
    BaseSelectEntity,
    BaseSensorEntity,
    BaseSwitchEntity,
)
from ...number import (
    MaxBatteryLevelEntity,
    MinBatteryLevelEntity,
)
from ...sensor import (
    LevelSensorEntity,
    MiscBinarySensorEntity,
    RemainSensorEntity,
    TempSensorEntity,
    InWattsSensorEntity,
    OutWattsSensorEntity,
    InEnergySensorEntity,
    OutEnergySensorEntity,
)
from ...switch import EnabledEntity
from .. import BaseDevice, const


class SmartHomePanel(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [
            MiscBinarySensorEntity(client, self, "heartbeat.gridSta", const.POWER_GRID)
                .with_icon("mdi:transmission-tower"),

            LevelSensorEntity(client, self, "heartbeat.backupBatPer", const.COMBINED_BATTERY_LEVEL)
                .attr("heartbeat.energyInfos[0].batteryPercentage", const.MAIN_BATTERY_LEVEL, 0),
            RemainSensorEntity(client, self, "heartbeat.backupChaTime", const.REMAINING_TIME)
                .attr("heartbeat.energyInfos[0].chargeTime", const.MAIN_CHARGE_REMAINING_TIME, 0)
                .attr("heartbeat.energyInfos[0].dischargeTime", const.MAIN_DISCHARGE_REMAINING_TIME, 0),

            TempSensorEntity(client, self, "heartbeat.energyInfos[0].emsBatTemp", const.MAIN_BATTERY_TEMP),
            InWattsSensorEntity(client, self, "heartbeat.energyInfos[0].lcdInputWatts", const.MAIN_BATTERY_IN_POWER)
                .with_energy().with_icon("mdi:transmission-tower"),
            OutWattsSensorEntity(client, self, "heartbeat.energyInfos[0].outputPower", const.MAIN_BATTERY_OUT_POWER)
                .with_energy().with_icon("mdi:home-battery"),
            InEnergySensorEntity(client, self, "heartbeat.gridDayWatth", const.POWER_GRID_TODAY),
            OutEnergySensorEntity(client, self, "heartbeat.backupDayWatth", const.BATTERY_TODAY),
        ]

    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return [
            MinBatteryLevelEntity(
                client, self, "'backupChaDiscCfg.discLower'", const.MIN_DISCHARGE_LEVEL, 0, 30,
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
                client, self, "'backupChaDiscCfg.forceChargeHigh'", const.MAX_CHARGE_LEVEL, 50, 100,
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
        ]

    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        return [
            EnabledEntity(
                client, self, "'epsModeInfo.eps'", const.EPS_MODE,
                lambda value: {
                    "operateType": "TCP",
                    "params": {"cmdSet": 11, "id": 24, "eps": int(value)},
                },
            ).with_category(EntityCategory.CONFIG).with_icon("mdi:power-plug-battery"),
            EnabledEntity(
                client, self, "heartbeat.backupCmdChCtrlInfos[0].ctrlSta", const.MAIN_BATTERY_CHARGE,
                lambda value: {
                    "operateType": "TCP",
                    "params": {
                        "cmdSet": 11,
                        "id": 17,
                        "sta": 2 if value else 0,
                        "ctrlMode": 1 if value else 0,
                        "ch": 10
                    },
                },
                enableValue=2,
                disableValue=0,
            ).with_category(EntityCategory.CONFIG).with_icon("mdi:battery-charging"),
        ]

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return []

    def flat_json(self):
        return False
