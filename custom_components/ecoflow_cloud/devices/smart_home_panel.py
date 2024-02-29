from typing import Any

from . import BaseDevice, const
from .. import EcoflowMQTTClient
from ..entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, BaseSelectEntity
from ..number import MaxBatteryLevelEntity, MinBatteryLevelEntity
from ..select import DictSelectEntity
from ..sensor import WattsSensorEntity, OutWattsSensorEntity, InWattsSensorEntity, LevelSensorEntity, \
    RemainSensorEntity, MiscBinarySensorEntity, StatusSensorEntity
from ..switch import EnabledEntity

import logging

_LOGGER = logging.getLogger(__name__)

MODES = {
    "Auto": {"sta": 0, "ctrlMode": 0},
    "Grid": {"sta": 0, "ctrlMode": 1},
    "Battery": {"sta": 1, "ctrlMode": 1},
    "Off": {"sta": 2, "ctrlMode": 1}
}

class ModeDictSelectEntity(DictSelectEntity):

    def __init__(self, client: EcoflowMQTTClient, n: int):
        super().__init__(client, "loadCmdChCtrlInfos[%i]" % n, const.SHP_CIRCUIT_N_MODE % (n + 1), MODES,
                         lambda value: {"moduleType": 0, "operateType": "TCP",
                                        "params": {"sta": value['sta'], "ctrlMode": value['ctrlMode'], "ch": n,
                                                   "cmdSet": 11, "id": 16}})

    def _update_value(self, val: Any) -> bool:
        _LOGGER.debug(f"ModeDictSelectEntity._update_value = {val}")
        return super()._update_value({"sta": val['ctrlSta'], "ctrlMode": val['ctrlMode']})

    def sample_value(self):
        return {"sta": -66666, "ctrlMode": -66666}

class GridChargeEnabledEntity(EnabledEntity):

    def __init__(self, client: EcoflowMQTTClient, n: int):
        super().__init__(client, "energyInfos[%i].stateBean.isGridCharge" % n, const.SHP_AC_N_CHARGING % (n + 1),
                          lambda value: {"moduleType": 0, "operateType": "TCP",
                                         "params": {"sta": value['sta'], "ctrlMode": value['ctrlMode'], "ch": 10 + n, "cmdSet": 11,
                                                    "id": 17}})

    def turn_on(self, **kwargs: Any) -> None:
        self.send_set_message(1, self.command_dict({"sta": 2, "ctrlMode": 1}))

    def turn_off(self, **kwargs: Any) -> None:
        self.send_set_message(0, self.command_dict({"sta": 0, "ctrlMode": 0}))

    def sample_value(self):
        return {"sta": -66666, "ctrlMode": -66666}

class EPSmodeEnabledEntity(EnabledEntity):

    def __init__(self, client: EcoflowMQTTClient):
        super().__init__(client, "eps", const.SHP_EPS_MODE, 
                          lambda value: {"moduleType": 0, "operateType": "TCP",
                                         "params": {"cmdSet": 11, "id": 24, "eps": value['eps']}})
        
    def turn_on(self, **kwargs: Any) -> None:
        self.send_set_message(1, self.command_dict({"eps": 1}))

    def turn_off(self, **kwargs: Any) -> None:
        self.send_set_message(0, self.command_dict({"eps": 0}))

    def sample_value(self):
        return {"eps": -66666}

class SmartHomePanel(BaseDevice):

    def sensors(self, client: EcoflowMQTTClient) -> list[BaseSensorEntity]:
        res = [StatusSensorEntity(client)]
 
        for i in range(0, 2):
            res.extend([
                LevelSensorEntity(client, "energyInfos[%i].batteryPercentage" % i, const.SHP_AC_N_BATTERY_LEVEL % (i + 1)),
                OutWattsSensorEntity(client, "energyInfos[%i].outputPower" % i, const.SHP_AC_N_OUT_POWER % (i + 1)),
                InWattsSensorEntity(client, "energyInfos[%i].lcdInputWatts" % i, const.SHP_AC_N_IN_POWER % (i + 1)),
                RemainSensorEntity(client, "energyInfos[%i].chargeTime" % i, const.SHP_AC_N_CHARGE_TIME % (i + 1)),
                RemainSensorEntity(client, "energyInfos[%i].dischargeTime" % i, const.SHP_AC_N_DISCHARGE_TIME % (i + 1)),
                MiscBinarySensorEntity(client, "energyInfos[%i].stateBean.isConnect" % i, const.SHP_AC_N_CONNECTED % (i + 1)),
                MiscBinarySensorEntity(client, "energyInfos[%i].stateBean.isEnable" % i, const.SHP_AC_N_ENABLED % (i + 1)),
                WattsSensorEntity(client, "infoList[%i].chWatt" % (i + 10), const.SHP_AC_N_POWER % (i + 1))
            ])
        
        for i in range(0, 10):
            res.append(WattsSensorEntity(client, "infoList[%i].chWatt" % i, const.SHP_CIRCUIT_N_POWER % (i + 1)))
            res.append(MiscBinarySensorEntity(client, "loadCmdChCtrlInfos[%i].ctrlMode" % i, const.SHP_CIRCUIT_N_AUTO % (i + 1)))

        return res

    def numbers(self, client: EcoflowMQTTClient) -> list[BaseNumberEntity]:
        return [
            MaxBatteryLevelEntity(client, "forceChargeHigh", const.MAX_CHARGE_LEVEL, 50, 100,
                                  lambda value, params: {"moduleType": 0, "operateType": "TCP",
                                                         "params": {"discLower": int(params.get("discLower", 0)),
                                                                    "forceChargeHigh": value,
                                                                    "cmdSet": 11, "id": 29}}),

            MinBatteryLevelEntity(client, "discLower", const.MAX_CHARGE_LEVEL, 0, 30,
                                  lambda value, params: {"moduleType": 0, "operateType": "TCP",
                                                         "params": {"discLower": value,
                                                                    "forceChargeHigh": int(
                                                                        params.get("forceChargeHigh", 100)),
                                                                    "cmdSet": 11, "id": 29}})

        ]

    def switches(self, client: EcoflowMQTTClient) -> list[BaseSwitchEntity]:
        return [
            GridChargeEnabledEntity(client, 0),
            GridChargeEnabledEntity(client, 1),
            EPSmodeEnabledEntity(client)
        ]

    def selects(self, client: EcoflowMQTTClient) -> list[BaseSelectEntity]:
        res = []
        for i in range(0, 10):
            res.append(ModeDictSelectEntity(client, i))

        return res
