from homeassistant import const
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .mqtt.ecoflow_mqtt import EcoflowMQTTClient, EcoflowAuthentication

DOMAIN = "ecoflow_cloud"

_PLATFORMS = {
    # Platform.BINARY_SENSOR,
    # Platform.LIGHT,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    auth = EcoflowAuthentication(entry.data[const.CONF_USERNAME], entry.data[const.CONF_PASSWORD])
    await hass.async_add_executor_job(auth.authorize)
    client = EcoflowMQTTClient(hass, entry, auth)

    hass.data[DOMAIN][entry.entry_id] = client
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    if not await hass.config_entries.async_unload_platforms(entry, _PLATFORMS):
        return False

    client: EcoflowMQTTClient = hass.data[DOMAIN].pop(entry.entry_id)
    client.stop()
    return True
