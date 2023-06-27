import struct
from typing import Any, Callable, Iterable

def _parse_dict(data: bytes, types: Iterable[tuple[str, int, Callable[[bytes], Any]]]):
    result = dict[str, Any]()
    index = 0
    _len = len(data)
    for (name, size, callback) in types:
        if name is not None:
            result[name] = callback(data[index:index + size])
        index += size
        if index >= _len:
            break
    return result

def _to_int(data: bytes):
    return int.from_bytes(data, "little")

def _to_uint(data: bytes):
    return struct.unpack('B', data[0])[0]

def _to_utf8(data: bytes):
    try:
        return data.decode("utf-8")
    except:
        return None

def parse_powerstream_heartbeat(data: bytes):
    return _parse_dict(data, [
        ("invErrCode", 1, _to_uint),
        ("invWarnCode", 1, _to_uint),
        ("pv1ErrCode", 1, _to_uint),
        ("pv1WarnCode", 1, _to_uint),
        ("pv2ErrCode", 1, _to_uint),
        ("pv2WarningCode", 1, _to_uint),
        ("batErrCode", 1, _to_uint),
        ("batWarningCode", 1, _to_uint),
        ("llcErrCode", 1, _to_uint),
        ("llcWarningCode", 1, _to_uint),
        ("pv1Statue", 1, _to_uint),
        ("pv2Statue", 1, _to_uint),
        ("batStatue", 1, _to_uint),
        ("llcStatue", 1, _to_uint),
        ("invStatue", 1, _to_uint),
        ("pv1InputVolt", 1, _to_int),
        ("pv1OpVolt", 1, _to_int),
        ("pv1InputCur", 1, _to_int),
        ("pv1InputWatts", 1, _to_int),
        ("pv1Temp", 1, _to_int),
        ("pv2InputVolt", 1, _to_int),
        ("pv2OpVolt", 1, _to_int),
        ("pv2InputCur", 1, _to_int),
        ("pv2InputWatts", 1, _to_int),
        ("pv2Temp", 1, _to_int),
        ("batInputVolt", 1, _to_int),
        ("batOpVolt", 1, _to_int),
        ("batInputCur", 1, _to_int),
        ("batInputWatts", 1, _to_int),
        ("batTemp", 1, _to_int),
        ("batSoc", 1, _to_uint),
        ("llcInputVolt", 1, _to_int),
        ("llcOpVolt", 1, _to_int),
        ("llcTemp", 1, _to_int),
        ("invInputVolt", 1, _to_int),
        ("invOpVolt", 1, _to_int),
        ("invOutputCur", 1, _to_int),
        ("invOutputWatts", 1, _to_int),
        ("invTemp", 1, _to_int),
        ("invFreq", 1, _to_int),
        ("invDcCur", 1, _to_int),
        ("bpType", 1, _to_int),
        ("invRelayStatus", 1, _to_int),
        ("pv1RelayStatus", 1, _to_int),
        ("pv2RelayStatus", 1, _to_int),
        ("installCountry", 1, _to_uint),
        ("installTown", 1, _to_uint),
        ("permanentWatts", 1, _to_uint),
        ("dynamicWatts", 1, _to_uint),
        ("supplyPriority", 1, _to_uint),
        ("lowerLimit", 1, _to_uint),
        ("upperLimit", 1, _to_uint),
        ("invOnOff", 1, _to_uint),
        ("wirelessErrCode", 1, _to_uint),
        ("wirelessWarnCode", 1, _to_uint),
        ("invBrightness", 1, _to_uint),
        ("heartbeatFrequency", 1, _to_uint),
        ("ratedPower", 1, _to_uint),
        ("serialNo", 16, _to_utf8)
    ])
