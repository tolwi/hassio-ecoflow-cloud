from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import BaseInternalDevice, const
from custom_components.ecoflow_cloud.number import (
    BatteryBackupLevel,
    ChargingPowerEntity,
    MaxBatteryLevelEntity,
    MinBatteryLevelEntity,
)
from custom_components.ecoflow_cloud.select import DictSelectEntity, TimeoutDictSelectEntity
from custom_components.ecoflow_cloud.sensor import (
    CapacitySensorEntity,
    ChargingStateSensorEntity,
    CyclesSensorEntity,
    InMilliVoltSensorEntity,
    InWattsSensorEntity,
    LevelSensorEntity,
    MilliVoltSensorEntity,
    OutMilliVoltSensorEntity,
    OutWattsSensorEntity,
    QuotaStatusSensorEntity,
    RemainSensorEntity,
    TempSensorEntity,
    VoltSensorEntity,
)
from custom_components.ecoflow_cloud.switch import EnabledEntity


class River2Pro(BaseInternalDevice):
    @staticmethod
    def default_charging_power_step() -> int:
        return 50

    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            LevelSensorEntity(client, self, "bms_bmsStatus.soc", const.MAIN_BATTERY_LEVEL)
            .attr("bms_bmsStatus.designCap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("bms_bmsStatus.fullCap", const.ATTR_FULL_CAPACITY, 0)
            .attr("bms_bmsStatus.remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, self, "bms_bmsStatus.designCap", const.MAIN_DESIGN_CAPACITY, False),
            CapacitySensorEntity(client, self, "bms_bmsStatus.fullCap", const.MAIN_FULL_CAPACITY, False),
            CapacitySensorEntity(client, self, "bms_bmsStatus.remainCap", const.MAIN_REMAIN_CAPACITY, False),
            LevelSensorEntity(client, self, "bms_bmsStatus.soh", const.SOH),
            LevelSensorEntity(client, self, "bms_emsStatus.lcdShowSoc", const.COMBINED_BATTERY_LEVEL),
            ChargingStateSensorEntity(client, self, "bms_emsStatus.chgState", const.BATTERY_CHARGING_STATE),
            InWattsSensorEntity(client, self, "pd.wattsInSum", const.TOTAL_IN_POWER).with_energy(),
            OutWattsSensorEntity(client, self, "pd.wattsOutSum", const.TOTAL_OUT_POWER).with_energy(),
            InWattsSensorEntity(client, self, "inv.inputWatts", const.AC_IN_POWER).with_energy(),
            OutWattsSensorEntity(client, self, "inv.outputWatts", const.AC_OUT_POWER).with_energy(),
            InMilliVoltSensorEntity(client, self, "inv.acInVol", const.AC_IN_VOLT),
            OutMilliVoltSensorEntity(client, self, "inv.invOutVol", const.AC_OUT_VOLT),
            InWattsSensorEntity(client, self, "pd.typecChaWatts", const.TYPE_C_IN_POWER),
            InWattsSensorEntity(client, self, "mppt.inWatts", const.SOLAR_IN_POWER).with_energy(),
            OutWattsSensorEntity(client, self, "pd.carWatts", const.DC_OUT_POWER),
            OutWattsSensorEntity(client, self, "pd.typec1Watts", const.TYPEC_OUT_POWER),
            OutWattsSensorEntity(client, self, "pd.usb1Watts", const.USB_OUT_POWER),
            # OutWattsSensorEntity(client, self, "pd.usb2Watts", const.USB_2_OUT_POWER),
            RemainSensorEntity(client, self, "bms_emsStatus.chgRemainTime", const.CHARGE_REMAINING_TIME),
            RemainSensorEntity(client, self, "bms_emsStatus.dsgRemainTime", const.DISCHARGE_REMAINING_TIME),
            RemainSensorEntity(client, self, "pd.remainTime", const.REMAINING_TIME),
            TempSensorEntity(client, self, "inv.outTemp", "Inv Out Temperature"),
            CyclesSensorEntity(client, self, "bms_bmsStatus.cycles", const.CYCLES),
            TempSensorEntity(client, self, "bms_bmsStatus.temp", const.BATTERY_TEMP)
            .attr("bms_bmsStatus.minCellTemp", const.ATTR_MIN_CELL_TEMP, 0)
            .attr("bms_bmsStatus.maxCellTemp", const.ATTR_MAX_CELL_TEMP, 0),
            TempSensorEntity(client, self, "bms_bmsStatus.minCellTemp", const.MIN_CELL_TEMP, False),
            TempSensorEntity(client, self, "bms_bmsStatus.maxCellTemp", const.MAX_CELL_TEMP, False),
            VoltSensorEntity(client, self, "bms_bmsStatus.vol", const.BATTERY_VOLT, False)
            .attr("bms_bmsStatus.minCellVol", const.ATTR_MIN_CELL_VOLT, 0)
            .attr("bms_bmsStatus.maxCellVol", const.ATTR_MAX_CELL_VOLT, 0),
            MilliVoltSensorEntity(client, self, "bms_bmsStatus.minCellVol", const.MIN_CELL_VOLT, False),
            MilliVoltSensorEntity(client, self, "bms_bmsStatus.maxCellVol", const.MAX_CELL_VOLT, False),
            # FanSensorEntity(client, self, "bms_emsStatus.fanLevel", "Fan Level"),
            QuotaStatusSensorEntity(client, self),
        ]

    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return [
            MaxBatteryLevelEntity(
                client,
                self,
                "bms_emsStatus.maxChargeSoc",
                const.MAX_CHARGE_LEVEL,
                50,
                100,
                lambda value: {"moduleType": 2, "operateType": "upsConfig", "params": {"maxChgSoc": int(value)}},
            ),
            MinBatteryLevelEntity(
                client,
                self,
                "bms_emsStatus.minDsgSoc",
                const.MIN_DISCHARGE_LEVEL,
                0,
                30,
                lambda value: {"moduleType": 2, "operateType": "dsgCfg", "params": {"minDsgSoc": int(value)}},
            ),
            ChargingPowerEntity(
                client,
                self,
                "mppt.cfgChgWatts",
                const.AC_CHARGING_POWER,
                100,
                950,
                lambda value: {
                    "moduleType": 5,
                    "operateType": "acChgCfg",
                    "params": {"chgWatts": int(value), "chgPauseFlag": 255},
                },
            ),
            BatteryBackupLevel(
                client,
                self,
                "pd.bpPowerSoc",
                const.BACKUP_RESERVE_LEVEL,
                5,
                100,
                "bms_emsStatus.minDsgSoc",
                "bms_emsStatus.maxChargeSoc",
                5,
                lambda value: {
                    "moduleType": 1,
                    "operateType": "watthConfig",
                    "params": {"isConfig": 1, "bpPowerSoc": int(value), "minDsgSoc": 0, "minChgSoc": 0},
                },
            ),
        ]

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return [
            EnabledEntity(
                client,
                self,
                "mppt.cfgAcEnabled",
                const.AC_ENABLED,
                lambda value: {
                    "moduleType": 5,
                    "operateType": "acOutCfg",
                    "params": {"enabled": value, "out_voltage": -1, "out_freq": 255, "xboost": 255},
                },
            ),
            EnabledEntity(
                client,
                self,
                "mppt.cfgAcXboost",
                const.XBOOST_ENABLED,
                lambda value: {
                    "moduleType": 5,
                    "operateType": "acOutCfg",
                    "params": {"enabled": 255, "out_voltage": -1, "out_freq": 255, "xboost": value},
                },
            ),
            EnabledEntity(
                client,
                self,
                "pd.carState",
                const.DC_ENABLED,
                lambda value: {"moduleType": 5, "operateType": "mpptCar", "params": {"enabled": value}},
            ),
            EnabledEntity(
                client,
                self,
                "pd.watchIsConfig",
                const.BP_ENABLED,
                lambda value, params: {
                    "moduleType": 1,
                    "operateType": "watthConfig",
                    "params": {"isConfig": value, "bpPowerSoc": value * 50, "minDsgSoc": 0, "minChgSoc": 0},
                },
            ),
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return [
            DictSelectEntity(
                client,
                self,
                "mppt.dcChgCurrent",
                const.DC_CHARGE_CURRENT,
                const.DC_CHARGE_CURRENT_OPTIONS,
                lambda value: {"moduleType": 5, "operateType": "dcChgCfg", "params": {"dcChgCfg": value}},
            ),
            DictSelectEntity(
                client,
                self,
                "mppt.cfgChgType",
                const.DC_MODE,
                const.DC_MODE_OPTIONS,
                lambda value: {"moduleType": 5, "operateType": "chaType", "params": {"chaType": value}},
            ),
            TimeoutDictSelectEntity(
                client,
                self,
                "mppt.scrStandbyMin",
                const.SCREEN_TIMEOUT,
                const.SCREEN_TIMEOUT_OPTIONS,
                lambda value: {
                    "moduleType": 5,
                    "operateType": "lcdCfg",
                    "params": {"brighLevel": 255, "delayOff": value},
                },
            ),
            TimeoutDictSelectEntity(
                client,
                self,
                "mppt.powStandbyMin",
                const.UNIT_TIMEOUT,
                const.UNIT_TIMEOUT_OPTIONS,
                lambda value: {"moduleType": 5, "operateType": "standby", "params": {"standbyMins": value}},
            ),
            TimeoutDictSelectEntity(
                client,
                self,
                "mppt.acStandbyMins",
                const.AC_TIMEOUT,
                const.AC_TIMEOUT_OPTIONS,
                lambda value: {"moduleType": 5, "operateType": "acStandby", "params": {"standbyMins": value}},
            ),
        ]
