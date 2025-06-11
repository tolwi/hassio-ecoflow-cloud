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


def to_plain(raw_data: dict[str, "Any"]) -> dict[str, "Any"]:
    new_params = {}
    prefix = ""
    if "typeCode" in raw_data:
        prefix1 = status_to_plain.get(
            raw_data["typeCode"], "unknown_" + raw_data["typeCode"]
        )
        prefix += f"{prefix1}."
    elif "cmdFunc" in raw_data and "cmdId" in raw_data:
        prefix += f"{raw_data['cmdFunc']}_{raw_data['cmdId']}."
    else:
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

    new_params2 = {}
    for k, v in new_params.items():
        new_params2[k] = v
        if isinstance(v, dict):
            for k2, v2 in v.items():
                new_params2[f"{k}.{k2}"] = v2

    result = {"params": new_params2}
    _LOGGER.debug(str(result))

    return result


def to_plain_other(raw_data: dict[str, "Any"]) -> dict[str, "Any"]:
    if not {"cmdFunc", "cmdId"}.issubset(raw_data):
        return raw_data  # Return unmodified if required keys are missing

    params = raw_data.get("param", {})
    new_params = {
        k: v for d in [params, raw_data.get("params", {})] for k, v in d.items()
    }

    if raw_data.get("addr") == "ems" and raw_data.get("cmdId") == 1:
        phases = ["pcsAPhase", "pcsBPhase", "pcsCPhase"]
        for phase in phases:
            for k, v in params.get(phase, {}).items():
                new_params[f"{phase}.{k}"] = v

        n_strings = len(params.get("mpptHeartBeat", [{}])[0].get("mpptPv", []))
        for i in range(1, n_strings + 1):
            for k, v in (
                params.get("mpptHeartBeat", [{}])[0].get(f"mpptPv{i}", {}).items()
            ):
                new_params[f"mpptPv{i}.{k}"] = v

    result = {"params": new_params}
    result.update({k: v for k, v in raw_data.items() if k not in ("param", "params")})

    return result
