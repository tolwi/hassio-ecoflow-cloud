# EcoFlow Cloud Integration for Home Assistant
Inspired by [hassio-ecoflow](https://github.com/vwt12eh8/hassio-ecoflow) and [ecoflow-mqtt-prometheus-exporter](https://github.com/berezhinskiy/ecoflow-mqtt-prometheus-exporter) this integration uses EcoFlow MQTT Broker `mqtt.ecoflow.com` to monitor and control the device.

## Installation

- Install as a custom repository via HACS
- Manually download and extract to the custom_components directory

Once installed, use Add Integration -> Ecoflow Cloud.

## Disclaimers

⚠️ Originally developed for personal use without a goal to cover all available device attributes

## Current state
<details><summary> DELTA_2 <i>(sensors: 34, switches: 7, sliders: 5, selects: 5)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Battery Level
- Total In Power
- Total Out Power
- AC In Power
- Solar In Power
- AC Out Power
- DC Out Power
- Type-C (1) Out Power
- Type-C (2) Out Power
- USB (1) Out Power
- USB (2) Out Power
- USB QC (1) Out Power
- USB QC (2) Out Power
- Charge Remaining Time
- Discharge Remaining Time
- Inv Out Temperature
- Cycles
- Battery Temperature
- Min Cell Temperature
- Max Cell Temperature
- Battery Volts
- Min Cell Volts
- Max Cell Volts
- Slave Battery Level
- Slave Battery Temperature
- Slave Min Cell Temperature
- Slave Max Cell Temperature
- Slave Battery Volts
- Slave Min Cell Volts
- Slave Max Cell Volts
- Slave Cycles
- Slave In Power
- Slave Out Power

*Switches*
- Beeper 
- USB Enabled 
- AC Always On 
- Prio Solar Charging 
- AC Enabled 
- X-Boost Enabled 
- DC (12V) Enabled 

*Sliders (numbers)*
- Max Charge Level 
- Min Discharge Level 
- Generator Auto Start Level 
- Generator Auto Stop Level 
- AC Charging Power 

*Selects*
- DC (12V) Charge Current 
- Screen Timeout 
- Unit Timeout 
- AC Timeout 
- DC (12V) Timeout 

</p></details>

<details><summary> RIVER_2 <i>(sensors: 20, switches: 3, sliders: 3, selects: 5)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Total In Power
- Total Out Power
- AC In Power
- Type-C In Power
- Solar In Power
- AC Out Power
- DC Out Power
- Type-C (1) Out Power
- USB Out Power
- Charge Remaining Time
- Discharge Remaining Time
- Inv Out Temperature
- Cycles
- Battery Temperature
- Min Cell Temperature
- Max Cell Temperature
- Battery Volts
- Min Cell Volts
- Max Cell Volts

*Switches*
- AC Enabled 
- X-Boost Enabled 
- DC (12V) Enabled 

*Sliders (numbers)*
- Max Charge Level 
- Min Discharge Level 
- AC Charging Power 

*Selects*
- DC (12V) Charge Current 
- DC Mode 
- Screen Timeout 
- Unit Timeout 
- AC Timeout 

</p></details>

<details><summary> RIVER_2_MAX <i>(sensors: 21, switches: 3, sliders: 3, selects: 5)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Total In Power
- Total Out Power
- AC In Power
- Type-C In Power
- Solar In Power
- AC Out Power
- DC Out Power
- Type-C (1) Out Power
- USB (1) Out Power
- USB (2) Out Power
- Charge Remaining Time
- Discharge Remaining Time
- Inv Out Temperature
- Cycles
- Battery Temperature
- Min Cell Temperature
- Max Cell Temperature
- Battery Volts
- Min Cell Volts
- Max Cell Volts

*Switches*
- AC Enabled 
- X-Boost Enabled 
- DC (12V) Enabled 

*Sliders (numbers)*
- Max Charge Level 
- Min Discharge Level 
- AC Charging Power 

*Selects*
- DC (12V) Charge Current 
- DC Mode 
- Screen Timeout 
- Unit Timeout 
- AC Timeout 

</p></details>

<details><summary> DELTA_PRO <i>(sensors: 24, switches: 5, sliders: 5, selects: 4)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Total In Power
- Total Out Power
- AC In Power
- Solar In Power
- AC Out Power
- DC Out Power
- DC Car Out Power
- DC Anderson Out Power
- Type-C (1) Out Power
- Type-C (2) Out Power
- USB (1) Out Power
- USB (2) Out Power
- USB QC (1) Out Power
- USB QC (2) Out Power
- Charge Remaining Time
- Discharge Remaining Time
- Cycles
- Battery Temperature
- Min Cell Temperature
- Max Cell Temperature
- Battery Volts
- Min Cell Volts
- Max Cell Volts

*Switches*
- Beeper 
- DC (12V) Enabled 
- AC Enabled 
- X-Boost Enabled 
- AC Always On 

*Sliders (numbers)*
- Max Charge Level 
- Min Discharge Level 
- Generator Auto Start Level 
- Generator Auto Stop Level 
- AC Charging Power 

*Selects*
- DC (12V) Charge Current 
- Screen Timeout 
- Unit Timeout 
- AC Timeout 

</p></details>

<details><summary> RIVER_MAX <i>(sensors: 26, switches: 4, sliders: 1, selects: 2)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Total In Power
- Total Out Power
- AC In Power
- AC Out Power
- DC Out Power
- Type-C Out Power
- USB (1) Out Power
- USB (2) Out Power
- USB (3) Out Power
- Remaining Time
- Cycles
- Battery Temperature
- Min Cell Temperature
- Max Cell Temperature
- Battery Volts
- Min Cell Volts
- Max Cell Volts
- Slave Battery Level
- Slave Battery Temperature
- Slave Min Cell Temperature
- Slave Max Cell Temperature
- Battery Volts
- Min Cell Volts
- Max Cell Volts
- Slave Cycles

*Switches*
- Beeper 
- AC Enabled 
- DC (12V) Enabled 
- X-Boost Enabled 

*Sliders (numbers)*
- Max Charge Level  (read-only)

*Selects*
- Unit Timeout 
- AC Timeout 

</p></details>

<details><summary> RIVER_PRO <i>(sensors: 13, switches: 3, sliders: 1, selects: 2)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Total In Power
- Total Out Power
- AC In Power
- AC Out Power
- DC Out Power
- Type-C Out Power
- USB (1) Out Power
- USB (2) Out Power
- USB (3) Out Power
- Remaining Time
- Battery Temperature
- Cycles

*Switches*
- Beeper  (read-only)
- AC Enabled  (read-only)
- X-Boost Enabled  (read-only)

*Sliders (numbers)*
- Max Charge Level  (read-only)

*Selects*
- Unit Timeout  (read-only)
- AC Timeout  (read-only)

</p></details>

## How to
- [Add/update device](docs/integration.md)