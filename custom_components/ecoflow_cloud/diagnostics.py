from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import ECOFLOW_DOMAIN
from .api import EcoflowApiClient


def _to_serializable(x):
    if isinstance(x, dict):
        x = {y: _to_serializable(x[y]) for y in x}
    elif isinstance(x, list):
        x = [_to_serializable(y) for y in x]
    elif isinstance(x, timedelta):
        x = x.__str__()
    elif hasattr(x, "isoformat"):
        x = x.isoformat()
    return x


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry):
    client: EcoflowApiClient = hass.data[ECOFLOW_DOMAIN][entry.entry_id]
    values: dict[str, Any] = {"EcoFlow": []}
    for sn, device in client.devices.items():
        value = {
            "device": device.device_info.device_type,
            "name": device.device_info.name,
            "sn": sn,
            "params_time": device.data.set_params_time,
            "status_time": device.data.set_status_time,
            "params": dict(sorted(device.data.params.items())),
            "set": [dict(sorted(k.items())) for k in device.data.set],
            "set_reply": [dict(sorted(k.items())) for k in device.data.set_reply],
            "get": [dict(sorted(k.items())) for k in device.data.get],
            "get_reply": [dict(sorted(k.items())) for k in device.data.get_reply],
            "set_status": [dict(sorted(k.items())) for k in device.data.set_status],
            "set_params": [dict(sorted(k.items())) for k in device.data.set_params],
        }
        if client.ble_recovery_manager is not None and client.ble_recovery_manager.supports_device(device.device_data):
            ble_state = client.ble_recovery_manager.state_attributes(sn)
            if ble_state:
                value["ble_recovery"] = _to_serializable(ble_state)
        values["EcoFlow"].append(value)
    return values
