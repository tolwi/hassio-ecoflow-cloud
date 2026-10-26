from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.binary_sensor import MiscBinarySensorEntity
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
    DcModeStateSensorEntity,
    Ft307FaultCodeSensorEntity,
    InMilliampSensorEntity,
    InMilliVoltSensorEntity,
    InWattsSensorEntity,
    LevelSensorEntity,
    MilliVoltSensorEntity,
    OutMilliVoltSensorEntity,
    OutWattsSensorEntity,
    QuotaStatusSensorEntity,
    RemainSensorEntity,
    StateOfHealthSensorEntity,
    StatusSensorEntity,
    TempSensorEntity,
    VoltSensorEntity,
)
from custom_components.ecoflow_cloud.switch import EnabledEntity


class River2(BaseInternalDevice):
    @staticmethod
    def default_charging_power_step() -> int:
        return 50

    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            # Some base RIVER_2 units report BMS/quota data under a
            # "bmsMaster."/"inv."/"pd." key set instead of the
            # "bms_bmsStatus."/"bms_emsStatus."/"mppt." set below - confirmed
            # via live diagnostics on a unit where every "bms_bmsStatus.*"
            # entity stayed permanently unknown while "bmsMaster.*" held the
            # real values (see issue #918). Both variants are registered
            # disabled+auto_enable so whichever one this device actually
            # reports wins and the other stays hidden.
            LevelSensorEntity(
                client, self, "bms_bmsStatus.soc", const.MAIN_BATTERY_LEVEL, enabled=False, auto_enable=True
            )
            .attr("bms_bmsStatus.designCap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("bms_bmsStatus.fullCap", const.ATTR_FULL_CAPACITY, 0)
            .attr("bms_bmsStatus.remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            LevelSensorEntity(client, self, "bmsMaster.soc", const.MAIN_BATTERY_LEVEL, enabled=False, auto_enable=True)
            .attr("bmsMaster.fullCap", const.ATTR_FULL_CAPACITY, 0)
            .attr("bmsMaster.remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, self, "bms_bmsStatus.designCap", const.MAIN_DESIGN_CAPACITY, False),
            CapacitySensorEntity(
                client, self, "bms_bmsStatus.fullCap", const.MAIN_FULL_CAPACITY, False, auto_enable=True
            ),
            CapacitySensorEntity(client, self, "bmsMaster.fullCap", const.MAIN_FULL_CAPACITY, False, auto_enable=True),
            CapacitySensorEntity(
                client, self, "bms_bmsStatus.remainCap", const.MAIN_REMAIN_CAPACITY, False, auto_enable=True
            ),
            CapacitySensorEntity(
                client, self, "bmsMaster.remainCap", const.MAIN_REMAIN_CAPACITY, False, auto_enable=True
            ),
            StateOfHealthSensorEntity(client, self, "bms_bmsStatus.soh", const.SOH),
            LevelSensorEntity(
                client, self, "bms_emsStatus.lcdShowSoc", const.COMBINED_BATTERY_LEVEL, enabled=False, auto_enable=True
            ),
            LevelSensorEntity(client, self, "pd.soc", const.COMBINED_BATTERY_LEVEL, enabled=False, auto_enable=True),
            ChargingStateSensorEntity(client, self, "bms_emsStatus.chgState", const.BATTERY_CHARGING_STATE),
            InWattsSensorEntity(client, self, "pd.wattsInSum", const.TOTAL_IN_POWER).with_energy(),
            OutWattsSensorEntity(client, self, "pd.wattsOutSum", const.TOTAL_OUT_POWER).with_energy(),
            # River 2 reports live PV telemetry under mppt.*; inv.dcIn* stays at 0
            # even while solar input power is non-zero.
            InMilliampSensorEntity(client, self, "mppt.inAmp", const.SOLAR_IN_CURRENT),
            InMilliVoltSensorEntity(client, self, "mppt.inVol", const.SOLAR_IN_VOLTAGE),
            InWattsSensorEntity(client, self, "inv.inputWatts", const.AC_IN_POWER).with_energy(),
            OutWattsSensorEntity(client, self, "inv.outputWatts", const.AC_OUT_POWER).with_energy(),
            InMilliVoltSensorEntity(client, self, "inv.acInVol", const.AC_IN_VOLT),
            OutMilliVoltSensorEntity(client, self, "inv.invOutVol", const.AC_OUT_VOLT),
            InWattsSensorEntity(client, self, "pd.typecChaWatts", const.TYPE_C_IN_POWER),
            InWattsSensorEntity(client, self, "mppt.inWatts", const.SOLAR_IN_POWER).with_energy(),
            OutWattsSensorEntity(client, self, "pd.carWatts", const.DC_OUT_POWER),
            OutWattsSensorEntity(client, self, "pd.typec1Watts", const.TYPEC_OUT_POWER),
            OutWattsSensorEntity(client, self, "pd.usb1Watts", const.USB_OUT_POWER),
            # Diagnostic only: reports which DC path is live, not a switchable 24V output like Delta Pro 3.
            DcModeStateSensorEntity(client, self, "mppt.chgType", "DC Mode", diagnostic=True),
            Ft307FaultCodeSensorEntity(client, self, "mppt.faultCode", "MPPT Fault", diagnostic=True),
            # OutWattsSensorEntity(client, self, "pd.usb2Watts", const.USB_2_OUT_POWER),
            RemainSensorEntity(client, self, "bms_emsStatus.chgRemainTime", const.CHARGE_REMAINING_TIME),
            RemainSensorEntity(client, self, "bms_emsStatus.dsgRemainTime", const.DISCHARGE_REMAINING_TIME),
            RemainSensorEntity(client, self, "pd.remainTime", const.REMAINING_TIME),
            TempSensorEntity(client, self, "inv.outTemp", "Inv Out Temperature"),
            CyclesSensorEntity(client, self, "bms_bmsStatus.cycles", const.CYCLES, enabled=False, auto_enable=True),
            CyclesSensorEntity(client, self, "bmsMaster.cycles", const.CYCLES, enabled=False, auto_enable=True),
            TempSensorEntity(
                client, self, "bms_bmsStatus.temp", const.BATTERY_TEMP, enabled=False, auto_enable=True
            )
            .attr("bms_bmsStatus.minCellTemp", const.ATTR_MIN_CELL_TEMP, 0)
            .attr("bms_bmsStatus.maxCellTemp", const.ATTR_MAX_CELL_TEMP, 0),
            TempSensorEntity(client, self, "bmsMaster.temp", const.BATTERY_TEMP, enabled=False, auto_enable=True),
            TempSensorEntity(client, self, "bms_bmsStatus.minCellTemp", const.MIN_CELL_TEMP, False),
            TempSensorEntity(client, self, "bms_bmsStatus.maxCellTemp", const.MAX_CELL_TEMP, False),
            VoltSensorEntity(client, self, "bms_bmsStatus.vol", const.BATTERY_VOLT, False, auto_enable=True)
            .attr("bms_bmsStatus.minCellVol", const.ATTR_MIN_CELL_VOLT, 0)
            .attr("bms_bmsStatus.maxCellVol", const.ATTR_MAX_CELL_VOLT, 0),
            # bmsMaster.vol is reported in millivolts on this hardware variant
            # (confirmed: raw ~29000-29700 matches an 8S LFP pack at ~3.6-3.7V/cell),
            # unlike bms_bmsStatus.vol above which is assumed to already be whole volts -
            # MilliVoltSensorEntity's suggested_unit_of_measurement handles the mV->V
            # display conversion, same as the cell-level volt sensors below.
            MilliVoltSensorEntity(client, self, "bmsMaster.vol", const.BATTERY_VOLT, False, auto_enable=True)
            .attr("bmsMaster.minCellVol", const.ATTR_MIN_CELL_VOLT, 0)
            .attr("bmsMaster.maxCellVol", const.ATTR_MAX_CELL_VOLT, 0),
            MilliVoltSensorEntity(
                client, self, "bms_bmsStatus.minCellVol", const.MIN_CELL_VOLT, False, auto_enable=True
            ),
            MilliVoltSensorEntity(client, self, "bmsMaster.minCellVol", const.MIN_CELL_VOLT, False, auto_enable=True),
            MilliVoltSensorEntity(
                client, self, "bms_bmsStatus.maxCellVol", const.MAX_CELL_VOLT, False, auto_enable=True
            ),
            MilliVoltSensorEntity(client, self, "bmsMaster.maxCellVol", const.MAX_CELL_VOLT, False, auto_enable=True),
            self._status_sensor(client),
            # FanSensorEntity(client, self, "bms_emsStatus.fanLevel", "Fan Level"),
        ]

    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        def max_charge_command(value):
            return {"moduleType": 2, "operateType": "upsConfig", "params": {"maxChgSoc": int(value)}}

        return [
            # See the sensors() comment above: dual key variants for the same
            # reason, confirmed via diagnostics on issue #918.
            MaxBatteryLevelEntity(
                client,
                self,
                "bms_emsStatus.maxChargeSoc",
                const.MAX_CHARGE_LEVEL,
                50,
                100,
                max_charge_command,
                enabled=False,
                auto_enable=True,
            ),
            MaxBatteryLevelEntity(
                client,
                self,
                "bmsMaster.maxChargeSoc",
                const.MAX_CHARGE_LEVEL,
                50,
                100,
                max_charge_command,
                enabled=False,
                auto_enable=True,
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
                360,
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
        def ac_enabled_command(value):
            return {
                "moduleType": 5,
                "operateType": "acOutCfg",
                "params": {"enabled": value, "out_voltage": -1, "out_freq": 255, "xboost": 255},
            }

        def ac_always_enabled_command(value, params):
            return {
                "moduleType": 1,
                "operateType": "acAutoOutConfig",
                "params": {
                    "acAutoOutConfig": value,
                    "minAcOutSoc": int(params.get("bms_emsStatus.minDsgSoc", 0)) + 5,
                },
            }

        def xboost_command(value):
            return {
                "moduleType": 5,
                "operateType": "acOutCfg",
                "params": {"enabled": 255, "out_voltage": -1, "out_freq": 255, "xboost": value},
            }

        def dc_enabled_command(value):
            return {"moduleType": 5, "operateType": "mpptCar", "params": {"enabled": value}}

        return [
            # See the sensors() comment above: dual key variants for the same
            # reason, confirmed via diagnostics on issue #918. Only the read
            # (state) key differs between variants - the write/command
            # payload is unverified against a "bmsMaster."/"inv." device and
            # reused as-is from the existing "mppt."/"pd." variant.
            EnabledEntity(
                client, self, "mppt.cfgAcEnabled", const.AC_ENABLED, ac_enabled_command, enabled=False, auto_enable=True
            ),
            EnabledEntity(
                client, self, "inv.cfgAcEnabled", const.AC_ENABLED, ac_enabled_command, enabled=False, auto_enable=True
            ),
            EnabledEntity(
                client,
                self,
                "pd.acAutoOutConfig",
                const.AC_ALWAYS_ENABLED,
                ac_always_enabled_command,
                enabled=False,
                auto_enable=True,
            ),
            EnabledEntity(
                client,
                self,
                "inv.acAutoOutConfig",
                const.AC_ALWAYS_ENABLED,
                ac_always_enabled_command,
                enabled=False,
                auto_enable=True,
            ),
            EnabledEntity(
                client, self, "mppt.cfgAcXboost", const.XBOOST_ENABLED, xboost_command, enabled=False, auto_enable=True
            ),
            EnabledEntity(
                client, self, "inv.cfgAcXboost", const.XBOOST_ENABLED, xboost_command, enabled=False, auto_enable=True
            ),
            EnabledEntity(
                client, self, "pd.carState", const.DC_ENABLED, dc_enabled_command, enabled=False, auto_enable=True
            ),
            EnabledEntity(
                client, self, "pd.carSwitch", const.DC_ENABLED, dc_enabled_command, enabled=False, auto_enable=True
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

    def binary_sensors(self, client: EcoflowApiClient) -> list[BinarySensorEntity]:
        return [
            # Read-only: confirmed via a live before/after diagnostics diff while
            # toggling "AC Slow Charging" in the app (issue #918 discussion), but
            # no verified write command exists for this device generation - see
            # the switches() comment for why this isn't a switch.
            MiscBinarySensorEntity(client, self, "inv.cfgAcChgModeFlg", const.AC_SLOW_CHARGE),
        ]

    def _status_sensor(self, client: EcoflowApiClient) -> StatusSensorEntity:
        return QuotaStatusSensorEntity(client, self)
