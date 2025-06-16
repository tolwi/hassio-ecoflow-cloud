import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)

plain_to_status: dict[str, str] = {
    "pd": "pdStatus",
    "mppt": "mpptStatus",
    "bms_emsStatus": "emsStatus",
    "bms_bmsStatus": "bmsStatus",
    "bms_bmsInfo": "bmsInfo",
    "inv": "invStatus",
    "bms_slave": "bmsSlaveStatus",
    "bms_slave_bmsSlaveStatus_1": "bmsSlaveStatus_1",
    "bms_slave_bmsSlaveStatus_2": "bmsSlaveStatus_2",
}

status_to_plain = dict((v, k) for (k, v) in plain_to_status.items())


def to_plain(raw_data: dict[str, Any]) -> dict[str, Any]:
    prefix = ""

    if "typeCode" in raw_data:
        prefix = status_to_plain.get(
            raw_data["typeCode"], f"unknown_{raw_data['typeCode']}"
        )
    elif "cmdFunc" in raw_data and "cmdId" in raw_data:
        prefix = f"{raw_data['cmdFunc']}_{raw_data['cmdId']}"

    flat_params = {}

    for section in ("param", "params"):
        if section in raw_data:
            section_data = flatten_any(raw_data[section])
            for k, v in section_data.items():
                full_key = f"{prefix}.{k}" if prefix else k
                flat_params[full_key] = v

    for k, v in raw_data.items():
        if k not in ("param", "params"):
            section_data = flatten_any(v, k)
            for sk, sv in section_data.items():
                full_key = f"{prefix}.{sk}" if prefix else sk
                flat_params[full_key] = sv

    result = {"params": flat_params}
    _LOGGER.debug(result)
    return result


def flatten_any(data, parent_key="", sep="."):
    items = {}
    if isinstance(data, dict):
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.update(flatten_any(v, new_key, sep=sep))
    elif isinstance(data, list):
        for i, v in enumerate(data):
            new_key = f"{parent_key}[{i}]"
            items.update(flatten_any(v, new_key, sep=sep))
    else:
        items[parent_key] = data
    return items
