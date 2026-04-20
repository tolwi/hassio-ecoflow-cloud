import logging
from typing import Any, Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.ecoflow_cloud.devices import (
    BaseDevice,
)

from . import ECOFLOW_DOMAIN
from .api import EcoflowApiClient, Message
from .entities import BaseSwitchEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    client: EcoflowApiClient = hass.data[ECOFLOW_DOMAIN][entry.entry_id]
    for sn, device in client.devices.items():
        async_add_entities(device.switches(client))


class EnabledEntity(BaseSwitchEntity[int]):
    def __init__(
        self,
        client: EcoflowApiClient,
        device: BaseDevice,
        mqtt_key: str,
        title: str,
        command: Callable[[int], dict[str, Any] | Message]
        | Callable[[int, dict[str, Any]], dict[str, Any] | Message]
        | None,
        enabled: bool = True,
        auto_enable: bool = False,
        enableValue: Any = None,
        disableValue: Any = None,
    ):
        super().__init__(client, device, mqtt_key, title, command, enabled, auto_enable)
        self._enable_value = enableValue
        self._disable_value = disableValue

    def _update_value(self, val: Any) -> bool:
        _LOGGER.debug("Updating switch " + self._attr_unique_id + " to " + str(val))
        self._attr_is_on = self._enable_value == val if self._enable_value is not None else bool(val)
        return True

    def turn_on(self, **kwargs: Any) -> None:
        if self._command:
            value = self._enable_value if self._enable_value is not None else 1
            self.send_set_message(value, self.command_dict(value))

    def turn_off(self, **kwargs: Any) -> None:
        if self._command:
            value = self._disable_value if self._disable_value is not None else 0
            self.send_set_message(value, self.command_dict(value))


class BeeperEntity(EnabledEntity):
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        client: EcoflowApiClient,
        device: BaseDevice,
        mqtt_key: str,
        title: str,
        command: Callable[[int], dict[str, Any] | Message]
        | Callable[[int, dict[str, Any]], dict[str, Any] | Message]
        | None,
        enabled: bool = True,
        auto_enable: bool = False,
        # Inverted logic for beeper
        enableValue: Any = 0,
        disableValue: Any = 1,
    ):
        super().__init__(
            client,
            device,
            mqtt_key,
            title,
            command,
            enabled,
            auto_enable,
            enableValue,
            disableValue,
        )

    @property
    def icon(self) -> str | None:
        if self.is_on:
            return "mdi:volume-high"
        else:
            return "mdi:volume-mute"


class InvertedBeeperEntity(EnabledEntity):
    _attr_entity_category = EntityCategory.CONFIG

    @property
    def icon(self) -> str | None:
        if self.is_on:
            return "mdi:volume-high"
        else:
            return "mdi:volume-mute"


class BypassBanScalarSwitch(EnabledEntity):
    """Grid-bypass switch reading state from a scalar varint mirror.

    Used by devices that expose the bypass state as a plain integer
    field in push telemetry (in contrast to a switch that would read
    an array index of a quota field).

    On DELTA 3 (protobuf transport) the state arrives via
    ``ban_bypass_en`` injected from field 146 of
    ``Delta3DisplayPropertyUpload``. The device sends Display updates
    both as deltas (when the bypass changes) and as full snapshots
    (in response to ``thing/property/get`` requests issued at HA
    integration setup), so the state is always live and never assumed.

    Semantics: ON = grid bypass disabled, battery runs standalone (no
    AC charging); OFF = grid bypass enabled, battery charges from AC
    input. Matches the "Disable grid bypass" toggle in the EcoFlow
    mobile app.
    """

    def _update_value(self, val: Any) -> bool:
        if isinstance(val, (int, bool)):
            new_state = bool(val)
            if self._attr_is_on != new_state:
                self._attr_is_on = new_state
                return True
        return False
