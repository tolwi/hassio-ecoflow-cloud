import logging
from typing import Dict, Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigEntry, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from . import DOMAIN, CONFIG_VERSION, CONF_ACCESS_KEY, CONF_SECRET_KEY, CONF_USERNAME, CONF_PASSWORD, \
    CONF_SELECT_DEVICE_KEY, CONF_DEVICE_TYPE, CONF_INSTALLATION_SITE, CONF_DEVICE_LIST, CONF_LOAD_AUTOMATIQUE, CONF_ENTRY_ID, CONF_DEVICE_NAME, CONF_DEVICE_ID, OPTS_DIAGNOSTIC_MODE, \
    OPTS_POWER_STEP, OPTS_REFRESH_PERIOD_SEC, DEFAULT_REFRESH_PERIOD_SEC
from .api import EcoflowException
from .devices import EcoflowDeviceInfo

_LOGGER = logging.getLogger(__name__)


API_SELECT_DEVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_SELECT_DEVICE_KEY): str
})


class EcoflowConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = CONFIG_VERSION

    def __init__(self) -> None:
        self.installation_site = "Home"
        self.config_entry: ConfigEntry | None = None

        self.username = None
        self.password = None

        self.secret_key = None
        self.access_key = None
        self.load_automatique_device = False
        self.cloud_device = None
        self.cloud_devices: dict[str, EcoflowDeviceInfo] = {}

    def set_device_list(self, device_list: list[EcoflowDeviceInfo]) -> None:
        for device in device_list:
            self.cloud_devices[f"{device.name} ({device.device_type})"] = device

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if not user_input:
            USER_STEP_SCHEMA = vol.Schema({
                vol.Required(CONF_INSTALLATION_SITE, default=self.installation_site): str
            })
            return self.async_show_form(step_id="user", data_schema=USER_STEP_SCHEMA)
        
        self.installation_site = user_input.get(CONF_INSTALLATION_SITE)
        unique_id = "api-" + self.installation_site
        existing_entry = await self.async_set_unique_id(unique_id, raise_on_progress=False)
        if existing_entry:
            data = existing_entry.data.copy()
            if CONF_USERNAME in data:
                self.username = data[CONF_USERNAME]
            if CONF_PASSWORD in data:
                self.password = data[CONF_PASSWORD]
            if CONF_SECRET_KEY in data:
                self.secret_key = data[CONF_SECRET_KEY]
            if CONF_ACCESS_KEY in data:
             self.access_key = data[CONF_ACCESS_KEY]

        return self.async_show_menu(
            step_id="reconfigure_user",
            menu_options=["api", "manual"]
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):

        if not user_input:
            USER_STEP_SCHEMA = vol.Schema({
                vol.Required(CONF_INSTALLATION_SITE, default=self.installation_site): str
            })
            return self.async_show_form(step_id="reconfigure", data_schema=USER_STEP_SCHEMA)
        
        self.installation_site = user_input.get(CONF_INSTALLATION_SITE)
        unique_id = "api-" + self.installation_site
        existing_entry = await self.async_set_unique_id(unique_id, raise_on_progress=False)
        if existing_entry:
            data = existing_entry.data.copy()
            if CONF_USERNAME in data:
                self.username = data[CONF_USERNAME]
            if CONF_PASSWORD in data:
                self.password = data[CONF_PASSWORD]
            if CONF_SECRET_KEY in data:
                self.secret_key = data[CONF_SECRET_KEY]
            if CONF_ACCESS_KEY in data:
             self.access_key = data[CONF_ACCESS_KEY]
            if CONF_LOAD_AUTOMATIQUE in data:
             self.load_automatique_device = data[CONF_LOAD_AUTOMATIQUE]

        return self.async_show_menu(
            step_id="reconfigure_user",
            menu_options=["api", "manual"]
        )
    async def async_step_reconfigure_user(self, user_input: dict[str, Any] | None = None):
        if not user_input:
            return self.async_show_menu(
                step_id="reconfigure_user",
                menu_options=["api", "manual"]
            )

    async def async_step_manual(self, user_input: dict[str, Any] | None = None) -> FlowResult:

        USER_AUTH_SCHEMA = vol.Schema({
            vol.Required(CONF_INSTALLATION_SITE, default=self.installation_site): str,
            vol.Required(CONF_USERNAME, default=self.username): str,
            vol.Required(CONF_PASSWORD, default=self.password): str,
        })
        if not user_input:
            return self.async_show_form(step_id="manual", data_schema=USER_AUTH_SCHEMA)

        self.installation_site = user_input.get(CONF_INSTALLATION_SITE)
        self.username = user_input.get(CONF_USERNAME)
        self.password = user_input.get(CONF_PASSWORD)

        from .api.private_api import EcoflowPrivateApiClient
        auth = EcoflowPrivateApiClient(self.username, self.password, self.installation_site)

        errors: Dict[str, str] = {}
        try:
            await auth.login()
        except EcoflowException as e:  # pylint: disable=broad-except
            errors["base"] = str(e)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception in login action")
            return self.async_abort(reason="unknown")

        if errors:
            return self.async_show_form(step_id="manual", data_schema=USER_AUTH_SCHEMA, errors=errors)

        return await self.async_step_manual_device_input()

    async def async_step_manual_device_input(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        from .devices.registry import devices
        if not user_input:
            device_list = list(devices.keys())
            return self.async_show_form(step_id="manual_device_input", data_schema=vol.Schema({
                vol.Required(CONF_DEVICE_TYPE): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=device_list,
                                                  mode=selector.SelectSelectorMode.DROPDOWN),
                ),
                vol.Required(CONF_DEVICE_NAME): str,
                vol.Required(CONF_DEVICE_ID): str,
            }))

        device = devices[user_input[CONF_DEVICE_TYPE]]

        options = {OPTS_POWER_STEP: device.charging_power_step(),
                   OPTS_REFRESH_PERIOD_SEC: DEFAULT_REFRESH_PERIOD_SEC,
                   OPTS_DIAGNOSTIC_MODE: user_input[CONF_DEVICE_TYPE] == "DIAGNOSTIC"}
        
        unique_id = "api-" + self.installation_site
        existing_entry = await self.async_set_unique_id(unique_id, raise_on_progress=False)

        if existing_entry:
            data = existing_entry.data.copy()
            data[CONF_USERNAME] = self.username
            data[CONF_PASSWORD] = self.password
            data[CONF_INSTALLATION_SITE] = self.installation_site
            data[CONF_ENTRY_ID] = existing_entry.entry_id
            to_delete = {}
            for device_data in data[CONF_DEVICE_LIST]:
                if device_data[CONF_DEVICE_ID] == self.cloud_device.sn:
                    to_delete = device_data
                    break
            if to_delete:
                data[CONF_DEVICE_LIST].remove(to_delete)

            data[CONF_DEVICE_LIST].append({
                CONF_DEVICE_TYPE: user_input[CONF_DEVICE_TYPE],
                CONF_DEVICE_NAME: user_input[CONF_DEVICE_NAME],
                CONF_DEVICE_ID: user_input[CONF_DEVICE_ID]
            })
            
            if self.hass.config_entries.async_update_entry(existing_entry, data=data):
                await self.hass.config_entries.async_reload(existing_entry.entry_id)
            return self.async_abort(reason="updated_successfully")
        else:
            data = {
                CONF_INSTALLATION_SITE: self.installation_site,
                CONF_USERNAME: self.username,
                CONF_PASSWORD: self.password,
                CONF_DEVICE_LIST:[{
                    CONF_DEVICE_TYPE: user_input[CONF_DEVICE_TYPE],
                    CONF_DEVICE_NAME: user_input[CONF_DEVICE_NAME],
                    CONF_DEVICE_ID: user_input[CONF_DEVICE_ID]
                }],
            }
            return self.async_create_entry(title=self.installation_site, data=data, options=options)


    async def async_step_api(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        API_KEYS_AUTH_SCHEMA = vol.Schema({
            vol.Required(CONF_INSTALLATION_SITE, default=self.installation_site): str,
            vol.Required(CONF_ACCESS_KEY, default=self.access_key): str,
            vol.Required(CONF_SECRET_KEY, default=self.secret_key): str,
            vol.Required(CONF_LOAD_AUTOMATIQUE, default=self.load_automatique_device): bool
        })

        if not user_input:
            return self.async_show_form(step_id="api", data_schema=API_KEYS_AUTH_SCHEMA)

        installation_site = user_input.get(CONF_INSTALLATION_SITE)
        access_key = user_input.get(CONF_ACCESS_KEY)
        secret_key = user_input.get(CONF_SECRET_KEY)
        load_automatique_device = user_input.get(CONF_LOAD_AUTOMATIQUE)

        from .api.public_api import EcoflowPublicApiClient
        auth = EcoflowPublicApiClient(access_key, secret_key, installation_site)

        errors: Dict[str, str] = {}
        try:
            await auth.login()
        except EcoflowException as e:  # pylint: disable=broad-except
            errors["base"] = str(e)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception in login action")
            return self.async_abort(reason="unknown")

        if errors:
            return self.async_show_form(step_id="api", data_schema=API_KEYS_AUTH_SCHEMA, errors=errors)

        self.installation_site = installation_site
        self.access_key = access_key
        self.secret_key = secret_key
        self.load_automatique_device = load_automatique_device

        if  load_automatique_device:
            unique_id = "api-" + self.installation_site
            await self.async_set_unique_id(unique_id, raise_on_progress=False)
            return self.async_create_entry(
                title=self.installation_site,
                data={
                    CONF_INSTALLATION_SITE: self.installation_site,
                    CONF_LOAD_AUTOMATIQUE: self.load_automatique_device,
                    CONF_ACCESS_KEY: self.access_key,
                    CONF_SECRET_KEY: self.secret_key
                },
                options={OPTS_POWER_STEP: 100,
                   OPTS_REFRESH_PERIOD_SEC: DEFAULT_REFRESH_PERIOD_SEC,
                   OPTS_DIAGNOSTIC_MODE: False}
            )
        else:
            try:
                devices = await auth.fetch_all_available_devices()
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception in fetch device action")
                return self.async_abort(reason="unknown")

            self.set_device_list(devices)

        return await self.async_step_select_device()

    async def async_step_select_device(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if not user_input:
            return self.async_show_form(step_id="select_device",
                                        data_schema=vol.Schema({
                                            vol.Required(CONF_SELECT_DEVICE_KEY): vol.In(list(self.cloud_devices))
                                        }))

        self.cloud_device = self.cloud_devices[user_input[CONF_SELECT_DEVICE_KEY]]
        unique_id = "api-" + self.installation_site
        await self.async_set_unique_id(unique_id, raise_on_progress=False)

        return await self.async_step_confirm_cloud_device()


    async def async_step_confirm_cloud_device(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        from .devices.registry import device_by_product
        if not user_input:
            device_list = list(device_by_product.keys())
            return self.async_show_form(step_id="confirm_cloud_device",
                                        data_schema=vol.Schema({
                                            vol.Required(CONF_DEVICE_TYPE, default=self.cloud_device.device_type):
                                                selector.SelectSelector(
                                                    selector.SelectSelectorConfig(options=device_list,
                                                                                  mode=selector.SelectSelectorMode.DROPDOWN),
                                                ),
                                            vol.Required(CONF_DEVICE_NAME, default=self.cloud_device.name): str,
                                            vol.Required(CONF_DEVICE_ID, default=self.cloud_device.sn): str,
                                        }))

        device = device_by_product[user_input[CONF_DEVICE_TYPE]]
        options = {OPTS_POWER_STEP: device.charging_power_step(),
                   OPTS_REFRESH_PERIOD_SEC: DEFAULT_REFRESH_PERIOD_SEC,
                   OPTS_DIAGNOSTIC_MODE: user_input[CONF_DEVICE_TYPE] == "DIAGNOSTIC"}

        unique_id = "api-" + self.installation_site
        existing_entry = await self.async_set_unique_id(unique_id, raise_on_progress=False)
        if existing_entry:
            data = existing_entry.data.copy()
            data[CONF_ACCESS_KEY] = self.access_key
            data[CONF_SECRET_KEY] = self.secret_key
            data[CONF_INSTALLATION_SITE] = self.installation_site
            data[CONF_LOAD_AUTOMATIQUE] = self.load_automatique_device
            data[CONF_ENTRY_ID] = existing_entry.entry_id
            if CONF_DEVICE_LIST in data:
                to_delete = {}
                for device_data in data[CONF_DEVICE_LIST]:
                    if device_data[CONF_DEVICE_ID] == self.cloud_device.sn:
                        to_delete = device_data
                if to_delete:
                    data[CONF_DEVICE_LIST].remove(to_delete)
            else:
                data[CONF_DEVICE_LIST]=[]
            data[CONF_DEVICE_LIST].append({
                CONF_DEVICE_TYPE: user_input[CONF_DEVICE_TYPE],
                CONF_DEVICE_NAME: user_input[CONF_DEVICE_NAME],
                CONF_DEVICE_ID: user_input[CONF_DEVICE_ID]
            })

            if self.hass.config_entries.async_update_entry(existing_entry, data=data):
                await self.hass.config_entries.async_reload(existing_entry.entry_id)
            return self.async_abort(reason="updated_successfully")
        else:
            return self.async_create_entry(
                title=self.installation_site,
                data={
                    CONF_INSTALLATION_SITE: self.installation_site,
                    CONF_LOAD_AUTOMATIQUE: self.load_automatique_device,
                    CONF_ACCESS_KEY: self.access_key,
                    CONF_SECRET_KEY: self.secret_key,
                    CONF_DEVICE_LIST:[{
                        CONF_DEVICE_TYPE: user_input[CONF_DEVICE_TYPE],
                        CONF_DEVICE_NAME: user_input[CONF_DEVICE_NAME],
                        CONF_DEVICE_ID: user_input[CONF_DEVICE_ID]
                    }],
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
                vol.Required(OPTS_POWER_STEP, default=self.config_entry.options[OPTS_POWER_STEP]): int,
                vol.Required(OPTS_REFRESH_PERIOD_SEC, default=self.config_entry.options[OPTS_REFRESH_PERIOD_SEC]): int,
                vol.Required(OPTS_DIAGNOSTIC_MODE, default=self.config_entry.options[OPTS_DIAGNOSTIC_MODE]): bool,
            })
        )
