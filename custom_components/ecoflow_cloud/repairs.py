from __future__ import annotations

from copy import deepcopy
from typing import Any

import voluptuous as vol
from homeassistant import data_entry_flow
from homeassistant.components.repairs import RepairsFlow
from homeassistant.core import HomeAssistant
from homeassistant.helpers import selector

from . import (
    CONF_DEVICE_LIST,
    OPTS_BLE_WIFI_PASSWORD,
    OPTS_BLE_WIFI_SSID,
)

_BLE_WIFI_CREDENTIALS_ISSUE_PREFIX = "ble_wifi_credentials_"


class BleWifiCredentialsRepairFlow(RepairsFlow):
    """Repair flow for EcoFlow BLE Wi-Fi credentials."""

    def __init__(self, issue_data: dict[str, Any] | None) -> None:
        self._issue_data = issue_data or {}

    async def async_step_init(
        self,
        user_input: dict[str, str] | None = None,
    ) -> data_entry_flow.FlowResult:
        """Handle the fix flow."""
        entry_id = self._issue_data.get("entry_id")
        serial_number = self._issue_data.get("serial_number")
        if not isinstance(entry_id, str) or not isinstance(serial_number, str):
            return self.async_abort(reason="entry_missing")

        entry = self.hass.config_entries.async_get_entry(entry_id)
        if entry is None:
            return self.async_abort(reason="entry_missing")

        device_options = entry.options.get(CONF_DEVICE_LIST, {}).get(serial_number)
        if device_options is None:
            return self.async_abort(reason="device_missing")

        if user_input is not None:
            ssid = user_input[OPTS_BLE_WIFI_SSID].strip()
            password = user_input[OPTS_BLE_WIFI_PASSWORD].strip()
            if not ssid or not password:
                return self.async_show_form(
                    step_id="init",
                    data_schema=self._schema(
                        ssid=user_input[OPTS_BLE_WIFI_SSID],
                        password=user_input[OPTS_BLE_WIFI_PASSWORD],
                    ),
                    errors={"base": "missing_credentials"},
                )

            new_options = deepcopy(dict(entry.options))
            new_options[CONF_DEVICE_LIST][serial_number][OPTS_BLE_WIFI_SSID] = ssid
            new_options[CONF_DEVICE_LIST][serial_number][OPTS_BLE_WIFI_PASSWORD] = password
            self.hass.config_entries.async_update_entry(entry, options=new_options)
            return self.async_create_entry(title="", data={})

        current_ssid = (
            self._issue_data.get("suggested_ssid")
            or device_options.get(OPTS_BLE_WIFI_SSID, "")
        )
        return self.async_show_form(
            step_id="init",
            data_schema=self._schema(ssid=current_ssid, password=""),
        )

    @staticmethod
    def _schema(*, ssid: str, password: str) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required(OPTS_BLE_WIFI_SSID, default=ssid): selector.TextSelector(),
                vol.Required(
                    OPTS_BLE_WIFI_PASSWORD,
                    default=password,
                ): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
            }
        )


async def async_create_fix_flow(
    hass: HomeAssistant,
    issue_id: str,
    data: dict[str, str | int | float | None] | None,
) -> RepairsFlow:
    """Create flow for a repairs issue."""
    if issue_id.startswith(_BLE_WIFI_CREDENTIALS_ISSUE_PREFIX):
        return BleWifiCredentialsRepairFlow(data)

    raise ValueError(f"Unsupported issue id: {issue_id}")
