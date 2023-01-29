from enum import Enum
from typing import Dict

import voluptuous as vol
from homeassistant import const
from homeassistant.config_entries import ConfigFlow, ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.schema_config_entry_flow import SchemaOptionsFlowHandler, SchemaFlowFormStep

from . import DOMAIN

class EcoflowModel(Enum):
    DELTA_2 = 1,
    RIVER_2 = 2,
    RIVER_2_MAX = 3,
    RIVER_2_PRO = 4,
    DELTA_PRO = 5,
    RIVER_MAX = 6,
    DIAGNOSTIC = 99

    @classmethod
    def list(cls) -> list[str]:
        return [e.name for e in EcoflowModel]


OPTIONS_SCHEMA = vol.Schema({
    vol.Required(const.CONF_USERNAME): str,
    vol.Required(const.CONF_PASSWORD): str,
    vol.Required(const.CONF_TYPE): selector.SelectSelector(
                                    selector.SelectSelectorConfig(options=EcoflowModel.list(),
                                                                  mode=selector.SelectSelectorMode.DROPDOWN),
                    ),
    vol.Required(const.CONF_NAME): str,
    vol.Required(const.CONF_DEVICE_ID): str,
})

OPTIONS_FLOW = {
    "init": SchemaFlowFormStep(OPTIONS_SCHEMA),
}


class EcoflowConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict = None):
        errors: Dict[str, str] = {}
        if user_input is not None and not errors:
            return self.async_create_entry(title=user_input[const.CONF_NAME], data=user_input)

        if user_input is None:
            user_input = {}

        return self.async_show_form(
            step_id="user",
            data_schema=OPTIONS_SCHEMA,
            last_step=True,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> SchemaOptionsFlowHandler:
        return SchemaOptionsFlowHandler(config_entry, OPTIONS_FLOW)
