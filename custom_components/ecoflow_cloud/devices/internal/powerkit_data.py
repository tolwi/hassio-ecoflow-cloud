"""Message shapes of the Power Kits app protocol (private_api).

Pure Python on purpose: no Home Assistant imports, so the payloads seen on
``/app/device/property/<hub sn>`` can be checked without a Home Assistant install.

A Power Hub does not report as one device. Every module (batteries, BMS, MPPT,
inverter, distribution panels, the hub's own wireless board) sends its own
heartbeat, and the payload is JSON wrapped twice: ``params`` maps the module type
to a *string* that itself is a JSON object keyed by module serial::

    {"moduleSn": "M101...", "moduleType": "bp5000", "operateType": "heartBeat",
     "params": {"bp5000": "{\\"M101...\\": {\\"soc\\": 88, ...}}"}}

The ``latestQuotas`` reply uses the same encoding under ``data.quotaMap``, one
entry per module type. The main battery additionally publishes the system totals
(``totalSoc``, ``totalInWatts``, ...) with ``operateType`` ``mainBP``.
"""

from __future__ import annotations

import json
from typing import Any

JSONDict = dict[str, Any]

MAIN_BATTERY_OPERATE_TYPE = "mainBP"

# Two modules can share one serial (the 2nd generation distribution box reports its AC
# board as "ldac" and its DC board as "lddc" under the same serial). Sub devices are
# listed by serial, so such modules get "<serial>#<module type>" as their list key.
SN_TYPE_SEPARATOR = "#"


def real_sn(sn: str) -> str:
    """The module serial behind a sub device key, with any "#<module type>" suffix removed."""
    return sn.split(SN_TYPE_SEPARATOR, 1)[0]


def decode_module_payload(value: Any) -> Any:
    """Return the JSON value hidden in a double-encoded string, or the value itself."""
    if isinstance(value, bytes | bytearray):
        value = value.decode("utf-8", errors="ignore")
    if isinstance(value, str):
        text = value.strip()
        if text[:1] in ("{", "["):
            try:
                return json.loads(text)
            except ValueError:
                return value
    return value


def _is_module_map(value: Any) -> bool:
    """True for ``{module_sn: {field: value}}`` shaped dicts."""
    return isinstance(value, dict) and len(value) > 0 and all(isinstance(v, dict) for v in value.values())


def parse_module_message(message: JSONDict) -> tuple[str | None, JSONDict]:
    """Flatten a module message to ``(module_sn, fields)``.

    The fields of the module named by ``moduleSn`` are lifted out of the nested map.
    Params that are not keyed by serial (``onLineModuleSnList`` lists, ...) are kept
    under their own name. ``fields`` is empty when the message carries nothing for
    the module.
    """
    module_sn = message.get("moduleSn")
    if not isinstance(module_sn, str) or not module_sn:
        module_sn = None

    fields: JSONDict = {}
    params = message.get("params")
    if not isinstance(params, dict):
        return module_sn, fields

    for key, raw_value in params.items():
        value = decode_module_payload(raw_value)
        if _is_module_map(value):
            if module_sn is not None and isinstance(value.get(module_sn), dict):
                fields.update(value[module_sn])
            # a map for other serials carries nothing for this module
            continue
        fields[key] = value
    return module_sn, fields


def quota_map_modules(quota_map: Any) -> dict[str, dict[str, JSONDict]]:
    """Decode ``quotaMap`` into ``{module_type: {module_sn: fields}}``, skipping entries of other shapes."""
    result: dict[str, dict[str, JSONDict]] = {}
    if not isinstance(quota_map, dict):
        return result
    for module_type, raw_value in quota_map.items():
        value = decode_module_payload(raw_value)
        if _is_module_map(value):
            result[str(module_type)] = value
    return result


def discover_modules(quota_map: Any, hub_sn: str) -> list[tuple[str, str]]:
    """``(module_type, module_sn)`` for every module in a ``latestQuotas`` reply, except the hub itself.

    The hub's own modules (``wireless``, ``gps``) report under the hub serial and stay
    part of the hub device. A serial can appear with several module types.
    """
    modules: list[tuple[str, str]] = []
    for module_type, by_sn in quota_map_modules(quota_map).items():
        for module_sn in by_sn:
            if module_sn == hub_sn or (module_type, module_sn) in modules:
                continue
            modules.append((module_type, module_sn))
    return modules


def module_quota_fields(quota_map: Any, module_type: str, module_sn: str) -> JSONDict:
    """Fields of one module from a ``latestQuotas`` reply, empty when the module is absent."""
    modules = quota_map_modules(quota_map)
    by_sn = modules.get(module_type)
    if by_sn is None or module_sn not in by_sn:
        # the configured type and the reported one can drift (firmware renames); match on serial
        by_sn = next((candidate for candidate in modules.values() if module_sn in candidate), {})
    fields = by_sn.get(module_sn)
    return dict(fields) if isinstance(fields, dict) else {}


def hub_fields_from_message(message: JSONDict, hub_sn: str) -> JSONDict | None:
    """What the hub device keeps from a module message, or None when the message is not about the hub.

    The hub owns its wireless module, which reports under the hub serial, and the
    system totals, which the main battery publishes as ``mainBP``.
    """
    module_sn, fields = parse_module_message(message)
    if module_sn == hub_sn:
        return fields
    if message.get("operateType") == MAIN_BATTERY_OPERATE_TYPE:
        return fields
    return None


def hub_quota_fields(quota_map: Any, hub_sn: str) -> JSONDict:
    """Hub fields from a ``latestQuotas`` reply.

    The hub owns the modules reporting under its own serial (``wireless``, ``gps``), the
    system totals (``bmsTotal``, a flat entry without serials) and any ``total*`` value
    the main battery carries.
    """
    fields: JSONDict = {}
    if not isinstance(quota_map, dict):
        return fields
    for module_type, raw_value in quota_map.items():
        value = decode_module_payload(raw_value)
        if _is_module_map(value):
            if str(module_type).startswith("bp"):
                for module_fields in value.values():
                    fields.update({k: v for k, v in module_fields.items() if k.startswith("total")})
            if hub_sn in value:
                fields.update(value[hub_sn])
        elif isinstance(value, dict):
            fields.update(value)
    return fields


def reply_online(reply: JSONDict) -> bool | None:
    """The ``online`` flag of a ``latestQuotas`` reply, None when it is missing or unreadable."""
    value = reply.get("online")
    if value is None or isinstance(value, bool):
        return value
    try:
        return int(value) == 1
    except TypeError, ValueError:
        return None


# The app lets the owner name the circuits of a distribution panel and give each an icon
# (``logoNum``). Each board answers one request with all its circuits in circuit order, and
# takes one circuit at a time when a name is set: numeric module type, read and write operation,
# all four captured from the app.
ALIAS_OPERATIONS: dict[str, tuple[int, str, str]] = {
    "lddc": (15368, "getDcAllAlias", "setDcChAlias"),
    "ldac": (15367, "getAcAllAlias", "setAcChAlias"),
}


def alias_request(module_type: str, module_sn: str) -> JSONDict | None:
    """The command that asks a panel board for the names of its circuits, None for other modules."""
    operations = ALIAS_OPERATIONS.get(module_type)
    if operations is None:
        return None
    numeric_type, read_operation, _ = operations
    return {"moduleSn": module_sn, "moduleType": numeric_type, "operateType": read_operation, "params": {}}


def alias_set_command(module_type: str, module_sn: str, index: int, alias: str, logo: int = 0) -> JSONDict | None:
    """The command that names circuit ``index`` (zero based) of a panel board, None for other modules.

    Captured on the AC board: ``{"operateType": "setAcChAlias", "params": {"id": 0,
    "chAlias": {"logoNum": 2, "alias": "..."}}}``.
    """
    operations = ALIAS_OPERATIONS.get(module_type)
    if operations is None:
        return None
    numeric_type, _, write_operation = operations
    return {
        "moduleSn": module_sn,
        "moduleType": numeric_type,
        "operateType": write_operation,
        "params": {"id": index, "chAlias": {"logoNum": logo, "alias": alias}},
    }


def _alias_entry(entry: Any) -> tuple[str, int]:
    if not isinstance(entry, dict):
        return "", 0
    alias = entry.get("alias")
    logo = entry.get("logoNum")
    return (str(alias).strip() if alias is not None else "", logo if isinstance(logo, int) else 0)


def parse_alias_entries(message: Any, module_type: str, module_sn: str) -> list[tuple[str, int]] | None:
    """The (name, icon) of every circuit in a getDcAllAlias / getAcAllAlias reply for this board, else None.

    A reply looks like ``{"operateType": "getDcAllAlias", "moduleSn": "M3L1...", "code": "0",
    "data": {"retSta": 0, "chAlias": [{"logoNum": 0, "alias": "DC CH1"}, ...]}}``.
    """
    operations = ALIAS_OPERATIONS.get(module_type)
    if operations is None or not isinstance(message, dict):
        return None
    if message.get("operateType") != operations[1] or message.get("moduleSn") != module_sn:
        return None
    data = message.get("data")
    if not isinstance(data, dict) or not isinstance(data.get("chAlias"), list):
        return None
    return [_alias_entry(entry) for entry in data["chAlias"]]


def parse_alias_reply(message: Any, module_type: str, module_sn: str) -> list[str] | None:
    """The circuit names in a getDcAllAlias / getAcAllAlias reply for this board, else None."""
    entries = parse_alias_entries(message, module_type, module_sn)
    return None if entries is None else [alias for alias, _ in entries]


def parse_alias_set(message: Any, module_type: str, module_sn: str) -> tuple[int, str, int] | None:
    """(index, name, icon) of a setDcChAlias / setAcChAlias command for this board, else None.

    The app publishes it on the set topic when the owner renames a circuit; so does this integration.
    """
    operations = ALIAS_OPERATIONS.get(module_type)
    if operations is None or not isinstance(message, dict):
        return None
    if message.get("operateType") != operations[2] or message.get("moduleSn") != module_sn:
        return None
    params = message.get("params")
    if not isinstance(params, dict) or not isinstance(params.get("id"), int) or isinstance(params["id"], bool):
        return None
    alias, logo = _alias_entry(params.get("chAlias"))
    return params["id"], alias, logo
