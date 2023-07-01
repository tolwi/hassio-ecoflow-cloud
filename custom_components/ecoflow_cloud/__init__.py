import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .config.const import CONF_DEVICE_TYPE, CONF_USERNAME, CONF_PASSWORD, OPTS_POWER_STEP, OPTS_REFRESH_PERIOD_SEC, \
    DEFAULT_REFRESH_PERIOD_SEC
from .mqtt.ecoflow_mqtt import EcoflowMQTTClient, EcoflowAuthentication

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ecoflow_cloud"

_PLATFORMS = {
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
}

ATTR_STATUS_SN = "SN"
ATTR_STATUS_QUOTA_UPDATES = "quota_update_count"
ATTR_STATUS_QUOTA_LAST_UPDATE = "quota_last_update"
ATTR_STATUS_DATA_LAST_UPDATE = "data_last_update"


async def async_migrate_entry(hass, config_entry: ConfigEntry):
    """Migrate old entry."""
    if config_entry.version == 1:
        from .devices.registry import devices
        device = devices[config_entry.data[CONF_DEVICE_TYPE]]

        new_data = {**config_entry.data}
        new_options = {OPTS_POWER_STEP: device.charging_power_step(),
                       OPTS_REFRESH_PERIOD_SEC: DEFAULT_REFRESH_PERIOD_SEC}

        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new_data, options=new_options)

    _LOGGER.info("Migration to version %s successful", config_entry.version)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    auth = EcoflowAuthentication(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])
    await hass.async_add_executor_job(auth.authorize)
    client = EcoflowMQTTClient(hass, entry, auth)

    hass.data[DOMAIN][entry.entry_id] = client
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    if not await hass.config_entries.async_unload_platforms(entry, _PLATFORMS):
        return False

    client: EcoflowMQTTClient = hass.data[DOMAIN].pop(entry.entry_id)
    client.stop()
    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
