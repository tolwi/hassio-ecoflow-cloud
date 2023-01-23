import random
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, EcoFlowBaseEntity
from .mqtt.ecoflow_mqtt import EcoflowMQTTClient
from .config_flow import EcoflowModel

commands = {
    "pd.beepMode_on": {"moduleType": 5, "operateType": "quietMode", "params": {"enabled": 0}},
    "pd.beepMode_off": {"moduleType": 5, "operateType": "quietMode", "params": {"enabled": 1}}
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowMQTTClient = hass.data[DOMAIN][entry.entry_id]
    entities = []

    if client.device_type == EcoflowModel.DELTA_2.name:
        entities.extend([
            SimpleEntity(client, "1", "pd.beepMode", "Beeper")
        ])

    async_add_entities(entities)


class SimpleEntity(SwitchEntity, EcoFlowBaseEntity):

    def turn_on(self, **kwargs: Any) -> None:
        if self._mqtt_key+'_on' in commands:
            self._client.send_message(commands[self._mqtt_key+'_on'])

    def turn_off(self, **kwargs: Any) -> None:
        if self._mqtt_key+'_off' in commands:
            self._client.send_message(commands[self._mqtt_key+'_off'])