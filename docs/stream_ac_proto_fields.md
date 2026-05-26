# Stream AC Pro protobuf field reference

This document tracks the protobuf field numbers used by the Stream AC Pro
(`product_id=58`, internal type `STREAM_AC`, EcoFlow codename **PD335**) and
their verification status against real hardware. Field numbers in this
device's protocol are direction-specific — a number that means one thing in
a write may mean something completely different in a read — so each is
tracked separately.

## How to read this

- **Status = ✅ verified**: round-tripped against a real device. Writes
  produce a `cmd_id=18, is_ack=1` reply *and* the new value is reflected in
  subsequent telemetry. Reads consistently surface the expected value.
- **Status = ⚠️ unverified**: the field number comes from a decompiled APK
  proto or an external reference. Behavior on real hardware is unknown.
- **Status = ❌ rejected**: the field number was tested and the device
  either silently ignored it (no ack) or acked without applying the value.

## Important: write fields must be empirically verified

> **The APK-decompiled `Pd335Sys.ConfigWrite` proto is *not* a reliable
> source of truth for this device's accepted write field numbers.**
> Read-side structure (DisplayPropertyUpload field layout) from the decompile
> appears reliable, but several write field numbers from `ConfigWrite` that
> the strategy doc enumerated do not work on this device:
>
> - Fields **33, 34** (`cfgMaxChgSoc`, `cfgMinDsgSoc`): the device acks with
>   `is_ack=1` but the value never updates in subsequent telemetry. Net:
>   silently ignored.
> - Fields **18, 19, 76, 377** (`cfgDc12VOutOpen`, `cfgUsbOpen`,
>   `cfgAcOutOpen`, `cfgAc2OutOpen`): the device does not ack at all. Net:
>   message dropped entirely.
>
> Possible explanations: the APK we decompiled targeted a different PD335
> variant or firmware version; this device's ConfigWrite uses a different
> field-numbering scheme; or these settings are configured through a
> different message id / command class entirely.
>
> **Treat every "new" write field as unverified until a capture session has
> shown the device both acks the write and echoes the new value in a
> subsequent telemetry frame.** See the capture-session guide at the end
> of this document.

## Verified write fields (use these with confidence)

| Write field | Wire shape | Purpose | Read mirror | Source |
|---:|---|---|---|---|
| 102 | top-level varint (0–95 typical) | `cfgBackupReverseSoc` — backup reserve SOC % | field 461 (`backupReverseSoc`) | commit `de63679` |
| 106 | nested sub-message; inner field 1/2/3/4 = 1; trailing empty field 546 commit marker | `cfgEnergyStrategyOperateMode` — operating-mode radio group (Self-Powered / Scheduled / TOU / Smart) | field 393 (matching inner field = 1) | commit `8b2c88c`, `ec524fb` |
| 168 | top-level varint (1 or 2) | `feedGridMode` — feed-in control on/off | field 1628 | commit `218ad96` |
| 380 | top-level varint (0 or 1) | `relay2Onoff` — AC1 relay click | not surfaced yet (field 380 in DisplayPropertyUpload is `plugInInfoPvVol`, an unrelated float — see the note in `stream_ac.py` `switches()`) | commit `218ad96` |

All four work via the existing `_build_proto_command` (or
`_build_proto_nested_command` for field 106) in
`custom_components/ecoflow_cloud/devices/internal/stream_ac.py`, using
`cmd_func=254, cmd_id=17`. The device acks within ~200–600 ms with
`cmd_func=254, cmd_id=18, is_ack=1` on the matching `seq`.

## Verified read fields (DisplayPropertyUpload)

These come through periodic `cmd_id=21` telemetry frames. Some appear in
small incremental uploads (every ~2 s), some only in larger frames (~2 min
cadence on this device, ~1020 bytes of pdata, starts with `9801...`).

| Read field | Type | Param name in `raw["params"]` | Notes |
|---:|---|---|---|
| 6 | varint | `f32ShowSoc` (integer percent) | top-level; surfaced by `_MANUAL_FIELD_MAP[6]` |
| 461 | varint | `backupReverseSoc` | top-level; surfaced by `_MANUAL_FIELD_MAP[461]` |
| 393 | wire-type-2 sub-message; inner field 1/2/3/4 = 1 indicates active mode | `energyStrategyOperateMode.activeMode` + four `energyStrategyOperateMode.operate*Open` flags | surfaced by `_RADIO_GROUP_MAP[393]` |
| 1628 | varint | `feedGridMode` | top-level; surfaced by `_MANUAL_FIELD_MAP[1628]` |
| 730 | varint | (candidate `cmsMinDsgSoc`; value matches device's min discharge SOC setting but not currently mapped) | top-level — passive observation only; no write currently routes here |
| 994 | varint | (candidate `cmsMaxChgSoc`; value matches device's max charge SOC setting but not currently mapped) | top-level — passive observation only; no write currently routes here |

Fields 730 and 994 are read candidates only — see the failed-write notes
above. Surfacing them as sensors would be safe; surfacing them as the
read side of a writable number entity would mislead users until the
matching write fields are identified.

## Failed write attempts

Recorded here so we don't burn time re-testing them with the same
approach. Each was tested with `cmd_func=254, cmd_id=17` and the value
encoded as a top-level varint (the same shape that works for fields 102,
168, 380).

| Tried | Intended setting | Failure mode | Tested |
|---:|---|---|---|
| 33 | `cfgMaxChgSoc` | acked (`is_ack=1`), value never applied (f994 unchanged) | session 2026-05-26 |
| 34 | `cfgMinDsgSoc` | acked, never applied (f730 unchanged) | session 2026-05-26 |
| 18 | `cfgDc12VOutOpen` | no ack, message dropped | session 2026-05-26 |
| 19 | `cfgUsbOpen` | no ack, message dropped | session 2026-05-26 |
| 76 | `cfgAcOutOpen` | no ack, message dropped | session 2026-05-26 |
| 377 | `cfgAc2OutOpen` | no ack, message dropped | session 2026-05-26 |

Implications by analogy: the strategy doc's other low-numbered
ConfigWrite fields (`cfgAcStandbyTime=10`, `cfgDcStandbyTime=11`,
`cfgScreenOffTime=12`, `cfgDevStandbyTime=13`, `cfgLcdLight=14`, etc.)
are likely also wrong as written. Do not implement entities for these
without first capturing the real write traffic.

## Capture session: identifying a write field empirically

The HA integration's MQTT client is subscribed to both
`/app/{appId}/{serial}/thing/property/set` (writes) and `/set_reply`
(acks). This means *every* write to the device — including writes sent
by the EcoFlow mobile app, the device's own UI sync, etc. — passes
through HA's view and is decoded by `_prepare_data`.

To identify the write field for a setting `X`:

1. Bump `custom_components.ecoflow_cloud` to `debug` level. Either edit
   `configuration.yaml` and restart, or call the `logger.set_level`
   service: `{"custom_components.ecoflow_cloud": "debug"}`.
2. Have the device powered up, MQTT-connected (`Status` sensor =
   `online` in HA), and physically observable.
3. In the EcoFlow mobile app, change setting `X` **and nothing else**.
   Note the wall-clock time of the change.
4. In HA log, find the lines within ~2 seconds of that timestamp:
   - A `DEBUG ... cmd id "17" fct id "254"` outgoing log entry shows
     up first — that's the write traveling through the broker.
   - The `payload` debug log just below contains the hex of the
     header. The `new payload` line shows the pdata bytes after the
     header was stripped.
   - A `cmd id "18" ... is_ack: 1` log entry within ~500 ms confirms
     the device accepted the write.
   - A subsequent `STREAM_AC_BOOL_GROUP field=N len=M hex=...` (or, if
     the field number is in `_MANUAL_FIELD_MAP`, a `Found N fields`
     followed by a state change on a HA entity) shows what the write
     contained.
5. Decode the pdata bytes manually to extract the (field, value) pair.
   Typical pattern: `08 <timestamp varint>` (field 6 = timestamp)
   followed by `<tag> <value>` where the tag encodes the target field
   number and wire type.

   A minimal Python decoder:

   ```python
   def varint(b, p):
       r, s = 0, 0
       while p < len(b):
           x = b[p]; p += 1
           r |= (x & 0x7f) << s
           if not (x & 0x80): return r, p
           s += 7
       return r, p

   data = bytes.fromhex("PASTE pdata HEX HERE")
   p = 0
   while p < len(data):
       tag, p = varint(data, p)
       fn, wt = tag >> 3, tag & 7
       if wt == 0:
           v, p = varint(data, p)
           print(f"field {fn}: varint = {v}")
       elif wt == 2:
           ln, p = varint(data, p)
           print(f"field {fn}: bytes[{ln}] = {data[p:p+ln].hex()}")
           p += ln
       else:
           break
   ```

6. Repeat the change in the EcoFlow app with the opposite value
   (toggle off, toggle on, etc.) to confirm the same field number
   carries a different value and identify the on/off encoding.
7. Verify the read side: leave the app's change in place, watch for
   the next telemetry frame (`cmd id "21"` with a large `new payload`
   starting with `9801...`), and find the field whose value changes
   between the pre-toggle and post-toggle captures. That's the read
   mirror.

The captured (write field, read field, on/off values) triple is then
enough to add a switch via `ProtoEnabledEntity` and an entry to
`_MANUAL_FIELD_MAP`.

## Capture-session priorities

When the next session happens, the highest-value targets to capture are:

1. **AC1 output**, **AC2 output**, **USB**, **DC 12V** — Phase F switches
   that are currently broken. Toggle each in the app, one at a time, both
   directions.
2. **Max charge SOC**, **min discharge SOC** — the SOC limit slider pair.
   Move the slider in the app from a known value to a clearly distinct
   value (e.g. max from 100 → 80; min from 5 → 15) and capture the write.
3. **Standby times** (AC, DC, screen, device, AC2) — change each timer in
   the app to a non-default value and capture.
4. **Beep**, **LCD brightness** — easy quality-of-life toggles in the app
   that share the same write infrastructure.

Each of these costs roughly one app interaction + one log capture. A
focused 15-minute session at home should be enough to resolve all of
Phases F + G.
