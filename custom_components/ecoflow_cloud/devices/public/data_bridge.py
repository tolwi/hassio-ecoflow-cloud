import logging

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


def to_plain(raw_data: dict[str, any]) -> dict[str, any]:
    new_params = {}
    prefix = ""
    if "typeCode" in raw_data:
        prefix1 = status_to_plain.get(
            raw_data["typeCode"], "unknown_" + raw_data["typeCode"]
        )
        prefix += f"{prefix1}."
    elif "cmdFunc" in raw_data and "cmdId" in raw_data:
        prefix += f"{raw_data['cmdFunc']}_{raw_data['cmdId']}."
    else :
        prefix += ""

    if "param" in raw_data:
        for k, v in raw_data["param"].items():
            new_params[f"{prefix}{k}"] = v

    if "params" in raw_data:
        for k, v in raw_data["params"].items():
            new_params[f"{prefix}{k}"] = v

    for k, v in raw_data.items():
        if k != "param" and k != "params":
            new_params[f"{prefix}{k}"] = v

    def _flatten(prefix_key: str, value: any):
        new_params2[prefix_key] = value
        if isinstance(value, dict):
            for k_child, v_child in value.items():
                next_key = f"{prefix_key}.{k_child}" if prefix_key else k_child
                _flatten(next_key, v_child)
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                next_key = f"{prefix_key}[{idx}]"
                _flatten(next_key, item)

    new_params2 = {}
    for k, v in new_params.items():
        _flatten(k, v)

    result = {"params": new_params2, "raw_data": raw_data}
    _LOGGER.debug(str(result))

    return result