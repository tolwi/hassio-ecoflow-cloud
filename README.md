# EcoFlow Cloud Integration for Home Assistant
Inspired by [hassio-ecoflow](https://github.com/vwt12eh8/hassio-ecoflow) and [ecoflow-mqtt-prometheus-exporter](https://github.com/berezhinskiy/ecoflow-mqtt-prometheus-exporter) this integration uses EcoFlow MQTT Broker `mqtt.ecoflow.com` to monitor and control the device.

## Installation

- Install as a custom repository via HACS
- Manually download and extract to the custom_components directory

Once installed, use Add Integration -> Ecoflow Cloud.

## Disclaimers
⚠️ Integration has only been tested with
  - RIVER 2 Max
  - DELTA 2

⚠️ Originally developed for personal use without a goal to cover all available device attributes

## Current state
*Sensors*:
 - Main Battery Level
 - Charge Remaining Time
 - Discharge Remaining Time
 - Total In Power
 - Total Out Power
 - Inv Out Temperature
 - Battery Temperature
 - Cycles

*Switches*
- AC Enabled
- DC (12V) Enabled
- USB Enabled (_Delta 2 only_)
- Beeper (_Delta 2 only_)

*Config values (Numbers)*
- Max Charge Level
- Min Discharge Level
- AC Charging Power
- Screen Timeout
- Unit Timeout
- AC Timeout
- DC (12V) Timeout (_Delta 2 only_)