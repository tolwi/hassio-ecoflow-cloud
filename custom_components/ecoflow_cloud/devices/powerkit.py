from homeassistant.const import Platform
from typing import Any

from . import const, BaseDevice, EntityMigration, MigrationAction
from .. import EcoflowMQTTClient
from ..entities import (
    BaseSensorEntity,
    BaseNumberEntity,
    BaseSwitchEntity,
    BaseSelectEntity,
)
from ..number import (
    ChargingPowerEntity,
    MinBatteryLevelEntity,
    MaxBatteryLevelEntity,
    MaxGenStopLevelEntity,
    MinGenStartLevelEntity,
    BatteryBackupLevel,
)
from ..select import DictSelectEntity, TimeoutDictSelectEntity
from ..sensor import (
    AmpSensorEntity,
    ChargingStateSensorEntity,
    DeciMilliVoltSensorEntity,
    FanSensorEntity,
    FrequencySensorEntity,
    InRawTotalWattsSolarSensorEntity,
    InWattsSolarSensorEntity,
    LevelSensorEntity,
    MiscSensorEntity,
    RemainSensorEntity,
    TempSensorEntity,
    CyclesSensorEntity,
    InWattsSensorEntity,
    OutWattsSensorEntity,
    QuotasStatusSensorEntity,
    MilliVoltSensorEntity,
    InMilliVoltSensorEntity,
    OutMilliVoltSensorEntity,
    CapacitySensorEntity,
)
from ..switch import BeeperEntity, EnabledEntity
import json


class PowerKit(BaseDevice):
    def sensors(self, client: EcoflowMQTTClient) -> list[BaseSensorEntity]:
        result: list[BaseSensorEntity] = list()
        params = client.data.params
        for key in params:
            if key.startswith("bp"):
                result = [
                    *result,
                    *self.batterieSensors(client, key, json.loads(params[key])),
                ]
            elif key == "iclow":
                result = [
                    *result,
                    *self.bmsSensors(client, key, json.loads(params[key])),
                ]
            elif key == "kitscc":
                result = [
                    *result,
                    *self.mpptSensors(client, key, json.loads(params[key])),
                ]
            elif key == "bbcout":
                result = [
                    *result,
                    *self.powerHubDCOutSensors(client, key, json.loads(params[key])),
                ]
            elif key == "bbcin":
                result = [
                    *result,
                    *self.powerHubDCInSensors(client, key, json.loads(params[key])),
                ]
            elif key == "lddc":
                result = [
                    *result,
                    *self.distributerDCOutSensors(client, key, json.loads(params[key])),
                ]
            elif key == "ichigh":
                result = [
                    *result,
                    *self.powerHubACOutSensors(client, key, json.loads(params[key])),
                ]
            elif key == "ldac":
                result = [
                    *result,
                    *self.distributerACOutSensors(client, key, json.loads(params[key])),
                ]
        return [
            *result,
            # TODO: Figure out some of the values
            # TODO: Add in config data
            # TODO: Add value editing
            # TODO: Support batteries ✅
            # TODO: Check AC Input
            # TODO: Check DC In via Smart Generator
            # TODO: Attempt alternator charging
        ]

    def batterieSensors(
        self, client: EcoflowMQTTClient, mainKey: str, params: dict[str, Any]
    ) -> list[BaseSensorEntity]:
        result: list[BaseSensorEntity] = list()

        for key in params.keys():
            entityKey = mainKey + "." + key + "."
            result = [
                *result,
                AmpSensorEntity(
                    client, f"{entityKey}amp", f"Ampere battery ({key})", True, True
                ),
                CapacitySensorEntity(
                    client, f"{entityKey}fullCap", f"max Capacity battery ({key})"
                ),
                ChargingStateSensorEntity(
                    client, f"{entityKey}soc", f"State of Charge (soc) battery ({key})"
                ),
                MilliVoltSensorEntity(
                    client,
                    f"{entityKey}minCellVol",
                    f"minimal cell voltage battery ({key})",
                ),
                CyclesSensorEntity(
                    client, f"{entityKey}cycles", f"full cycle count battery ({key})"
                ),
                MilliVoltSensorEntity(
                    client, f"{entityKey}vol", f"current voltage battery ({key})"
                ),
                CapacitySensorEntity(
                    client, f"{entityKey}remainCap", f"current Capacity battery ({key})"
                ),
                InWattsSensorEntity(
                    client, f"{entityKey}inWatts", f"Charing power battery ({key})"
                ),
                TempSensorEntity(
                    client, f"{entityKey}temp", f"temperatur battery ({key})"
                ),
                RemainSensorEntity(
                    client,
                    f"{entityKey}remainTime",
                    f"remaining time battery ({key})",
                ),
                MilliVoltSensorEntity(
                    client,
                    f"{entityKey}maxCellVol",
                    f"maximum cell voltage battery ({key})",
                ),
                OutWattsSensorEntity(
                    client, f"{entityKey}outWatts", f"discharing power battery ({key})"
                ),
            ]
        return result

    def bmsSensors(
        self, client: EcoflowMQTTClient, mainKey: str, params: dict[str, Any]
    ) -> list[BaseSensorEntity]:
        result: list[BaseSensorEntity] = list()

        for key in params.keys():
            entityKey = mainKey + "." + key + "."
            result = [
                *result,
                LevelSensorEntity(
                    client, f"{entityKey}realSoc", const.MAIN_BATTERY_LEVEL
                ),
                MiscSensorEntity(client, f"{entityKey}errCode", "BMS Error Code"),  # 0
                MiscSensorEntity(
                    client, f"{entityKey}warn_code", "BMS Warning Code"
                ),  # 0
                MiscSensorEntity(
                    client, f"{entityKey}event_code", "BMS Event Code", False
                ),  # 0
                TempSensorEntity(
                    client, f"{entityKey}dcTemp", "BMS DC Temperature", True
                ),  # 37
                ChargingStateSensorEntity(
                    client,
                    f"{entityKey}chgDsgState",
                    "BMS Charge Discharge State",
                    False,
                ),  # 1
                MilliVoltSensorEntity(
                    client, f"{entityKey}chgBatVol", "BMS Charge Voltage", False
                ),  # 54161
                MiscSensorEntity(
                    client, f"{entityKey}chgType", "BMS Charge Type", False
                ),  # 1
                MiscSensorEntity(
                    client, f"{entityKey}chgInType", "BMS Charge In Type", False
                ),  # 1
                MiscSensorEntity(
                    client, f"{entityKey}chrgFlag", "BMS Charge Flag", False
                ),  # 1
                AmpSensorEntity(
                    client, f"{entityKey}maxChgCurr", "BMS Max Charge Current", False
                ),  # 0
                MiscSensorEntity(
                    client, f"{entityKey}extKitType", "BMS External Kit Type", False
                ),  # 0
                AmpSensorEntity(
                    client, f"{entityKey}bmsChgCurr", "BMS Bus Current", False
                ),
                DeciMilliVoltSensorEntity(
                    client, f"{entityKey}busVol", "BMS Bus Voltage", True
                ),  # 454198
                MiscSensorEntity(
                    client, f"{entityKey}lsplFlag", "BMS LSPL Flag", False
                ),  # 0
                MiscSensorEntity(
                    client, f"{entityKey}protectState", "BMS Protect State"
                ),  # 0
                AmpSensorEntity(
                    client, f"{entityKey}batCurr", "BMS Battery Current", False
                ),  # 386
                FanSensorEntity(
                    client, f"{entityKey}fanLevel", "Fan Level", False
                ),  # 2
            ]
        return result

    def mpptSensors(
        self, client: EcoflowMQTTClient, mainKey: str, params: dict[str, Any]
    ) -> list[BaseSensorEntity]:
        result: list[BaseSensorEntity] = list()

        for key in params.keys():
            entityKey = mainKey + "." + key + "."
            result = [
                *result,
                # MPPT
                InRawTotalWattsSolarSensorEntity(
                    client, f"{entityKey}batWatts", const.SOLAR_AND_ALT_IN_POWER, True
                ),
                AmpSensorEntity(
                    client, f"{entityKey}batCurr", "Solar Battery Current", True
                ),
                MilliVoltSensorEntity(
                    client, f"{entityKey}batVol", "Solar Battery Voltage", True
                ),
                InWattsSolarSensorEntity(
                    client, f"{entityKey}pv1InWatts", const.SOLAR_2_IN_POWER, True
                ),
                MilliVoltSensorEntity(
                    client, f"{entityKey}pv1InVol", "Solar (2) In Voltage", True
                ),
                AmpSensorEntity(
                    client, f"{entityKey}pv1InCurr", "Solar (2) In Current", True
                ),
                MiscSensorEntity(
                    client, f"{entityKey}pv1ErrCode", "Solar (2) Error Code", True
                ),
                MiscSensorEntity(
                    client, f"{entityKey}pv1_hot_out", "Solar (2) Hot Out", False
                ),
                MiscSensorEntity(
                    client, f"{entityKey}pv1InputFlag", "Solar (2) Input Flag", False
                ),
                MiscSensorEntity(
                    client, f"{entityKey}pv1WorkMode", "Solar (2) Work Mode", False
                ),
                MiscSensorEntity(
                    client, f"{entityKey}mppt1SwSta", "Solar (2) Enabled", True
                ),
                MiscSensorEntity(
                    client, f"{entityKey}eventCode1", "Solar (2) Event Code", False
                ),
                MiscSensorEntity(
                    client, f"{entityKey}warnCode1", "Solar (2) Warn Code", True
                ),
                TempSensorEntity(
                    client, f"{entityKey}hs1Temp", "Solar (2) Temperature", True
                ),
                InWattsSolarSensorEntity(
                    client, f"{entityKey}pv2InWatts", "Solar (3) In Power", True
                ),
                MilliVoltSensorEntity(
                    client, f"{entityKey}pv2InVol", "Solar (3) In Voltage", True
                ),
                AmpSensorEntity(
                    client, f"{entityKey}pv2InCurr", "Solar (3) In Current", True
                ),
                MiscSensorEntity(
                    client, f"{entityKey}pv2ErrCode", "Solar (3) Error Code", True
                ),
                MiscSensorEntity(
                    client, f"{entityKey}pv2_hot_out", "Solar (3) Hot Out", False
                ),
                MiscSensorEntity(
                    client, f"{entityKey}pv2InputFlag", "Solar (3) Input Flag", False
                ),
                MiscSensorEntity(
                    client, f"{entityKey}pv2WorkMode", "Solar (3) Work Mode", False
                ),
                MiscSensorEntity(
                    client, f"{entityKey}mppt2SwSta", "Solar (3) Enabled", True
                ),
                MiscSensorEntity(
                    client, f"{entityKey}eventCode2", "Solar (3) Event Code", False
                ),
                MiscSensorEntity(
                    client, f"{entityKey}warnCode2", "Solar (3) Warn Code", True
                ),
                TempSensorEntity(
                    client, f"{entityKey}hs2Temp", "Solar (3) Temperature", True
                ),
                AmpSensorEntity(
                    client, f"{entityKey}chgEnergy", "Solar Total Charge Current", False
                ),  # Not in use
                AmpSensorEntity(
                    client, f"{entityKey}dayEnergy", "Solar Energy for Day", False
                ),  # Not in use
            ]
        return result

    def powerHubDCOutSensors(
        self, client: EcoflowMQTTClient, mainKey: str, params: dict[str, Any]
    ) -> list[BaseSensorEntity]:
        result: list[BaseSensorEntity] = list()

        for key in params.keys():
            entityKey = mainKey + "." + key + "."
            result = [
                *result,
                # Power Hub DC Out
                AmpSensorEntity(
                    client, f"{entityKey}ldOutCurr", "DC Out Current", True
                ),  # 14999 DC output to distributer
                OutWattsSensorEntity(
                    client, f"{entityKey}ldOutWatts", "DC Out Power", True
                ),  # 396 DC output to distributer
                OutWattsSensorEntity(
                    client, f"{entityKey}batWatts", "DC Out Battery Power", True
                ),  # 425 DC output from battery including BMS and Distributer power
                AmpSensorEntity(
                    client, f"{entityKey}l1Curr", "DC 1 Out Battery Current", False
                ),  # 6990 DC output from battery including BMS and Distributer power
                AmpSensorEntity(
                    client, f"{entityKey}l2Curr", "DC 2 Out Battery Current", False
                ),  # 6869 DC output from battery including BMS and Distributer power
                MilliVoltSensorEntity(
                    client, f"{entityKey}batVol", "DC Out Battery Voltage", False
                ),  # 54136 DC output from battery including BMS and Distributer power
            ]
        return result

    def powerHubDCInSensors(
        self, client: EcoflowMQTTClient, mainKey: str, params: dict[str, Any]
    ) -> list[BaseSensorEntity]:
        result: list[BaseSensorEntity] = list()

        for key in params.keys():
            entityKey = mainKey + "." + key + "."
            result = [
                *result,
                # Power Hub DC In
                MiscSensorEntity(
                    client, f"{entityKey}workMode", "DC Work Mode 1", False
                ),  # 54136 DC input
                MiscSensorEntity(
                    client, f"{entityKey}workMode2", "DC Work Mode 2", False
                ),  # 54136 DC input
                MiscSensorEntity(
                    client, f"{entityKey}inHwTpe", "DC In Hardware Type", True
                ),  # 54136 DC input
                MiscSensorEntity(
                    client, f"{entityKey}bpOnlinePos", "DC Online Pos", False
                ),  # 54136 DC input
                MiscSensorEntity(
                    client, f"{entityKey}dayEnergy", "DC In Energy for Day", False
                ),  # 54136 Not in use
                MiscSensorEntity(
                    client,
                    f"{entityKey}shakeCtrlDisable",
                    "Disable Shake Control",
                    False,
                ),  # 54136 DC input
                MiscSensorEntity(
                    client, f"{entityKey}isCarMoving", "Is Car Moving", False
                ),  # 54136 DC input
                MiscSensorEntity(
                    client, f"{entityKey}eventCode", "DC In Event Code", False
                ),  # 0 DC input
                MiscSensorEntity(
                    client, f"{entityKey}warnCode", "DC In Warning Code", True
                ),  # 0 DC input
                MiscSensorEntity(
                    client, f"{entityKey}errCode", "DC In Error Code", True
                ),  # 10000 DC input
                OutWattsSensorEntity(
                    client, f"{entityKey}batWatts", "DC In Battery Power", True
                ),  # 4 DC input
                AmpSensorEntity(
                    client, f"{entityKey}batCurr", "DC In Battery Current", True
                ),  # 78 DC input
                MilliVoltSensorEntity(
                    client, f"{entityKey}batVol", "DC In Battery Voltage", True
                ),  # 53438 DC input
                MiscSensorEntity(
                    client, f"{entityKey}allowDsgOn", "DC Allow Discharge", True
                ),  # 1 DC input
                AmpSensorEntity(
                    client, f"{entityKey}dsgEnergy", "DC Discharge Energy", False
                ),  # 789 Unsure what this one is. Could be some kind of total
                MiscSensorEntity(
                    client, f"{entityKey}dcInState", "DC In State", True
                ),  # 0 DC input
                OutWattsSensorEntity(
                    client, f"{entityKey}dcInWatts", "DC In Power", True
                ),  # 0 DC input
                AmpSensorEntity(
                    client, f"{entityKey}dcInCurr", "DC In Current", True
                ),  # 0 DC input
                MilliVoltSensorEntity(
                    client, f"{entityKey}dcInVol", "DC In Voltage", True
                ),  # 0 DC input
                MiscSensorEntity(
                    client, f"{entityKey}chgPause", "DC Charge Paused", True
                ),  # 1 DC input
                MiscSensorEntity(
                    client, f"{entityKey}chgType", "DC Charge Type", True
                ),  # 0 DC input
                AmpSensorEntity(
                    client, f"{entityKey}chgMaxCurr", "DC Charge Max Current", True
                ),  # 30000 DC input
                MiscSensorEntity(
                    client, f"{entityKey}chargeMode", "DC Charge Mode", True
                ),  # 0 DC input
                AmpSensorEntity(
                    client, f"{entityKey}l1Curr", "DC In L1 Current", False
                ),  # -5 DC input
                AmpSensorEntity(
                    client, f"{entityKey}l2Curr", "DC In L2 Current", False
                ),  # -45 DC input
                TempSensorEntity(
                    client, f"{entityKey}hs1Temp", "DC In HS1 Temperature", True
                ),  # 32 DC input
                TempSensorEntity(
                    client, f"{entityKey}hs2Temp", "DC In HS2 Temperature", True
                ),  # 32 DC input
                TempSensorEntity(
                    client, f"{entityKey}pcbTemp", "DC In PCB Temperature", True
                ),  # 0 DC input
                MiscSensorEntity(
                    client, f"{entityKey}altCableUnit", "Alt. Cable Unit", True
                ),  # 0 DC input
                MiscSensorEntity(
                    client, f"{entityKey}altCableLen", "Alt. Cable Length", True
                ),  # 600 DC input
                MiscSensorEntity(
                    client, f"{entityKey}altVoltLmt", "Alt. Cable Voltage Limit", True
                ),  # 130 DC input
                MiscSensorEntity(
                    client, f"{entityKey}altVoltLmtEn", "Alt. Voltage Limit En", True
                ),  # 1 DC input
            ]
        return result

    def powerHubACOutSensors(
        self, client: EcoflowMQTTClient, mainKey: str, params: dict[str, Any]
    ) -> list[BaseSensorEntity]:
        result: list[BaseSensorEntity] = list()

        for key in params.keys():
            entityKey = mainKey + "." + key + "."
            result = [
                *result,
                # Power Hub AC Out
                OutMilliVoltSensorEntity(
                    client, f"{entityKey}outVol", "AC Out Voltage", True
                ),  # 240070
                # MiscSensorEntity(client, f"{entityKey}outVa", 'AC Out VA', True), # 361
                AmpSensorEntity(
                    client, f"{entityKey}outCurr", "AC Out Current", True
                ),  # 2432
                MiscSensorEntity(
                    client, f"{entityKey}invType", "AC Inverter Type", False
                ),  # 0
                FrequencySensorEntity(
                    client, f"{entityKey}inFreq", "AC In Frequency", True
                ),  # 0
                OutWattsSensorEntity(
                    client, f"{entityKey}inWatts", "AC In Power", True
                ),  # 0
                AmpSensorEntity(
                    client, f"{entityKey}inCurr", "AC In Current", True
                ),  # 0
                OutMilliVoltSensorEntity(
                    client, f"{entityKey}inVol", "AC In Voltage", True
                ),  # 0
                MiscSensorEntity(
                    client, f"{entityKey}invSwSta", "AC Out Enabled", True
                ),  # 1
                TempSensorEntity(
                    client, f"{entityKey}acTemp", "AC Inverter Temperature", True
                ),  # 1
                OutWattsSensorEntity(
                    client, f"{entityKey}outWatts", "AC Out Power", True
                ),  # 165
                OutWattsSensorEntity(
                    client, f"{entityKey}ch2Watt", "AC Outlet Power", True
                ),  # 165
                AmpSensorEntity(
                    client, f"{entityKey}outAmp2", "AC Outlet Current", True
                ),  # 0
                FrequencySensorEntity(
                    client, f"{entityKey}cfgOutFreq", "AC Config Out Frequency", False
                ),  # 1
                FrequencySensorEntity(
                    client, f"{entityKey}outFreq", "AC Out Frequency", True
                ),  # 1
                MiscSensorEntity(
                    client, f"{entityKey}standbyTime", "AC Standby Time", False
                ),  # 1
                OutWattsSensorEntity(
                    client, f"{entityKey}inputWhInDay", "AC Input Day Power", False
                ),  # Not in use
                OutWattsSensorEntity(
                    client, f"{entityKey}outputWhInDay", "AC Output Day Power", False
                ),  # Not in use
            ]
        return result

    def distributerDCOutSensors(
        self, client: EcoflowMQTTClient, mainKey: str, params: dict[str, Any]
    ) -> list[BaseSensorEntity]:
        result: list[BaseSensorEntity] = list()

        for key in params.keys():
            entityKey = mainKey + "." + key + "."
            result = [
                *result,
                # Distributer DC Out
                OutWattsSensorEntity(
                    client, f"{entityKey}dcTotalWatts", "Distributer DC Out Power", True
                ),  # 402
                # OutWattsSensorEntity(client, f"{entityKey}dcChWatt", const.DISTRIBUTER_DC_OUT_POWER, True), # [402, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                # OutWattsSensorEntity(client, f"{entityKey}dcChCur", const.DISTRIBUTER_DC_OUT_POWER, True), # [15401, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                TempSensorEntity(
                    client,
                    f"{entityKey}dcTemp1",
                    "Distributer - DC Temperature 1",
                    True,
                ),  # 38
                TempSensorEntity(
                    client,
                    f"{entityKey}dcTemp2",
                    "Distributer - DC Temperature 2",
                    True,
                ),  # 37
                MiscSensorEntity(
                    client, f"{entityKey}dcChRelay", "DC Out Ch Relay", False
                ),  # 1
                MiscSensorEntity(
                    client, f"{entityKey}dcChSta", "DC Out Enabled", True
                ),  # 4033
                # MiscSensorEntity(client, f"{entityKey}errorCodeAdd", 'DC Out Relay Errors, True), # [40000,40040,40080,40120,40160,40200,40240,40280,40320,40360,40400,40440,40800]
                MiscSensorEntity(
                    client, f"{entityKey}dcSetChSta", "DC Out Set Ch State", False
                ),  # 0
                OutMilliVoltSensorEntity(
                    client, f"{entityKey}dcInVol", "DC Out Voltage", True
                ),  # 26163
            ]
        return result

    def distributerACOutSensors(
        self, client: EcoflowMQTTClient, mainKey: str, params: dict[str, Any]
    ) -> list[BaseSensorEntity]:
        result: list[BaseSensorEntity] = list()

        for key in params.keys():
            entityKey = mainKey + "." + key + "."
            result = [
                *result,
                # Distributer AC Out
                OutWattsSensorEntity(
                    client, f"{entityKey}acTotalWatts", "Distributer AC Out Power", True
                ),  # 165
                # OutWattsSensorEntity(client, f"{entityKey}acChWatt", const.DISTRIBUTER_DC_OUT_POWER, True), # [140, 0, 0, 0, 0, 25]
                # OutWattsSensorEntity(client, f"{entityKey}acChCur", const.DISTRIBUTER_DC_OUT_POWER, True), # [1028, 0, 0, 0, 0, 817]
                OutWattsSensorEntity(
                    client, f"{entityKey}outWatts", "AC Inverter In Power", True
                ),  # 184
                OutMilliVoltSensorEntity(
                    client, f"{entityKey}acInVol", "AC Inverter In Voltage", True
                ),  # 240834
                TempSensorEntity(
                    client, f"{entityKey}acTemp1", "Distributer AC Temperature 1", True
                ),  # 42
                TempSensorEntity(
                    client, f"{entityKey}acTemp2", "Distributer AC Temperature 2", True
                ),  # 42
                # MiscSensorEntity(client, f"{entityKey}errorCodeAdd", 'AC Relay Errors', True), # [30000,30040,30080,30120,30160,30200,30800] One extra likely due to Power Hub AC Out
                MiscSensorEntity(
                    client, f"{entityKey}acChSta", "AC Charge State", True
                ),  # 0
            ]
        return result

    def numbers(self, client: EcoflowMQTTClient) -> list[BaseNumberEntity]:
        return [
            MaxBatteryLevelEntity(
                client,
                "bms_emsStatus.maxChargeSoc",
                const.MAX_CHARGE_LEVEL,
                50,
                100,
                lambda value: {
                    "moduleType": 2,
                    "operateType": "upsConfig",
                    "params": {"maxChgSoc": int(value)},
                },
            ),
            MinBatteryLevelEntity(
                client,
                "bms_emsStatus.minDsgSoc",
                const.MIN_DISCHARGE_LEVEL,
                0,
                30,
                lambda value: {
                    "moduleType": 2,
                    "operateType": "dsgCfg",
                    "params": {"minDsgSoc": int(value)},
                },
            ),
            BatteryBackupLevel(
                client,
                "pd.bpPowerSoc",
                const.BACKUP_RESERVE_LEVEL,
                5,
                100,
                "bms_emsStatus.minDsgSoc",
                "bms_emsStatus.maxChargeSoc",
                lambda value: {
                    "moduleType": 1,
                    "operateType": "watthConfig",
                    "params": {
                        "isConfig": 1,
                        "bpPowerSoc": int(value),
                        "minDsgSoc": 0,
                        "minChgSoc": 0,
                    },
                },
            ),
            MinGenStartLevelEntity(
                client,
                "bms_emsStatus.minOpenOilEb",
                const.GEN_AUTO_START_LEVEL,
                0,
                30,
                lambda value: {
                    "moduleType": 2,
                    "operateType": "openOilSoc",
                    "params": {"openOilSoc": value},
                },
            ),
            MaxGenStopLevelEntity(
                client,
                "bms_emsStatus.maxCloseOilEb",
                const.GEN_AUTO_STOP_LEVEL,
                50,
                100,
                lambda value: {
                    "moduleType": 2,
                    "operateType": "closeOilSoc",
                    "params": {"closeOilSoc": value},
                },
            ),
            ChargingPowerEntity(
                client,
                "mppt.cfgChgWatts",
                const.AC_CHARGING_POWER,
                200,
                1200,
                lambda value: {
                    "moduleType": 5,
                    "operateType": "acChgCfg",
                    "params": {"chgWatts": int(value), "chgPauseFlag": 255},
                },
            ),
        ]

    def switches(self, client: EcoflowMQTTClient) -> list[BaseSwitchEntity]:
        return [
            BeeperEntity(
                client,
                "mppt.beepState",
                const.BEEPER,
                lambda value: {
                    "moduleType": 5,
                    "operateType": "quietMode",
                    "params": {"enabled": value},
                },
            ),
            EnabledEntity(
                client,
                "pd.dcOutState",
                const.USB_ENABLED,
                lambda value: {
                    "moduleType": 15362,
                    "operateType": "chSwitch",
                    "params": {"bitsSwSta": value},
                },
            ),
            EnabledEntity(
                client,
                "pd.dcOutState",
                const.USB_ENABLED,
                lambda value: {
                    "moduleType": 1,
                    "operateType": "dcOutCfg",
                    "params": {"enabled": value},
                },
            ),
            EnabledEntity(
                client,
                "pd.acAutoOutConfig",
                const.AC_ALWAYS_ENABLED,
                lambda value, params: {
                    "moduleType": 1,
                    "operateType": "acAutoOutConfig",
                    "params": {
                        "acAutoOutConfig": value,
                        "minAcOutSoc": int(params.get("bms_emsStatus.minDsgSoc", 0))
                        + 5,
                    },
                },
            ),
            EnabledEntity(
                client,
                "pd.pvChgPrioSet",
                const.PV_PRIO,
                lambda value: {
                    "moduleType": 1,
                    "operateType": "pvChangePrio",
                    "params": {"pvChangeSet": value},
                },
            ),
            EnabledEntity(
                client,
                "mppt.cfgAcEnabled",
                const.AC_ENABLED,
                lambda value: {
                    "moduleType": 5,
                    "operateType": "acOutCfg",
                    "params": {
                        "enabled": value,
                        "out_voltage": -1,
                        "out_freq": 255,
                        "xboost": 255,
                    },
                },
            ),
            EnabledEntity(
                client,
                "mppt.cfgAcXboost",
                const.XBOOST_ENABLED,
                lambda value: {
                    "moduleType": 5,
                    "operateType": "acOutCfg",
                    "params": {
                        "enabled": 255,
                        "out_voltage": -1,
                        "out_freq": 255,
                        "xboost": value,
                    },
                },
            ),
            EnabledEntity(
                client,
                "pd.carState",
                const.DC_ENABLED,
                lambda value: {
                    "moduleType": 5,
                    "operateType": "mpptCar",
                    "params": {"enabled": value},
                },
            ),
            EnabledEntity(
                client,
                "pd.bpPowerSoc",
                const.BP_ENABLED,
                lambda value: {
                    "moduleType": 1,
                    "operateType": "watthConfig",
                    "params": {
                        "bpPowerSoc": value,
                        "minChgSoc": 0,
                        "isConfig": value,
                        "minDsgSoc": 0,
                    },
                },
            ),
        ]

    def selects(self, client: EcoflowMQTTClient) -> list[BaseSelectEntity]:
        return [
            DictSelectEntity(
                client,
                "mppt.dcChgCurrent",
                const.DC_CHARGE_CURRENT,
                const.DC_CHARGE_CURRENT_OPTIONS,
                lambda value: {
                    "moduleType": 5,
                    "operateType": "dcChgCfg",
                    "params": {"dcChgCfg": value},
                },
            ),
            TimeoutDictSelectEntity(
                client,
                "pd.lcdOffSec",
                const.SCREEN_TIMEOUT,
                const.SCREEN_TIMEOUT_OPTIONS,
                lambda value: {
                    "moduleType": 1,
                    "operateType": "lcdCfg",
                    "params": {"brighLevel": 255, "delayOff": value},
                },
            ),
            TimeoutDictSelectEntity(
                client,
                "pd.standbyMin",
                const.UNIT_TIMEOUT,
                const.UNIT_TIMEOUT_OPTIONS,
                lambda value: {
                    "moduleType": 1,
                    "operateType": "standbyTime",
                    "params": {"standbyMin": value},
                },
            ),
            TimeoutDictSelectEntity(
                client,
                "mppt.acStandbyMins",
                const.AC_TIMEOUT,
                const.AC_TIMEOUT_OPTIONS,
                lambda value: {
                    "moduleType": 5,
                    "operateType": "standbyTime",
                    "params": {"standbyMins": value},
                },
            ),
            TimeoutDictSelectEntity(
                client,
                "mppt.carStandbyMin",
                const.DC_TIMEOUT,
                const.DC_TIMEOUT_OPTIONS,
                lambda value: {
                    "moduleType": 5,
                    "operateType": "carStandby",
                    "params": {"standbyMins": value},
                },
            ),
        ]

    def migrate(self, version) -> list[EntityMigration]:
        if version == 2:
            return [EntityMigration("pd.soc", Platform.SENSOR, MigrationAction.REMOVE)]
        return []
