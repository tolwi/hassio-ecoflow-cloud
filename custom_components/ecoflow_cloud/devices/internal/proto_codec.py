import struct
import time


def _pb_varint(value: int) -> bytes:
    """Encode unsigned integer as protobuf varint."""
    result = []
    while value > 0x7f:
        result.append((value & 0x7f) | 0x80)
        value >>= 7
    result.append(value & 0x7f)
    return bytes(result)


def _pb_fv(field_num: int, value: float) -> bytes:
    """Encode field as fixed32 (float)."""
    field_header = (field_num << 3) | 5
    return _pb_varint(field_header) + struct.pack('<f', value)


def _pb_fb(field_num: int, value: float) -> bytes:
    """Encode field as fixed64 (double)."""
    field_header = (field_num << 3) | 1
    return _pb_varint(field_header) + struct.pack('<d', value)


def _stream_pdata(*field_value_pairs) -> bytes:
    """Build StreamACConfigWrite pdata with field-value pairs."""
    pdata = b''
    utc_header = (6 << 3) | 0
    pdata += _pb_varint(utc_header) + _pb_varint(int(time.time()))
    for field_num, value in field_value_pairs:
        field_header = (field_num << 3) | 0
        pdata += _pb_varint(field_header) + _pb_varint(int(value))
    return pdata


def _stream_wrap_cmd(pdata: bytes, seq_ms: int = None, need_ack: int = 1) -> bytes:
    """Wrap ConfigWrite pdata in StreamACSendHeaderMsg + StreamACHeader envelope."""
    if seq_ms is None:
        seq_ms = int(time.time() * 1000)

    header = b''

    # pdata (field 1)
    pdata_header = (1 << 3) | 2
    header += _pb_varint(pdata_header) + _pb_varint(len(pdata)) + pdata

    # src (field 2) = 1
    src_header = (2 << 3) | 0
    header += _pb_varint(src_header) + _pb_varint(1)

    # dest (field 3) = 2
    dest_header = (3 << 3) | 0
    header += _pb_varint(dest_header) + _pb_varint(2)

    # cmd_func (field 8) = 254
    func_header = (8 << 3) | 0
    header += _pb_varint(func_header) + _pb_varint(254)

    # cmd_id (field 9) = 17
    id_header = (9 << 3) | 0
    header += _pb_varint(id_header) + _pb_varint(17)

    # data_len (field 10)
    dlen_header = (10 << 3) | 0
    header += _pb_varint(dlen_header) + _pb_varint(len(pdata))

    # need_ack (field 11)
    ack_header = (11 << 3) | 0
    header += _pb_varint(ack_header) + _pb_varint(need_ack)

    # seq (field 14) — MILLISECONDS (critical: not seconds)
    seq_header = (14 << 3) | 0
    header += _pb_varint(seq_header) + _pb_varint(seq_ms)

    # product_id (field 15) = 56
    prod_header = (15 << 3) | 0
    header += _pb_varint(prod_header) + _pb_varint(56)

    # version (field 16) = 3
    ver_header = (16 << 3) | 0
    header += _pb_varint(ver_header) + _pb_varint(3)

    # payload_ver (field 17) = 1
    pver_header = (17 << 3) | 0
    header += _pb_varint(pver_header) + _pb_varint(1)

    # from (field 23) = "Android"
    from_header = (23 << 3) | 2
    from_str = b"Android"
    header += _pb_varint(from_header) + _pb_varint(len(from_str)) + from_str

    # Wrap in StreamACSendHeaderMsg (field 1)
    msg_header = (1 << 3) | 2
    full = _pb_varint(msg_header) + _pb_varint(len(header)) + header

    return full


def build_feed_limit(watts: int) -> bytes:
    """Build SET command for feed-in power limit (field 169)."""
    pdata = _stream_pdata((169, watts))
    return _stream_wrap_cmd(pdata)


def build_max_chg_soc(soc: int, min_dsg_soc: int = None) -> bytes:
    """Build SET command for max charge SOC (field 33) + min discharge (field 34)."""
    pairs = [(33, soc)]
    if min_dsg_soc is not None:
        pairs.append((34, min_dsg_soc))
    pdata = _stream_pdata(*pairs)
    return _stream_wrap_cmd(pdata)


def build_min_dsg_soc(soc: int, max_chg_soc: int = None) -> bytes:
    """Build SET command for min discharge SOC (field 34) + max charge (field 33)."""
    pairs = [(34, soc)]
    if max_chg_soc is not None:
        pairs.append((33, max_chg_soc))
    pdata = _stream_pdata(*pairs)
    return _stream_wrap_cmd(pdata)


def build_backup_soc(soc: int) -> bytes:
    """Build SET command for backup reserve SOC (field 102)."""
    pdata = _stream_pdata((102, soc))
    return _stream_wrap_cmd(pdata)


def build_relay(field_num: int, on: bool) -> bytes:
    """Build SET command for AC relay (field 380=relay2, 381=relay3)."""
    pdata = _stream_pdata((field_num, 1 if on else 0))
    return _stream_wrap_cmd(pdata)
