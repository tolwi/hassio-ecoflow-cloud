from homeassistant.const import Platform

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


class PowerKit(BaseDevice):
    def sensors(self, client: EcoflowMQTTClient) -> list[BaseSensorEntity]:
        return [
            # TODO: Figure out some of the values
            # TODO: Add in config data
            # TODO: Add value editing
            # TODO: Support batteries
            # TODO: Check AC Input
            # TODO: Check DC In via Smart Generator
            # TODO: Attempt alternator charging
            # BMS
            LevelSensorEntity(client, "iclow.realSoc", const.MAIN_BATTERY_LEVEL),
            MiscSensorEntity(client, "iclow.errCode", "BMS Error Code"),  # 0
            MiscSensorEntity(client, "iclow.warn_code", "BMS Warning Code"),  # 0
            MiscSensorEntity(client, "iclow.event_code", "BMS Event Code", False),  # 0
            TempSensorEntity(client, "iclow.dcTemp", "BMS DC Temperature", True),  # 37
            ChargingStateSensorEntity(
                client, "iclow.chgDsgState", "BMS Charge Discharge State", False
            ),  # 1
            MilliVoltSensorEntity(
                client, "iclow.chgBatVol", "BMS Charge Voltage", False
            ),  # 54161
            MiscSensorEntity(client, "iclow.chgType", "BMS Charge Type", False),  # 1
            MiscSensorEntity(
                client, "iclow.chgInType", "BMS Charge In Type", False
            ),  # 1
            MiscSensorEntity(client, "iclow.chrgFlag", "BMS Charge Flag", False),  # 1
            AmpSensorEntity(
                client, "iclow.maxChgCurr", "BMS Max Charge Current", False
            ),  # 0
            MiscSensorEntity(
                client, "iclow.extKitType", "BMS External Kit Type", False
            ),  # 0
            AmpSensorEntity(client, "iclow.bmsChgCurr", "BMS Bus Current", False),
            DeciMilliVoltSensorEntity(
                client, "iclow.busVol", "BMS Bus Voltage", True
            ),  # 454198
            MiscSensorEntity(client, "iclow.lsplFlag", "BMS LSPL Flag", False),  # 0
            MiscSensorEntity(client, "iclow.protectState", "BMS Protect State"),  # 0
            AmpSensorEntity(
                client, "iclow.batCurr", "BMS Battery Current", False
            ),  # 386
            FanSensorEntity(client, "iclow.fanLevel", "Fan Level", False),  # 2
            # MPPT
            InRawTotalWattsSolarSensorEntity(
                client, "kitscc.batWatts", const.SOLAR_AND_ALT_IN_POWER, True
            ),
            AmpSensorEntity(client, "kitscc.batCurr", "Solar Battery Current", True),
            MilliVoltSensorEntity(
                client, "kitscc.batVol", "Solar Battery Voltage", True
            ),
            InWattsSolarSensorEntity(
                client, "kitscc.pv1InWatts", const.SOLAR_2_IN_POWER, True
            ),
            MilliVoltSensorEntity(
                client, "kitscc.pv1InVol", "Solar (2) In Voltage", True
            ),
            AmpSensorEntity(client, "kitscc.pv1InCurr", "Solar (2) In Current", True),
            MiscSensorEntity(client, "kitscc.pv1ErrCode", "Solar (2) Error Code", True),
            MiscSensorEntity(client, "kitscc.pv1_hot_out", "Solar (2) Hot Out", False),
            MiscSensorEntity(
                client, "kitscc.pv1InputFlag", "Solar (2) Input Flag", False
            ),
            MiscSensorEntity(
                client, "kitscc.pv1WorkMode", "Solar (2) Work Mode", False
            ),
            MiscSensorEntity(client, "kitscc.mppt1SwSta", "Solar (2) Enabled", True),
            MiscSensorEntity(
                client, "kitscc.eventCode1", "Solar (2) Event Code", False
            ),
            MiscSensorEntity(client, "kitscc.warnCode1", "Solar (2) Warn Code", True),
            TempSensorEntity(client, "kitscc.hs1Temp", "Solar (2) Temperature", True),
            InWattsSolarSensorEntity(
                client, "kitscc.pv2InWatts", "Solar (3) In Power", True
            ),
            MilliVoltSensorEntity(
                client, "kitscc.pv2InVol", "Solar (3) In Voltage", True
            ),
            AmpSensorEntity(client, "kitscc.pv2InCurr", "Solar (3) In Current", True),
            MiscSensorEntity(client, "kitscc.pv2ErrCode", "Solar (3) Error Code", True),
            MiscSensorEntity(client, "kitscc.pv2_hot_out", "Solar (3) Hot Out", False),
            MiscSensorEntity(
                client, "kitscc.pv2InputFlag", "Solar (3) Input Flag", False
            ),
            MiscSensorEntity(
                client, "kitscc.pv2WorkMode", "Solar (3) Work Mode", False
            ),
            MiscSensorEntity(client, "kitscc.mppt2SwSta", "Solar (3) Enabled", True),
            MiscSensorEntity(
                client, "kitscc.eventCode2", "Solar (3) Event Code", False
            ),
            MiscSensorEntity(client, "kitscc.warnCode2", "Solar (3) Warn Code", True),
            TempSensorEntity(client, "kitscc.hs2Temp", "Solar (3) Temperature", True),
            AmpSensorEntity(
                client, "kitscc.chgEnergy", "Solar Total Charge Current", False
            ),  # Not in use
            AmpSensorEntity(
                client, "kitscc.dayEnergy", "Solar Energy for Day", False
            ),  # Not in use
            # Power Hub DC Out
            AmpSensorEntity(
                client, "bbcout.ldOutCurr", "DC Out Current", True
            ),  # 14999 DC output to distributer
            OutWattsSensorEntity(
                client, "bbcout.ldOutWatts", "DC Out Power", True
            ),  # 396 DC output to distributer
            OutWattsSensorEntity(
                client, "bbcout.batWatts", "DC Out Battery Power", True
            ),  # 425 DC output from battery including BMS and Distributer power
            AmpSensorEntity(
                client, "bbcout.l1Curr", "DC 1 Out Battery Current", False
            ),  # 6990 DC output from battery including BMS and Distributer power
            AmpSensorEntity(
                client, "bbcout.l2Curr", "DC 2 Out Battery Current", False
            ),  # 6869 DC output from battery including BMS and Distributer power
            MilliVoltSensorEntity(
                client, "bbcout.batVol", "DC Out Battery Voltage", False
            ),  # 54136 DC output from battery including BMS and Distributer power
            # Power Hub DC In
            MiscSensorEntity(
                client, "bbcin.workMode", "DC Work Mode 1", False
            ),  # 54136 DC input
            MiscSensorEntity(
                client, "bbcin.workMode2", "DC Work Mode 2", False
            ),  # 54136 DC input
            MiscSensorEntity(
                client, "bbcin.inHwTpe", "DC In Hardware Type", True
            ),  # 54136 DC input
            MiscSensorEntity(
                client, "bbcin.bpOnlinePos", "DC Online Pos", False
            ),  # 54136 DC input
            MiscSensorEntity(
                client, "bbcin.dayEnergy", "DC In Energy for Day", False
            ),  # 54136 Not in use
            MiscSensorEntity(
                client, "bbcin.shakeCtrlDisable", "Disable Shake Control", False
            ),  # 54136 DC input
            MiscSensorEntity(
                client, "bbcin.isCarMoving", "Is Car Moving", False
            ),  # 54136 DC input
            MiscSensorEntity(
                client, "bbcin.eventCode", "DC In Event Code", False
            ),  # 0 DC input
            MiscSensorEntity(
                client, "bbcin.warnCode", "DC In Warning Code", True
            ),  # 0 DC input
            MiscSensorEntity(
                client, "bbcin.errCode", "DC In Error Code", True
            ),  # 10000 DC input
            OutWattsSensorEntity(
                client, "bbcin.batWatts", "DC In Battery Power", True
            ),  # 4 DC input
            AmpSensorEntity(
                client, "bbcin.batCurr", "DC In Battery Current", True
            ),  # 78 DC input
            MilliVoltSensorEntity(
                client, "bbcin.batVol", "DC In Battery Voltage", True
            ),  # 53438 DC input
            MiscSensorEntity(
                client, "bbcin.allowDsgOn", "DC Allow Discharge", True
            ),  # 1 DC input
            AmpSensorEntity(
                client, "bbcin.dsgEnergy", "DC Discharge Energy", False
            ),  # 789 Unsure what this one is. Could be some kind of total
            MiscSensorEntity(
                client, "bbcin.dcInState", "DC In State", True
            ),  # 0 DC input
            OutWattsSensorEntity(
                client, "bbcin.dcInWatts", "DC In Power", True
            ),  # 0 DC input
            AmpSensorEntity(
                client, "bbcin.dcInCurr", "DC In Current", True
            ),  # 0 DC input
            MilliVoltSensorEntity(
                client, "bbcin.dcInVol", "DC In Voltage", True
            ),  # 0 DC input
            MiscSensorEntity(
                client, "bbcin.chgPause", "DC Charge Paused", True
            ),  # 1 DC input
            MiscSensorEntity(
                client, "bbcin.chgType", "DC Charge Type", True
            ),  # 0 DC input
            AmpSensorEntity(
                client, "bbcin.chgMaxCurr", "DC Charge Max Current", True
            ),  # 30000 DC input
            MiscSensorEntity(
                client, "bbcin.chargeMode", "DC Charge Mode", True
            ),  # 0 DC input
            AmpSensorEntity(
                client, "bbcin.l1Curr", "DC In L1 Current", False
            ),  # -5 DC input
            AmpSensorEntity(
                client, "bbcin.l2Curr", "DC In L2 Current", False
            ),  # -45 DC input
            TempSensorEntity(
                client, "bbcin.hs1Temp", "DC In HS1 Temperature", True
            ),  # 32 DC input
            TempSensorEntity(
                client, "bbcin.hs2Temp", "DC In HS2 Temperature", True
            ),  # 32 DC input
            TempSensorEntity(
                client, "bbcin.pcbTemp", "DC In PCB Temperature", True
            ),  # 0 DC input
            MiscSensorEntity(
                client, "bbcin.altCableUnit", "Alt. Cable Unit", True
            ),  # 0 DC input
            MiscSensorEntity(
                client, "bbcin.altCableLen", "Alt. Cable Length", True
            ),  # 600 DC input
            MiscSensorEntity(
                client, "bbcin.altVoltLmt", "Alt. Cable Voltage Limit", True
            ),  # 130 DC input
            MiscSensorEntity(
                client, "bbcin.altVoltLmtEn", "Alt. Voltage Limit En", True
            ),  # 1 DC input
            # Distributer DC Out
            OutWattsSensorEntity(
                client, "lddc.dcTotalWatts", "Distributer DC Out Power", True
            ),  # 402
            # OutWattsSensorEntity(client, "lddc.dcChWatt", const.DISTRIBUTER_DC_OUT_POWER, True), # [402, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            # OutWattsSensorEntity(client, "lddc.dcChCur", const.DISTRIBUTER_DC_OUT_POWER, True), # [15401, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            TempSensorEntity(
                client, "lddc.dcTemp1", "Distributer - DC Temperature 1", True
            ),  # 38
            TempSensorEntity(
                client, "lddc.dcTemp2", "Distributer - DC Temperature 2", True
            ),  # 37
            MiscSensorEntity(client, "lddc.dcChRelay", "DC Out Ch Relay", False),  # 1
            MiscSensorEntity(client, "lddc.dcChSta", "DC Out Enabled", True),  # 4033
            # MiscSensorEntity(client, "lddc.errorCodeAdd", 'DC Out Relay Errors, True), # [40000,40040,40080,40120,40160,40200,40240,40280,40320,40360,40400,40440,40800]
            MiscSensorEntity(
                client, "lddc.dcSetChSta", "DC Out Set Ch State", False
            ),  # 0
            OutMilliVoltSensorEntity(
                client, "lddc.dcInVol", "DC Out Voltage", True
            ),  # 26163
            # Power Hub AC Out
            OutMilliVoltSensorEntity(
                client, "ichigh.outVol", "AC Out Voltage", True
            ),  # 240070
            # MiscSensorEntity(client, "ichigh.outVa", 'AC Out VA', True), # 361
            AmpSensorEntity(client, "ichigh.outCurr", "AC Out Current", True),  # 2432
            MiscSensorEntity(client, "ichigh.invType", "AC Inverter Type", False),  # 0
            FrequencySensorEntity(
                client, "ichigh.inFreq", "AC In Frequency", True
            ),  # 0
            OutWattsSensorEntity(client, "ichigh.inWatts", "AC In Power", True),  # 0
            AmpSensorEntity(client, "ichigh.inCurr", "AC In Current", True),  # 0
            OutMilliVoltSensorEntity(
                client, "ichigh.inVol", "AC In Voltage", True
            ),  # 0
            MiscSensorEntity(client, "ichigh.invSwSta", "AC Out Enabled", True),  # 1
            TempSensorEntity(
                client, "ichigh.acTemp", "AC Inverter Temperature", True
            ),  # 1
            OutWattsSensorEntity(
                client, "ichigh.outWatts", "AC Out Power", True
            ),  # 165
            OutWattsSensorEntity(
                client, "ichigh.ch2Watt", "AC Outlet Power", True
            ),  # 165
            AmpSensorEntity(client, "ichigh.outAmp2", "AC Outlet Current", True),  # 0
            FrequencySensorEntity(
                client, "ichigh.cfgOutFreq", "AC Config Out Frequency", False
            ),  # 1
            FrequencySensorEntity(
                client, "ichigh.outFreq", "AC Out Frequency", True
            ),  # 1
            MiscSensorEntity(
                client, "ichigh.standbyTime", "AC Standby Time", False
            ),  # 1
            OutWattsSensorEntity(
                client, "ichigh.inputWhInDay", "AC Input Day Power", False
            ),  # Not in use
            OutWattsSensorEntity(
                client, "ichigh.outputWhInDay", "AC Output Day Power", False
            ),  # Not in use
            # Distributer AC Out
            OutWattsSensorEntity(
                client, "ldac.acTotalWatts", "Distributer AC Out Power", True
            ),  # 165
            # OutWattsSensorEntity(client, "ldac.acChWatt", const.DISTRIBUTER_DC_OUT_POWER, True), # [140, 0, 0, 0, 0, 25]
            # OutWattsSensorEntity(client, "ldac.acChCur", const.DISTRIBUTER_DC_OUT_POWER, True), # [1028, 0, 0, 0, 0, 817]
            OutWattsSensorEntity(
                client, "ldac.outWatts", "AC Inverter In Power", True
            ),  # 184
            OutMilliVoltSensorEntity(
                client, "ldac.acInVol", "AC Inverter In Voltage", True
            ),  # 240834
            TempSensorEntity(
                client, "ldac.acTemp1", "Distributer AC Temperature 1", True
            ),  # 42
            TempSensorEntity(
                client, "ldac.acTemp2", "Distributer AC Temperature 2", True
            ),  # 42
            # MiscSensorEntity(client, "ldac.errorCodeAdd", 'AC Relay Errors', True), # [30000,30040,30080,30120,30160,30200,30800] One extra likely due to Power Hub AC Out
            MiscSensorEntity(client, "ldac.acChSta", "AC Charge State", True),  # 0
        ]

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
