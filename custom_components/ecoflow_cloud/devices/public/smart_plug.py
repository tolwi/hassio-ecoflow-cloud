from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from .data_bridge import to_plain

from custom_components.ecoflow_cloud import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import BaseDevice, const
from custom_components.ecoflow_cloud.number import BrightnessLevelEntity
from custom_components.ecoflow_cloud.sensor import TempSensorEntity, VoltSensorEntity, AmpSensorEntity, \
    DeciwattsSensorEntity
from custom_components.ecoflow_cloud.switch import EnabledEntity


class SmartPlug(BaseDevice):

    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            TempSensorEntity(client, self, "2_1.temp", const.TEMPERATURE),
            VoltSensorEntity(client, self, "2_1.volt", const.VOLT),
            AmpSensorEntity(client, self, "2_1.current", const.CURRENT)
                .attr("2_1.maxCur", const.MAX_CURRENT, 0),
            DeciwattsSensorEntity(client, self, "2_1.watts", const.POWER)

        ]

    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return [
            BrightnessLevelEntity(client, self, "2_1.brightness", const.BRIGHTNESS, 0, 1023,
                                  lambda value: {"sn": self.device_info.sn,
                                                "cmdCode": "WN511_SOCKET_SET_BRIGHTNESS_PACK", 
                                                 "params": {"brightness": value}}),
        ]

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return [
            EnabledEntity(client, self, "2_1.switchSta", const.MODE_ON,
                          lambda value: {"sn": self.device_info.sn,
                                         "cmdCode": "WN511_SOCKET_SET_PLUG_SWITCH_MESSAGE", 
                                         "params": {"plugSwitch": value}}),
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return []

    def _prepare_data(self, raw_data) -> dict[str, any]:
        res = super()._prepare_data(raw_data)
        res = to_plain(res)

        return res