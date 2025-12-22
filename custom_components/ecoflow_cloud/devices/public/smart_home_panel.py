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
    MaxBatteryLevelEntity,
    MinBatteryLevelEntity,
)
from custom_components.ecoflow_cloud.sensor import (
    InEnergySensorEntity,
    InWattsSensorEntity,
    LevelSensorEntity,
    OutEnergySensorEntity,
    OutWattsSensorEntity,
    RemainSensorEntity,
    TempSensorEntity,
)
from custom_components.ecoflow_cloud.switch import EnabledEntity


class SmartHomePanel(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            LevelSensorEntity(client, self, "heartbeat.backupBatPer", const.COMBINED_BATTERY_LEVEL).attr(
                "heartbeat.energyInfos[0].batteryPercentage", const.MAIN_BATTERY_LEVEL, 0
            ),
            RemainSensorEntity(client, self, "heartbeat.backupChaTime", const.REMAINING_TIME)
            .attr("heartbeat.energyInfos[0].chargeTime", const.MAIN_CHARGE_REMAINING_TIME, 0)
            .attr("heartbeat.energyInfos[0].dischargeTime", const.MAIN_DISCHARGE_REMAINING_TIME, 0),
            TempSensorEntity(client, self, "heartbeat.energyInfos[0].emsBatTemp", const.MAIN_BATTERY_TEMP),
            InWattsSensorEntity(client, self, "heartbeat.energyInfos[0].lcdInputWatts", const.MAIN_BATTERY_IN_POWER)
            .with_energy()
            .with_icon("mdi:transmission-tower"),
            OutWattsSensorEntity(client, self, "heartbeat.energyInfos[0].outputPower", const.MAIN_BATTERY_OUT_POWER)
            .with_energy()
            .with_icon("mdi:home-battery"),
            InEnergySensorEntity(client, self, "heartbeat.gridDayWatth", const.POWER_GRID_TODAY),
            OutEnergySensorEntity(client, self, "heartbeat.backupDayWatth", const.BATTERY_TODAY),
        ]

    def binary_sensors(self, client: EcoflowApiClient) -> list[BinarySensorEntity]:
        return [
            MiscBinarySensorEntity(client, self, "heartbeat.gridSta", const.POWER_GRID).with_icon(
                "mdi:transmission-tower"
            ),
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
                "heartbeat.backupCmdChCtrlInfos[0].ctrlSta",
                const.MAIN_BATTERY_CHARGE,
                lambda value: {
                    "operateType": "TCP",
                    "params": {
                        "cmdSet": 11,
                        "id": 17,
                        "sta": 2 if value else 0,
                        "ctrlMode": 1 if value else 0,
                        "ch": 10,
                    },
                },
                enableValue=2,
                disableValue=0,
            )
            .with_category(EntityCategory.CONFIG)
            .with_icon("mdi:battery-charging"),
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return []

    def flat_json(self):
        return False
