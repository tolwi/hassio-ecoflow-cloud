
plain_to_status: dict[str, str] = {
        "pd": "pdStatus",
        "mppt": "mpptStatus",
        "bms_emsStatus": "emsStatus",
        "bms_bmsStatus": "bmsStatus",
        "inv": "invStatus",
        "bms_slave": "bmsSlaveStatus",
        "bms_slave_bmsSlaveStatus_1": "bmsSlaveStatus_1",
        "bms_slave_bmsSlaveStatus_2": "bmsSlaveStatus_2"
}

status_to_plain = dict((v, k) for (k, v) in plain_to_status.items())

def to_plain(raw_data: dict[str, any]) -> dict[str, any]:
    if "typeCode" in raw_data:
        prefix = status_to_plain.get(raw_data["typeCode"], "unknown_"+raw_data["typeCode"])
        new_params = {}
        if "params" in raw_data:
            for (k, v) in raw_data["params"].items():
                new_params[f"{prefix}.{k}"] = v
        if "param" in raw_data:
            for (k, v) in raw_data["param"].items():
                new_params[f"{prefix}.{k}"] = v

        result = {"params": new_params}
        for (k, v) in raw_data.items():
            if k != "param" and k != "params":
                result[k] = v

        return result
    else:
        if "cmdFunc" in raw_data and "cmdId" in raw_data:
            new_params = {}
            prefix = f"{raw_data['cmdFunc']}_{raw_data['cmdId']}"

            if "param" in raw_data:
                for (k, v) in raw_data["param"].items():
                    new_params[f"{prefix}.{k}"] = v

            if "params" in raw_data:
                for (k, v) in raw_data["params"].items():
                    new_params[f"{prefix}.{k}"] = v

            result = {"params": new_params}
            for (k, v) in raw_data.items():
                if k != "param" and k != "params":
                    result[k] = v

            return result

        return raw_data