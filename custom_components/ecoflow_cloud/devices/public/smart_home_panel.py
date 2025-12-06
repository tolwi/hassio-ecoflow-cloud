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
    WattsSensorEntity,
)
from ...switch import EnabledEntity
from .. import BaseDevice, const


class SmartHomePanel(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [
            # Grid/Power Monitoring
            MiscBinarySensorEntity(client, self, "heartbeat.gridSta", "Power Grid"),

            # Battery/Backup Monitoring
            LevelSensorEntity(client, self, "heartbeat.backupBatPer", const.COMBINED_BATTERY_LEVEL),
            RemainSensorEntity(client, self, "heartbeat.backupChaTime", const.DISCHARGE_REMAINING_TIME),

            # First battery Monitoring
            LevelSensorEntity(client, self, "heartbeat.energyInfos[0].batteryPercentage", const.MAIN_BATTERY_LEVEL),
            RemainSensorEntity(client, self, "heartbeat.energyInfos[0].chargeTime", "Main Charge Remaining Time"),
            RemainSensorEntity(client, self, "heartbeat.energyInfos[0].dischargeTime", "Main Discharge Remaining Time"),
            TempSensorEntity(client, self, "heartbeat.energyInfos[0].emsBatTemp", "Main Battery Temperature"),
            WattsSensorEntity(client, self, "heartbeat.energyInfos[0].outputPower", "Main Battery Output Power"),
        ]

    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return [
            MinBatteryLevelEntity(
                client,
                self,
                "'backupChaDiscCfg.discLower'",
                "Backup Discharge Lower Limit",
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
                "Backup Force Charge High Limit",
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

    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        entity = EnabledEntity(
            client, self, "'epsModeInfo.eps'", "EPS Mode",
            lambda value: {
                "operateType": "TCP",
                "params": {"cmdSet": 11, "id": 24, "eps": int(value) },
            },
        )
        entity._attr_entity_category = EntityCategory.CONFIG
        entity._attr_icon = "mdi:power-plug-battery"
        return [entity]

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return []

    def flat_json(self):
        return False

    def _prepare_data(self, raw_data) -> dict[str, any]:
        res = super()._prepare_data(raw_data)
        new_params = {}

        def flatten_dict(d, parent_key=''):
            items = {}
            for k, v in d.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                items[new_key] = v
                if isinstance(v, dict):
                    items.update(flatten_dict(v, new_key))
            return items

        if "params" in res:
            new_params = flatten_dict(res["params"])

        for k, v in res.items():
            if k != "params":
                new_params[k] = v

        return {"params": new_params, "raw_data": res}
