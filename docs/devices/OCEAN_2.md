## OCEAN 2 / OCEAN 2 Plus (EXPERIMENTAL)

**Status: experimental / help wanted.** This is a brand-new EcoFlow product
line (three-phase and single-phase home battery storage, announced
March/April 2026) that is not covered by EcoFlow's Developer API and is not
part of the same account/app family as DELTA/RIVER/PowerStream/PowerOcean.
Support here is based on packet-capturing the official EcoFlow web portal
(https://user-portal.ecoflow.com) rather than on any official documentation,
so treat all sensor values as unverified until confirmed against your own
system.

Do not confuse this with **PowerOcean** (`devices/public/powerocean.py`),
which is a different, older EcoFlow product.

### How this was reverse engineered

1. The portal's browser dashboard talks to the standard EcoFlow MQTT broker
   (`mqtt-e.ecoflow.com:8084`) over MQTT-over-WebSocket - the exact same
   broker and topic scheme (`/app/device/property/{deviceSn}`) used by every
   other EcoFlow device in this project.
2. Messages use the same `Header` / `SendHeaderMsg` protobuf envelope as
   every other device (identical field numbers to e.g. `Wave3Header` in
   `wave3.proto`).
3. Live telemetry arrives as `cmd_func = 254` (the "extended command set"
   marker), `cmd_id = 39`.
4. `Header.pdata` is only obfuscated when `Header.enc_type == 1`, using a
   single repeating-byte XOR keyed by `seq & 0xFF` - not AES, no secret key.
   This is the exact same scheme already used by this project's own
   `smart_meter.py` (`message.pdata = bytes([byte ^ (message.seq % 256) for
   byte in message.pdata])`), which gives good independent confidence that
   this is right.
5. What's *not* confirmed: the exact protobuf schema of the decoded `pdata`
   itself (which field number means `bpSoc`, `sysGridPwr`, etc). The portal's
   own React code clearly destructures an object with fields named
   `emsState`, `sysEnergyStreamReport` (containing `mpptPwr`, `sysLoadPwr`,
   `sysGridPwr`, `bpPwr`, `bpSoc`, `pvInvPwr`), `edevHpUiReport`,
   `edevListReport`, `edevHrParamReport`, `edevEnergyLists` - but the
   compiled protobuf reader that maps wire field numbers to those names
   lives in a part of the minified bundle that hasn't been located yet.

See `custom_components/ecoflow_cloud/devices/internal/ocean2_protocol.py` for
the full technical write-up. That module embeds a self-test using two real
captured frames that validates the envelope/XOR handling - run it with
`python3 -m custom_components.ecoflow_cloud.devices.internal.ocean2_protocol`.

### Known limitation: partial/incremental updates

Like most EcoFlow devices, unchanged fields are simply omitted from a given
MQTT message (normal proto3 behaviour) rather than being resent every time.
A single message is therefore a partial update, not a full snapshot - the
portal itself explicitly merges incoming partial updates into a persisted
state object. This integration currently exposes whatever was in the
*latest* message as-is (via `EcoflowDataHolder`'s usual param merging); it
does not yet replicate the portal's full stateful merge logic.

### Sensors

- **OCEAN 2 Raw Telemetry (Diagnostic)** - always available. State is the
  message sequence number; attributes contain the fully generic decode of
  the latest `cmd_func=254, cmd_id=39` payload (`raw_decoded`), plus
  `cmd_func`/`cmd_id`/`enc_type`. Use this to correlate raw field numbers
  against the EcoFlow app while the exact schema gets pinned down.
- **Experimental Power (field 7.N / 87.N, unconfirmed)** *(disabled by
  default)* - two groups of per-phase(-ish) float32 power readings that were
  in the right order of magnitude compared to the live dashboard at capture
  time. Which group is Solar vs Home load vs something else entirely is
  **not confirmed** - in both captures Grid and Battery power were 0 W, so
  Solar and Home load happened to be numerically equal and could not be told
  apart from the raw values alone.
- **Status** - standard quota/online status sensor.

### Help wanted

If you have an OCEAN 2, the single most useful thing you can do is capture a
few MQTT frames (browser devtools -> Network -> the `mqtt` WebSocket
connection -> right-click a message -> copy/save) at a moment when Grid
power, Battery power, and SoC are all clearly non-zero/non-100%, together
with a screenshot of the dashboard at the same moment. Compare the numbers
in the "OCEAN 2 Raw Telemetry" sensor's `raw_decoded` attribute against what
the app shows, and open an issue/PR with what you find so the field mapping
in `ocean2_protocol.py` can be completed and promoted to real named sensors.
