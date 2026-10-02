# Example dashboards

Starting points you can paste into Home Assistant and adapt. They only use entities this
integration creates (no template sensors or helpers to set up first).

## PowerOcean Pro (US) — `ocean_pro.yaml`

For the Ocean Pro inverter (HR51…) together with its Smart Panel (HR61…). Three views:

- **Live** — power flow (solar / grid / battery / home), operating mode, grid connection,
  grid frequency, and a 24 h power history.
- **Strings** — volts, amps, watts and the inverter's own MPPT state/fault code for each of
  the 8 PV inputs, plus per-string power and voltage history. Voltage is what separates
  shade from a bypassed or open string; the view includes a short guide.
- **Circuits** — every Smart Panel circuit drawing power right now, highest first.

### Requirements

Two frontend cards from HACS (Frontend section):

- [power-flow-card-plus](https://github.com/flixlix/power-flow-card-plus)
- [auto-entities](https://github.com/thomasloven/lovelace-auto-entities)

Everything else is a built-in card.

### Setup

1. Find your entity prefixes: Settings → Devices & services → EcoFlow Cloud → open the
   inverter device and click any sensor, e.g. `sensor.hr51xxxxxxxxxxxx_pv1_power`. The part
   between `sensor.` and `_pv1_power` is your inverter prefix. Do the same on the panel device
   (`sensor.hr61xxxxxxxxxxxx_battery_level`).
2. In `ocean_pro.yaml`, replace every `INVERTER` with the inverter prefix and every `PANEL`
   with the panel prefix.
3. Replace `PANEL_DEVICE_NAME` with the panel's device name exactly as HA shows it.
4. Settings → Dashboards → Add dashboard → open it → ⋮ → Edit dashboard → ⋮ → Raw
   configuration editor → paste → Save.

### If a card says "Entity not available"

- **Prefixes can differ between sensors on the same device.** Sensors added in a later
  version can get a different entity_id prefix (for example after the device was renamed or
  moved to an area). Open the device page, find the sensor by name, and use its actual
  entity_id.
- **Entities you renamed** keep your name, not the default one in this file.
- **Disabled entities** don't appear. Some diagnostics ship disabled; enable them on the
  device page.
- The Strings view needs the per-string voltage, current and MPPT sensors, which arrived
  after the original Ocean Pro support. Update the integration if they're missing.

The sensor list for each device is in [`docs/devices`](../devices).
