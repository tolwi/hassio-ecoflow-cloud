from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import DOMAIN
from .mqtt.ecoflow_mqtt import EcoflowMQTTClient


def _to_serializable(x):
    t = type(x)
    if t is dict:
        x = {y: _to_serializable(x[y]) for y in x}
    if t is timedelta:
        x = x.__str__()
    return x


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry):
    client: EcoflowMQTTClient = hass.data[DOMAIN][entry.entry_id]
    values = {
        'data': dict(sorted(client.data.params.items())),
        'set_commands': client.data.set_commands,
        'set_replies': client.data.set_replies,
        'get_commands': client.data.get_commands,
        'get_replies': client.data.get_replies,
        'raw_data': client.data.raw_data,
    }
    return values
