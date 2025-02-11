from homeassistant.const import Platform
from typing import Any, Callable, cast

from ...DeviceData import DeviceData, ChildDeviceData
from custom_components.ecoflow_cloud.api import EcoflowApiClient

from .. import EcoflowDeviceInfo, const, BaseDevice
from ...entities import (
    BaseSensorEntity,
    BaseNumberEntity,
    BaseSwitchEntity,
    BaseSelectEntity,
)
from ...number import (
    AcChargingPowerInAmpereEntity,
    ChargingPowerEntity,
    MinBatteryLevelEntity,
    MaxBatteryLevelEntity,
    MaxGenStopLevelEntity,
    MinGenStartLevelEntity,
    BatteryBackupLevel,
)
from ...select import DictSelectEntity, TimeoutDictSelectEntity
from ...sensor import (
    AmpSensorEntity,
    ChargingStateSensorEntity,
    DeciMilliVoltSensorEntity,
    FanSensorEntity,
    FrequencySensorEntity,
    InRawTotalWattsSolarSensorEntity,
    InWattsSolarSensorEntity,
    LevelSensorEntity,
    MiscSensorEntity,
    OutAmpSensorEntity,
    RemainSensorEntity,
    TempSensorEntity,
    CyclesSensorEntity,
    InWattsSensorEntity,
    OutWattsSensorEntity,
    QuotaStatusSensorEntity,
    MilliVoltSensorEntity,
    InMilliVoltSensorEntity,
    OutMilliVoltSensorEntity,
    CapacitySensorEntity,
)
from ...switch import BeeperEntity, BitMaskEnableEntity, EnabledEntity
import json
from homeassistant.core import HomeAssistant


class PowerKit(BaseDevice):
    def __init__(self, device_info: EcoflowDeviceInfo, device_data: DeviceData) -> None:
        self.dcSwitchFunction: Callable[[str, int], dict[str, Any]] = (
            lambda sn, value: {
                "id": 123456789,
                "version": "1.0",
                "moduleSn": sn,
                "moduleType": 15362,
                "operateType": "chSwitch",
                "params": {
                    "bitsSwSta": value,
                },
            }
        )
        """
        Variable contains a function to set the state of the DC switch of the DC distribution panel
        """
        if device_data.device_type != "PowerKit":
            childData: ChildDeviceData = cast(ChildDeviceData, device_data)
            if device_data.device_type.startswith("bp"):
                device_data.display_name = (
                    f"PowerKit Battery ({childData.parent.sn}.{childData.sn})"
                )
            elif device_data.device_type == "iclow":
                device_data.display_name = (
                    f"PowerKit Bms ({childData.parent.sn}.{childData.sn})"
                )
            elif device_data.device_type == "kitscc":
                device_data.display_name = (
                    f"PowerKit Mppt ({childData.parent.sn}.{childData.sn})"
                )
            elif device_data.device_type == "bbcout":
                device_data.display_name = (
                    f"PowerKit Hub DC Out ({childData.parent.sn}.{childData.sn})"
                )
            elif device_data.device_type == "bbcin":
                device_data.display_name = (
                    f"PowerKit Hub DC In ({childData.parent.sn}.{childData.sn})"
                )
            elif device_data.device_type == "lddc":
                device_data.display_name = f"PowerKit Distrubution Panel DC Out ({childData.parent.sn}.{childData.sn})"
            elif device_data.device_type == "ichigh":
                device_data.display_name = (
                    f"PowerKit Hub AC Out ({childData.parent.sn}.{childData.sn})"
                )
            elif device_data.device_type == "ldac":
                device_data.display_name = f"PowerKit Distrubution Panel AC Out ({childData.parent.sn}.{childData.sn})"
        super().__init__(device_info, device_data)

    def flat_json(self):
        return False

    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        params = self.data.params

        if self.device_data.device_type.startswith("bp"):
            return self.batterieSensors(client, self.device_data.sn, params)
        elif self.device_data.device_type == "iclow":
            return self.bmsSensors(client, self.device_data.sn, params)
        elif self.device_data.device_type == "kitscc":
            return self.mpptSensors(client, self.device_data.sn, params)
        elif self.device_data.device_type == "bbcout":
            return self.powerHubDCOutSensors(client, self.device_data.sn, params)
        elif self.device_data.device_type == "bbcin":
            return self.powerHubDCInSensors(client, self.device_data.sn, params)
        elif self.device_data.device_type == "lddc":
            return self.distributerDCOutSensors(client, self.device_data.sn, params)
        elif self.device_data.device_type == "ichigh":
            return self.powerHubACOutSensors(client, self.device_data.sn, params)
        elif self.device_data.device_type == "ldac":
            return self.distributerACOutSensors(client, self.device_data.sn, params)
        return []
        # TODO: Check DC In via Smart Generator

    def batterieSensors(
        self, client: EcoflowApiClient, mainKey: str, params: dict[str, Any]
    ) -> list[BaseSensorEntity]:
        entityKey = mainKey + "."
        return [
            AmpSensorEntity(
                client,
                self,
                "amp",
                f"Ampere battery ({mainKey})",
                True,
                True,
            ),
            CapacitySensorEntity(
                client, self, f"fullCap", f"max Capacity battery ({mainKey})"
            ),
            LevelSensorEntity(
                client,
                self,
                "soc",
                f"State of Charge (soc) battery ({mainKey})",
            ),
            MilliVoltSensorEntity(
                client,
                self,
                "minCellVol",
                f"minimal cell voltage battery ({mainKey})",
            ),
            CyclesSensorEntity(
                client,
                self,
                "cycles",
                f"full cycle count battery ({mainKey})",
            ),
            MilliVoltSensorEntity(
                client, self, "vol", f"current voltage battery ({mainKey})"
            ),
            CapacitySensorEntity(
                client,
                self,
                "remainCap",
                f"current Capacity battery ({mainKey})",
            ),
            InWattsSensorEntity(
                client,
                self,
                "inWatts",
                f"Charing power battery ({mainKey})",
            ),
            TempSensorEntity(client, self, "temp", f"temperatur battery ({mainKey})"),
            RemainSensorEntity(
                client,
                self,
                "remainTime",
                f"remaining time battery ({mainKey})",
            ),
            MilliVoltSensorEntity(
                client,
                self,
                "maxCellVol",
                f"maximum cell voltage battery ({mainKey})",
            ),
            OutWattsSensorEntity(
                client,
                self,
                "outWatts",
                f"discharing power battery ({mainKey})",
            ),
        ]

    def bmsSensors(
        self, client: EcoflowApiClient, mainKey: str, params: dict[str, Any]
    ) -> list[BaseSensorEntity]:
        entityKey = mainKey + "."
        return [
            LevelSensorEntity(client, self, "realSoc", const.MAIN_BATTERY_LEVEL),
            MiscSensorEntity(client, self, "errCode", "BMS Error Code"),  # 0
            MiscSensorEntity(client, self, "warn_code", "BMS Warning Code"),  # 0
            MiscSensorEntity(client, self, "event_code", "BMS Event Code", False),  # 0
            TempSensorEntity(client, self, "dcTemp", "BMS DC Temperature", True),  # 37
            ChargingStateSensorEntity(
                client,
                self,
                "chgDsgState",
                "BMS Charge Discharge State",
                False,
            ),  # 1
            MilliVoltSensorEntity(
                client, self, "chgBatVol", "BMS Charge Voltage", False
            ),  # 54161
            MiscSensorEntity(client, self, "chgType", "BMS Charge Type", False),  # 1
            MiscSensorEntity(
                client, self, "chgInType", "BMS Charge In Type", False
            ),  # 1
            MiscSensorEntity(client, self, "chrgFlag", "BMS Charge Flag", False),  # 1
            AmpSensorEntity(
                client,
                self,
                "maxChgCurr",
                "BMS Max Charge Current",
                False,
            ),  # 0
            MiscSensorEntity(
                client,
                self,
                "extKitType",
                "BMS External Kit Type",
                False,
            ),  # 0
            AmpSensorEntity(client, self, "bmsChgCurr", "BMS Bus Current", False),
            DeciMilliVoltSensorEntity(
                client, self, "busVol", "BMS Bus Voltage", True
            ),  # 454198
            MiscSensorEntity(client, self, "lsplFlag", "BMS LSPL Flag", False),  # 0
            MiscSensorEntity(client, self, "protectState", "BMS Protect State"),  # 0
            AmpSensorEntity(
                client, self, "batCurr", "BMS Battery Current", False
            ),  # 386
            FanSensorEntity(client, self, "fanLevel", "Fan Level", False),  # 2
        ]

    def mpptSensors(
        self, client: EcoflowApiClient, mainKey: str, params: dict[str, Any]
    ) -> list[BaseSensorEntity]:
        entityKey = mainKey + "."
        return [
            # MPPT
            InRawTotalWattsSolarSensorEntity(
                client,
                self,
                "batWatts",
                const.SOLAR_AND_ALT_IN_POWER,
                True,
            ),
            AmpSensorEntity(client, self, "batCurr", "Solar Battery Current", True),
            MilliVoltSensorEntity(
                client, self, "batVol", "Solar Battery Voltage", True
            ),
            InWattsSolarSensorEntity(
                client, self, "pv1InWatts", const.SOLAR_2_IN_POWER, True
            ),
            MilliVoltSensorEntity(
                client, self, "pv1InVol", "Solar (2) In Voltage", True
            ),
            AmpSensorEntity(client, self, "pv1InCurr", "Solar (2) In Current", True),
            MiscSensorEntity(client, self, "pv1ErrCode", "Solar (2) Error Code", True),
            MiscSensorEntity(client, self, "pv1_hot_out", "Solar (2) Hot Out", False),
            MiscSensorEntity(
                client,
                self,
                "pv1InputFlag",
                "Solar (2) Input Flag",
                False,
            ),
            MiscSensorEntity(
                client,
                self,
                "pv1WorkMode",
                "Solar (2) Work Mode",
                False,
            ),
            MiscSensorEntity(client, self, "mppt1SwSta", "Solar (2) Enabled", True),
            MiscSensorEntity(
                client,
                self,
                "eventCode1",
                "Solar (2) Event Code",
                False,
            ),
            MiscSensorEntity(client, self, "warnCode1", "Solar (2) Warn Code", True),
            TempSensorEntity(client, self, "hs1Temp", "Solar (2) Temperature", True),
            InWattsSolarSensorEntity(
                client, self, "pv2InWatts", "Solar (3) In Power", True
            ),
            MilliVoltSensorEntity(
                client, self, "pv2InVol", "Solar (3) In Voltage", True
            ),
            AmpSensorEntity(client, self, "pv2InCurr", "Solar (3) In Current", True),
            MiscSensorEntity(client, self, "pv2ErrCode", "Solar (3) Error Code", True),
            MiscSensorEntity(client, self, "pv2_hot_out", "Solar (3) Hot Out", False),
            MiscSensorEntity(
                client,
                self,
                "pv2InputFlag",
                "Solar (3) Input Flag",
                False,
            ),
            MiscSensorEntity(
                client,
                self,
                "pv2WorkMode",
                "Solar (3) Work Mode",
                False,
            ),
            MiscSensorEntity(client, self, "mppt2SwSta", "Solar (3) Enabled", True),
            MiscSensorEntity(
                client,
                self,
                "eventCode2",
                "Solar (3) Event Code",
                False,
            ),
            MiscSensorEntity(client, self, "warnCode2", "Solar (3) Warn Code", True),
            TempSensorEntity(client, self, "hs2Temp", "Solar (3) Temperature", True),
            AmpSensorEntity(
                client,
                self,
                "chgEnergy",
                "Solar Total Charge Current",
                False,
            ),  # Not in use
            AmpSensorEntity(
                client, self, "dayEnergy", "Solar Energy for Day", False
            ),  # Not in use
        ]

    def powerHubDCOutSensors(
        self, client: EcoflowApiClient, mainKey: str, params: dict[str, Any]
    ) -> list[BaseSensorEntity]:
        entityKey = mainKey + "."
        return [
            # Power Hub DC Out
            AmpSensorEntity(
                client, self, "ldOutCurr", "DC Out Current", True
            ),  # 14999 DC output to distributer
            OutWattsSensorEntity(
                client, self, "ldOutWatts", "DC Out Power", True
            ),  # 396 DC output to distributer
            OutWattsSensorEntity(
                client, self, "batWatts", "DC Out Battery Power", True
            ),  # 425 DC output from battery including BMS and Distributer power
            AmpSensorEntity(
                client,
                self,
                "l1Curr",
                "DC 1 Out Battery Current",
                False,
            ),  # 6990 DC output from battery including BMS and Distributer power
            AmpSensorEntity(
                client,
                self,
                "l2Curr",
                "DC 2 Out Battery Current",
                False,
            ),  # 6869 DC output from battery including BMS and Distributer power
            MilliVoltSensorEntity(
                client, self, "batVol", "DC Out Battery Voltage", False
            ),  # 54136 DC output from battery including BMS and Distributer power
        ]

    def powerHubDCInSensors(
        self, client: EcoflowApiClient, mainKey: str, params: dict[str, Any]
    ) -> list[BaseSensorEntity]:
        entityKey = mainKey + "."
        return [
            # Power Hub DC In
            MiscSensorEntity(
                client, self, "workMode", "DC Work Mode 1", False
            ),  # 54136 DC input
            MiscSensorEntity(
                client, self, "workMode2", "DC Work Mode 2", False
            ),  # 54136 DC input
            MiscSensorEntity(
                client, self, "inHwTpe", "DC In Hardware Type", True
            ),  # 54136 DC input
            MiscSensorEntity(
                client, self, "bpOnlinePos", "DC Online Pos", False
            ),  # 54136 DC input
            MiscSensorEntity(
                client, self, "dayEnergy", "DC In Energy for Day", False
            ),  # 54136 Not in use
            MiscSensorEntity(
                client,
                self,
                "shakeCtrlDisable",
                "Disable Shake Control",
                False,
            ),  # 54136 DC input
            MiscSensorEntity(
                client, self, "isCarMoving", "Is Car Moving", False
            ),  # 54136 DC input
            MiscSensorEntity(
                client, self, "eventCode", "DC In Event Code", False
            ),  # 0 DC input
            MiscSensorEntity(
                client, self, "warnCode", "DC In Warning Code", True
            ),  # 0 DC input
            MiscSensorEntity(
                client, self, "errCode", "DC In Error Code", True
            ),  # 10000 DC input
            OutWattsSensorEntity(
                client, self, "batWatts", "DC In Battery Power", True
            ),  # 4 DC input
            AmpSensorEntity(
                client, self, "batCurr", "DC In Battery Current", True
            ),  # 78 DC input
            MilliVoltSensorEntity(
                client, self, "batVol", "DC In Battery Voltage", True
            ),  # 53438 DC input
            MiscSensorEntity(
                client, self, "allowDsgOn", "DC Allow Discharge", True
            ),  # 1 DC input
            AmpSensorEntity(
                client, self, "dsgEnergy", "DC Discharge Energy", False
            ),  # 789 Unsure what this one is. Could be some kind of total
            MiscSensorEntity(
                client, self, "dcInState", "DC In State", True
            ),  # 0 DC input
            OutWattsSensorEntity(
                client, self, "dcInWatts", "DC In Power", True
            ),  # 0 DC input
            AmpSensorEntity(
                client, self, "dcInCurr", "DC In Current", True
            ),  # 0 DC input
            MilliVoltSensorEntity(
                client, self, "dcInVol", "DC In Voltage", True
            ),  # 0 DC input
            MiscSensorEntity(
                client, self, "chgPause", "DC Charge Paused", True
            ),  # 1 DC input
            MiscSensorEntity(
                client, self, "chgType", "DC Charge Type", True
            ),  # 0 DC input
            AmpSensorEntity(
                client,
                self,
                "chgMaxCurr",
                "DC Charge Max Current",
                True,
            ),  # 30000 DC input
            MiscSensorEntity(
                client, self, "chargeMode", "DC Charge Mode", True
            ),  # 0 DC input
            AmpSensorEntity(
                client, self, "l1Curr", "DC In L1 Current", False
            ),  # -5 DC input
            AmpSensorEntity(
                client, self, "l2Curr", "DC In L2 Current", False
            ),  # -45 DC input
            TempSensorEntity(
                client, self, "hs1Temp", "DC In HS1 Temperature", True
            ),  # 32 DC input
            TempSensorEntity(
                client, self, "hs2Temp", "DC In HS2 Temperature", True
            ),  # 32 DC input
            TempSensorEntity(
                client, self, "pcbTemp", "DC In PCB Temperature", True
            ),  # 0 DC input
            MiscSensorEntity(
                client, self, "altCableUnit", "Alt. Cable Unit", True
            ),  # 0 DC input
            MiscSensorEntity(
                client, self, "altCableLen", "Alt. Cable Length", True
            ),  # 600 DC input
            MiscSensorEntity(
                client,
                self,
                "altVoltLmt",
                "Alt. Cable Voltage Limit",
                True,
            ),  # 130 DC input
            MiscSensorEntity(
                client,
                self,
                "altVoltLmtEn",
                "Alt. Voltage Limit En",
                True,
            ),  # 1 DC input
        ]

    def powerHubACOutSensors(
        self, client: EcoflowApiClient, mainKey: str, params: dict[str, Any]
    ) -> list[BaseSensorEntity]:
        entityKey = mainKey + "."
        return [
            # Power Hub AC Out
            OutMilliVoltSensorEntity(
                client, self, "outVol", "AC Out Voltage", True
            ),  # 240070
            # MiscSensorEntity(client, "outVa", 'AC Out VA', True), # 361
            AmpSensorEntity(client, self, "outCurr", "AC Out Current", True),  # 2432
            MiscSensorEntity(client, self, "invType", "AC Inverter Type", False),  # 0
            FrequencySensorEntity(client, self, "inFreq", "AC In Frequency", True),  # 0
            OutWattsSensorEntity(client, self, "inWatts", "AC In Power", True),  # 0
            AmpSensorEntity(client, self, "inCurr", "AC In Current", True),  # 0
            OutMilliVoltSensorEntity(client, self, "inVol", "AC In Voltage", True),  # 0
            MiscSensorEntity(client, self, "invSwSta", "AC Out Enabled", True),  # 1
            TempSensorEntity(
                client, self, "acTemp", "AC Inverter Temperature", True
            ),  # 1
            OutWattsSensorEntity(client, self, "outWatts", "AC Out Power", True),  # 165
            OutWattsSensorEntity(
                client, self, "ch2Watt", "AC Outlet Power", True
            ),  # 165
            AmpSensorEntity(client, self, "outAmp2", "AC Outlet Current", True),  # 0
            FrequencySensorEntity(
                client,
                self,
                "cfgOutFreq",
                "AC Config Out Frequency",
                False,
            ),  # 1
            FrequencySensorEntity(
                client, self, "outFreq", "AC Out Frequency", True
            ),  # 1
            MiscSensorEntity(
                client, self, "standbyTime", "AC Standby Time", False
            ),  # 1
            OutWattsSensorEntity(
                client,
                self,
                "inputWhInDay",
                "AC Input Day Power",
                False,
            ),  # Not in use
            OutWattsSensorEntity(
                client,
                self,
                "outputWhInDay",
                "AC Output Day Power",
                False,
            ),  # Not in use
        ]

    def distributerDCOutSensors(
        self, client: EcoflowApiClient, mainKey: str, params: dict[str, Any]
    ) -> list[BaseSensorEntity]:
        entityKey = mainKey + "."
        return [
            # Distributer DC Out
            OutWattsSensorEntity(
                client,
                self,
                "dcTotalWatts",
                "Distributer DC Out Power",
                True,
            ),  # 402
            OutWattsSensorEntity(
                client, self, "dcChWatt[0]", "DC Out 1", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutWattsSensorEntity(
                client, self, "dcChWatt[1]", "DC Out 2", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutWattsSensorEntity(
                client, self, "dcChWatt[2]", "DC Out 3", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutWattsSensorEntity(
                client, self, "dcChWatt[3]", "DC Out 4", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutWattsSensorEntity(
                client, self, "dcChWatt[4]", "DC Out 5", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutWattsSensorEntity(
                client, self, "dcChWatt[5]", "DC Out 6", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutWattsSensorEntity(
                client, self, "dcChWatt[6]", "DC Out 7", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutWattsSensorEntity(
                client, self, "dcChWatt[7]", "DC Out 8", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutWattsSensorEntity(
                client, self, "dcChWatt[8]", "DC Out 9", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutWattsSensorEntity(
                client, self, "dcChWatt[9]", "DC Out 10", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutWattsSensorEntity(
                client, self, "dcChWatt[10]", "DC Out 11", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutWattsSensorEntity(
                client, self, "dcChWatt[11]", "DC Out 12", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutAmpSensorEntity(
                client, self, "dcChCur[0]", "DC Ampere Out 1", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutAmpSensorEntity(
                client, self, "dcChCur[1]", "DC Ampere Out 2", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutAmpSensorEntity(
                client, self, "dcChCur[2]", "DC Ampere Out 3", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutAmpSensorEntity(
                client, self, "dcChCur[3]", "DC Ampere Out 4", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutAmpSensorEntity(
                client, self, "dcChCur[4]", "DC Ampere Out 5", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutAmpSensorEntity(
                client, self, "dcChCur[5]", "DC Ampere Out 6", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutAmpSensorEntity(
                client, self, "dcChCur[6]", "DC Ampere Out 7", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutAmpSensorEntity(
                client, self, "dcChCur[7]", "DC Ampere Out 8", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutAmpSensorEntity(
                client, self, "dcChCur[8]", "DC Ampere Out 9", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutAmpSensorEntity(
                client, self, "dcChCur[9]", "DC Ampere Out 10", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutAmpSensorEntity(
                client, self, "dcChCur[10]", "DC Ampere Out 11", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutAmpSensorEntity(
                client, self, "dcChCur[11]", "DC Ampere Out 12", True
            ),  # [140, 0, 0, 0, 0, 25]
            TempSensorEntity(
                client,
                self,
                "dcTemp1",
                "Distributer - DC Temperature 1",
                True,
            ),  # 38
            TempSensorEntity(
                client,
                self,
                "dcTemp2",
                "Distributer - DC Temperature 2",
                True,
            ),  # 37
            MiscSensorEntity(client, self, "dcChRelay", "DC Out Ch Relay", False),  # 1
            MiscSensorEntity(client, self, "dcChSta", "DC Out Enabled", True),  # 4033
            # MiscSensorEntity(client, "errorCodeAdd", 'DC Out Relay Errors, True), # [40000,40040,40080,40120,40160,40200,40240,40280,40320,40360,40400,40440,40800]
            MiscSensorEntity(
                client, self, "dcSetChSta", "DC Out Set Ch State", False
            ),  # 0
            OutMilliVoltSensorEntity(
                client, self, "dcInVol", "DC Out Voltage", True
            ),  # 26163
        ]

    def distributerACOutSensors(
        self, client: EcoflowApiClient, mainKey: str, params: dict[str, Any]
    ) -> list[BaseSensorEntity]:
        entityKey = mainKey + "."
        return [
            # Distributer AC Out
            OutWattsSensorEntity(
                client,
                self,
                "acTotalWatts",
                "Distributer AC Out Power",
                True,
            ),  # 165
            OutWattsSensorEntity(
                client, self, "acChWatt[0]", "AC Out 1", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutWattsSensorEntity(
                client, self, "acChWatt[1]", "AC Out 2", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutWattsSensorEntity(
                client, self, "acChWatt[2]", "AC Out 3", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutWattsSensorEntity(
                client, self, "acChWatt[3]", "AC Out 4", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutWattsSensorEntity(
                client, self, "acChWatt[4]", "AC Out 5", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutWattsSensorEntity(
                client, self, "acChWatt[5]", "AC Out 6", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutAmpSensorEntity(
                client, self, "acChCur[0]", "AC Ampere Out 1", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutAmpSensorEntity(
                client, self, "acChCur[1]", "AC Ampere Out 2", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutAmpSensorEntity(
                client, self, "acChCur[2]", "AC Ampere Out 3", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutAmpSensorEntity(
                client, self, "acChCur[3]", "AC Ampere Out 4", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutAmpSensorEntity(
                client, self, "acChCur[4]", "AC Ampere Out 5", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutAmpSensorEntity(
                client, self, "acChCur[5]", "AC Ampere Out 6", True
            ),  # [140, 0, 0, 0, 0, 25]
            OutWattsSensorEntity(
                client, self, "outWatts", "AC Inverter In Power", True
            ),  # 184
            OutMilliVoltSensorEntity(
                client, self, "acInVol", "AC Inverter In Voltage", True
            ),  # 240834
            TempSensorEntity(
                client,
                self,
                "acTemp1",
                "Distributer AC Temperature 1",
                True,
            ),  # 42
            TempSensorEntity(
                client,
                self,
                "acTemp2",
                "Distributer AC Temperature 2",
                True,
            ),  # 42
            # MiscSensorEntity(client, "errorCodeAdd", 'AC Relay Errors', True), # [30000,30040,30080,30120,30160,30200,30800] One extra likely due to Power Hub AC Out
            MiscSensorEntity(client, self, "acChSta", "AC Charge State", True),  # 0
        ]

    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        if self.device_data.device_type == "iclow":
            return [
                AcChargingPowerInAmpereEntity(
                    client,
                    self,
                    "NotExisting",
                    const.AC_CHARGING_POWER,
                    0,
                    16,  # This is not the real limit of the powerkit, but because it has a normal 230V plug, we don't allow here to go over 16A because you will maybe frie your socket
                    lambda value: {
                        "id": 123456789,
                        "version": "1.0",
                        "sn": self.device_data.parent.sn,
                        "moduleSn": self.device_data.sn,
                        "moduleType": 15365,
                        "operateType": "dischgIcParaSet",
                        "params": {"acCurrMaxSet": int(value)},
                    },
                ),
            ]
        return []

    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        if self.device_data.device_type == "lddc":
            return [
                BitMaskEnableEntity(
                    client,
                    self,
                    "dcChRelay.1",
                    "DC Switch 1",
                    self.dcSwitchFunction,
                ),
                BitMaskEnableEntity(
                    client,
                    self,
                    "dcChRelay.2",
                    "DC Switch 2",
                    self.dcSwitchFunction,
                ),
                BitMaskEnableEntity(
                    client,
                    self,
                    "dcChRelay.3",
                    "DC Switch 3",
                    self.dcSwitchFunction,
                ),
                BitMaskEnableEntity(
                    client,
                    self,
                    "dcChRelay.4",
                    "DC Switch 4",
                    self.dcSwitchFunction,
                ),
                BitMaskEnableEntity(
                    client,
                    self,
                    "dcChRelay.5",
                    "DC Switch 5",
                    self.dcSwitchFunction,
                ),
                BitMaskEnableEntity(
                    client,
                    self,
                    "dcChRelay.6",
                    "DC Switch 6",
                    self.dcSwitchFunction,
                ),
            ]
        if self.device_data.device_type == "ichigh":
            return [
                EnabledEntity(
                    client,
                    self,
                    "passByModeEn",
                    "Prioretize grid",
                    lambda value: {
                        "id": 123456789,
                        "version": "1.0",
                        "moduleSn": self.device_data.sn,
                        "moduleType": 15365,
                        "operateType": "dsgIcParaSet",
                        "params": {
                            "dsgLowPwrEn": 255,
                            "pfcDsgModeEn": 255,
                            "passByCurrMax": 255,
                            "passByModeEn": 1 if value == 1 else 2,
                        },
                    },
                    enableValue=1,
                ),
            ]
        if self.device_data.device_type == "iclow":
            return [
                EnabledEntity(
                    client,
                    self,
                    # TODO: reading is on ichigh and setting on iclow
                    "invSwSta",
                    "AC Output",
                    lambda value: {
                        "id": 123456789,
                        "version": "1.0",
                        "moduleSn": self.device_data.sn,
                        "moduleType": 15365,
                        "operateType": "dischgIcParaSet",
                        "params": {
                            "powerOn": 1 if value == 1 else 0,
                            "acCurrMaxSet": 255,
                            "acChgDisa": 255,
                            "acFrequencySet": 255,
                            "acVolSet": 255,
                        },
                    },
                ),
                EnabledEntity(
                    client,
                    self,
                    "chgDsgState",
                    # That is the good button!
                    "AC Charging",
                    lambda value: {
                        "id": 123456789,
                        "version": "1.0",
                        "moduleSn": self.device_data.sn,
                        "moduleType": 15365,
                        "operateType": "dischgIcParaSet",
                        "params": {
                            "acCurrMaxSet": 255,
                            "powerOn": 255,
                            "acChgDisa": 0 if value == 1 else 1,
                            "acFrequencySet": 255,
                            "wakeup": 1,
                            "standbyTime": 255,
                            "acRlyCtrlDisable": 255,
                            "acVolSet": 255,
                            "passByMaxCurr": 255,
                        },
                    },
                    enableValue=2,
                ),
            ]
        if self.device_data.device_type == "bbcin":
            return [
                EnabledEntity(
                    client,
                    self,
                    "not_existing",  # we want to use dcOutSta here but it is again on another device (bbcout)
                    "Main DC Output",
                    lambda value: {
                        "id": 123456789,
                        "version": "1.0",
                        "moduleSn": self.device_data.sn,
                        "moduleType": 15362,
                        "operateType": "dischgParaSet",
                        "params": {
                            "swSta": 1 if value == 1 else 0,
                        },
                    },
                    enableValue=1,
                ),
            ]
        return []

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return []
