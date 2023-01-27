from typing import Any, Callable

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, EcoFlowBaseEntity
from .config_flow import EcoflowModel
from .mqtt.ecoflow_mqtt import EcoflowMQTTClient


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowMQTTClient = hass.data[DOMAIN][entry.entry_id]

    if client.device_type == EcoflowModel.DIAGNOSTIC.name:
        return

    entities = []

    if client.device_type == EcoflowModel.DELTA_PRO.name:
        entities.extend([
            BeeperEntity(client, "mppt.beepState", "Beeper",
                         lambda value: {"moduleType": 0, "operateType": "TCP", "params": {"id": 38, "enabled": value}}),
            EnabledEntity(client, "pd.dcOutState", "USB Enabled",
                          lambda value: {"moduleType": 0, "operateType": "TCP",
                                         "params": {"id": 34, "enabled": value}}),
            EnabledEntity(client, "inv.cfgAcEnabled", "AC Enabled",
                          lambda value: {"moduleType": 0, "operateType": "TCP",
                                         "params": {"id": 66, "enabled": value}}),

            EnabledEntity(client, "inv.cfgAcXboost", "X-Boost Enabled",
                          lambda value: {"moduleType": 0, "operateType": "TCP", "params": {"id": 66, "xboost": value}}),

            EnabledEntity(client, "inv.acPassByAutoEn", "AC Always On",
                          lambda value: {"moduleType": 0, "operateType": "TCP", "params": {"id": 84, "enabled": value}})

        ])

    if client.device_type == EcoflowModel.DELTA_2.name:
        entities.extend([

            BeeperEntity(client, "mppt.beepState", "Beeper",
                         lambda value: {"moduleType": 5, "operateType": "quietMode", "params": {"enabled": value}}),

            EnabledEntity(client, "pd.dcOutState", "USB Enabled",
                          lambda value: {"moduleType": 1, "operateType": "dcOutCfg", "params": {"enabled": value}}),

            EnabledEntity(client, "pd.acAutoOnCfg", "AC Always On",
                          lambda value: {"moduleType": 1, "operateType": "acAutoOn", "params": {"cfg": value}}),

            EnabledEntity(client, "mppt.cfgAcEnabled", "AC Enabled",
                          lambda value: {"moduleType": 5, "operateType": "acOutCfg",
                                         "params": {"enabled": value, "out_voltage": -1, "out_freq": 255,
                                                    "xboost": 255}}),

            EnabledEntity(client, "pd.carState", "DC (12V) Enabled",
                          lambda value: {"moduleType": 5, "operateType": "mpptCar", "params": {"enabled": value}}),
        ])

    if client.device_type == EcoflowModel.RIVER_2_MAX.name:
        entities.extend([
            EnabledEntity(client, "mppt.cfgAcEnabled", "AC Enabled",
                          lambda value: {"moduleType": 5, "operateType": "acOutCfg",
                                         "params": {"enabled": value, "out_voltage": -1, "out_freq": 255,
                                                    "xboost": 255}}),

            EnabledEntity(client, "pd.carState", "DC (12V) Enabled",
                          lambda value: {"moduleType": 5, "operateType": "mpptCar", "params": {"enabled": value}}),
        ])

    async_add_entities(entities)


class EnabledEntity(SwitchEntity, EcoFlowBaseEntity):

    def __init__(self, client: EcoflowMQTTClient, mqtt_key: str, title: str,
                 command: Callable[[int], dict[str, any]] | None, enabled: bool = True, auto_enable: bool = False):
        super().__init__(client, mqtt_key, title, enabled, auto_enable)
        self.__command = command

    def _update_value(self, val: Any) -> bool:
        self._attr_is_on = bool(val)
        return True

    def turn_on(self, **kwargs: Any) -> None:
        if self.__command:
            data = self.__command(1)
            self._client.send_message(data)

    def turn_off(self, **kwargs: Any) -> None:
        if self.__command:
            data = self.__command(0)
            self._client.send_message(data)


class DisabledEntity(SwitchEntity, EcoFlowBaseEntity):

    def __init__(self, client: EcoflowMQTTClient, mqtt_key: str, title: str,
                 command: Callable[[int], dict[str, any]] | None, enabled: bool = True, auto_enable: bool = False):
        super().__init__(client, mqtt_key, title, enabled, auto_enable)
        self.__command = command

    def _update_value(self, val: Any) -> bool:
        self._attr_is_off = bool(val)
        return True

    def turn_on(self, **kwargs: Any) -> None:
        if self.__command:
            data = self.__command(0)
            self._client.send_message(data)

    def turn_off(self, **kwargs: Any) -> None:
        if self.__command:
            data = self.__command(1)
            self._client.send_message(data)


class BeeperEntity(DisabledEntity):
    _attr_entity_category = EntityCategory.CONFIG
