import logging

from homeassistant.helpers.entity import EntityCategory
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import UnitOfPower

from custom_components.ecoflow_cloud.select import DictSelectEntity
from custom_components.ecoflow_cloud.switch import EnabledEntity

from ...api import EcoflowApiClient
from ...entities import (
    BaseNumberEntity,
    BaseSelectEntity,
    BaseSensorEntity,
    BaseSwitchEntity,
)
from ...number import (
    ChargingPowerEntity,
    MaxBatteryLevelEntity,
    MinBatteryLevelEntity,
    ValueUpdateEntity,
)
from ...sensor import (
    CyclesSensorEntity,
    InWattsSensorEntity,
    LevelSensorEntity,
    MiscBinarySensorEntity,
    OutWattsSensorEntity,
    QuotaScheduledStatusSensorEntity,
    RemainSensorEntity,
    VoltSensorEntity,
    WattsSensorEntity,
)
from .. import BaseDevice, const

_LOGGER = logging.getLogger(__name__)


class SmartHomePanel2(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        # Find all split-phase circuits
        circuits = []
        for x in range(1, 13):
            name: str = self.data.params.get(
                f"pd303_mc.loadIncreInfo.hall1IncreInfo.ch{x}Info.chName",
                "Breaker" + str(x),
            )
            is_split: bool = self.data.params.get(
                f"pd303_mc.loadIncreInfo.hall1IncreInfo.ch{x}Info.splitphase.linkMark",
                False,
            )
            split_reference: int = self.data.params.get(
                f"pd303_mc.loadIncreInfo.hall1IncreInfo.ch{x}Info.splitphase.linkCh", 0
            )

            if is_split:
                if x < split_reference:  # The first of the split pair
                    # Add our combined split circuit
                    circuits.append(self._sensorsCircuit(client, x, name, True, True))
                else:  # The second of the split pair
                    name = self.data.params.get(
                        f"pd303_mc.loadIncreInfo.hall1IncreInfo.ch{split_reference}Info.chName",
                        "Breaker " + str(split_reference),
                    )
                name = f"{name} (circuit {x})"
            # Add normal circuits and the individual split circuits. We don't auto_enable individual split circuits
            circuits.append(self._sensorsCircuit(client, x, name, False, not is_split))
        return [
            QuotaScheduledStatusSensorEntity(
                client, self, 60
            ),  # Refresh Quota All every 60 seconds so settings changed in app are reflected here
            InWattsSensorEntity(
                client, self, "'wattInfo.gridWatt'", const.AC_IN_POWER
            ).with_energy(),
            OutWattsSensorEntity(
                client, self, "'wattInfo.allHallWatt'", const.AC_OUT_POWER
            ).with_energy(),
            LevelSensorEntity(
                client,
                self,
                "'backupIncreInfo.backupBatPer'",
                const.COMBINED_BATTERY_LEVEL,
            ),
            RemainSensorEntity(
                client,
                self,
                "'backupInfo.backupDischargeTime'",
                const.DISCHARGE_REMAINING_TIME,
            ),
            MiscBinarySensorEntity(
                client, self, "'pd303_mc.masterIncreInfo.gridSta'", const.POWER_GRID
            ).with_icon("mdi:transmission-tower-off"),
            VoltSensorEntity(
                client,
                self,
                "'pd303_mc.masterIncreInfo.gridVol'",
                const.POWER_GRID_VOLTAGE,
                False,
            ),
            MiscBinarySensorEntity(
                client, self, "'pd303_mc.inStormMode'", const.IN_STORM_MODE
            ).with_icon("mdi:flash-alert"),
            *[
                CyclesSensorEntity(
                    client,
                    self,
                    f"'pd303_mc.masterIncreInfo.masterRly{x}Cnt'",
                    const.RELAY_N_OPERATION_COUNT % x,
                    False,
                ).with_icon("mdi:cog-clockwise")
                for x in range(1, 5)
            ],
            *[
                self._sensorsBattery(
                    client,
                    x,
                    self.data.params.get(
                        f"pd303_mc.backupIncreInfo.ch{x}Info.backupIsReady", False
                    ),
                )
                for x in range(1, 4)
            ],
            *[
                self._sensorsBatteryPower(
                    client,
                    x,
                    self.data.params.get(
                        f"pd303_mc.backupIncreInfo.ch{x}Info.backupIsReady", False
                    ),
                )
                for x in range(1, 4)
            ],
            *circuits,
        ]

    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return [
            MinBatteryLevelEntity(
                client,
                self,
                "'backupReserveSoc'",
                const.BACKUP_RESERVE_LEVEL,
                10,
                50,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "PD303_APP_SET",
                    "params": {"backupReserveSoc": value},
                },
            ),
            ChargingPowerEntity(
                client,
                self,
                "'chargeWattPower'",
                const.AC_CHARGING_POWER,
                500,
                7200,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "PD303_APP_SET",
                    "params": {"chargeWattPower": value},
                },
            ),
            MaxBatteryLevelEntity(
                client,
                self,
                "'foceChargeHight'",
                const.MAX_CHARGE_LEVEL,
                80,
                100,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "PD303_APP_SET",
                    "params": {"foceChargeHight": value},
                },
            ),
            ChargingPowerEntity(
                client,
                self,
                "'pd303_mc.oilEngineWatt'",
                const.GEN_BAT_CHARGING_POWER,
                500,
                3000,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "PD303_APP_SET",
                    "params": {"oilEngineWatt": value},
                },
            ).with_icon("mdi:generator-mobile"),
            ValueUpdateEntity(
                client,
                self,
                "'oilMaxOutputWatt'",
                const.GEN_MAX_OUTPUT_POWER,
                3000,
                12000,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "PD303_APP_SET",
                    "params": {"oilMaxOutputWatt": value},
                },
            )
            .with_device_class(SensorDeviceClass.POWER)
            .with_unit_of_measurement(UnitOfPower.WATT)
            .with_icon("mdi:generator-mobile"),
        ]

    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        # Find all split-phase circuits
        circuits = []
        for x in range(1, 13):
            name: str = self.data.params.get(
                f"pd303_mc.loadIncreInfo.hall1IncreInfo.ch{x}Info.chName",
                "Breaker " + str(x),
            )
            is_split: bool = self.data.params.get(
                f"pd303_mc.loadIncreInfo.hall1IncreInfo.ch{x}Info.splitphase.linkMark",
                False,
            )
            split_reference: int = self.data.params.get(
                f"pd303_mc.loadIncreInfo.hall1IncreInfo.ch{x}Info.splitphase.linkCh", 0
            )

            if not is_split or x < split_reference:
                circuits.append(self._switchesCircuits(client, x, name, is_split))

        return [
            EnabledEntity(
                client,
                self,
                "epsModeInfo",
                "EPS Mode",
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "PD303_APP_SET",
                    "params": {
                        "epsModeInfo": value == 1,
                        "smartBackupMode": 0,  # Disable Smart Backup Mode when enabling EPS Mode
                    },
                },
            )
            .with_category(EntityCategory.CONFIG)
            .with_icon("mdi:power-plug-battery"),
            EnabledEntity(
                client,
                self,
                "stormIsEnable",
                "Storm Guard",
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "PD303_APP_SET",
                    "params": {"stormIsEnable": value == 1},
                },
            )
            .with_category(EntityCategory.CONFIG)
            .with_icon("mdi:weather-lightning"),
            *[
                self._switchesBatteryEnabled(
                    client,
                    x,
                    self.data.params.get(
                        f"pd303_mc.backupIncreInfo.ch{x}Info.backupIsReady", False
                    ),
                )
                for x in range(1, 4)
            ],
            *[
                self._switchesBatteryForceCharge(
                    client,
                    x,
                    self.data.params.get(
                        f"pd303_mc.backupIncreInfo.ch{x}Info.backupIsReady", False
                    ),
                )
                for x in range(1, 4)
            ],
            *circuits,
        ]

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return [
            DictSelectEntity(
                client,
                self,
                "'smartBackupMode'",
                const.SMART_BACKUP_MODE,
                const.SMART_BACKUP_MODE_OPTIONS,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "PD303_APP_SET",
                    "params": {
                        "smartBackupMode": value,
                        "epsModeInfo": False,  # Disable EPS Mode when enabling Smart Backup Mode
                    },
                },
            ),
            DictSelectEntity(
                client,
                self,
                "'pd303_mc.oilType'",
                const.GEN_TYPE,
                const.GEN_TYPE_OPTIONS,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "PD303_APP_SET",
                    "params": {"oilType": value},
                },
            ).with_icon("mdi:generator-mobile"),
        ]

    def _switchesBatteryEnabled(
        self, client: EcoflowApiClient, index: int, enabled: bool
    ) -> BaseSelectEntity:
        return (
            EnabledEntity(
                client,
                self,
                f"'ch{index}EnableSet'",
                f"{const.BATTERY} {index}",
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "PD303_APP_SET",
                    "params": {f"ch{index}EnableSet": value},
                },
                enabled,
                False,
                1,
                2,
            )
            .with_category(EntityCategory.CONFIG)
            .with_icon("mdi:battery-off")
        )

    def _switchesBatteryForceCharge(
        self, client: EcoflowApiClient, index: int, enable: bool
    ) -> BaseSwitchEntity:
        return (
            EnabledEntity(
                client,
                self,
                f"ch{index}ForceCharge",
                f"{const.BATTERY_N_FORCE_CHARGE % index}",
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "PD303_APP_SET",
                    "params": {f"ch{index}ForceCharge": value},
                },
                enable,
                True,
                "FORCE_CHARGE_ON",
                "FORCE_CHARGE_OFF",
            )
            .with_category(EntityCategory.CONFIG)
            .with_icon("mdi:battery-charging")
        )

    def _switchesCircuits(
        self, client: EcoflowApiClient, index: int, name: str, split: bool
    ) -> BaseSwitchEntity:
        def command_lambda(value):
            hall_info = {f"ch{index}Sta": {"loadSta": value}}
            if split:
                hall_info[f"ch{index + 2}Sta"] = {"loadSta": value}
            return {
                "sn": self.device_info.sn,
                "cmdCode": "PD303_APP_SET",
                "params": {"loadIncreInfo": {"hall1IncreInfo": hall_info}},
            }

        return EnabledEntity(
            client,
            self,
            f"'pd303_mc.loadIncreInfo.hall1IncreInfo.ch{index}Sta.loadSta'",
            name,
            command_lambda,
            True,
            True,
            "LOAD_CH_POWER_ON",
            "LOAD_CH_POWER_OFF",
        )

    def _sensorsCircuit(
        self,
        client: EcoflowApiClient,
        index: int,
        name: str,
        is_linked_split: bool,
        enabled: bool,
    ) -> BaseSensorEntity:
        # NOTE: jsonpath-ng does not support an array index list (ex. 'loadInfo.hall1Watt'[0,2]),
        #       but we CAN use a slice (ex. [0:3:2]) because the split circuits are always 2 apart
        circuit = (
            OutWattsSensorEntity(
                client,
                self,
                f"'loadInfo.hall1Watt'[{index - 1}:{index + 2}:2]"
                if is_linked_split
                else f"'loadInfo.hall1Watt'[{index - 1}]",
                f"{name} {const.POWER}",
                enabled,
                False,
            )
            .with_energy()
            .with_category(EntityCategory.DIAGNOSTIC)
        )
        return circuit.with_multiple_value_sum() if is_linked_split else circuit

    def _sensorsBattery(
        self, client: EcoflowApiClient, index: int, enabled: bool
    ) -> BaseSensorEntity:
        return LevelSensorEntity(
            client,
            self,
            f"'backupIncreInfo.Energy{index}Info.batteryPercentage'",
            const.BATTERY_N_LEVEL % index,
            enabled,
        )

    def _sensorsBatteryPower(
        self, client: EcoflowApiClient, index: int, enabled: bool
    ) -> BaseSensorEntity:
        return WattsSensorEntity(
            client,
            self,
            f"'wattInfo.chWatt'[{index - 1}]",
            const.BATTERY_N_POWER % index,
            enabled,
        ).with_energy(False)

    def flat_json(self):
        return False

    def _prepare_data(self, raw_data) -> dict[str, any]:
        res = super()._prepare_data(raw_data)
        new_params = {}

        if "param" in res:
            for k, v in res["param"].items():
                new_params[f"{k}"] = v

        if "params" in res:
            for k, v in res["params"].items():
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
