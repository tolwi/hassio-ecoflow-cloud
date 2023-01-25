from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, EcoFlowBaseEntity
from .config_flow import EcoflowModel
from .mqtt.ecoflow_mqtt import EcoflowMQTTClient

commands = {
    "mppt.beepState_on": {"moduleType": 5, "operateType": "quietMode", "params": {"enabled": 0}},
    "mppt.beepState_off": {"moduleType": 5, "operateType": "quietMode", "params": {"enabled": 1}},

    "pd.dcOutState_on": {"moduleType": 1, "operateType": "dcOutCfg", "params": {"enabled": 1}},
    "pd.dcOutState_off": {"moduleType": 1, "operateType": "dcOutCfg", "params": {"enabled": 0}},

    "pd.acEnabled_on":  {"moduleType": 5, "operateType": "acOutCfg",
                         "params": {"enabled": 1, "out_voltage": -1, "out_freq": 255, "xboost": 255}},
    "pd.acEnabled_off": {"moduleType": 5, "operateType": "acOutCfg",
                         "params": {"enabled": 0, "out_voltage": -1, "out_freq": 255, "xboost": 255}},

    "mppt.cfgAcEnabled_on":  {"moduleType": 5, "operateType": "acOutCfg",
                              "params": {"enabled": 1, "out_voltage": -1, "out_freq": 255, "xboost": 255}},
    "mppt.cfgAcEnabled_off": {"moduleType": 5, "operateType": "acOutCfg",
                              "params": {"enabled": 0, "out_voltage": -1, "out_freq": 255, "xboost": 255}},

    "pd.carState_on": {"moduleType": 5, "operateType": "mpptCar", "params": {"enabled": 1}},
    "pd.carState_off": {"moduleType": 5, "operateType": "mpptCar", "params": {"enabled": 0}}
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowMQTTClient = hass.data[DOMAIN][entry.entry_id]

    if client.device_type == EcoflowModel.DIAGNOSTIC.name:
        return

    entities = [
        SimpleEntity(client, "pd.carState", "DC (12V) Enabled"),
    ]

    if client.device_type == EcoflowModel.DELTA_2.name:
        entities.extend([
            BeeperEntity(client, "mppt.beepState", "Beeper"),
            SimpleEntity(client, "pd.dcOutState", "USB Enabled"),
            SimpleEntity(client, "pd.acEnabled", "AC Enabled"),
            SimpleEntity(client, "pd.carState", "DC (12V) Enabled")
        ])

    if client.device_type == EcoflowModel.RIVER_2_MAX.name:
        entities.extend([
            SimpleEntity(client, "mppt.cfgAcEnabled", "AC Enabled"),
            SimpleEntity(client, "pd.carState", "DC (12V) Enabled")
        ])

    async_add_entities(entities)


class SimpleEntity(SwitchEntity, EcoFlowBaseEntity):

    def turn_on(self, **kwargs: Any) -> None:
        if self._mqtt_key + '_on' in commands:
            self._client.send_message(commands[self._mqtt_key + '_on'])

    def turn_off(self, **kwargs: Any) -> None:
        if self._mqtt_key + '_off' in commands:
            self._client.send_message(commands[self._mqtt_key + '_off'])

    def _prepare_value(self, val: Any) -> Any:
        if val == 1:
            self._attr_is_on = True
        else:
            self._attr_is_on = False
        return val


class BeeperEntity(SimpleEntity):
    _attr_entity_category = EntityCategory.CONFIG
    def _prepare_value(self, val: Any) -> Any:
        if val == 1:
            self._attr_is_on = False
            return 0
        else:
            self._attr_is_on = True
            return 1
