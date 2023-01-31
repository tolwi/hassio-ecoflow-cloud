from typing import Callable, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.ecoflow_cloud import EcoflowMQTTClient, DOMAIN
from custom_components.ecoflow_cloud.entities import BaseSelectEntity

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowMQTTClient = hass.data[DOMAIN][entry.entry_id]

    from .devices.registry import devices
    if client.device_type in devices:
        entities = devices[client.device_type].selects(client)
        async_add_entities(entities)


class DictSelectEntity(BaseSelectEntity):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_available = False

    def __init__(self, client: EcoflowMQTTClient, mqtt_key: str, title: str, options: dict[str, int],
                 command: Callable[[int], dict[str, any]] | None, enabled: bool = True, auto_enable: bool = False):
        super().__init__(client, mqtt_key, title, enabled, auto_enable)
        self.__options_dict = options
        self.__command = command
        self._attr_options = list(options.keys())

    def _update_value(self, val: Any) -> bool:
        ival = int(val)
        lval = [k for k, v in self.__options_dict.items() if v == ival]
        self._attr_current_option = lval[0]
        return True

    async def async_select_option(self, option: str):
        if self.__command:
            val = self.__options_dict[option]
            self.send_message(val, self.__command(val))

class TimeoutDictSelectEntity(DictSelectEntity):
    _attr_icon = "mdi:timer-outline"


