
plain_to_status: dict[str, str] = {
        "pd": "pdStatus",
        "mppt": "mpptStatus",
        "bms_emsStatus": "emsStatus",
        "bms_bmsStatus": "bmsStatus",
        "inv": "invStatus",
        "bms_slave": "bmsSlaveStatus"
}

status_to_plain = dict((v, k) for (k, v) in plain_to_status.items())

def to_plain(raw_data: dict[str, any]) -> dict[str, any]:
    if "typeCode" in raw_data:
        prefix = status_to_plain.get(raw_data["typeCode"], "unknown_"+raw_data["typeCode"])
        new_params = {}
        for (k, v) in raw_data["params"].items():
            new_params[f"{prefix}.{k}"] = v

        result = {"params": new_params}
        for (k, v) in raw_data.items():
            if k != "params":
                result[k] = v

        return result
    else:
        return raw_data