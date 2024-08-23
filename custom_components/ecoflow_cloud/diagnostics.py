from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import ECOFLOW_DOMAIN
from .api import EcoflowApiClient


def _to_serializable(x):
    t = type(x)
    if t is dict:
        x = {y: _to_serializable(x[y]) for y in x}
    if t is timedelta:
        x = x.__str__()
    return x


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry):
    client: EcoflowApiClient = hass.data[ECOFLOW_DOMAIN][entry.entry_id]
    values = {"EcoFlow":[]}
    for (sn, device) in client.devices.items():
        value = {
            'device':    device.device_info.device_type,
            'name':      device.device_info.name,
            'sn':        sn,
            'params':    dict(sorted(device.data.params.items())),
            'set':       [dict(sorted(k.items())) for k in device.data.set],
            'set_reply': [dict(sorted(k.items())) for k in device.data.set_reply],
            'get':       [dict(sorted(k.items())) for k in device.data.get],
            'get_reply': [dict(sorted(k.items())) for k in device.data.get_reply],
            'raw_data': device.data.raw_data,
        }
        values["EcoFlow"].append(value)
    return values
