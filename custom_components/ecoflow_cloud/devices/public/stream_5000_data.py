"""Normalize STREAM 5000 public API quotas from HTTP and MQTT.

HTTP quota/all uses keys such as "sysEnergyStreamReport-pvPwr".
MQTT uses nested JSON such as {"sysEnergyStreamReport": {"pvPwr": 200}}.
The rest of this integration expects a flat dict with dotted keys.
"""

from collections.abc import Mapping
from typing import Any

GROUPS = frozenset({
    "sysEnergyStreamReport",
    "bpBackupConfig",
    "powerParameterConfig",
    "devSwitch",
})


def normalize_quota(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Flatten known STREAM 5000 groups while preserving other raw keys.

    This is deliberately limited to the documented groups: an unrelated
    hyphen in a parameter name must not be interpreted as nesting.
    """
    params = raw.get("params", raw)
    if not isinstance(params, Mapping):
        return {}

    result: dict[str, Any] = {}
    for key, value in params.items():
        if not isinstance(key, str):
            continue
        if key in GROUPS and isinstance(value, Mapping):
            for nested_key, nested_value in value.items():
                if isinstance(nested_key, str):
                    result[f"{key}.{nested_key}"] = nested_value
        elif "-" in key and key.split("-", 1)[0] in GROUPS:
            group, field = key.split("-", 1)
            result[f"{group}.{field}"] = value
        else:
            result[key] = value
    return result
