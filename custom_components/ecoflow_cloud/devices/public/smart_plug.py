from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity

from custom_components.ecoflow_cloud import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import BaseDevice, const
from custom_components.ecoflow_cloud.number import BrightnessLevelEntity
from custom_components.ecoflow_cloud.sensor import TempSensorEntity, VoltSensorEntity, AmpSensorEntity, \
    WattsSensorEntity
from custom_components.ecoflow_cloud.switch import EnabledEntity


class SmartPlug(BaseDevice):

    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            TempSensorEntity(client, "2_1.temp", const.TEMPERATURE),
            VoltSensorEntity(client, "2_1.volt", const.VOLT),
            AmpSensorEntity(client, "2_1.current", const.CURRENT)
                .attr("2_1.maxCur", const.MAX_CURRENT, 0),
            WattsSensorEntity(client, "2_1.watts", const.POWER)

        ]

    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return [
            BrightnessLevelEntity(client, "2_1.brightness", const.BRIGHTNESS, 0, 1023,
                                  lambda value: {"cmdCode": "WN511_SOCKET_SET_BRIGHTNESS_PACK", "params": {"brightness": value}}),
        ]

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return [
            EnabledEntity(client, "2_1.switchSta", const.MODE_ON,
                          lambda value: {"cmdCode": "WN511_SET_SUPPLY_PRIORITY_PACK", "params": {"plugSwitch": value}}),
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return []

    def prepare_data(self, raw_data) -> dict[str, any]:
        res = super().prepare_data(raw_data)

        if "cmdFunc" in res and "cmdId" in res:
            new_params = {}
            prefix = f"{res['cmdFunc']}_{res['cmdId']}"

            for (k, v) in raw_data["params"].items():
                new_params[f"{prefix}.{k}"] = v

            result = {"params": new_params}
            for (k, v) in raw_data.items():
                if k != "params":
                    result[k] = v

            return result

        return res