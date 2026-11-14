from __future__ import annotations

import logging
from collections.abc import Mapping
from copy import deepcopy
from typing import Any

import voluptuous as vol
from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import selector
from homeassistant.helpers.device_registry import DeviceRegistry
from homeassistant.helpers.entity_registry import EntityRegistry

from custom_components.ecoflow_cloud import (
    CONF_ACCESS_KEY,
    CONF_API_HOST,
    CONF_DEVICE_ID,
    CONF_DEVICE_LIST,
    CONF_DEVICE_NAME,
    CONF_DEVICE_TYPE,
    CONF_GROUP,
    CONF_IGNORED_MODULES,
    CONF_PARENT_SN,
    CONF_PASSWORD,
    CONF_SECRET_KEY,
    CONF_SELECT_DEVICE_KEY,
    CONF_TO_REDACT,
    CONF_USERNAME,
    CONFIG_VERSION,
    DEFAULT_ASSUME_OFFLINE_SEC,
    DEFAULT_ENERGY_UPDATE_INTERVAL_SEC,
    DEFAULT_REFRESH_PERIOD_SEC,
    DEFAULT_RESET_SENSORS_ON_OFFLINE,
    ECOFLOW_DOMAIN,
    OPTS_ASSUME_OFFLINE_SEC,
    OPTS_DIAGNOSTIC_MODE,
    OPTS_ENERGY_UPDATE_INTERVAL_SEC,
    OPTS_POWER_STEP,
    OPTS_REFRESH_PERIOD_SEC,
    OPTS_RESET_SENSORS_ON_OFFLINE,
    OPTS_VERBOSE_STATUS_MODE,
    DeviceData,
    DeviceOptions,
    extract_devices,
)

from .api import EcoflowAuthException, EcoflowException
from .devices import EcoflowDeviceInfo

_LOGGER = logging.getLogger(__name__)

API_SELECT_DEVICE_SCHEMA = vol.Schema({vol.Required(CONF_SELECT_DEVICE_KEY): str})


def _modules_from_public_quota(data: dict[str, Any]) -> list[tuple[str, str]]:
    """``(module_type, module_sn)`` pairs from a public API ``/device/quota/all`` response.

    The response for a Power Kit is a FLAT dict whose keys look like
    "<moduleType>.<moduleSn>.<field>" (e.g. "bp5000.M101Z3B4ZE5A0737.soc"), with
    scalar values. Aggregate keys such as "bmsTotal.<field>" carry no module serial.
    Older firmware/API returned a nested dict ({type: {sn: {...}}}); support both.
    """
    discovered: list[tuple[str, str]] = []
    for key, value in data.items():
        parts = key.split(".")
        if len(parts) >= 3:
            sub_device_type, sub_device_sn = parts[0], parts[1]
            if (sub_device_type, sub_device_sn) not in discovered:
                discovered.append((sub_device_type, sub_device_sn))
        elif isinstance(value, dict):
            # legacy nested shape: {sub_device_type: {sub_device_sn: {...}}}
            for sub_device_sn, item in value.items():
                if isinstance(item, dict | list) and (key, sub_device_sn) not in discovered:
                    discovered.append((key, sub_device_sn))
    return discovered


class EcoflowConfigFlow(ConfigFlow, domain=ECOFLOW_DOMAIN):
    VERSION = CONFIG_VERSION

    def __init__(self) -> None:
        self.auth = None
        self.config_entry: ConfigEntry | None = None
        self.new_data = {}
        self.new_options = {}

        self.cloud_device = None
        self.cloud_devices: dict[str, EcoflowDeviceInfo] = {}
        self.local_devices: dict[str, DeviceData] = {}
        # serials of the devices added in this flow; their module discovery is expected to succeed
        self.added_devices: set[str] = set()

    def set_current_config_entry(self, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry
        self.new_data = deepcopy(dict(config_entry.data))
        self.new_options = deepcopy(dict(config_entry.options))

    def set_device_list(self, device_list: list[EcoflowDeviceInfo]) -> None:
        for device in device_list:
            self.cloud_devices[f"{device.name} ({device.device_type})"] = device

    def set_local_device_list(self, devices: list[DeviceData]) -> None:
        for device in devices:
            self.local_devices[f"{device.name} ({device.sn})"] = device

    async def update_or_create(self, discover: bool = True):
        if discover:
            await self._discover_sub_devices()

        if self.config_entry:  # reconfig flow
            _LOGGER.info(
                ".. reconfigure: entry = %s, data = %s, options = %s ",
                str(self.config_entry),
                async_redact_data(self.new_data, CONF_TO_REDACT),
                str(self.new_options),
            )
            if self.hass.config_entries.async_update_entry(
                entry=self.config_entry, data=self.new_data, options=self.new_options
            ):
                # reload if changed
                self.hass.config_entries.async_schedule_reload(self.config_entry.entry_id)

            return self.async_abort(reason="reconfigure_successful")

        else:
            _LOGGER.info(
                ".. create: entry = %s, data = %s, options = %s ",
                str(self.config_entry),
                async_redact_data(self.new_data, CONF_TO_REDACT),
                str(self.new_options),
            )

            return self.async_create_entry(
                title=self.new_data[CONF_GROUP],
                data=self.new_data,
                options=self.new_options,
            )

    async def _discover_sub_devices(self) -> None:
        """Add the modules of every multi-module device (Power Kits) that are not configured yet.

        Runs for the create and the reconfigure flow alike, except right after a removal.
        Configured sub devices keep their names and options, modules removed through the
        remove-device flow stay removed (their parent remembers them), and a module that was
        offline at an earlier discovery is added as soon as the hub reports it.
        """
        from .devices.internal.powerkit_data import SN_TYPE_SEPARATOR, real_sn
        from .devices.registry import device_support_sub_devices

        device_list = self.new_data.get(CONF_DEVICE_LIST, {})

        # iterate over a snapshot: the loop mutates new_data[CONF_DEVICE_LIST]
        for sn, device_data in list(device_list.items()):
            if device_data[CONF_DEVICE_TYPE] not in device_support_sub_devices or CONF_PARENT_SN in device_data:
                continue

            try:
                discovered = await self._discover_modules(sn)
            except Exception:
                _LOGGER.exception("Module discovery for %s failed; reconfigure the integration to retry", sn)
                continue
            if not discovered:
                if sn in self.added_devices:
                    _LOGGER.warning(
                        "No modules reported for %s; is it online? Reconfigure the integration to retry", sn
                    )
                continue

            configured = {
                (d[CONF_DEVICE_TYPE], real_sn(key)) for key, d in device_list.items() if d.get(CONF_PARENT_SN) == sn
            }
            ignored = set(device_data.get(CONF_IGNORED_MODULES, []))

            # some modules (e.g. "wireless") report under the parent's serial; skip
            # those to avoid overwriting the parent device entry
            modules = [(t, s) for t, s in discovered if s != sn]
            serial_count = {s: sum(1 for _, x in modules if x == s) for _, s in modules}
            for sub_device_type, sub_device_sn in modules:
                # the device list is keyed by serial; modules sharing one get a typed key
                key = sub_device_sn
                if serial_count[sub_device_sn] > 1:
                    key = f"{sub_device_sn}{SN_TYPE_SEPARATOR}{sub_device_type}"
                if (sub_device_type, sub_device_sn) in configured or key in ignored or sub_device_sn in ignored:
                    continue
                self.new_data[CONF_DEVICE_LIST][key] = {
                    CONF_DEVICE_NAME: f"{device_data[CONF_DEVICE_NAME]}.{sub_device_type}.{sub_device_sn}",
                    CONF_DEVICE_TYPE: sub_device_type,
                    CONF_PARENT_SN: sn,
                }
                self.new_options[CONF_DEVICE_LIST][key] = dict(self.new_options[CONF_DEVICE_LIST][sn])
                _LOGGER.info("Added module %s (%s) of %s", sub_device_sn, sub_device_type, sn)

    async def _discover_modules(self, sn: str) -> list[tuple[str, str]]:
        """``(module_type, module_sn)`` of a multi-module device, from whichever API the flow is logged in to."""
        from .api.private_api import EcoflowPrivateApiClient
        from .api.public_api import EcoflowPublicApiClient

        if isinstance(self.auth, EcoflowPublicApiClient):
            all_device_info = await self.auth.call_api("/device/quota/all", {"sn": sn})
            return _modules_from_public_quota(all_device_info.get("data", {}))

        if isinstance(self.auth, EcoflowPrivateApiClient):
            from .devices.internal.powerkit_data import discover_modules

            # the app protocol has no REST quota call; ask the hub itself over MQTT
            reply = await self.auth.fetch_latest_quotas(sn)
            if reply is None:
                return []
            return discover_modules(reply.get("quotaMap"), sn)

        return []

    def remove_device(self, sn: str):
        # Get the device registry
        device_reg: DeviceRegistry = dr.async_get(self.hass)

        if CONF_ACCESS_KEY in self.config_entry.data:
            identifiers = {(ECOFLOW_DOMAIN, f"api-{sn}")}
        else:
            identifiers = {(ECOFLOW_DOMAIN, f"{sn}")}

        device = device_reg.async_get_device(identifiers=identifiers)
        _LOGGER.debug(".. getting device by %s: %s", str(identifiers), str(device))

        # Remove all entities for this device
        if getattr(device, "id", None) is not None:
            ent_reg: EntityRegistry = er.async_get(self.hass)
            entities = er.async_entries_for_device(ent_reg, device.id)

            for entity in entities:
                ent_reg.async_remove(entity.entity_id)

            # Remove the device from the device registry
            device_reg.async_remove_device(device.id)

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if self.config_entry:  # reconfigure flow
            return await self.async_step_choose_type()

        if not user_input:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({vol.Required(CONF_GROUP, default=self.new_data.get(CONF_GROUP, "Home")): str}),
            )

        self.new_data[CONF_GROUP] = user_input.get(CONF_GROUP)
        existing_entry = await self.async_set_unique_id("group-" + self.new_data[CONF_GROUP], raise_on_progress=False)

        if existing_entry:
            return self.async_abort(reason="do_reconfigure_existing")

        return await self.async_step_choose_type()

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        self.set_current_config_entry(self.hass.config_entries.async_get_entry(self.context["entry_id"]))
        return await self.async_step_user()

    async def async_step_reauth(self, entry_data: Mapping[str, Any] | None = None):
        self.set_current_config_entry(self.hass.config_entries.async_get_entry(self.context["entry_id"]))
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None):
        public_api = CONF_ACCESS_KEY in self.new_data

        # HA fills "name" from the entry title on newer cores; set it so older ones match
        placeholders = {"name": self.new_data.get(CONF_GROUP, "")}

        if not user_input:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=self._schema_for(public_api),
                description_placeholders=placeholders,
            )

        if public_api:
            self._set_api_credentials(user_input)
            self.auth = self._create_api_client()
        else:
            self._set_manual_credentials(user_input)
            self.auth = self._create_manual_client()

        errors: dict[str, str] = {}
        try:
            await self.auth.login()
        except EcoflowAuthException as e:
            errors["base"] = "invalid_access_key" if public_api else str(e)
        except EcoflowException as e:
            errors["base"] = str(e)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception in reauth login action")
            return self.async_abort(reason="unknown")

        if errors:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=self._schema_for(public_api),
                errors=errors,
                description_placeholders=placeholders,
            )

        # credentials only: the device list and its options stay as they were
        self.hass.config_entries.async_update_entry(entry=self.config_entry, data=self.new_data)
        # unconditional: the entry is in a failed state even when the data did not change
        self.hass.config_entries.async_schedule_reload(self.config_entry.entry_id)
        return self.async_abort(reason="reauth_successful")

    async def async_step_choose_type(self, user_input: dict[str, Any] | None = None):
        if self.config_entry:  # reconfig flow
            if CONF_ACCESS_KEY in self.config_entry.data:
                return await self.async_step_api()
            else:
                return await self.async_step_manual()

        if not user_input:
            return self.async_show_menu(step_id="choose_type", menu_options=["api", "manual"])

    def _manual_schema(self) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required(CONF_API_HOST, default=self.new_data.get(CONF_API_HOST, "api.ecoflow.com")): str,
                vol.Required(CONF_USERNAME, default=self.new_data.get(CONF_USERNAME, "")): str,
                vol.Required(CONF_PASSWORD, default=self.new_data.get(CONF_PASSWORD, "")): str,
            }
        )

    def _api_schema(self) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required(
                    CONF_API_HOST, default=self.new_data.get(CONF_API_HOST, "api-e.ecoflow.com")
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=["api-e.ecoflow.com", "api-a.ecoflow.com"],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    ),
                ),
                vol.Required(CONF_ACCESS_KEY, default=self.new_data.get(CONF_ACCESS_KEY, "")): str,
                vol.Required(CONF_SECRET_KEY, default=self.new_data.get(CONF_SECRET_KEY, "")): str,
            }
        )

    def _schema_for(self, public_api: bool) -> vol.Schema:
        return self._api_schema() if public_api else self._manual_schema()

    def _set_manual_credentials(self, user_input: dict[str, Any]) -> None:
        self.new_data[CONF_API_HOST] = user_input.get(CONF_API_HOST)
        self.new_data[CONF_USERNAME] = user_input.get(CONF_USERNAME)
        self.new_data[CONF_PASSWORD] = user_input.get(CONF_PASSWORD)

    def _set_api_credentials(self, user_input: dict[str, Any]) -> None:
        self.new_data[CONF_API_HOST] = user_input.get(CONF_API_HOST)
        # keys get pasted from the developer portal, often with stray whitespace that breaks the signature
        self.new_data[CONF_ACCESS_KEY] = user_input.get(CONF_ACCESS_KEY, "").strip()
        self.new_data[CONF_SECRET_KEY] = user_input.get(CONF_SECRET_KEY, "").strip()

    def _create_manual_client(self):
        from .api.private_api import EcoflowPrivateApiClient

        return EcoflowPrivateApiClient(
            self.new_data[CONF_API_HOST],
            self.new_data[CONF_USERNAME],
            self.new_data[CONF_PASSWORD],
            self.new_data[CONF_GROUP],
        )

    def _create_api_client(self):
        from .api.public_api import EcoflowPublicApiClient

        return EcoflowPublicApiClient(
            self.new_data[CONF_API_HOST],
            self.new_data[CONF_ACCESS_KEY],
            self.new_data[CONF_SECRET_KEY],
            self.new_data[CONF_GROUP],
        )

    async def async_step_manual(self, user_input: dict[str, Any] | None = None):
        if not user_input:
            return self.async_show_form(step_id="manual", data_schema=self._manual_schema())

        self._set_manual_credentials(user_input)
        self.auth = self._create_manual_client()

        errors: dict[str, str] = {}
        try:
            await self.auth.login()
        except EcoflowException as e:  # pylint: disable=broad-except
            errors["base"] = str(e)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception in login action")
            return self.async_abort(reason="unknown")

        if errors:
            return self.async_show_form(step_id="manual", data_schema=self._manual_schema(), errors=errors)

        if self.config_entry:  # reconfig flow
            devices = extract_devices(self.config_entry)
            self.set_local_device_list(list(devices.values()))

            return self.async_show_menu(
                step_id="manual",
                menu_options=["manual_add_device", "remove_device", "finish"],
            )
        else:
            return await self.async_step_manual_device_input()

    async def async_step_manual_add_device(self, user_input: dict[str, Any] | None = None):
        return await self.async_step_manual_device_input()

    async def async_step_manual_device_input(self, user_input: dict[str, Any] | None = None):
        from .devices.registry import devices

        if not user_input:
            device_list = list(devices.keys())
            device_list.remove("DIAGNOSTIC")
            return self.async_show_form(
                step_id="manual_device_input",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_DEVICE_TYPE): selector.SelectSelector(
                            selector.SelectSelectorConfig(
                                options=device_list,
                                mode=selector.SelectSelectorMode.DROPDOWN,
                            ),
                        ),
                        vol.Required(CONF_DEVICE_NAME): str,
                        vol.Required(CONF_DEVICE_ID): str,
                    }
                ),
            )

        device = devices[user_input[CONF_DEVICE_TYPE]]

        sn = user_input[CONF_DEVICE_ID]
        if CONF_DEVICE_LIST not in self.new_data:
            self.new_data[CONF_DEVICE_LIST] = {}
            self.new_options[CONF_DEVICE_LIST] = {}

        self.new_data[CONF_DEVICE_LIST][sn] = {
            CONF_DEVICE_NAME: user_input[CONF_DEVICE_NAME],
            CONF_DEVICE_TYPE: user_input[CONF_DEVICE_TYPE],
        }
        self.added_devices.add(sn)
        self.new_options[CONF_DEVICE_LIST][sn] = {
            OPTS_REFRESH_PERIOD_SEC: DEFAULT_REFRESH_PERIOD_SEC,
            OPTS_POWER_STEP: device.default_charging_power_step(),
            OPTS_DIAGNOSTIC_MODE: False,
            OPTS_VERBOSE_STATUS_MODE: False,
            OPTS_ASSUME_OFFLINE_SEC: DEFAULT_ASSUME_OFFLINE_SEC,
            OPTS_RESET_SENSORS_ON_OFFLINE: DEFAULT_RESET_SENSORS_ON_OFFLINE,
            OPTS_ENERGY_UPDATE_INTERVAL_SEC: DEFAULT_ENERGY_UPDATE_INTERVAL_SEC,
        }

        return await self.update_or_create()

    async def async_step_api(self, user_input: dict[str, Any] | None = None):
        if not user_input:
            return self.async_show_form(step_id="api", data_schema=self._api_schema())

        self._set_api_credentials(user_input)
        self.auth = self._create_api_client()

        errors: dict[str, str] = {}
        try:
            await self.auth.login()
        except EcoflowAuthException:
            errors["base"] = "invalid_access_key"
        except EcoflowException as e:  # pylint: disable=broad-except
            errors["base"] = str(e)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception in login action")
            return self.async_abort(reason="unknown")

        if errors:
            # rebuilt, not reused: the schema defaults now carry the credentials just entered
            return self.async_show_form(step_id="api", data_schema=self._api_schema(), errors=errors)

        if self.config_entry:  # reconfig flow
            devices = extract_devices(self.config_entry)
            self.set_local_device_list(list(devices.values()))

            return self.async_show_menu(
                step_id="api",
                menu_options=["api_add_device", "remove_device", "finish"],
            )
        else:
            return await self.async_step_select_device()

    async def async_step_api_add_device(self, user_input: dict[str, Any] | None = None):
        return await self.async_step_select_device()

    async def async_step_finish(self, user_input: dict[str, Any] | None = None):
        return await self.update_or_create()

    async def async_step_remove_device(self, user_input: dict[str, Any] | None = None):
        if len(self.local_devices) == 1:
            return self.async_abort(reason="remove_last_device")

        if not user_input:
            return self.async_show_form(
                step_id="remove_device",
                last_step=True,
                data_schema=vol.Schema({vol.Required(CONF_SELECT_DEVICE_KEY): vol.In(list(self.local_devices))}),
            )
        target_device = self.local_devices[user_input[CONF_SELECT_DEVICE_KEY]]
        device_list = self.new_data[CONF_DEVICE_LIST]
        # a multi-module device takes its modules with it; a module left behind would point to a
        # missing parent and keep the whole entry from loading
        removed = [target_device.sn] + [
            key for key, data in device_list.items() if data.get(CONF_PARENT_SN) == target_device.sn
        ]
        if len([key for key in device_list if key not in removed]) < 1:
            return self.async_abort(reason="remove_last_device")

        for key in removed:
            device_list.pop(key, None)
            self.new_options.get(CONF_DEVICE_LIST, {}).pop(key, None)
            self.remove_device(key)

        # a removed module stays removed: its parent remembers it across discoveries
        parent_data = device_list.get(target_device.parent.sn) if target_device.parent is not None else None
        if parent_data is not None:
            ignored = list(parent_data.get(CONF_IGNORED_MODULES, []))
            if target_device.sn not in ignored:
                ignored.append(target_device.sn)
            parent_data[CONF_IGNORED_MODULES] = ignored

        # no discovery here: it would add the module just removed straight back
        return await self.update_or_create(discover=False)

    async def async_step_select_device(self, user_input: dict[str, Any] | None = None):
        if not user_input:
            try:
                devices = await self.auth.fetch_all_available_devices()
                self.set_device_list(devices)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception in fetch device action")
                return self.async_abort(reason="unknown")

            target_devices = [k for k, v in self.cloud_devices.items() if k not in self.local_devices]
            if len(target_devices) < 1:
                return self.async_abort(reason="no_device_to_add")

            return self.async_show_form(
                step_id="select_device",
                data_schema=vol.Schema({vol.Required(CONF_SELECT_DEVICE_KEY): vol.In(list(target_devices))}),
            )

        self.cloud_device = self.cloud_devices[user_input[CONF_SELECT_DEVICE_KEY]]

        return await self.async_step_confirm_cloud_device()

    async def async_step_confirm_cloud_device(self, user_input: dict[str, Any] | None = None):
        from .devices.registry import device_by_product

        if not user_input:
            device_list = list(device_by_product.keys())
            return self.async_show_form(
                step_id="confirm_cloud_device",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_DEVICE_TYPE, default=self.cloud_device.device_type): selector.SelectSelector(
                            selector.SelectSelectorConfig(
                                options=device_list,
                                mode=selector.SelectSelectorMode.DROPDOWN,
                            ),
                        ),
                        vol.Required(CONF_DEVICE_NAME, default=self.cloud_device.name): str,
                        vol.Required(CONF_DEVICE_ID, default=self.cloud_device.sn): str,
                    }
                ),
            )

        device = device_by_product[user_input[CONF_DEVICE_TYPE]]

        sn = user_input[CONF_DEVICE_ID]

        if CONF_DEVICE_LIST not in self.new_data:
            self.new_data[CONF_DEVICE_LIST] = {}
            self.new_options[CONF_DEVICE_LIST] = {}

        self.new_data[CONF_DEVICE_LIST][sn] = {
            CONF_DEVICE_NAME: user_input[CONF_DEVICE_NAME],
            CONF_DEVICE_TYPE: user_input[CONF_DEVICE_TYPE],
        }
        self.added_devices.add(sn)
        self.new_options[CONF_DEVICE_LIST][sn] = {
            OPTS_REFRESH_PERIOD_SEC: DEFAULT_REFRESH_PERIOD_SEC,
            OPTS_POWER_STEP: device.default_charging_power_step(),
            OPTS_DIAGNOSTIC_MODE: ("Diagnostic".lower() == user_input[CONF_DEVICE_TYPE].lower()),
            OPTS_VERBOSE_STATUS_MODE: False,
            OPTS_ASSUME_OFFLINE_SEC: DEFAULT_ASSUME_OFFLINE_SEC,
            OPTS_RESET_SENSORS_ON_OFFLINE: DEFAULT_RESET_SENSORS_ON_OFFLINE,
            OPTS_ENERGY_UPDATE_INTERVAL_SEC: DEFAULT_ENERGY_UPDATE_INTERVAL_SEC,
        }

        return await self.update_or_create()

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> EcoflowOptionsFlow:
        return EcoflowOptionsFlow()


class EcoflowOptionsFlow(OptionsFlow):
    def __init__(self) -> None:
        # HA 2024.12+: config_entry is auto-injected by the framework after __init__.
        # Device extraction is deferred to async_step_init.
        self.devices: dict[str, DeviceData] = {}
        self.device_selector = {}
        self.selected_device = None

    def _ensure_devices_loaded(self) -> None:
        if not self.device_selector:
            self.devices = extract_devices(self.config_entry)
            for device in self.devices.values():
                self.device_selector[f"{device.name} ({device.sn})"] = device

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        self._ensure_devices_loaded()
        if user_input is None:
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema(
                    {vol.Required(CONF_SELECT_DEVICE_KEY): vol.In(list(self.device_selector.keys()))}
                ),
            )

        self.selected_device = self.device_selector[user_input[CONF_SELECT_DEVICE_KEY]]
        return await self.async_step_options()

    async def async_step_options(self, user_input: dict[str, Any] | None = None):
        if user_input is None:
            device_options: DeviceOptions = self.devices[self.selected_device.sn].options

            return self.async_show_form(
                step_id="options",
                last_step=True,
                data_schema=vol.Schema(
                    {
                        vol.Required(OPTS_POWER_STEP, default=device_options.power_step): int,
                        vol.Required(
                            OPTS_REFRESH_PERIOD_SEC,
                            default=device_options.refresh_period,
                        ): int,
                        vol.Required(OPTS_DIAGNOSTIC_MODE, default=device_options.diagnostic_mode): bool,
                        vol.Required(OPTS_VERBOSE_STATUS_MODE, default=device_options.verbose_status_mode): bool,
                        vol.Required(OPTS_ASSUME_OFFLINE_SEC, default=device_options.assume_offline_sec): int,
                        vol.Required(
                            OPTS_RESET_SENSORS_ON_OFFLINE,
                            default=device_options.reset_sensors_on_offline,
                        ): bool,
                        vol.Required(
                            OPTS_ENERGY_UPDATE_INTERVAL_SEC,
                            default=device_options.energy_update_interval,
                        ): vol.All(int, vol.Range(min=0)),
                    }
                ),
            )

        # Copy the nested device list too. A shallow copy edits the entry's live options in place, so HA
        # compares the result to itself, sees no change, and neither saves the options nor reloads.
        new_options = {**self.config_entry.options}
        new_options[CONF_DEVICE_LIST] = {**self.config_entry.options[CONF_DEVICE_LIST]}
        new_options[CONF_DEVICE_LIST][self.selected_device.sn] = {
            OPTS_POWER_STEP: user_input[OPTS_POWER_STEP],
            OPTS_REFRESH_PERIOD_SEC: user_input[OPTS_REFRESH_PERIOD_SEC],
            OPTS_DIAGNOSTIC_MODE: user_input[OPTS_DIAGNOSTIC_MODE],
            OPTS_VERBOSE_STATUS_MODE: user_input[OPTS_VERBOSE_STATUS_MODE],
            OPTS_ASSUME_OFFLINE_SEC: user_input[OPTS_ASSUME_OFFLINE_SEC],
            OPTS_RESET_SENSORS_ON_OFFLINE: user_input[OPTS_RESET_SENSORS_ON_OFFLINE],
            OPTS_ENERGY_UPDATE_INTERVAL_SEC: user_input[OPTS_ENERGY_UPDATE_INTERVAL_SEC],
        }

        return self.async_create_entry(title="", data=new_options)
