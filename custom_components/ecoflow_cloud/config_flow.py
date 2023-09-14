import logging
from typing import Dict, Any

import voluptuous as vol
from homeassistant import const
from homeassistant.config_entries import ConfigFlow, ConfigEntry, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from . import DOMAIN, CONFIG_VERSION
from .config.const import EcoflowModel, CONF_USERNAME, CONF_PASSWORD, CONF_DEVICE_TYPE, CONF_DEVICE_NAME, \
    CONF_DEVICE_ID, OPTS_POWER_STEP, OPTS_REFRESH_PERIOD_SEC, DEFAULT_REFRESH_PERIOD_SEC

_LOGGER = logging.getLogger(__name__)


class EcoflowConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = CONFIG_VERSION

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: Dict[str, str] = {}
        if user_input is not None and not errors:
            from .devices.registry import devices
            device = devices[user_input[CONF_DEVICE_TYPE]]

            options = {OPTS_POWER_STEP: device.charging_power_step(), OPTS_REFRESH_PERIOD_SEC: DEFAULT_REFRESH_PERIOD_SEC}

            return self.async_create_entry(title=user_input[const.CONF_NAME], data=user_input, options=options)

        return self.async_show_form(
            step_id="user",
            last_step=True,
            data_schema=vol.Schema({
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_DEVICE_TYPE): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=EcoflowModel.list(),
                                                  mode=selector.SelectSelectorMode.DROPDOWN),
                ),
                vol.Required(CONF_DEVICE_NAME): str,
                vol.Required(CONF_DEVICE_ID): str,
            })

        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return EcoflowOptionsFlow(config_entry)


class EcoflowOptionsFlow(OptionsFlow):
    def __init__(self, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            last_step=True,
            data_schema=vol.Schema({
                vol.Optional(OPTS_POWER_STEP,
                             default=self.config_entry.options[OPTS_POWER_STEP]): int,
                vol.Optional(OPTS_REFRESH_PERIOD_SEC,
                             default=self.config_entry.options[OPTS_REFRESH_PERIOD_SEC]): int,
            })
        )
