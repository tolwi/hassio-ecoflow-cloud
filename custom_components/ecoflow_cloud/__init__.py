import logging
from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import EcoflowApiClient
from .api.private_api import EcoflowPrivateApiClient
from .api.public_api import EcoflowPublicApiClient

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ecoflow_cloud"
CONFIG_VERSION = 5

_PLATFORMS = {
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.BUTTON,

}

ATTR_STATUS_SN = "SN"
ATTR_STATUS_UPDATES = "status_request_count"
ATTR_STATUS_LAST_UPDATE = "status_last_update"
ATTR_STATUS_DATA_LAST_UPDATE = "data_last_update"
ATTR_STATUS_RECONNECTS = "reconnects"
ATTR_STATUS_PHASE = "status_phase"

CONF_AUTH_TYPE: Final = "auth_type"

CONF_USERNAME: Final = "username"
CONF_PASSWORD: Final = "password"
CONF_ACCESS_KEY: Final = "access_key"
CONF_SECRET_KEY: Final = "secret_key"
CONF_INSTALLATION_SITE: Final = "installation_site"
CONF_ENTRY_ID: Final = "entry_id"

CONF_SELECT_DEVICE_KEY: Final = "select_device"

CONF_DEVICE_TYPE: Final = "device_type"
CONF_DEVICE_NAME: Final = "device_name"
CONF_DEVICE_ID: Final = "device_id"
OPTS_DIAGNOSTIC_MODE: Final = "diagnostic_mode"
OPTS_POWER_STEP: Final = "power_step"
OPTS_REFRESH_PERIOD_SEC: Final = "refresh_period_sec"

DEFAULT_REFRESH_PERIOD_SEC: Final = 5



async def async_migrate_entry(hass, config_entry: ConfigEntry):
    """Migrate old entry."""
    entry_version = config_entry.version
    if entry_version <= 1:
        from .devices.registry import devices as device_registry
        device = device_registry[config_entry.data[CONF_DEVICE_TYPE]]

        new_data = {**config_entry.data}
        new_options = {OPTS_POWER_STEP: device.charging_power_step(),
                       OPTS_REFRESH_PERIOD_SEC: DEFAULT_REFRESH_PERIOD_SEC}

    if entry_version <= 2:
        hass.config_entries.async_update_entry(config_entry, data=new_data, options=new_options)
        _LOGGER.info("Migration to version %s successful", config_entry.version)

    if entry_version <= 3:
        new_data = {**config_entry.data}
        new_data[CONF_DEVICE_TYPE] = new_data["type"]
        new_data[CONF_DEVICE_NAME] = new_data["name"]
        del new_data["type"]
        del new_data["name"]

        new_options = {**config_entry.options, OPTS_DIAGNOSTIC_MODE: False}

        config_entry.version = CONFIG_VERSION
        hass.config_entries.async_update_entry(config_entry, data=new_data, options=new_options)
        _LOGGER.info("Migration to version %s successful", config_entry.version)

    if entry_version <= 4:
        new_data = {**config_entry.data}
        new_options = {**config_entry.options}
        try:
            if new_data[CONF_INSTALLATION_SITE] is None:  # The variable
                new_data[CONF_INSTALLATION_SITE] = "Home"
        except NameError:
            new_data[CONF_INSTALLATION_SITE] = "Home"

        config_entry.version = CONFIG_VERSION
        hass.config_entries.async_update_entry(config_entry, data=new_data, options=new_options)
        _LOGGER.info("Migration to version %s successful", config_entry.version)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    if CONF_USERNAME in entry.data and CONF_PASSWORD in entry.data:
        api_client = EcoflowPrivateApiClient(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD], entry.data[CONF_INSTALLATION_SITE])

    elif CONF_ACCESS_KEY in entry.data and CONF_SECRET_KEY in entry.data:
        api_client = EcoflowPublicApiClient(entry.data[CONF_ACCESS_KEY], entry.data[CONF_SECRET_KEY], entry.data[CONF_INSTALLATION_SITE])

    else:
        return False

    await api_client.login()
    api_client.configure_device(entry.data[CONF_DEVICE_ID], entry.data[CONF_DEVICE_NAME], entry.data[CONF_DEVICE_TYPE])
    api_client.device.configure(int(entry.options[OPTS_REFRESH_PERIOD_SEC]), bool(entry.options[OPTS_DIAGNOSTIC_MODE]))
    hass.data[DOMAIN][entry.entry_id] = api_client

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    await api_client.quota_all()

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    if not await hass.config_entries.async_unload_platforms(entry, _PLATFORMS):
        return False

    client: EcoflowApiClient = hass.data[DOMAIN].pop(entry.entry_id)
    client.stop()
    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
