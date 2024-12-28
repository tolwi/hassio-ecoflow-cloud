import asyncio
from typing import Callable, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ECOFLOW_DOMAIN
from .api import EcoflowApiClient
from .entities import BaseSelectEntity
from .devices import BaseDevice


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowApiClient = hass.data[ECOFLOW_DOMAIN][entry.entry_id]
    # the following line waits here as long as possible,
    # so the client.data object gets filled with the data
    # from the mqtt queue.
    # this helps to figure out the exact sensor layout in the devices implementation.
    # 9 seconds is one second lower then the warning message of hass.
    # One second should be enaugh time to configure all entities.
    await asyncio.sleep(9)
    for (sn, device) in client.devices.items():
        async_add_entities(device.selects(client))

class DictSelectEntity(BaseSelectEntity):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_available = False

    def __init__(
        self,
        client: EcoflowApiClient,
        device: BaseDevice,
        mqtt_key: str,
        title: str,
        options: dict[str, int],
        command: Callable[[int], dict[str, Any]] | None,
        enabled: bool = True,
        auto_enable: bool = False
    ):
        super().__init__(client, device, mqtt_key, title, command, enabled, auto_enable)
        self._options_dict = options
        self._options = list(options.keys())
        self._current_option = None

    def options_dict(self) -> dict[str, int]:
        return self._options_dict

    def _update_value(self, val: Any) -> bool:
        ival = int(val)
        lval = [k for k, v in self._options_dict.items() if v == ival]
        if len(lval) == 1:
            self._current_option = lval[0]
            return True
        else:
            return False

    @property
    def options(self) -> list[str]:
        """Return available select options."""
        return self._options

    @property
    def current_option(self) -> str:
        """Return current select option."""
        return self._current_option

    def select_option(self, option: str) -> None:
        if self._command:
            val = self._options_dict[option]
            self.send_set_message(val, self.command_dict(val))

class TimeoutDictSelectEntity(DictSelectEntity):
    _attr_icon = "mdi:timer-outline"

class PowerDictSelectEntity(DictSelectEntity):
    _attr_icon = "mdi:battery-charging-wireless"
