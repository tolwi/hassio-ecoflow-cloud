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
    VoltSensorEntity,
    FrequencySensorEntity,
    AmpSensorEntity,
)
from custom_components.ecoflow_cloud.switch import EnabledEntity


class SmartHomePanel(BaseDevice):
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
            self._batteryChargeSwitch(client, 1, True),
            self._batteryChargeSwitch(client, 2, False),
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return []

    def flat_json(self):
        return False
    
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
