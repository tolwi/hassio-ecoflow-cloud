# STREAM 5000 / STREAM AC 5000 — Public API (experimental)

This implementation uses **only the official EcoFlow Developer API**, with
signed HTTP quota requests and the public JSON MQTT broker. It does **not** use
the private mobile-app API or protobuf.

- STREAM 5000: `ES21` serial prefix
- STREAM AC 5000: `ES22` serial prefix
- Device mapping is handled by `devices/registry.py`; detection is handled by
  `api/public_api.py`.
- MQTT nested groups and HTTP hyphen-separated keys are normalized to common
  dotted keys by `devices/public/stream_5000_data.py`.
- All writes use BKW3 public JSON commands: `cmdId=38`, `cmdFunc=254`,
  `dirDest=1`, `dirSrc=1`, `dest=2`, `needAck=true`.

## Sensors

| Entity | Public API quota field |
|---|---|
| Battery Level | `sysEnergyStreamReport.bpSoc` |
| Power PV Sum | `sysEnergyStreamReport.pvPwr` |
| Power Battery | `sysEnergyStreamReport.bpPwr` |
| Power Sys Load | `sysEnergyStreamReport.loadPwr` |
| Power Grid | `sysEnergyStreamReport.gridPwr` |
| Power AC SYS | `sysEnergyStreamReport.onGridPwr` |
| Status | Existing generic status sensor |

## Controls

- Backup Reserve (switch): `bpBackupConfig.backupSocOnOff`
- Backup Reserve Level (number, 0–100%):
  `bpBackupConfig.backupSoc`; setting this also enables backup reserve.
- Feed-in Limit (switch): `powerParameterConfig.feedToGridLimitOnOff`
- AC Socket (switch): `devSwitch.acSocketOnoff`
- Operating Mode (select): `workMode` with values
  `SELF_CONSUMPTION`, `AI_MODE`, `TIMER_TASK`, `POU_MODE`,
  `EMERGENCY_STOP`.

**Important:** Writes have not been validated on physical ES21/ES22 hardware.
The public Developer API may also deny access to these models, despite
publishing their API specification; check that the serial appears in
`/device/list` and `/device/quota/all` succeeds before attempting writes.
For the AC Socket command, verify whether the device serial is the system
serial or a component serial, as described in EcoFlow's public documentation.

## Verification

Parser unit tests are in `tests/test_stream_5000_data.py`:

```sh
python -m unittest discover -s tests -p 'test_stream_5000_data.py'
```

Remaining validation: retrieve a redacted real quota response, verify each
field and AC socket target, then test changes while monitoring acknowledgements
and states. Do not automate power commands before that verification.

Documentation reference:
https://developer-eu.ecoflow.com/us/document/PP3?id=2115695633708867585
