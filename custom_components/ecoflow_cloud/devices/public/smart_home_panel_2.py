from .data_bridge import to_plain
from ...api import EcoflowApiClient
from ...sensor import StatusSensorEntity, WattsSensorEntity, InWattsSensorEntity, LevelSensorEntity, OutWattsSensorEntity, RemainSensorEntity, IntegralEnergySensor
from .. import BaseDevice, const
from ...entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, BaseSelectEntity
from custom_components.ecoflow_cloud.switch import EnabledEntity
from custom_components.ecoflow_cloud.select import DictSelectEntity
from ...number import MaxBatteryLevelEntity, ChargingPowerEntity, MinBatteryLevelEntity

class SmartHomePanel2(BaseDevice):

    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [
            IntegralEnergySensor(InWattsSensorEntity(client, self, "'wattInfo.gridWatt'", const.AC_IN_POWER)),
            IntegralEnergySensor(OutWattsSensorEntity(client, self, "'wattInfo.allHallWatt'", const.AC_OUT_POWER)),
            LevelSensorEntity(client, self, "'backupIncreInfo.backupBatPer'", const.COMBINED_BATTERY_LEVEL),
            RemainSensorEntity(client, self, "'backupInfo.backupDischargeTime'", const.DISCHARGE_REMAINING_TIME),
            self._sensorsSwitch(client, 0),
            self._sensorsSwitch(client, 1),
            self._sensorsSwitch(client, 2),
            self._sensorsSwitch(client, 3),
            self._sensorsSwitch(client, 4),
            self._sensorsSwitch(client, 5),
            self._sensorsSwitch(client, 6),
            self._sensorsSwitch(client, 7),
            self._sensorsSwitch(client, 8),
            self._sensorsSwitch(client, 9),
            self._sensorsSwitch(client, 10),
            self._sensorsSwitch(client, 11),
            self._sensorsBattery(client, 1),
            self._sensorsBattery(client, 2),
            self._sensorsBattery(client, 3),
            self._sensorsBatteryPower(client, 0),
            self._sensorsBatteryPower(client, 1),
            self._sensorsBatteryPower(client, 2),
        ]

    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return [
            MinBatteryLevelEntity(
                client,
                self,
                "'backupReserveSoc'",
                "Backup reserve level",
                10,
                50,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "PD303_APP_SET",
                    "params": {"backupReserveSoc": value}
                },
            ),
            ChargingPowerEntity(
                client,
                self,
                "'chargeWattPower'",
                "Charging power",
                500,
                7200,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "PD303_APP_SET",
                    "params": {"chargeWattPower": value}
                },
            ),
            MaxBatteryLevelEntity(
                client,
                self,
                "'foceChargeHight'",
                "Charging limit",
                80,
                100,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "PD303_APP_SET",
                    "params": {"foceChargeHight": value}
                },
            )
        ]

    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        return [
            EnabledEntity(
                client,
                self,
                "epsModeInfo",
                "EPS Mode",
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "PD303_APP_SET",
                    "params": {"epsModeInfo": value == 1}
                },
            ),
            EnabledEntity(
                client,
                self,
                "stormIsEnable",
                "Storm Guard",
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "PD303_APP_SET",
                    "params": {"stormIsEnable": value == 1}
                },
            ),
        ]

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return [
            self._selectsBatteryStatus(client, 1),
            self._selectsBatteryStatus(client, 2),
            self._selectsBatteryStatus(client, 3),
            self._selectsBatteryForceCharge(client, 1),
            self._selectsBatteryForceCharge(client, 2),
            self._selectsBatteryForceCharge(client, 3),
            DictSelectEntity(
                client,
                self,
                "'smartBackupMode'",
                const.SMART_BACKUP_MODE,
                const.SMART_BACKUP_MODE_OPTIONS,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "PD303_APP_SET",
                    "params": {"smartBackupMode": value}
                },
            )
        ]

    def _selectsBatteryStatus(self, client: EcoflowApiClient, index: int) -> BaseSelectEntity:
        return DictSelectEntity(
            client,
            self,
            f"'ch{index}EnableSet'",
            f"{const.BATTERY_STATUS} {index}",
            const.BATTERY_STATUS_OPTIONS,
            lambda value: {
                "sn": self.device_info.sn,
                "cmdCode": "PD303_APP_SET",
                "params": {f"ch{index}EnableSet": value}
            },
        )

    def _selectsBatteryForceCharge(self, client: EcoflowApiClient, index: int) -> BaseSelectEntity:
        return DictSelectEntity(
            client,
            self,
            f"'ch{index}ForceCharge'",
            f"{const.BATTERY_FORCE_CHARGE} {index}",
            const.BATTERY_FORCE_CHARGE_OPTIONS,
            lambda value: {
                "sn": self.device_info.sn,
                "cmdCode": "PD303_APP_SET",
                "params": {f"ch{index}ForceCharge": value}
            },
        )

    def _sensorsSwitch(self, client: EcoflowApiClient, index: int) -> BaseSensorEntity:
        return IntegralEnergySensor(OutWattsSensorEntity(client, self, f"'loadInfo.hall1Watt'[{index}]", f"Breaker {index + 1} Power"))

    def _sensorsBattery(self, client: EcoflowApiClient, index: int) -> BaseSensorEntity:
        return LevelSensorEntity(client, self, f"'backupIncreInfo.Energy{index}Info.batteryPercentage'", f"Battery {index} Level")

    def _sensorsBatteryPower(self, client: EcoflowApiClient, index: int) -> BaseSensorEntity:
        return WattsSensorEntity(client, self, f"'wattInfo.chWatt'[{index}]", f"Battery {index + 1} Power")

    def flat_json(self):
        return False

    def _prepare_data(self, raw_data) -> dict[str, any]:
        res = super()._prepare_data(raw_data)
        new_params = {}

        if "param" in res:
            for k, v in res["param"].items():
                new_params[f"{k}"] = v

        for k, v in res.items():
            if k != "param" and k != "params":
                new_params[f"{k}"] = v

        new_params2 = {}
        for k, v in new_params.items():
            new_params2[k] = v
            if isinstance(v, dict):
                for k2, v2 in v.items():
                    new_params2[f"{k}.{k2}"] = v2

        return {"params": new_params2, "raw_data": res}
