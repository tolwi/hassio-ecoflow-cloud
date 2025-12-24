# import logging
# _LOGGER = logging.getLogger(__name__)

from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import BaseDevice, const
from custom_components.ecoflow_cloud.devices.public import data_bridge
from custom_components.ecoflow_cloud.number import ChargingPowerEntity, MaxBatteryLevelEntity, MinBatteryLevelEntity
from custom_components.ecoflow_cloud.sensor import (
    AmpSensorEntity,
    FrequencySensorEntity,
    InWattsSensorEntity,
    LevelSensorEntity,
    MiscSensorEntity,
    OutWattsSensorEntity,
    QuotaScheduledStatusSensorEntity,
    RemainSensorEntity,
    VoltSensorEntity,
)
from custom_components.ecoflow_cloud.switch import EnabledEntity


class DeltaProUltra(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            QuotaScheduledStatusSensorEntity(client, self, 300),  # required to call quota/all every 5 minutes
            RemainSensorEntity(client, self, "hs_yj751_pd_appshow_addr.remainTime", const.REMAINING_TIME),
            LevelSensorEntity(client, self, "hs_yj751_pd_appshow_addr.soc", const.BATTERY_LEVEL_SOC),
            MiscSensorEntity(client, self, "hs_yj751_pd_appshow_addr.bpNum", const.BATTERY_COUNT),
            MiscSensorEntity(client, self, "hs_yj751_pd_appshow_addr.fullCombo", const.WIRELESS_4G_DATA_MAX, False),
            MiscSensorEntity(
                client, self, "hs_yj751_pd_appshow_addr.remainCombo", const.WIRELESS_4G_DATA_REMAINING, False
            ),
            MiscSensorEntity(
                client, self, "hs_yj751_pd_appshow_addr.wireless4gCon", const.WIRELESS_4G_REGISTERED, False
            ),
            MiscSensorEntity(
                client, self, "hs_yj751_pd_appshow_addr.wirlesss4gErrCode", const.WIRELESS_4G_ERROR_CODE, False
            ),
            MiscSensorEntity(client, self, "hs_yj751_pd_appshow_addr.simIccid", const.WIRELESS_4G_SIM_ID, False),
            MiscSensorEntity(
                client, self, "hs_yj751_pd_appshow_addr.wireless4GSta", const.INTERNET_CONNECTION_TYPE, False
            ),
            MiscSensorEntity(client, self, "hs_yj751_pd_appshow_addr.sysErrCode", const.ERROR_CODE),
            InWattsSensorEntity(
                client, self, "hs_yj751_pd_appshow_addr.wattsInSum", const.TOTAL_IN_POWER
            ).with_energy(),
            OutWattsSensorEntity(
                client, self, "hs_yj751_pd_appshow_addr.wattsOutSum", const.TOTAL_OUT_POWER
            ).with_energy(),
            InWattsSensorEntity(
                client, self, "hs_yj751_pd_appshow_addr.inAc5p8Pwr", const.PIO_PORT_IN_POWER
            ).with_energy(),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.inAc5p8Amp", const.PIO_PORT_IN_CURRENT, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.inAc5p8Vol", const.PIO_PORT_IN_VOLTAGE, False),
            OutWattsSensorEntity(
                client, self, "hs_yj751_pd_appshow_addr.outAc5p8Pwr", const.PIO_PORT_OUT_POWER
            ).with_energy(),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAc5p8Amp", const.PIO_PORT_OUT_CURRENT, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAc5p8Vol", const.PIO_PORT_OUT_VOLTAGE, False),
            MiscSensorEntity(client, self, "hs_yj751_pd_appshow_addr.access5p8InType", const.PIO_PORT_INPUT_TYPE),
            InWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.inAcC20Pwr", const.AC_IN_POWER).with_energy(
                False
            ),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.inAcC20Amp", const.AC_IN_CURRENT, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.inAcC20Vol", const.AC_IN_VOLT, False),
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outUsb1Pwr", const.USB_1_OUT_POWER)
            .with_energy(False)
            .with_icon("mdi:usb-port"),
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outUsb2Pwr", const.USB_2_OUT_POWER)
            .with_energy(False)
            .with_icon("mdi:usb-port"),
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outTypec1Pwr", const.TYPEC_1_OUT_POWER)
            .with_energy(False)
            .with_icon("mdi:usb-c-port"),
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outTypec2Pwr", const.TYPEC_2_OUT_POWER)
            .with_energy(False)
            .with_icon("mdi:usb-c-port"),
            InWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.inHvMpptPwr", const.SOLAR_1_IN_POWER)
            .with_energy()
            .with_icon("mdi:solar-power"),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.inHvMpptAmp", const.SOLAR_1_IN_AMPS, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.inHvMpptVol", const.SOLAR_1_IN_VOLTS, False),
            InWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.inLvMpptPwr", const.SOLAR_2_IN_POWER)
            .with_energy()
            .with_icon("mdi:solar-power"),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.inLvMpptAmp", const.SOLAR_2_IN_AMPS, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.inLvMpptVol", const.SOLAR_2_IN_VOLTS, False),
            # 20A 120V Backup UPS
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outAcL11Pwr", const.AC_N_OUT_POWER % 1)
            .with_energy(False)
            .with_icon("mdi:power-socket-us"),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL11Amp", const.AC_N_OUT_CURRENT % 1, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL11Vol", const.AC_N_OUT_VOLTAGE % 1, False),
            FrequencySensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL11Pf", const.AC_N_OUT_FREQ % 1, False),
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outAcL12Pwr", const.AC_N_OUT_POWER % 2)
            .with_energy(False)
            .with_icon("mdi:power-socket-us"),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL12Amp", const.AC_N_OUT_CURRENT % 2, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL12Vol", const.AC_N_OUT_VOLTAGE % 2, False),
            FrequencySensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL12Pf", const.AC_N_OUT_FREQ % 2, False),
            # 20A 120V Online UPS
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outAcL21Pwr", const.AC_N_OUT_POWER % 3)
            .with_energy(False)
            .with_icon("mdi:power-socket-us"),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL21Amp", const.AC_N_OUT_CURRENT % 3, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL21Vol", const.AC_N_OUT_VOLTAGE % 3, False),
            FrequencySensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL21Pf", const.AC_N_OUT_FREQ % 3, False),
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outAcL22Pwr", const.AC_N_OUT_POWER % 4)
            .with_energy(False)
            .with_icon("mdi:power-socket-us"),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL22Amp", const.AC_N_OUT_CURRENT % 4, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL22Vol", const.AC_N_OUT_VOLTAGE % 4, False),
            FrequencySensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL22Pf", const.AC_N_OUT_FREQ % 4, False),
            # 30A 120V
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outAcL14Pwr", const.AC_N_OUT_POWER % 5)
            .with_energy(False)
            .with_icon("mdi:power-socket-au"),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL14Amp", const.AC_N_OUT_CURRENT % 5, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL14Vol", const.AC_N_OUT_VOLTAGE % 5, False),
            FrequencySensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL14Pf", const.AC_N_OUT_FREQ % 5, False),
            # 30A 120/240V
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outAcTtPwr", const.AC_N_OUT_POWER % 6)
            .with_energy(False)
            .with_icon("mdi:power-socket-de"),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcTtAmp", const.AC_N_OUT_CURRENT % 6, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcTtVol", const.AC_N_OUT_VOLTAGE % 6, False),
            FrequencySensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcTtPf", const.AC_N_OUT_FREQ % 6, False),
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outAdsPwr", const.DC_ANDERSON_OUT_POWER)
            .with_energy(False)
            .with_icon("mdi:connection"),
        ]

    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return [
            MinBatteryLevelEntity(
                client,
                self,
                "hs_yj751_pd_app_set_info_addr.dsgMinSoc",
                const.MIN_DISCHARGE_LEVEL,
                0,
                30,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "YJ751_PD_DSG_SOC_MIN_SET",
                    "params": {"minDsgSoc": value},
                },
            ),
            MaxBatteryLevelEntity(
                client,
                self,
                "hs_yj751_pd_app_set_info_addr.chgMaxSoc",
                const.MAX_CHARGE_LEVEL,
                50,
                100,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "YJ751_PD_CHG_SOC_MAX_SET",
                    "params": {"maxChgSoc": value},
                },
            ),
            ChargingPowerEntity(
                client,
                self,
                "hs_yj751_pd_app_set_info_addr.chgC20SetWatts",
                const.AC_CHARGING_POWER,
                600,
                1800,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "YJ751_PD_AC_CHG_SET",
                    "params": {"chgC20Watts": value},
                },
            ).with_icon("mdi:power-plug"),
            ChargingPowerEntity(
                client,
                self,
                "hs_yj751_pd_app_set_info_addr.chg5p8SetWatts",
                const.PIO_PORT_CHARGING_POWER,
                600,
                7200,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "YJ751_PD_AC_CHG_SET",
                    "params": {"chg5p8Watts": value},
                },
            ),
        ]

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return [
            EnabledEntity(
                client,
                self,
                "hs_yj751_pd_appshow_addr.wireless4gOn",
                const.WIRELESS_4G_ENABLED,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "YJ751_PD_4G_SWITCH_SET",
                    "params": {"en4GOpen": value},
                },
            ).with_icon("mdi:signal-4g"),
            EnabledEntity(
                client,
                self,
                "hs_yj751_pd_app_set_info_addr.bmsModeSet",
                const.BATTERY_AUTO_HEATING_ENABLED,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "YJ751_PD_BP_HEAT_SET",
                    "params": {"enBpHeat": value},
                },
            ).with_icon("mdi:thermometer-check"),
            EnabledEntity(
                client,
                self,
                "hs_yj751_pd_appshow_addr.showFlag.6",
                const.DC_MODE,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "YJ751_PD_DC_SWITCH_SET",
                    "params": {"enable": value},
                },
            ).with_icon("mdi:current-dc"),
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return []

    def _prepare_data(self, raw_data) -> dict[str, Any]:
        res = super()._prepare_data(raw_data)
        res = self.to_plain_nested_addr_prefix(res)

        # split showFlag into separate keys for each bit using documentation's bit ordering
        if "hs_yj751_pd_appshow_addr.showFlag" in res["params"] and isinstance(
            res["params"]["hs_yj751_pd_appshow_addr.showFlag"], int
        ):
            documentation_bit_order = ((res["params"]["hs_yj751_pd_appshow_addr.showFlag"] >> 4) & 3855) | (
                res["params"]["hs_yj751_pd_appshow_addr.showFlag"] << 4
            )
            for x in range(16):
                res["params"][f"hs_yj751_pd_appshow_addr.showFlag.{x + 1}"] = (documentation_bit_order >> x) & 1
        return res

    def to_plain_nested_addr_prefix(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        if "typeCode" in raw_data:
            prefix = data_bridge.status_to_plain.get(raw_data["typeCode"], "unknown_" + raw_data["typeCode"])
        elif "addr" in raw_data:
            prefix = raw_data["addr"]
        elif "cmdFunc" in raw_data and "cmdId" in raw_data:
            prefix = f"{raw_data['cmdFunc']}_{raw_data['cmdId']}"
        else:
            # Used for quota/all responses
            return raw_data

        new_params: dict[str, Any] = {}
        if "params" in raw_data:
            self.nested_to_top_level(new_params, prefix, raw_data["params"])
        if "param" in raw_data:
            self.nested_to_top_level(new_params, prefix, raw_data["param"])

        result: dict[str, Any] = {"params": new_params}
        for k, v in raw_data.items():
            if k != "param" and k != "params":
                result[k] = v
        return result

    def nested_to_top_level(self, dest: dict[str, Any], k: str, v: Any):
        """Converts each nested dict/list value to a top-level key of
        the prefix followed by dot notation path to the value.
        ex.
            {"a": [123, {"b": 456}]} -> {"a.0": 123, "a.1.b": 456}
        """
        if isinstance(v, dict):
            for kk, vv in v.items():
                self.nested_to_top_level(dest, f"{k}.{kk}", vv)
        elif isinstance(v, list):
            for ii, vv in enumerate(v):
                self.nested_to_top_level(dest, f"{k}.{ii}", vv)
        else:
            dest[k] = v
