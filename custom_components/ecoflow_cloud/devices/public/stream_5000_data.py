"""Normalize official STREAM 5000 HTTP and MQTT quota fields.

The Developer API may return the same field in three shapes:
- Nested MQTT: {"sysEnergyStreamReport": {"bpSoc": 15}}
- Canonical dotted: {"sysEnergyStreamReport.bpSoc": 15}
- Legacy/hyphen HTTP: {"sysEnergyStreamReport-bpSoc": 32}

When several shapes coexist, nested fields take precedence over dotted
fields, which take precedence over hyphenated fields. This matters for
diagnostics that accumulate readings across different update ticks.
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
    """Flatten supported BKW3 groups, using deterministic field precedence."""
    params = raw.get("params", raw)
    if not isinstance(params, Mapping):
        return {}

    result: dict[str, Any] = {}

    # Least authoritative: HTTP hyphen form can coexist with stale readings.
    for key, value in params.items():
        if not isinstance(key, str) or "-" not in key:
            continue
        group, field = key.split("-", 1)
        if group in GROUPS:
            result[f"{group}.{field}"] = value

    # Canonical dotted keys supersede their hyphen equivalents.
    # Preserve unrelated values unchanged.
    for key, value in params.items():
        if not isinstance(key, str):
            continue
        if key in GROUPS and isinstance(value, Mapping):
            continue
        if "-" in key and key.split("-", 1)[0] in GROUPS:
            continue
        result[key] = value

    # Most authoritative: live structured group values.
    for group in GROUPS:
        value = params.get(group)
        if not isinstance(value, Mapping):
            continue
        for nested_key, nested_value in value.items():
            if isinstance(nested_key, str):
                result[f"{group}.{nested_key}"] = nested_value

    return result
