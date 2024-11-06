
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
    
def to_plain_other(raw_data: dict[str, any]) -> dict[str, any]:
    
    if "cmdFunc" in raw_data and "cmdId" in raw_data:
        new_params = {}

        if "param" in raw_data:
            if raw_data["addr"] == "ems" and raw_data["cmdId"] == 1:
                phases = ["pcsAPhase", "pcsBPhase", "pcsCPhase"]
                for i, phase in enumerate(phases):
                    for k, v in raw_data["param"][phase].items():
                        new_params[f"{phase}.{k}"] = v

                n_strings = len(raw_data["param"]["mpptHeartBeat"][0]["mpptPv"])
                mpptpvs = []
                for i in range(1, n_strings + 1):
                    mpptpvs.append(f"mpptPv{i}")
                for i, mpptpv in enumerate(mpptpvs):
                    for k, v in raw_data["param"]["mpptHeartBeat"][0]["mpptPv"][i].items():
                        new_params[f"{mpptpv}.{k}"] = v
            else:
                for (k, v) in raw_data["param"].items():
                    new_params[k] = v

                if "params" in raw_data:
                    for (k, v) in raw_data["params"].items():
                        new_params[k] = v
                            

        result = {"params": new_params}
        for (k, v) in raw_data.items():
            if k not in ("param", "params"):
                result[k] = v

        return result

    return raw_data
