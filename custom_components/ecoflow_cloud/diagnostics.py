from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import DOMAIN
from .api import EcoflowApiClient


def _to_serializable(x):
    t = type(x)
    if t is dict:
        x = {y: _to_serializable(x[y]) for y in x}
    if t is timedelta:
        x = x.__str__()
    return x


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry):
    client: EcoflowApiClient = hass.data[DOMAIN][entry.entry_id]
    values = {
        'device':    client.device.device_info.device_type,
        'params':     dict(sorted(client.device.data.params.items())),
        'set':       [dict(sorted(k.items())) for k in client.device.data.set],
        'set_reply': [dict(sorted(k.items())) for k in client.device.data.set_reply],
        'get':       [dict(sorted(k.items())) for k in client.device.data.get],
        'get_reply': [dict(sorted(k.items())) for k in client.device.data.get_reply],
        'raw_data': client.device.data.raw_data,
    }
    return values
