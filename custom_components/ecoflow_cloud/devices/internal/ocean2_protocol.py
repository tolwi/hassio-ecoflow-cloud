"""Wire-level protocol handling for the EcoFlow OCEAN 2 home battery.

Reverse-engineering status (as of 2026-07-10)
----------------------------------------------
The OCEAN 2 / OCEAN 2 Plus product line is not covered by EcoFlow's public
Developer API and is not part of the same "IOT_APP" device family as
DELTA/RIVER, so none of the existing private-API device classes in this
project apply to it directly. The findings below come from packet-capturing
the official EcoFlow web portal (https://user-portal.ecoflow.com) while it
talks to the standard EcoFlow MQTT broker (``mqtt-e.ecoflow.com:8084``) over
MQTT-over-WebSocket, and from reading the portal's (unminified-by-us, but not
literally deobfuscated) JavaScript bundle.

Confirmed:
  * OCEAN 2 publishes to the exact same MQTT topic scheme as every other
    EcoFlow device: ``/app/device/property/{deviceSn}``.
  * The outer envelope is the same ``Header`` / ``SendHeaderMsg`` protobuf
    schema used across the whole EcoFlow product line (identical field
    numbers to e.g. ``wave3.proto`` / ``ef_delta3.proto`` in this repo).
  * Telemetry updates arrive with ``cmd_func == 254`` (the "extended
    command set" marker) and ``cmd_id == 39``.
  * ``Header.pdata`` is only XOR-"encrypted" when ``Header.enc_type == 1``
    (single repeating byte key, see :func:`maybe_decrypt_pdata` below,
    taken near-verbatim from the portal's own ``getXor`` helper). In both
    frames captured so far ``enc_type`` was unset/0, i.e. ``pdata`` was
    already plain protobuf. AES is *not* involved.
  * After removing the envelope (and decrypting if needed), ``pdata`` is
    itself a protobuf message. Its exact .proto schema (field numbers ->
    field names) is *not* fully confirmed yet - see NOT confirmed below.

NOT confirmed yet (help wanted - see docs/devices/OCEAN_2.md):
  * Which field number corresponds to which named quantity
    (``bpSoc``, ``bpPwr``, ``sysGridPwr``, ``sysLoadPwr``, ``mpptPwr``, ...).
    The portal's own React code destructures an object with those names from
    a decoded message, but the compiled protobuf reader that maps wire field
    numbers to those names lives in a part of the bundle we have not
    located.
  * Because EcoFlow only serializes non-default/changed fields (normal
    proto3 behaviour), a single MQTT message is a *partial* update, not a
    full state snapshot - a stateful merge (like the portal itself does) is
    required to build a complete picture over time.

Given the above, this module deliberately does **not** pretend to know the
full schema. It:

  1. Robustly parses the envelope (high confidence, validated against two
     real captured frames - run this module directly, i.e.
     ``python3 -m custom_components.ecoflow_cloud.devices.internal.ocean2_protocol``,
     to re-run that validation).
  2. Generically decodes whatever protobuf structure is inside ``pdata``
     into a plain, JSON-serializable nested dict, without assuming field
     semantics.
  3. Additionally extracts two repeated groups of plausible per-phase power
     readings (float32, tag numbers 7 and 87 at the top level) as
     "experimental" values, since they showed values in the right ballpark
     compared to the portal's live dashboard - but which of the two is
     "Solar" vs "Home load" (they were near-identical in both samples
     because the observed system had Grid=0W/Battery=0W, i.e. Solar and
     Home load were coincidentally equal) is *not yet confirmed*.
"""

from __future__ import annotations

import dataclasses
from typing import Any

# ---------------------------------------------------------------------------
# Generic protobuf wire-format decoding (no compiled .proto / protoc needed)
# ---------------------------------------------------------------------------


class ProtoParseError(Exception):
    """Raised when a byte buffer does not look like a valid protobuf message."""


def _read_varint(buf: bytes, i: int) -> tuple[int, int]:
    result = 0
    shift = 0
    start = i
    while True:
        if i >= len(buf):
            raise ProtoParseError(f"Unexpected end of buffer reading varint at offset {start}")
        b = buf[i]
        result |= (b & 0x7F) << shift
        i += 1
        if not (b & 0x80):
            break
        shift += 7
        if shift > 63:
            raise ProtoParseError(f"Varint too long at offset {start}")
    return result, i


# (field_number, wire_type, raw_value)
RawField = tuple[int, int, Any]


def decode_fields(buf: bytes) -> list[RawField]:
    """Decode ``buf`` into a flat list of (field_number, wire_type, value) tuples.

    wire_type 0 -> value is an int (varint)
    wire_type 1 -> value is 8 raw bytes (64-bit)
    wire_type 2 -> value is raw bytes (length-delimited: string/bytes/submessage)
    wire_type 5 -> value is 4 raw bytes (32-bit)

    Raises ProtoParseError if ``buf`` does not look like valid protobuf.
    """
    i = 0
    fields: list[RawField] = []
    n = len(buf)
    while i < n:
        tag, i = _read_varint(buf, i)
        field_no = tag >> 3
        wire_type = tag & 0x7
        if field_no == 0:
            raise ProtoParseError("Field number 0 is invalid")
        if wire_type == 0:
            val, i = _read_varint(buf, i)
        elif wire_type == 1:
            if i + 8 > n:
                raise ProtoParseError("Truncated 64-bit field")
            val, i = buf[i : i + 8], i + 8
        elif wire_type == 2:
            length, i = _read_varint(buf, i)
            if i + length > n:
                raise ProtoParseError("Truncated length-delimited field")
            val, i = buf[i : i + length], i + length
        elif wire_type == 5:
            if i + 4 > n:
                raise ProtoParseError("Truncated 32-bit field")
            val, i = buf[i : i + 4], i + 4
        else:
            raise ProtoParseError(f"Unsupported wire type {wire_type} at field {field_no}")
        fields.append((field_no, wire_type, val))
    return fields


def _float32_le(b: bytes) -> float:
    import struct

    return struct.unpack("<f", b)[0]


def to_plain_value(field_no: int, wire_type: int, val: Any) -> Any:
    """Best-effort conversion of a single raw field into a JSON-friendly value."""
    if wire_type == 0:
        return val
    if wire_type == 5:
        # Most 32-bit fixed fields observed so far decode cleanly as float32.
        return round(_float32_le(val), 4)
    if wire_type == 1:
        return val.hex()
    if wire_type == 2:
        # Try nested message first, then utf-8 text, else hex.
        try:
            sub = decode_fields(val)
            if sub:
                return generic_decode(val)
        except ProtoParseError:
            pass
        try:
            return val.decode("utf-8")
        except UnicodeDecodeError:
            return val.hex()
    return None


def generic_decode(buf: bytes) -> dict[str, Any]:
    """Recursively decode ``buf`` into a nested, JSON-serializable dict.

    Keys are ``f<field_number>`` (repeated field numbers become a list).
    This makes no assumption about field semantics - it is meant as a
    diagnostic/raw view, and as the basis for eventually pinning down the
    real schema by comparing against known-good values from the EcoFlow app.
    """
    out: dict[str, Any] = {}
    for field_no, wire_type, val in decode_fields(buf):
        key = f"f{field_no}"
        decoded = to_plain_value(field_no, wire_type, val)
        if key in out:
            existing = out[key]
            if isinstance(existing, list):
                existing.append(decoded)
            else:
                out[key] = [existing, decoded]
        else:
            out[key] = decoded
    return out


# ---------------------------------------------------------------------------
# Header / SendHeaderMsg envelope
# (field numbers confirmed identical to e.g. Wave3Header in wave3.proto)
# ---------------------------------------------------------------------------

_HEADER_INT_FIELDS = {
    2: "src",
    3: "dest",
    4: "d_src",
    5: "d_dest",
    6: "enc_type",
    7: "check_type",
    8: "cmd_func",
    9: "cmd_id",
    10: "data_len",
    11: "need_ack",
    12: "is_ack",
    14: "seq",
    15: "product_id",
    16: "version",
    17: "payload_ver",
    18: "time_snap",
    19: "is_rw_cmd",
    20: "is_queue",
    21: "ack_type",
}
_HEADER_STRING_FIELDS = {
    22: "code",
    23: "from_",
    24: "module_sn",
    25: "device_sn",
}


@dataclasses.dataclass
class Ocean2Header:
    pdata: bytes | None = None
    src: int | None = None
    dest: int | None = None
    d_src: int | None = None
    d_dest: int | None = None
    enc_type: int | None = None
    check_type: int | None = None
    cmd_func: int | None = None
    cmd_id: int | None = None
    data_len: int | None = None
    need_ack: int | None = None
    is_ack: int | None = None
    seq: int | None = None
    product_id: int | None = None
    version: int | None = None
    payload_ver: int | None = None
    time_snap: int | None = None
    is_rw_cmd: int | None = None
    is_queue: int | None = None
    ack_type: int | None = None
    code: str | None = None
    from_: str | None = None
    module_sn: str | None = None
    device_sn: str | None = None


def _parse_single_header(buf: bytes) -> Ocean2Header:
    header = Ocean2Header()
    for field_no, wire_type, val in decode_fields(buf):
        if field_no == 1 and wire_type == 2:
            header.pdata = val
        elif field_no in _HEADER_INT_FIELDS and wire_type == 0:
            setattr(header, _HEADER_INT_FIELDS[field_no], val)
        elif field_no in _HEADER_STRING_FIELDS and wire_type == 2:
            try:
                setattr(header, _HEADER_STRING_FIELDS[field_no], val.decode("utf-8"))
            except UnicodeDecodeError:
                pass
    return header


def parse_send_header_msg(raw_mqtt_payload: bytes) -> list[Ocean2Header]:
    """Parse a ``SendHeaderMsg`` (the MQTT PUBLISH payload, *after* stripping
    the MQTT fixed header/topic - i.e. exactly what paho-mqtt hands you in
    ``message.payload``) into a list of :class:`Ocean2Header`.

    ``SendHeaderMsg`` is ``{ repeated Header msg = 1; }``, so at the top
    level we expect one or more length-delimited field-1 entries, each of
    which is itself a ``Header`` message.
    """
    headers: list[Ocean2Header] = []
    for field_no, wire_type, val in decode_fields(raw_mqtt_payload):
        if field_no == 1 and wire_type == 2:
            headers.append(_parse_single_header(val))
    return headers


# ---------------------------------------------------------------------------
# XOR "encryption" (only applied when Header.enc_type == 1)
# ---------------------------------------------------------------------------


def maybe_decrypt_pdata(pdata: bytes, seq: int | None, enc_type: int | None) -> bytes:
    """Mirrors the portal JS's ``getXor(pdata, seq)``, only called when
    ``enc_type == 1``:

        function Sr(e, t) {
          t < 0 && (t &= 255);
          for (let n = 0; n < e.length; n++) {
            let r = e[n] < 0 ? 255 & e[n] : e[n];
            e[n] = 255 & (r ^ t);
          }
          return e;
        }

    Despite the misleading name this is a plain single-byte repeating XOR:
    every byte of ``pdata`` is XORed with ``seq & 0xFF`` (the JS masks the
    *result* to a byte, which is equivalent to masking the key first since
    XOR has no carries). It is NOT AES and needs no secret key.
    """
    if enc_type != 1 or seq is None:
        return pdata
    key = seq & 0xFF
    return bytes((b ^ key) & 0xFF for b in pdata)


# ---------------------------------------------------------------------------
# Best-effort extraction of the "known-ish" telemetry message
# (cmd_func == 254, cmd_id == 39 - the portal calls this "displayPropertyUpload")
# ---------------------------------------------------------------------------

DISPLAY_PROPERTY_UPLOAD_CMD_FUNC = 254
DISPLAY_PROPERTY_UPLOAD_CMD_ID = 39

# Top-level field numbers observed (across 2 captured frames) to contain
# repeated float32 values that are plausibly per-phase power readings, in
# the right order of magnitude compared to the portal dashboard at capture
# time. NOT CONFIRMED which is Solar vs Home load vs something else -
# treat as experimental/diagnostic only.
_EXPERIMENTAL_POWER_GROUPS = (7, 87)


def _encode_varint(value: int) -> bytes:
    out = bytearray()
    v = value
    while True:
        b = v & 0x7F
        v >>= 7
        if v:
            out.append(b | 0x80)
        else:
            out.append(b)
            break
    return bytes(out)


def _encode_tag(field_no: int, wire_type: int) -> bytes:
    return _encode_varint((field_no << 3) | wire_type)


def _encode_varint_field(field_no: int, value: int) -> bytes:
    return _encode_tag(field_no, 0) + _encode_varint(value)


def _encode_bytes_field(field_no: int, value: bytes) -> bytes:
    return _encode_tag(field_no, 2) + _encode_varint(len(value)) + value


def _encode_string_field(field_no: int, value: str) -> bytes:
    return _encode_bytes_field(field_no, value.encode("utf-8"))


def encode_header_message(
    *,
    device_sn: str,
    cmd_func: int,
    cmd_id: int,
    seq: int,
    src: int | None = None,
    dest: int | None = None,
    d_src: int | None = None,
    d_dest: int | None = None,
    check_type: int | None = None,
    need_ack: int | None = None,
    version: int | None = None,
    payload_ver: int | None = None,
    from_: str | None = None,
    pdata: bytes | None = None,
) -> bytes:
    """Encode a single ``Header`` message (field numbers as documented above).

    Only used to build outgoing "give me your state" heartbeat-style
    requests - the exact fields EcoFlow's own apps set for a given request
    kind vary a bit; we mirror what this project's other (confirmed
    working) private-API devices send for their ``HEARTBEAT`` command.
    """
    out = bytearray()
    if pdata is not None:
        out += _encode_bytes_field(1, pdata)
    if src is not None:
        out += _encode_varint_field(2, src)
    if dest is not None:
        out += _encode_varint_field(3, dest)
    if d_src is not None:
        out += _encode_varint_field(4, d_src)
    if d_dest is not None:
        out += _encode_varint_field(5, d_dest)
    if check_type is not None:
        out += _encode_varint_field(7, check_type)
    out += _encode_varint_field(8, cmd_func)
    out += _encode_varint_field(9, cmd_id)
    if pdata is not None:
        out += _encode_varint_field(10, len(pdata))
    if need_ack is not None:
        out += _encode_varint_field(11, need_ack)
    out += _encode_varint_field(14, seq)
    if version is not None:
        out += _encode_varint_field(16, version)
    if payload_ver is not None:
        out += _encode_varint_field(17, payload_ver)
    if from_ is not None:
        out += _encode_string_field(23, from_)
    out += _encode_string_field(25, device_sn)
    return bytes(out)


def encode_send_header_msg(header_bytes: bytes) -> bytes:
    """Wrap a single encoded ``Header`` message in a ``SendHeaderMsg``
    (``{ repeated Header msg = 1; }``)."""
    return _encode_bytes_field(1, header_bytes)


def decode_display_property_upload(pdata: bytes) -> dict[str, Any]:
    """Generic decode of a (cmd_func=254, cmd_id=39) payload.

    Returns a dict with:
      * ``raw``: the fully generic nested decode (see :func:`generic_decode`)
      * ``experimental_power_groups``: dict of {group_field_no: {sub_field_no: watts}}
        for the tentative per-phase power groups described above.
    """
    raw = generic_decode(pdata)

    experimental: dict[str, dict[str, float]] = {}
    for field_no, wire_type, val in decode_fields(pdata):
        if field_no in _EXPERIMENTAL_POWER_GROUPS and wire_type == 2:
            try:
                sub_fields = decode_fields(val)
            except ProtoParseError:
                continue
            group: dict[str, float] = {}
            for sub_no, sub_wt, sub_val in sub_fields:
                if sub_wt == 5:
                    group[f"f{sub_no}"] = round(_float32_le(sub_val), 2)
            if group:
                experimental.setdefault(f"group_{field_no}", {}).update(group)

    return {"raw": raw, "experimental_power_groups": experimental}


# ---------------------------------------------------------------------------
# Self-test: validates the envelope/XOR/generic-decode logic above against
# two real MQTT frames captured from the EcoFlow web portal (base64, MQTT
# PUBLISH frame including the fixed header + topic, exactly as copied out of
# the browser's WebSocket devtools). Deliberately dependency-free (stdlib
# only) and self-contained in this file rather than in a separate tests/
# directory, since this repo's .gitignore excludes "tests"/"requirements.
# test.txt" (i.e. testing here appears to be intentionally kept local to
# each contributor rather than checked in).
#
# Run with:  python3 -m custom_components.ecoflow_cloud.devices.internal.ocean2_protocol
# ---------------------------------------------------------------------------

_SELFTEST_FRAME_1_B64 = (
    "MIgCACUvYXBwL2RldmljZS9wcm9wZXJ0eS9SRTE3WkUxQVZKM0gwMDIzCt4BCoMBIm0N"
    "sGUlRBo5ChEdmj9+wyW37cBDLaML50MwAQoRHcRCikIlFJ0KQy1Z5RpDMAIKER1mkUlD"
    "Jf8jtkItuy9dQzADIhIKByV2+vRDKAEKByVIwgpCKANyFwoHCAEVYfXmQwoMCAIVPpV8"
    "QyWxwQdFOgoNAABSRCUAANJEugUFDQDAU0QQYBggIAEoATgDQP4BSCdQgwFYAXDH7bwE"
    "eP4BgAEEwgEQUkUxN1pFMUFWSjNIMDAyM8oBEFJFMTdaRTFBVkozSDAwMjPSARBSRTE3"
    "WkUxQVZKM0gwMDIz"
)
_SELFTEST_FRAME_2_B64 = (
    "MKUBACUvYXBwL2RldmljZS9wcm9wZXJ0eS9SRTE3WkUxQVZKM0gwMDIzCnwKIzoPDQCA"
    "F0QdAIAXRDUAgBdEugUPDQBAGEQdAEAYRDUAQBhEEGAYICABKAE4A0D+AUgnUCNYAXCS"
    "yMIEeP4BgAEEwgEQUkUxN1pFMUFWSjNIMDAyM8oBEFJFMTdaRTFBVkozSDAwMjPSARBS"
    "RTE3WkUxQVZKM0gwMDIz"
)


def _selftest_strip_mqtt_publish(raw_frame: bytes) -> tuple[str, bytes]:
    i = 1
    mult = 1
    rem_len = 0
    while True:
        b = raw_frame[i]
        rem_len += (b & 0x7F) * mult
        i += 1
        if not (b & 0x80):
            break
        mult *= 128
    topic_len = (raw_frame[i] << 8) | raw_frame[i + 1]
    i += 2
    topic = raw_frame[i : i + topic_len].decode("utf-8")
    i += topic_len
    return topic, raw_frame[i:]


def _selftest() -> None:
    import base64

    def check(cond: bool, msg: str) -> None:
        if not cond:
            raise AssertionError(msg)
        print(f"  ok: {msg}")

    print("Frame 1:")
    topic, payload = _selftest_strip_mqtt_publish(base64.b64decode(_SELFTEST_FRAME_1_B64))
    check(topic == "/app/device/property/RE17ZE1AVJ3H0023", "topic matches")
    headers = parse_send_header_msg(payload)
    check(len(headers) == 1, "exactly one Header in SendHeaderMsg")
    h = headers[0]
    check(h.device_sn == "RE17ZE1AVJ3H0023", "device_sn matches")
    check(h.cmd_func == 254 and h.cmd_id == 39, "cmd_func/cmd_id == 254/39")
    check(h.seq == 9385671, "seq matches")
    check(h.enc_type is None, "enc_type unset (no XOR needed)")
    pdata = maybe_decrypt_pdata(h.pdata, h.seq, h.enc_type)
    decoded = decode_display_property_upload(pdata)
    groups = decoded["experimental_power_groups"]
    check(abs(groups["group_7"]["f1"] - 840.0) < 0.1, "group_7.f1 ~= 840.0")
    check(abs(groups["group_7"]["f4"] - 1680.0) < 0.1, "group_7.f4 ~= 1680.0")
    check(abs(groups["group_87"]["f1"] - 847.0) < 0.1, "group_87.f1 ~= 847.0")

    print("Frame 2 (captured alongside a dashboard screenshot showing"
          " Solar=604W/Home=604W/Grid=0W/Battery=0W/SoC=100%):")
    topic, payload = _selftest_strip_mqtt_publish(base64.b64decode(_SELFTEST_FRAME_2_B64))
    headers = parse_send_header_msg(payload)
    h = headers[0]
    check(h.cmd_func == 254 and h.cmd_id == 39, "cmd_func/cmd_id == 254/39")
    check(h.seq == 9479186, "seq matches")
    pdata = maybe_decrypt_pdata(h.pdata, h.seq, h.enc_type)
    decoded = decode_display_property_upload(pdata)
    groups = decoded["experimental_power_groups"]
    for value in groups["group_7"].values():
        check(abs(value - 606.0) < 5, f"group_7 value {value} ~= 606.0 (dashboard: ~604W)")
    for value in groups["group_87"].values():
        check(abs(value - 609.0) < 5, f"group_87 value {value} ~= 609.0 (dashboard: ~604W)")

    print("XOR helper vs. portal's own getXor() reference:")

    def reference_get_xor(data: bytes, key: int) -> bytes:
        if key < 0:
            key &= 255
        return bytes((b ^ key) & 0xFF for b in data)

    sample = bytes(range(256))
    for seq in (0, 1, 199, 9385671, 9479186):
        key = seq & 0xFF
        check(
            maybe_decrypt_pdata(sample, seq, enc_type=1) == reference_get_xor(sample, key),
            f"XOR matches reference for seq={seq}",
        )
    check(maybe_decrypt_pdata(sample, 12345, enc_type=0) == sample, "enc_type=0 -> passthrough")
    check(maybe_decrypt_pdata(sample, 12345, enc_type=None) == sample, "enc_type unset -> passthrough")

    print("Header encode/decode round-trip:")
    header_bytes = encode_header_message(
        device_sn="RE17ZE1AVJ3H0023",
        cmd_func=20,
        cmd_id=1,
        seq=123456789,
        src=32,
        dest=32,
        from_="HomeAssistant",
    )
    parsed = parse_send_header_msg(encode_send_header_msg(header_bytes))
    check(len(parsed) == 1, "round-trip produces one Header")
    h = parsed[0]
    check(
        (h.device_sn, h.cmd_func, h.cmd_id, h.seq, h.src, h.dest, h.from_)
        == ("RE17ZE1AVJ3H0023", 20, 1, 123456789, 32, 32, "HomeAssistant"),
        "round-trip fields match",
    )

    print("Malformed input handling:")
    try:
        decode_fields(b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff")
        raise AssertionError("expected ProtoParseError")
    except ProtoParseError:
        print("  ok: malformed input raises ProtoParseError")

    print("\nAll self-tests passed.")


if __name__ == "__main__":
    _selftest()
