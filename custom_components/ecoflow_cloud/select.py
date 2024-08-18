from typing import Callable, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN
from .api import EcoflowApiClient
from .entities import BaseSelectEntity
from .devices import BaseDevice


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowApiClient = hass.data[DOMAIN][entry.entry_id]
    for (sn, device) in client.devices.items():
        async_add_entities(device.selects(client))


class DictSelectEntity(BaseSelectEntity):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_available = False
    def __init__(self, client: EcoflowApiClient, device: BaseDevice, mqtt_key: str, title: str, options: dict[str, int],
                 command: Callable[[int], dict[str, Any]] | None, enabled: bool = True, auto_enable: bool = False):
        super().__init__(client, device, mqtt_key, title, command, enabled, auto_enable)
        self.__options_dict = options
        self._attr_options = list(options.keys())

    def options_dict(self) -> dict[str, int]:
        return self.__options_dict

    def _update_value(self, val: Any) -> bool:
        ival = int(val)
        lval = [k for k, v in self.__options_dict.items() if v == ival]
        if len(lval) == 1:
            self._attr_current_option = lval[0]
            return True
        else:
            return False

    async def async_select_option(self, option: str):
        if self._command:
            val = self.__options_dict[option]
            self.send_set_message(val, self.command_dict(val))


class TimeoutDictSelectEntity(DictSelectEntity):
    _attr_icon = "mdi:timer-outline"

class PowerDictSelectEntity(DictSelectEntity):
    _attr_icon = "mdi:battery-charging-wireless"
