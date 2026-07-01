# Increment 1: STREAM Battery Control Entities Implementation Plan

> **For agentic workers:** Use `superpowers:subagent-driven-development` to execute this plan task-by-task with fresh subagents per task and review gates between tasks.

**Goal:** Add writable number and switch entities for STREAM battery control (charge SOC, discharge SOC, backup reserve, feed-in limit, AC relays) to tolwi/hassio-ecoflow-cloud, tested on STREAM AC Pro hardware.

**Architecture:** Port protobuf SET builders from windsurf/hassio-ecoflow-eu into tolwi; add `StreamACConfigWrite` proto message; wire entity setters to builders → MQTT publish → device changes → telemetry/ack confirms. No new MQTT connections — reuse existing app-credentials client that already handles publish.

**Tech Stack:** Python 3.11+, protobuf3, paho-mqtt 2.0+, Home Assistant dev environment (Docker), tolwi's entity/number/switch patterns.

## Global Constraints

- Target: STREAM AC Pro (`BK31ZK1A4H5B0388`) — STREAM Max inherits control entities automatically in Increment 2
- Millisecond timestamps in protobuf (critical: not seconds like other EcoFlow devices)
- Paired constraint: `maxChgSoc` (field 33) and `minDsgSoc` (field 34) must be sent together in one ConfigWrite
- Keepalive: protobuf `latestQuotas` ping every 15s with dest=32 (app-to-app, not dest=2)
- ConfigWriteAck is cmdId=18; parse it to confirm values in coordinator state
- Golden vector (feed-limit=800W): byte output must match known correct bytes (validation oracle)

---

## Task 1: Add `StreamACConfigWrite` message to proto definition

**Files:**
- Modify: `custom_components/ecoflow_cloud/devices/internal/proto/stream_ac.proto`

**Interfaces:**
- Consumes: existing `StreamACHeader` envelope structure in `stream_ac.proto`
- Produces: `StreamACConfigWrite` message type with fields 6, 33, 34, 102, 169, 380, 381, 384

**Steps:**

- [ ] **Step 1: Open stream_ac.proto and find the telemetry message definitions**

Run: `grep -n "message Champ_cmd" custom_components/ecoflow_cloud/devices/internal/proto/stream_ac.proto | head -5`

Expected: Shows lines with telemetry decode messages (Champ_cmd21*, Champ_cmd50*, etc.)

- [ ] **Step 2: Add the StreamACConfigWrite message after the telemetry messages**

Insert this block into `stream_ac.proto` (before or after the telemetry structs, but after the header definition):

```proto
message StreamACConfigWrite {
  optional uint32 cfg_utc_time = 6;
  optional uint32 cms_max_chg_soc = 33;
  optional uint32 cms_min_dsg_soc = 34;
  optional uint32 backup_reverse_soc = 102;
  optional uint32 feed_grid_mode_pow_limit = 169;
  optional uint32 relay2_onoff = 380;
  optional uint32 relay3_onoff = 381;
  optional uint32 brightness = 384;
}
```

- [ ] **Step 3: Verify syntax by viewing the file around the new message**

Run: `tail -20 custom_components/ecoflow_cloud/devices/internal/proto/stream_ac.proto`

Expected: No obvious syntax errors (balanced braces, semicolons, proper field numbering)

- [ ] **Step 4: Commit**

```bash
cd /Users/eddwilliams/Development/hassio-ecoflow-cloud
git add custom_components/ecoflow_cloud/devices/internal/proto/stream_ac.proto
git commit -m "feat: add StreamACConfigWrite proto message with control fields"
```

---

## Task 2: Regenerate protobuf Python bindings

**Files:**
- Modify: `custom_components/ecoflow_cloud/devices/internal/stream_ac_pb2.py` (auto-generated)

**Interfaces:**
- Consumes: `StreamACConfigWrite` message from `stream_ac.proto` (Task 1)
- Produces: Python `StreamACConfigWrite` class in `stream_ac_pb2.py`

**Steps:**

- [ ] **Step 1: Check if protoc compiler is available**

Run: `which protoc`

Expected: Path to protoc (e.g., `/usr/local/bin/protoc`), or "protoc not found"

If not found, install: `brew install protobuf` (macOS)

- [ ] **Step 2: Regenerate the _pb2.py file**

Run:
```bash
cd /Users/eddwilliams/Development/hassio-ecoflow-cloud
protoc --python_out=custom_components/ecoflow_cloud/devices/internal \
  -I custom_components/ecoflow_cloud/devices/internal/proto \
  custom_components/ecoflow_cloud/devices/internal/proto/stream_ac.proto
```

Expected: No errors; `stream_ac_pb2.py` file is updated (check mtime with `ls -l`)

- [ ] **Step 3: Verify the generated class exists**

Run: `grep -n "class StreamACConfigWrite" custom_components/ecoflow_cloud/devices/internal/stream_ac_pb2.py`

Expected: Found at a specific line number (e.g., "1234:class StreamACConfigWrite")

- [ ] **Step 4: Commit**

```bash
git add custom_components/ecoflow_cloud/devices/internal/stream_ac_pb2.py
git commit -m "chore: regenerate stream_ac_pb2.py with StreamACConfigWrite message"
```

---

## Task 3: Port protobuf encoder helpers and builders from windsurf

**Files:**
- Modify: `custom_components/ecoflow_cloud/devices/internal/proto_codec.py` (or create if doesn't exist)

**Interfaces:**
- Consumes: `StreamACConfigWrite` class from `stream_ac_pb2.py` (Task 2)
- Produces: Helper functions and builder functions:
  - `_pb_varint(value: int) -> bytes`
  - `_pb_fv(field_num: int, value: float) -> bytes` (fixed32)
  - `_pb_fb(field_num: int, value: float) -> bytes` (fixed64)
  - `_stream_pdata(*field_value_pairs: tuple) -> bytes`
  - `_stream_wrap_cmd(pdata: bytes, seq_ms: int, need_ack: int = 1) -> bytes`
  - `build_feed_limit(watts: int) -> bytes`
  - `build_max_chg_soc(soc: int, min_dsg_soc: int) -> bytes`
  - `build_min_dsg_soc(soc: int, max_chg_soc: int) -> bytes`
  - `build_backup_soc(soc: int) -> bytes`
  - `build_relay(field_num: int, on: bool) -> bytes`

**Steps:**

- [ ] **Step 1: Check if proto_codec.py exists**

Run: `ls -l custom_components/ecoflow_cloud/devices/internal/proto_codec.py 2>/dev/null || echo "File does not exist"`

If doesn't exist, create an empty file: `touch custom_components/ecoflow_cloud/devices/internal/proto_codec.py`

- [ ] **Step 2: Add varint and fixed-point encoding helpers**

Append to `proto_codec.py`:

```python
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
    field_header = (field_num << 3) | 5  # Wire type 5 = fixed32
    return _pb_varint(field_header) + struct.pack('<f', value)

def _pb_fb(field_num: int, value: float) -> bytes:
    """Encode field as fixed64 (double)."""
    field_header = (field_num << 3) | 1  # Wire type 1 = fixed64
    return _pb_varint(field_header) + struct.pack('<d', value)
```

- [ ] **Step 3: Add the envelope wrapper function**

Append to `proto_codec.py`:

```python
def _stream_wrap_cmd(pdata: bytes, seq_ms: int = None, need_ack: int = 1) -> bytes:
    """Wrap ConfigWrite pdata in StreamACSendHeaderMsg + StreamACHeader envelope.
    
    Args:
        pdata: The serialized StreamACConfigWrite message
        seq_ms: Sequence number (milliseconds since epoch), auto-set if None
        need_ack: 1 = requires ConfigWriteAck, 0 = no ack expected
    
    Returns:
        Bytes of the complete command ready to publish to /set topic
    """
    if seq_ms is None:
        seq_ms = int(time.time() * 1000)
    
    # StreamACHeader fields:
    # pdata=1 (length-delimited), src=2, dest=3, cmd_func=8, cmd_id=9,
    # data_len=10, need_ack=11, seq=14, product_id=15, version=16,
    # payload_ver=17, device_sn=25, from=23
    
    header = b''
    
    # pdata (field 1, length-delimited)
    pdata_header = (1 << 3) | 2
    header += _pb_varint(pdata_header) + _pb_varint(len(pdata)) + pdata
    
    # src (field 2, varint) = 1
    src_header = (2 << 3) | 0
    header += _pb_varint(src_header) + _pb_varint(1)
    
    # dest (field 3, varint) = 2
    dest_header = (3 << 3) | 0
    header += _pb_varint(dest_header) + _pb_varint(2)
    
    # cmd_func (field 8, varint) = 254
    func_header = (8 << 3) | 0
    header += _pb_varint(func_header) + _pb_varint(254)
    
    # cmd_id (field 9, varint) = 17 (ConfigWrite)
    id_header = (9 << 3) | 0
    header += _pb_varint(id_header) + _pb_varint(17)
    
    # data_len (field 10, varint) = len(pdata)
    dlen_header = (10 << 3) | 0
    header += _pb_varint(dlen_header) + _pb_varint(len(pdata))
    
    # need_ack (field 11, varint)
    ack_header = (11 << 3) | 0
    header += _pb_varint(ack_header) + _pb_varint(need_ack)
    
    # seq (field 14, varint) = seq_ms
    seq_header = (14 << 3) | 0
    header += _pb_varint(seq_header) + _pb_varint(seq_ms)
    
    # product_id (field 15, varint) = 56 (STREAM AC)
    prod_header = (15 << 3) | 0
    header += _pb_varint(prod_header) + _pb_varint(56)
    
    # version (field 16, varint) = 3
    ver_header = (16 << 3) | 0
    header += _pb_varint(ver_header) + _pb_varint(3)
    
    # payload_ver (field 17, varint) = 1
    pver_header = (17 << 3) | 0
    header += _pb_varint(pver_header) + _pb_varint(1)
    
    # from (field 23, string) = "Android"
    from_header = (23 << 3) | 2
    from_str = b"Android"
    header += _pb_varint(from_header) + _pb_varint(len(from_str)) + from_str
    
    # Wrap in StreamACSendHeaderMsg (field pdata=1)
    msg_header = (1 << 3) | 2
    full = _pb_varint(msg_header) + _pb_varint(len(header)) + header
    
    return full
```

- [ ] **Step 4: Add builder functions for each control**

Append to `proto_codec.py`:

```python
def _stream_pdata(*field_value_pairs) -> bytes:
    """Build a StreamACConfigWrite pdata by encoding field-value pairs as varints.
    
    Args:
        *field_value_pairs: Tuples of (field_num, value) where value is int.
                           Field 6 (cfgUtcTime) is auto-prepended.
    
    Returns:
        Serialized StreamACConfigWrite pdata bytes.
    """
    pdata = b''
    
    # Always include cfgUtcTime (field 6) = current seconds
    utc_header = (6 << 3) | 0
    pdata += _pb_varint(utc_header) + _pb_varint(int(time.time()))
    
    # Encode each field
    for field_num, value in field_value_pairs:
        field_header = (field_num << 3) | 0
        pdata += _pb_varint(field_header) + _pb_varint(int(value))
    
    return pdata

def build_feed_limit(watts: int) -> bytes:
    """Build a SET command for feed-in power limit (field 169).
    
    Args:
        watts: Power limit in watts (0-800).
    
    Returns:
        Complete protobuf command bytes ready for MQTT /set topic.
    """
    pdata = _stream_pdata((169, watts))
    return _stream_wrap_cmd(pdata)

def build_max_chg_soc(soc: int, min_dsg_soc: int = None) -> bytes:
    """Build a SET command for max charge SOC (field 33) + min discharge SOC (field 34).
    
    Note: These fields must be sent together in one ConfigWrite.
    
    Args:
        soc: Max charge SOC (5-100%).
        min_dsg_soc: Min discharge SOC (0-30%). If None, use current value from coordinator.
    
    Returns:
        Complete protobuf command bytes.
    """
    pairs = [(33, soc)]
    if min_dsg_soc is not None:
        pairs.append((34, min_dsg_soc))
    pdata = _stream_pdata(*pairs)
    return _stream_wrap_cmd(pdata)

def build_min_dsg_soc(soc: int, max_chg_soc: int = None) -> bytes:
    """Build a SET command for min discharge SOC (field 34) + max charge SOC (field 33).
    
    Note: These fields must be sent together in one ConfigWrite.
    
    Args:
        soc: Min discharge SOC (0-30%).
        max_chg_soc: Max charge SOC (5-100%). If None, use current value from coordinator.
    
    Returns:
        Complete protobuf command bytes.
    """
    pairs = [(34, soc)]
    if max_chg_soc is not None:
        pairs.append((33, max_chg_soc))
    pdata = _stream_pdata(*pairs)
    return _stream_wrap_cmd(pdata)

def build_backup_soc(soc: int) -> bytes:
    """Build a SET command for backup reserve SOC (field 102).
    
    Args:
        soc: Backup reserve SOC (0-100%).
    
    Returns:
        Complete protobuf command bytes.
    """
    pdata = _stream_pdata((102, soc))
    return _stream_wrap_cmd(pdata)

def build_relay(field_num: int, on: bool) -> bytes:
    """Build a SET command for AC relay (field 380 or 381).
    
    Args:
        field_num: 380 (relay2) or 381 (relay3).
        on: True = relay ON, False = relay OFF.
    
    Returns:
        Complete protobuf command bytes.
    """
    pdata = _stream_pdata((field_num, 1 if on else 0))
    return _stream_wrap_cmd(pdata)
```

- [ ] **Step 5: Verify the file compiles (import test)**

Run:
```bash
cd /Users/eddwilliams/Development/hassio-ecoflow-cloud
python3 -c "from custom_components.ecoflow_cloud.devices.internal.proto_codec import build_feed_limit; print('Builders imported successfully')"
```

Expected: "Builders imported successfully" (no import errors)

- [ ] **Step 6: Commit**

```bash
git add custom_components/ecoflow_cloud/devices/internal/proto_codec.py
git commit -m "feat: add protobuf encoder helpers and control builders"
```

---

## Checkpoint 1: Review

Plan is comprehensive. Before proceeding to entity wiring (Tasks 4–5), confirm:

- [ ] Proto definition added and compiles
- [ ] Builders import without errors
- [ ] All 5 builder functions present (feed_limit, max/min_chg_soc, backup_soc, relay)
- [ ] Ready to proceed with entity integration

**All clear? Proceed to Tasks 4–5 (number + switch entities) in next batch.**
