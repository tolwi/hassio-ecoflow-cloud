import logging
from typing import Dict, Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigEntry, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from . import DOMAIN, CONFIG_VERSION
from .api import EcoflowException
from .config import const
from .devices import EcoflowDeviceInfo

_LOGGER = logging.getLogger(__name__)

API_KEYS_AUTH_SCHEMA = vol.Schema({
    vol.Required(const.CONF_ACCESS_KEY): str,
    vol.Required(const.CONF_SECRET_KEY): str
})

USER_AUTH_SCHEMA = vol.Schema({
    vol.Required(const.CONF_USERNAME): str,
    vol.Required(const.CONF_PASSWORD): str
})

USER_MANUAL_DEVICE_SCHEMA = vol.Schema({
    vol.Required(const.CONF_DEVICE_TYPE): selector.SelectSelector(
        selector.SelectSelectorConfig(options=const.EcoflowModel.list(),
                                      mode=selector.SelectSelectorMode.DROPDOWN),
    ),
    vol.Required(const.CONF_DEVICE_NAME): str,
    vol.Required(const.CONF_DEVICE_ID): str,
})
API_SELECT_DEVICE_SCHEMA = vol.Schema({
    vol.Required(const.CONF_SELECT_DEVICE_KEY): str
})


class EcoflowConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = CONFIG_VERSION

    def __init__(self) -> None:
        self.username = None
        self.password = None

        self.secret_key = None
        self.access_key = None
        self.cloud_device = None
        self.cloud_devices: dict[str, EcoflowDeviceInfo] = {}

    def set_device_list(self, device_list: list[EcoflowDeviceInfo]) -> None:
        for device in device_list:
            self.cloud_devices[f"{device.name} ({device.device_type})"] = device

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if not user_input:
            return self.async_show_menu(
                step_id="user",
                menu_options=["api", "manual"]
            )

    async def async_step_manual(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if not user_input:
            return self.async_show_form(step_id="manual", data_schema=USER_AUTH_SCHEMA)

        self.username = user_input.get(const.CONF_USERNAME)
        self.password = user_input.get(const.CONF_PASSWORD)

        from .api.private_api import EcoflowPrivateApiClient
        auth = EcoflowPrivateApiClient(self.username, self.password)

        errors: Dict[str, str] = {}
        try:
            if not await self.hass.async_add_executor_job(auth.login):
                errors["base"] = "user_login_error"

        except EcoflowException as e:  # pylint: disable=broad-except
            errors["base"] = str(e)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception in login action")
            return self.async_abort(reason="unknown")

        if errors:
            return self.async_show_form(step_id="manual", data_schema=USER_AUTH_SCHEMA, errors=errors)

        return await self.async_step_manual_device_input()

    async def async_step_manual_device_input(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if not user_input:
            return self.async_show_form(step_id="manual_device_input", data_schema=USER_MANUAL_DEVICE_SCHEMA)

        from .devices.registry import devices
        device = devices[user_input[const.CONF_DEVICE_TYPE]]

        options = {const.OPTS_POWER_STEP: device.charging_power_step(),
                   const.OPTS_REFRESH_PERIOD_SEC: const.DEFAULT_REFRESH_PERIOD_SEC,
                   const.OPTS_DIAGNOSTIC_MODE: user_input[const.CONF_DEVICE_TYPE] == "DIAGNOSTIC"}

        data = {
            const.CONF_USERNAME: self.username,
            const.CONF_PASSWORD: self.password,
            const.CONF_DEVICE_TYPE: user_input[const.CONF_DEVICE_TYPE],
            const.CONF_DEVICE_NAME: user_input[const.CONF_DEVICE_NAME],
            const.CONF_DEVICE_ID: user_input[const.CONF_DEVICE_ID],
        }

        return self.async_create_entry(title=user_input[const.CONF_DEVICE_NAME], data=data, options=options)

    async def async_step_api(self, user_input: dict[str, Any] | None = None) -> FlowResult:

        if not user_input:
            return self.async_show_form(step_id="api", data_schema=API_KEYS_AUTH_SCHEMA)

        access_key = user_input.get(const.CONF_ACCESS_KEY)
        secret_key = user_input.get(const.CONF_SECRET_KEY)

        from .api.public_api import EcoflowPublicApiClient
        auth = EcoflowPublicApiClient(access_key, secret_key)

        errors: Dict[str, str] = {}
        try:
            if not await self.hass.async_add_executor_job(auth.login):
                errors["base"] = "cloud_login_error"

        except EcoflowException as e:  # pylint: disable=broad-except
            errors["base"] = str(e)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception in login action")
            return self.async_abort(reason="unknown")

        if errors:
            return self.async_show_form(step_id="api", data_schema=API_KEYS_AUTH_SCHEMA, errors=errors)

        try:
            devices = await auth.fetch_all_available_devices()
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception in fetch device action")
            return self.async_abort(reason="unknown")

        self.set_device_list(devices)

        self.access_key = access_key
        self.secret_key = secret_key

        return await self.async_step_select_device()

    async def async_step_select_device(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if not user_input:
            return self.async_show_form(step_id="select_device",
                                        data_schema=vol.Schema({
                                            vol.Required(const.CONF_SELECT_DEVICE_KEY): vol.In(list(self.cloud_devices))
                                        }))

        self.cloud_device = self.cloud_devices[user_input["select_device"]]
        unique_id = "api-" + self.cloud_device.sn
        existing_entry = await self.async_set_unique_id(unique_id, raise_on_progress=False)
        if existing_entry:
            data = existing_entry.data.copy()
            data[const.CONF_ACCESS_KEY] = self.access_key
            data[const.CONF_SECRET_KEY] = self.secret_key

            if self.hass.config_entries.async_update_entry(existing_entry, data=data):
                await self.hass.config_entries.async_reload(existing_entry.entry_id)
            return self.async_abort(reason="updated_successfully")
        else:

            return await self.async_step_confirm_cloud_device()

    async def async_step_confirm_cloud_device(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if not user_input:
            return self.async_show_form(step_id="confirm_cloud_device",
                                        data_schema=vol.Schema({
                                            vol.Required(const.CONF_DEVICE_TYPE, default=self.cloud_device.device_type): selector.SelectSelector(
                                                selector.SelectSelectorConfig(options=const.EcoflowApiProducts.list(),
                                                                              mode=selector.SelectSelectorMode.DROPDOWN),
                                            ),
                                            vol.Required(const.CONF_DEVICE_NAME, default=self.cloud_device.name): str,
                                            vol.Required(const.CONF_DEVICE_ID, default=self.cloud_device.sn): str,
                                        }))

        from .devices.registry import device_by_product
        device = device_by_product[user_input[const.CONF_DEVICE_TYPE]]
        options = {const.OPTS_POWER_STEP: device.charging_power_step(),
                   const.OPTS_REFRESH_PERIOD_SEC: const.DEFAULT_REFRESH_PERIOD_SEC,
                   const.OPTS_DIAGNOSTIC_MODE: user_input[const.CONF_DEVICE_TYPE] == "DIAGNOSTIC"}
        return self.async_create_entry(
            title=user_input[const.CONF_DEVICE_NAME],
            data={
                const.CONF_ACCESS_KEY: self.access_key,
                const.CONF_SECRET_KEY: self.secret_key,
                const.CONF_DEVICE_TYPE: user_input[const.CONF_DEVICE_TYPE],
                const.CONF_DEVICE_NAME: user_input[const.CONF_DEVICE_NAME],
                const.CONF_DEVICE_ID: user_input[const.CONF_DEVICE_ID],
            },
            options=options
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
                vol.Required(const.OPTS_POWER_STEP,
                             default=self.config_entry.options[const.OPTS_POWER_STEP]): int,
                vol.Required(const.OPTS_REFRESH_PERIOD_SEC,
                             default=self.config_entry.options[const.OPTS_REFRESH_PERIOD_SEC]): int,
                vol.Required(const.OPTS_DIAGNOSTIC_MODE,
                             default=self.config_entry.options[const.OPTS_DIAGNOSTIC_MODE]): bool,
            })
        )
