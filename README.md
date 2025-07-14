# EcoFlow Cloud Integration for Home Assistant
[![GitHub release](https://img.shields.io/github/release/tolwi/hassio-ecoflow-cloud?include_prereleases=&sort=semver&color=blue)](https://github.com/tolwi/hassio-ecoflow-cloud/releases/)
[![issues - hassio-ecoflow-cloud](https://img.shields.io/github/issues/tolwi/hassio-ecoflow-cloud)](https://github.com/tolwi/hassio-ecoflow-cloud/issues)
[![GH-code-size](https://img.shields.io/github/languages/code-size/tolwi/hassio-ecoflow-cloud?color=red)](https://github.com/tolwi/hassio-ecoflow-cloud)
[![GH-last-commit](https://img.shields.io/github/last-commit/tolwi/hassio-ecoflow-cloud?style=flat-square)](https://github.com/tolwi/hassio-ecoflow-cloud/commits/main)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![HACS validation](https://github.com/tolwi/hassio-ecoflow-cloud/workflows/Validate%20with%20hassfest%20and%20HACS/badge.svg)](https://github.com/tolwi/hassio-ecoflow-cloud/actions?query=workflow:"Validate%20with%20hassfest%20and%20HACS")

Inspired by [hassio-ecoflow](https://github.com/vwt12eh8/hassio-ecoflow) and [ecoflow-mqtt-prometheus-exporter](https://github.com/berezhinskiy/ecoflow-mqtt-prometheus-exporter) this integration uses EcoFlow MQTT Broker `mqtt.ecoflow.com` to monitor and control the device.

## Installation

- Install as a custom repository via HACS
- Manually download and extract to the custom_components directory

Once installed, use Add Integration -> Ecoflow Cloud.

## Disclaimers

⚠️ Originally developed for personal use without a goal to cover all available device attributes

## Current state
### Devices available with private_api
<details><summary> DELTA_2 <i>(sensors: 45, switches: 8, sliders: 6, selects: 5)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Main Design Capacity  _(disabled)_
- Main Full Capacity  _(disabled)_
- Main Remain Capacity  _(disabled)_
- State of Health
- Battery Level
- Total In Power
- Total Out Power
- AC In Power
- AC Out Power
- AC In Volts
- AC Out Volts
- Solar In Power
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
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Slave Battery Level  _(auto)_
- Slave Design Capacity  _(disabled)_
- Slave Full Capacity  _(disabled)_
- Slave Remain Capacity  _(disabled)_
- Slave State of Health
- Slave Battery Temperature  _(auto)_
- Slave Min Cell Temperature  _(disabled)_
- Slave Max Cell Temperature  _(disabled)_
- Slave Battery Volts  _(disabled)_
- Slave Min Cell Volts  _(disabled)_
- Slave Max Cell Volts  _(disabled)_
- Slave Cycles  _(auto)_
- Slave In Power  _(auto)_
- Slave Out Power  _(auto)_
- Status

*Switches*
- Beeper 
- USB Enabled 
- AC Always On 
- Prio Solar Charging 
- AC Enabled 
- X-Boost Enabled 
- DC (12V) Enabled 
- Backup Reserve Enabled 

*Sliders (numbers)*
- Max Charge Level 
- Min Discharge Level 
- Backup Reserve Level 
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

<details><summary> RIVER_2 <i>(sensors: 32, switches: 5, sliders: 4, selects: 5)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Main Design Capacity  _(disabled)_
- Main Full Capacity  _(disabled)_
- Main Remain Capacity  _(disabled)_
- State of Health
- Battery Level
- Battery Charging State
- Total In Power
- Total Out Power
- Solar In Current
- Solar In Voltage
- AC In Power
- AC Out Power
- AC In Volts
- AC Out Volts
- Type-C In Power
- Solar In Power
- DC Out Power
- Type-C Out Power
- USB Out Power
- Charge Remaining Time
- Discharge Remaining Time
- Remaining Time
- Inv Out Temperature
- Cycles
- Battery Temperature
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Status

*Switches*
- AC Enabled 
- AC Always On 
- X-Boost Enabled 
- DC (12V) Enabled 
- Backup Reserve Enabled 

*Sliders (numbers)*
- Max Charge Level 
- Min Discharge Level 
- AC Charging Power 
- Backup Reserve Level 

*Selects*
- DC (12V) Charge Current 
- DC Mode 
- Screen Timeout 
- Unit Timeout 
- AC Timeout 

</p></details>

<details><summary> RIVER_2_MAX <i>(sensors: 32, switches: 5, sliders: 4, selects: 5)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Main Design Capacity  _(disabled)_
- Main Full Capacity  _(disabled)_
- Main Remain Capacity  _(disabled)_
- State of Health
- Battery Level
- Battery Charging State
- Total In Power
- Total Out Power
- Solar In Current
- Solar In Voltage
- AC In Power
- AC Out Power
- AC In Volts
- AC Out Volts
- Type-C In Power
- Solar In Power
- DC Out Power
- Type-C Out Power
- USB Out Power
- Charge Remaining Time
- Discharge Remaining Time
- Remaining Time
- Inv Out Temperature
- Cycles
- Battery Temperature
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Status

*Switches*
- AC Enabled 
- AC Always On 
- X-Boost Enabled 
- DC (12V) Enabled 
- Backup Reserve Enabled 

*Sliders (numbers)*
- Max Charge Level 
- Min Discharge Level 
- AC Charging Power 
- Backup Reserve Level 

*Selects*
- DC (12V) Charge Current 
- DC Mode 
- Screen Timeout 
- Unit Timeout 
- AC Timeout 

</p></details>

<details><summary> RIVER_2_PRO <i>(sensors: 30, switches: 3, sliders: 3, selects: 5)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Main Design Capacity  _(disabled)_
- Main Full Capacity  _(disabled)_
- Main Remain Capacity  _(disabled)_
- State of Health
- Battery Level
- Battery Charging State
- Total In Power
- Total Out Power
- AC In Power
- AC Out Power
- AC In Volts
- AC Out Volts
- Type-C In Power
- Solar In Power
- DC Out Power
- Type-C Out Power
- USB Out Power
- Charge Remaining Time
- Discharge Remaining Time
- Remaining Time
- Inv Out Temperature
- Cycles
- Battery Temperature
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Status

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

<details><summary> DELTA_PRO <i>(sensors: 71, switches: 6, sliders: 6, selects: 4)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Main Battery Level (Precise)  _(disabled)_
- Main Design Capacity  _(disabled)_
- Main Full Capacity  _(disabled)_
- Main Remain Capacity  _(disabled)_
- State of Health
- Battery Level
- Battery Level (Precise)  _(disabled)_
- Total In Power
- Total Out Power
- AC In Power
- AC Out Power
- AC In Volts
- AC Out Volts
- Solar In Power
- Solar In Voltage
- Solar In Current
- DC Out Power
- DC Out Voltage
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
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Main Battery Current  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Solar In Energy
- Battery Charge Energy from AC
- Battery Charge Energy from DC
- Battery Discharge Energy to AC
- Battery Discharge Energy to DC
- Slave 1 Battery Level  _(auto)_
- Slave 1 Battery Level (Precise)  _(disabled)_
- Slave 1 Design Capacity  _(disabled)_
- Slave 1 Full Capacity  _(disabled)_
- Slave 1 Remain Capacity  _(disabled)_
- Slave 1 State of Health
- Slave 1 Battery Temperature  _(auto)_
- Slave 1 In Power  _(auto)_
- Slave 1 Out Power  _(auto)_
- Slave 2 Battery Level  _(auto)_
- Slave 2 Battery Level (Precise)  _(disabled)_
- Slave 2 Design Capacity  _(disabled)_
- Slave 2 Full Capacity  _(disabled)_
- Slave 2 Remain Capacity  _(disabled)_
- Slave 2 State of Health
- Slave 1 Battery Volts  _(disabled)_
- Slave 1 Min Cell Volts  _(disabled)_
- Slave 1 Max Cell Volts  _(disabled)_
- Slave 1 Battery Current  _(disabled)_
- Slave 2 Battery Volts  _(disabled)_
- Slave 2 Min Cell Volts  _(disabled)_
- Slave 2 Max Cell Volts  _(disabled)_
- Slave 2 Battery Current  _(disabled)_
- Slave 2 Battery Temperature  _(auto)_
- Slave 2 In Power  _(auto)_
- Slave 2 Out Power  _(auto)_
- Slave 1 Cycles  _(disabled)_
- Slave 2 Cycles  _(disabled)_
- Status

*Switches*
- Beeper 
- DC (12V) Enabled 
- AC Enabled 
- X-Boost Enabled 
- AC Always On 
- Backup Reserve Enabled 

*Sliders (numbers)*
- Max Charge Level 
- Min Discharge Level 
- Backup Reserve Level 
- Generator Auto Start Level 
- Generator Auto Stop Level 
- AC Charging Power 

*Selects*
- DC (12V) Charge Current 
- Screen Timeout 
- Unit Timeout 
- AC Timeout 

</p></details>

<details><summary> RIVER_MAX <i>(sensors: 49, switches: 5, sliders: 1, selects: 3)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Main Design Capacity  _(disabled)_
- Main Full Capacity  _(disabled)_
- Main Remain Capacity  _(disabled)_
- Battery Level
- Total In Power
- Total Out Power
- Solar In Current
- Solar In Voltage
- AC In Power
- AC Out Power
- AC In Volts
- AC Out Volts
- DC Out Power
- Type-C Out Power
- DC Temperature  _(disabled)_
- USB C Temperature  _(disabled)_
- USB (1) Out Power
- USB (2) Out Power
- USB (3) Out Power
- Remaining Time
- Cycles
- Battery Temperature
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Battery Current  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Inverter Inside Temperature
- Inverter Outside Temperature
- Solar In Energy
- Battery Charge Energy from AC
- Battery Charge Energy from DC
- Battery Discharge Energy to AC
- Battery Discharge Energy to DC
- Slave Battery Level  _(auto)_
- Slave Design Capacity  _(disabled)_
- Slave Full Capacity  _(disabled)_
- Slave Remain Capacity  _(disabled)_
- Slave Battery Temperature  _(auto)_
- Slave Min Cell Temperature  _(disabled)_
- Slave Max Cell Temperature  _(disabled)_
- Slave Battery Current  _(disabled)_
- Slave Battery Volts  _(disabled)_
- Slave Min Cell Volts  _(disabled)_
- Slave Max Cell Volts  _(disabled)_
- Slave Cycles  _(auto)_
- Status

*Switches*
- Beeper 
- AC Enabled 
- DC (12V) Enabled 
- X-Boost Enabled 
- Auto Fan Speed 

*Sliders (numbers)*
- Max Charge Level 

*Selects*
- Unit Timeout 
- DC (12V) Timeout 
- AC Timeout 

</p></details>

<details><summary> RIVER_PRO <i>(sensors: 47, switches: 7, sliders: 1, selects: 3)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Main Full Capacity  _(disabled)_
- Main Remain Capacity  _(disabled)_
- Battery Level
- Total In Power
- Total Out Power
- Solar In Current
- Solar In Voltage
- AC In Power
- AC Out Power
- AC In Volts
- AC Out Volts
- DC Out Power
- Type-C Out Power
- DC Temperature  _(disabled)_
- USB C Temperature  _(disabled)_
- USB (1) Out Power
- USB (2) Out Power
- USB (3) Out Power
- Remaining Time
- Cycles
- Battery Temperature
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Battery Current  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Inverter Inside Temperature
- Inverter Outside Temperature
- Solar In Energy
- Battery Charge Energy from AC
- Battery Charge Energy from DC
- Battery Discharge Energy to AC
- Battery Discharge Energy to DC
- Slave Battery Level  _(auto)_
- Slave Full Capacity  _(disabled)_
- Slave Remain Capacity  _(disabled)_
- Slave Cycles  _(auto)_
- Slave Battery Temperature  _(auto)_
- Slave Min Cell Temperature  _(disabled)_
- Slave Max Cell Temperature  _(disabled)_
- Slave Battery Current  _(disabled)_
- Slave Battery Volts  _(disabled)_
- Slave Min Cell Volts  _(disabled)_
- Slave Max Cell Volts  _(disabled)_
- Status

*Switches*
- Beeper 
- AC Always On 
- DC (12V) Enabled 
- AC Enabled 
- X-Boost Enabled 
- AC Slow Charging 
- Auto Fan Speed 

*Sliders (numbers)*
- Max Charge Level 

*Selects*
- Unit Timeout 
- DC (12V) Timeout 
- AC Timeout 

</p></details>

<details><summary> RIVER_MINI <i>(sensors: 17, switches: 2, sliders: 1, selects: 0)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- AC In Power
- AC Out Power
- AC In Volts
- AC Out Volts
- Solar In Voltage
- Solar In Current
- Inverter Inside Temperature
- Inverter Outside Temperature
- Solar In Energy
- Battery Charge Energy from AC
- Battery Charge Energy from DC
- Battery Discharge Energy to AC
- Battery Discharge Energy to DC
- Total In Power
- Total Out Power
- Cycles

*Switches*
- AC Enabled 
- X-Boost Enabled 

*Sliders (numbers)*
- Max Charge Level 

*Selects*

</p></details>

<details><summary> DELTA_MINI <i>(sensors: 39, switches: 4, sliders: 3, selects: 4)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Main Battery Level (Precise)  _(disabled)_
- Main Design Capacity  _(disabled)_
- Main Full Capacity  _(disabled)_
- Main Remain Capacity  _(disabled)_
- State of Health
- Battery Level
- Battery Level (Precise)  _(disabled)_
- Total In Power
- Total Out Power
- AC In Power
- AC Out Power
- AC In Volts
- AC Out Volts
- Solar In Power
- Solar In Voltage
- Solar In Current
- DC Out Power
- DC Out Voltage
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
- Battery Temperature  _(disabled)_
- Main Battery Current  _(disabled)_
- Battery Volts  _(disabled)_
- Solar In Energy
- Battery Charge Energy from AC
- Battery Charge Energy from DC
- Battery Discharge Energy to AC
- Battery Discharge Energy to DC
- Status

*Switches*
- Beeper 
- DC (12V) Enabled 
- AC Enabled 
- X-Boost Enabled 

*Sliders (numbers)*
- Max Charge Level 
- Min Discharge Level 
- AC Charging Power 

*Selects*
- DC (12V) Charge Current 
- Screen Timeout 
- Unit Timeout 
- AC Timeout 

</p></details>

<details><summary> DELTA_MAX <i>(sensors: 70, switches: 7, sliders: 5, selects: 0)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Main Battery Level (Precise)  _(disabled)_
- Main Design Capacity  _(disabled)_
- Main Full Capacity  _(disabled)_
- Main Remain Capacity  _(disabled)_
- State of Health
- Battery Level
- Battery Level (Precise)  _(disabled)_
- Total In Power
- Total Out Power
- Main Battery Current
- AC In Power
- AC Out Power
- AC In Volts
- AC Out Volts
- Solar In Power
- Solar In Voltage
- Solar In Current
- DC Out Power
- DC Out Voltage
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
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Solar In Energy
- Battery Charge Energy from AC
- Battery Charge Energy from DC
- Battery Discharge Energy to AC
- Battery Discharge Energy to DC
- Slave 1 Battery Level  _(auto)_
- Slave 1 Battery Level (Precise)  _(disabled)_
- Slave 1 Design Capacity  _(disabled)_
- Slave 1 Full Capacity  _(disabled)_
- Slave 1 Remain Capacity  _(disabled)_
- Slave 1 State of Health
- Slave 1 Battery Temperature  _(auto)_
- Slave 1 In Power  _(auto)_
- Slave 1 Out Power  _(auto)_
- Slave 2 Battery Level  _(auto)_
- Slave 2 Battery Level (Precise)  _(disabled)_
- Slave 2 Design Capacity  _(disabled)_
- Slave 2 Full Capacity  _(disabled)_
- Slave 2 Remain Capacity  _(disabled)_
- Slave 2 State of Health
- Slave 1 Battery Volts  _(disabled)_
- Slave 1 Min Cell Volts  _(disabled)_
- Slave 1 Max Cell Volts  _(disabled)_
- Slave 1 Battery Current  _(disabled)_
- Slave 2 Battery Volts  _(disabled)_
- Slave 2 Min Cell Volts  _(disabled)_
- Slave 2 Max Cell Volts  _(disabled)_
- Slave 2 Battery Current  _(disabled)_
- Slave 2 Battery Temperature  _(auto)_
- Slave 2 In Power  _(auto)_
- Slave 2 Out Power  _(auto)_
- Slave 1 Cycles  _(disabled)_
- Slave 2 Cycles  _(disabled)_
- Status

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

</p></details>

<details><summary> DELTA_2_MAX <i>(sensors: 80, switches: 7, sliders: 6, selects: 3)</i> </summary>
<p>

*Sensors*
- Cumulative Capacity Charge (mAh)  _(disabled)_
- Cumulative Energy Charge (Wh)
- Cumulative Capacity Discharge (mAh)  _(disabled)_
- Cumulative Energy Discharge (Wh)
- Main Battery Level
- Main Design Capacity  _(disabled)_
- Main Full Capacity  _(disabled)_
- Main Remain Capacity  _(disabled)_
- State of Health
- Battery Level
- Total In Power
- Total Out Power
- AC In Power
- AC Out Power
- AC In Volts
- AC Out Volts
- Solar (1) In Power
- Solar (2) In Power
- Solar (1) In Volts
- Solar (2) In Volts
- Solar (1) In Amps
- Solar (2) In Amps
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
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Battery level SOC  _(auto)_
- Slave 1 Cumulative Capacity Charge (mAh)  _(auto)_
- Slave 1 Cumulative Energy Charge (Wh)  _(disabled)_
- Slave 1 Cumulative Capacity Discharge (mAh)  _(auto)_
- Slave 1 Cumulative Energy Discharge (Wh)  _(disabled)_
- Slave 1 Battery Level  _(auto)_
- Slave 1 Design Capacity  _(disabled)_
- Slave 1 Full Capacity  _(disabled)_
- Slave 1 Remain Capacity  _(disabled)_
- Slave 1 Battery Temperature  _(auto)_
- Slave 1 Min Cell Temperature  _(disabled)_
- Slave 1 Max Cell Temperature  _(disabled)_
- Slave 1 Battery Volts  _(disabled)_
- Slave 1 Min Cell Volts  _(disabled)_
- Slave 1 Max Cell Volts  _(disabled)_
- Slave 1 Cycles  _(auto)_
- Slave 1 State of Health  _(auto)_
- Slave 1 In Power  _(auto)_
- Slave 1 Out Power  _(auto)_
- Slave 1 Battery level SOC  _(auto)_
- Slave 2 Cumulative Capacity Charge (mAh)  _(disabled)_
- Slave 2 Cumulative Energy Charge (Wh)  _(auto)_
- Slave 2 Cumulative Capacity Discharge (mAh)  _(disabled)_
- Slave 2 Cumulative Energy Discharge (Wh)  _(auto)_
- Slave 2 Battery Level  _(auto)_
- Slave 2 Design Capacity  _(disabled)_
- Slave 2 Full Capacity  _(disabled)_
- Slave 2 Remain Capacity  _(disabled)_
- Slave 2 Battery Temperature  _(auto)_
- Slave 2 Min Cell Temperature  _(disabled)_
- Slave 2 Max Cell Temperature  _(disabled)_
- Slave 2 Battery Volts  _(disabled)_
- Slave 2 Min Cell Volts  _(disabled)_
- Slave 2 Max Cell Volts  _(disabled)_
- Slave 2 Cycles  _(auto)_
- Slave 2 State of Health  _(auto)_
- Slave 2 In Power  _(auto)_
- Slave 2 Out Power  _(auto)_
- Slave 2 Battery level SOC  _(auto)_
- Status
- Status (Scheduled)

*Switches*
- Beeper 
- USB Enabled 
- AC Always On 
- AC Enabled 
- X-Boost Enabled 
- DC (12V) Enabled 
- Backup Reserve Enabled 

*Sliders (numbers)*
- Max Charge Level 
- Min Discharge Level 
- Backup Reserve Level 
- Generator Auto Start Level 
- Generator Auto Stop Level 
- AC Charging Power 

*Selects*
- Screen Timeout 
- Unit Timeout 
- AC Timeout 

</p></details>

<details><summary> POWERSTREAM <i>(sensors: 57, switches: 0, sliders: 0, selects: 0)</i> </summary>
<p>

*Sensors*
- Solar 1 Watts
- Solar 1 Input Potential
- Solar 1 Op Potential
- Solar 1 Currrent
- Solar 1 Temperature
- Solar 1 Relay Status
- Solar 1 Error Code  _(disabled)_
- Solar 1 Warning Code  _(disabled)_
- Solar 1 Status  _(disabled)_
- Solar 2 Watts
- Solar 2 Input Potential
- Solar 2 Op Potential
- Solar 2 Current
- Solar 2 Temperature
- Solar 2 Relay Status
- Solar 2 Error Code  _(disabled)_
- Solar 2 Warning Code  _(disabled)_
- Solar 2 Status  _(disabled)_
- Battery Type  _(disabled)_
- Battery Charge
- Battery Input Watts
- Battery Input Potential
- Battery Op Potential
- Battery Input Current
- Battery Temperature
- Charge Time
- Discharge Time
- Battery Error Code  _(disabled)_
- Battery Warning Code  _(disabled)_
- Battery Status  _(disabled)_
- LLC Input Potential  _(disabled)_
- LLC Op Potential  _(disabled)_
- LLC Error Code  _(disabled)_
- LLC Warning Code  _(disabled)_
- LLC Status  _(disabled)_
- Inverter On/Off Status
- Inverter Output Watts
- Inverter Output Potential  _(disabled)_
- Inverter Op Potential
- Inverter Output Current
- Inverter DC Current
- Inverter Frequency
- Inverter Temperature
- Inverter Relay Status
- Inverter Error Code  _(disabled)_
- Inverter Warning Code  _(disabled)_
- Inverter Status  _(disabled)_
- Other Loads
- Smart Plug Loads
- Rated Power
- Lower Battery Limit  _(disabled)_
- Upper Battery Limit  _(disabled)_
- Wireless Error Code  _(disabled)_
- Wireless Warning Code  _(disabled)_
- LED Brightness  _(disabled)_
- Heartbeat Frequency  _(disabled)_
- Status

*Switches*

*Sliders (numbers)*

*Selects*

</p></details>

<details><summary> GLACIER <i>(sensors: 33, switches: 3, sliders: 3, selects: 0)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Main Design Capacity  _(disabled)_
- Main Full Capacity  _(disabled)_
- Main Remain Capacity  _(disabled)_
- Battery Level
- Battery Charging State
- Total In Power
- Total Out Power
- Motor Power
- Charge Remaining Time
- Discharge Remaining Time
- Cycles
- Battery Temperature
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Battery Present
- XT60 State
- Fan Level
- Ambient Temperature
- Exhaust Temperature
- Water Temperature
- Left Temperature
- Right Temperature
- Dual Zone Mode
- Ice Time Remain
- Ice Percentage
- Ice Make Mode
- Ice Alert
- Ice Water Level OK
- Status

*Switches*
- Beeper 
- Eco Mode 
- Power 

*Sliders (numbers)*
- Left Set Temperature 
- Combined Set Temperature 
- Right Set Temperature 

*Selects*

</p></details>

<details><summary> WAVE_2 <i>(sensors: 27, switches: 0, sliders: 1, selects: 4)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Main Remain Capacity  _(disabled)_
- Battery Temperature
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Charge Remaining Time
- Discharge Remaining Time
- Condensation temperature  _(disabled)_
- Return air temperature in condensation zone  _(disabled)_
- Air outlet temperature  _(disabled)_
- Evaporation temperature  _(disabled)_
- Exhaust temperature  _(disabled)_
- Evaporation zone return air temperature  _(disabled)_
- Air outlet temperature  _(disabled)_
- Ambient temperature  _(disabled)_
- PV input power
- Battery output power
- PV charging power
- AC input power
- Power supply power
- System power
- Battery power
- Motor operating power
- Battery output power
- AC input power
- PV input power
- Status

*Switches*

*Sliders (numbers)*
- Set Temperature 

*Selects*
- Wind speed 
- Main mode 
- Remote startup/shutdown 
- Sub-mode 

</p></details>

<details><summary> SMART_METER <i>(sensors: 20, switches: 0, sliders: 0, selects: 0)</i> </summary>
<p>

*Sensors*
- Power Grid Global
- Power Grid L1  _(disabled)_
- Power Grid L2  _(disabled)_
- Power Grid L3  _(disabled)_
- Power Grid (L1) In Amps  _(disabled)_
- Power Grid (L2) In Amps  _(disabled)_
- Power Grid (L3) In Amps  _(disabled)_
- Power Grid (L1) Volts  _(disabled)_
- Power Grid (L2) Volts  _(disabled)_
- Power Grid (L3) Volts  _(disabled)_
- Flag L1  _(disabled)_
- Flag L2  _(disabled)_
- Flag L3  _(disabled)_
- L1 Lifetime net usage  _(disabled)_
- L2 Lifetime net usage  _(disabled)_
- L3 Lifetime net usage  _(disabled)_
- Lifetime consumption
- Lifetime injection (2)  _(disabled)_
- Lifetime net usage
- Lifetime injection

*Switches*

*Sliders (numbers)*

*Selects*

</p></details>

<details><summary> STREAM_AC <i>(sensors: 39, switches: 0, sliders: 0, selects: 0)</i> </summary>
<p>

*Sensors*
- Cumulative Capacity Charge (mAh)  _(disabled)_
- Cumulative Energy Charge (Wh)  _(disabled)_
- Cumulative Capacity Discharge (mAh)  _(disabled)_
- Cumulative Energy Discharge (Wh)  _(disabled)_
- Charge Remaining Time  _(disabled)_
- Discharge Remaining Time  _(disabled)_
- Cycles  _(disabled)_
- Design Capacity  _(disabled)_
- Power Battery SOC  _(disabled)_
- Full Capacity  _(disabled)_
- Power AC
- Power Volts  _(disabled)_
- In Power  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Max Cell Volts  _(disabled)_
- Min Cell Temperature  _(disabled)_
- Min Cell Volts  _(disabled)_
- Out Power  _(disabled)_
- Power Battery
- Power PV 1  _(auto)_
- Power PV 2  _(auto)_
- Power PV 3  _(auto)_
- Power PV 4  _(auto)_
- Power PV Sum
- Power SCHUKO1  _(auto)_
- Power SCHUKO2  _(auto)_
- Power Grid
- Power Sys Load
- Power Sys Load From Battery
- Power Sys Load From Grid
- Power Sys Load From PV
- Real State of Health  _(disabled)_
- Remain Capacity  _(disabled)_
- Remaining Time  _(disabled)_
- Power Battery  _(disabled)_
- State of Health  _(disabled)_
- Power AC SYS  _(disabled)_
- Battery Temperature  _(disabled)_
- Battery Volts  _(disabled)_

*Switches*

*Sliders (numbers)*

*Selects*

</p></details>

<details><summary> STREAM_PRO <i>(sensors: 39, switches: 0, sliders: 0, selects: 0)</i> </summary>
<p>

*Sensors*
- Cumulative Capacity Charge (mAh)  _(disabled)_
- Cumulative Energy Charge (Wh)  _(disabled)_
- Cumulative Capacity Discharge (mAh)  _(disabled)_
- Cumulative Energy Discharge (Wh)  _(disabled)_
- Charge Remaining Time  _(disabled)_
- Discharge Remaining Time  _(disabled)_
- Cycles  _(disabled)_
- Design Capacity  _(disabled)_
- Power Battery SOC  _(disabled)_
- Full Capacity  _(disabled)_
- Power AC
- Power Volts  _(disabled)_
- In Power  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Max Cell Volts  _(disabled)_
- Min Cell Temperature  _(disabled)_
- Min Cell Volts  _(disabled)_
- Out Power  _(disabled)_
- Power Battery
- Power PV 1  _(auto)_
- Power PV 2  _(auto)_
- Power PV 3  _(auto)_
- Power PV 4  _(auto)_
- Power PV Sum
- Power SCHUKO1  _(auto)_
- Power SCHUKO2  _(auto)_
- Power Grid
- Power Sys Load
- Power Sys Load From Battery
- Power Sys Load From Grid
- Power Sys Load From PV
- Real State of Health  _(disabled)_
- Remain Capacity  _(disabled)_
- Remaining Time  _(disabled)_
- Power Battery  _(disabled)_
- State of Health  _(disabled)_
- Power AC SYS  _(disabled)_
- Battery Temperature  _(disabled)_
- Battery Volts  _(disabled)_

*Switches*

*Sliders (numbers)*

*Selects*

</p></details>

<details><summary> STREAM_ULTRA <i>(sensors: 39, switches: 0, sliders: 0, selects: 0)</i> </summary>
<p>

*Sensors*
- Cumulative Capacity Charge (mAh)  _(disabled)_
- Cumulative Energy Charge (Wh)  _(disabled)_
- Cumulative Capacity Discharge (mAh)  _(disabled)_
- Cumulative Energy Discharge (Wh)  _(disabled)_
- Charge Remaining Time  _(disabled)_
- Discharge Remaining Time  _(disabled)_
- Cycles  _(disabled)_
- Design Capacity  _(disabled)_
- Power Battery SOC  _(disabled)_
- Full Capacity  _(disabled)_
- Power AC
- Power Volts  _(disabled)_
- In Power  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Max Cell Volts  _(disabled)_
- Min Cell Temperature  _(disabled)_
- Min Cell Volts  _(disabled)_
- Out Power  _(disabled)_
- Power Battery
- Power PV 1  _(auto)_
- Power PV 2  _(auto)_
- Power PV 3  _(auto)_
- Power PV 4  _(auto)_
- Power PV Sum
- Power SCHUKO1  _(auto)_
- Power SCHUKO2  _(auto)_
- Power Grid
- Power Sys Load
- Power Sys Load From Battery
- Power Sys Load From Grid
- Power Sys Load From PV
- Real State of Health  _(disabled)_
- Remain Capacity  _(disabled)_
- Remaining Time  _(disabled)_
- Power Battery  _(disabled)_
- State of Health  _(disabled)_
- Power AC SYS  _(disabled)_
- Battery Temperature  _(disabled)_
- Battery Volts  _(disabled)_

*Switches*

*Sliders (numbers)*

*Selects*

</p></details>

### Devices available with public_api
<details><summary> DELTA Max (API) <i>(sensors: 70, switches: 7, sliders: 5, selects: 0)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Main Battery Level (Precise)  _(disabled)_
- Main Design Capacity  _(disabled)_
- Main Full Capacity  _(disabled)_
- Main Remain Capacity  _(disabled)_
- State of Health
- Battery Level
- Battery Level (Precise)  _(disabled)_
- Total In Power
- Total Out Power
- Main Battery Current
- AC In Power
- AC Out Power
- AC In Volts
- AC Out Volts
- Solar In Power
- Solar In Voltage
- Solar In Current
- DC Out Power
- DC Out Voltage
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
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Solar In Energy
- Battery Charge Energy from AC
- Battery Charge Energy from DC
- Battery Discharge Energy to AC
- Battery Discharge Energy to DC
- Slave 1 Battery Level  _(auto)_
- Slave 1 Battery Level (Precise)  _(disabled)_
- Slave 1 Design Capacity  _(disabled)_
- Slave 1 Full Capacity  _(disabled)_
- Slave 1 Remain Capacity  _(disabled)_
- Slave 1 State of Health
- Slave 1 Battery Temperature  _(auto)_
- Slave 1 In Power  _(auto)_
- Slave 1 Out Power  _(auto)_
- Slave 2 Battery Level  _(auto)_
- Slave 2 Battery Level (Precise)  _(disabled)_
- Slave 2 Design Capacity  _(disabled)_
- Slave 2 Full Capacity  _(disabled)_
- Slave 2 Remain Capacity  _(disabled)_
- Slave 2 State of Health
- Slave 1 Battery Volts  _(disabled)_
- Slave 1 Min Cell Volts  _(disabled)_
- Slave 1 Max Cell Volts  _(disabled)_
- Slave 1 Battery Current  _(disabled)_
- Slave 2 Battery Volts  _(disabled)_
- Slave 2 Min Cell Volts  _(disabled)_
- Slave 2 Max Cell Volts  _(disabled)_
- Slave 2 Battery Current  _(disabled)_
- Slave 2 Battery Temperature  _(auto)_
- Slave 2 In Power  _(auto)_
- Slave 2 Out Power  _(auto)_
- Slave 1 Cycles  _(disabled)_
- Slave 2 Cycles  _(disabled)_
- Status

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

</p></details>

<details><summary> DELTA Pro (API) <i>(sensors: 71, switches: 6, sliders: 6, selects: 4)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Main Battery Level (Precise)  _(disabled)_
- Main Design Capacity  _(disabled)_
- Main Full Capacity  _(disabled)_
- Main Remain Capacity  _(disabled)_
- State of Health
- Battery Level
- Battery Level (Precise)  _(disabled)_
- Total In Power
- Total Out Power
- Main Battery Current
- AC In Power
- AC Out Power
- AC In Volts
- AC Out Volts
- Solar In Power
- Solar In Voltage
- Solar In Current
- DC Out Power
- DC Out Voltage
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
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Solar In Energy
- Battery Charge Energy from AC
- Battery Charge Energy from DC
- Battery Discharge Energy to AC
- Battery Discharge Energy to DC
- Slave 1 Battery Level  _(auto)_
- Slave 1 Battery Level (Precise)  _(disabled)_
- Slave 1 Design Capacity  _(disabled)_
- Slave 1 Full Capacity  _(disabled)_
- Slave 1 Remain Capacity  _(disabled)_
- Slave 1 State of Health
- Slave 1 Battery Temperature  _(auto)_
- Slave 1 In Power  _(auto)_
- Slave 1 Out Power  _(auto)_
- Slave 2 Battery Level  _(auto)_
- Slave 2 Battery Level (Precise)  _(disabled)_
- Slave 2 Design Capacity  _(disabled)_
- Slave 2 Full Capacity  _(disabled)_
- Slave 2 Remain Capacity  _(disabled)_
- Slave 2 State of Health
- Slave 1 Battery Volts  _(disabled)_
- Slave 1 Min Cell Volts  _(disabled)_
- Slave 1 Max Cell Volts  _(disabled)_
- Slave 1 Battery Current  _(disabled)_
- Slave 2 Battery Volts  _(disabled)_
- Slave 2 Min Cell Volts  _(disabled)_
- Slave 2 Max Cell Volts  _(disabled)_
- Slave 2 Battery Current  _(disabled)_
- Slave 2 Battery Temperature  _(auto)_
- Slave 2 In Power  _(auto)_
- Slave 2 Out Power  _(auto)_
- Slave 1 Cycles  _(disabled)_
- Slave 2 Cycles  _(disabled)_
- Status

*Switches*
- Beeper 
- DC (12V) Enabled 
- AC Enabled 
- X-Boost Enabled 
- AC Always On 
- Backup Reserve Enabled 

*Sliders (numbers)*
- Max Charge Level 
- Min Discharge Level 
- Backup Reserve Level 
- Generator Auto Start Level 
- Generator Auto Stop Level 
- AC Charging Power 

*Selects*
- DC (12V) Charge Current 
- Screen Timeout 
- Unit Timeout 
- AC Timeout 

</p></details>

<details><summary> DELTA 2 (API) <i>(sensors: 45, switches: 8, sliders: 6, selects: 5)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Main Design Capacity  _(disabled)_
- Main Full Capacity  _(disabled)_
- Main Remain Capacity  _(disabled)_
- State of Health
- Battery Level
- Total In Power
- Total Out Power
- AC In Power
- AC Out Power
- AC In Volts
- AC Out Volts
- Solar In Power
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
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Slave Battery Level  _(auto)_
- Slave Design Capacity  _(disabled)_
- Slave Full Capacity  _(disabled)_
- Slave Remain Capacity  _(disabled)_
- Slave State of Health
- Slave Battery Temperature  _(auto)_
- Slave Min Cell Temperature  _(disabled)_
- Slave Max Cell Temperature  _(disabled)_
- Slave Battery Volts  _(disabled)_
- Slave Min Cell Volts  _(disabled)_
- Slave Max Cell Volts  _(disabled)_
- Slave Cycles  _(auto)_
- Slave In Power  _(auto)_
- Slave Out Power  _(auto)_
- Status

*Switches*
- Beeper 
- USB Enabled 
- AC Always On 
- Prio Solar Charging 
- AC Enabled 
- X-Boost Enabled 
- DC (12V) Enabled 
- Backup Reserve Enabled 

*Sliders (numbers)*
- Max Charge Level 
- Min Discharge Level 
- Backup Reserve Level 
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

<details><summary> DELTA 2 Max (API) <i>(sensors: 80, switches: 7, sliders: 6, selects: 3)</i> </summary>
<p>

*Sensors*
- Cumulative Capacity Charge (mAh)  _(disabled)_
- Cumulative Energy Charge (Wh)
- Cumulative Capacity Discharge (mAh)  _(disabled)_
- Cumulative Energy Discharge (Wh)
- Main Battery Level
- Main Design Capacity  _(disabled)_
- Main Full Capacity  _(disabled)_
- Main Remain Capacity  _(disabled)_
- State of Health
- Battery Level
- Total In Power
- Total Out Power
- AC In Power
- AC Out Power
- AC In Volts
- AC Out Volts
- Solar (1) In Power
- Solar (2) In Power
- Solar (1) In Volts
- Solar (2) In Volts
- Solar (1) In Amps
- Solar (2) In Amps
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
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Battery level SOC  _(auto)_
- Slave 1 Cumulative Capacity Charge (mAh)  _(auto)_
- Slave 1 Cumulative Energy Charge (Wh)  _(disabled)_
- Slave 1 Cumulative Capacity Discharge (mAh)  _(auto)_
- Slave 1 Cumulative Energy Discharge (Wh)  _(disabled)_
- Slave 1 Battery Level  _(auto)_
- Slave 1 Design Capacity  _(disabled)_
- Slave 1 Full Capacity  _(disabled)_
- Slave 1 Remain Capacity  _(disabled)_
- Slave 1 Battery Temperature  _(auto)_
- Slave 1 Min Cell Temperature  _(disabled)_
- Slave 1 Max Cell Temperature  _(disabled)_
- Slave 1 Battery Volts  _(disabled)_
- Slave 1 Min Cell Volts  _(disabled)_
- Slave 1 Max Cell Volts  _(disabled)_
- Slave 1 Cycles  _(auto)_
- Slave 1 State of Health  _(auto)_
- Slave 1 In Power  _(auto)_
- Slave 1 Out Power  _(auto)_
- Slave 1 Battery level SOC  _(auto)_
- Slave 2 Cumulative Capacity Charge (mAh)  _(disabled)_
- Slave 2 Cumulative Energy Charge (Wh)  _(auto)_
- Slave 2 Cumulative Capacity Discharge (mAh)  _(disabled)_
- Slave 2 Cumulative Energy Discharge (Wh)  _(auto)_
- Slave 2 Battery Level  _(auto)_
- Slave 2 Design Capacity  _(disabled)_
- Slave 2 Full Capacity  _(disabled)_
- Slave 2 Remain Capacity  _(disabled)_
- Slave 2 Battery Temperature  _(auto)_
- Slave 2 Min Cell Temperature  _(disabled)_
- Slave 2 Max Cell Temperature  _(disabled)_
- Slave 2 Battery Volts  _(disabled)_
- Slave 2 Min Cell Volts  _(disabled)_
- Slave 2 Max Cell Volts  _(disabled)_
- Slave 2 Cycles  _(auto)_
- Slave 2 State of Health  _(auto)_
- Slave 2 In Power  _(auto)_
- Slave 2 Out Power  _(auto)_
- Slave 2 Battery level SOC  _(auto)_
- Status
- Status (Scheduled)

*Switches*
- Beeper 
- USB Enabled 
- AC Always On 
- AC Enabled 
- X-Boost Enabled 
- DC (12V) Enabled 
- Backup Reserve Enabled 

*Sliders (numbers)*
- Max Charge Level 
- Min Discharge Level 
- Backup Reserve Level 
- Generator Auto Start Level 
- Generator Auto Stop Level 
- AC Charging Power 

*Selects*
- Screen Timeout 
- Unit Timeout 
- AC Timeout 

</p></details>

<details><summary> RIVER 2 (API) <i>(sensors: 32, switches: 5, sliders: 4, selects: 5)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Main Design Capacity  _(disabled)_
- Main Full Capacity  _(disabled)_
- Main Remain Capacity  _(disabled)_
- State of Health
- Battery Level
- Battery Charging State
- Total In Power
- Total Out Power
- Solar In Current
- Solar In Voltage
- AC In Power
- AC Out Power
- AC In Volts
- AC Out Volts
- Type-C In Power
- Solar In Power
- DC Out Power
- Type-C Out Power
- USB Out Power
- Charge Remaining Time
- Discharge Remaining Time
- Remaining Time
- Inv Out Temperature
- Cycles
- Battery Temperature
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Status

*Switches*
- AC Enabled 
- AC Always On 
- X-Boost Enabled 
- DC (12V) Enabled 
- Backup Reserve Enabled 

*Sliders (numbers)*
- Max Charge Level 
- Min Discharge Level 
- AC Charging Power 
- Backup Reserve Level 

*Selects*
- DC (12V) Charge Current 
- DC Mode 
- Screen Timeout 
- Unit Timeout 
- AC Timeout 

</p></details>

<details><summary> RIVER 2 Max (API) <i>(sensors: 32, switches: 5, sliders: 4, selects: 5)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Main Design Capacity  _(disabled)_
- Main Full Capacity  _(disabled)_
- Main Remain Capacity  _(disabled)_
- State of Health
- Battery Level
- Battery Charging State
- Total In Power
- Total Out Power
- Solar In Current
- Solar In Voltage
- AC In Power
- AC Out Power
- AC In Volts
- AC Out Volts
- Type-C In Power
- Solar In Power
- DC Out Power
- Type-C Out Power
- USB Out Power
- Charge Remaining Time
- Discharge Remaining Time
- Remaining Time
- Inv Out Temperature
- Cycles
- Battery Temperature
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Status

*Switches*
- AC Enabled 
- AC Always On 
- X-Boost Enabled 
- DC (12V) Enabled 
- Backup Reserve Enabled 

*Sliders (numbers)*
- Max Charge Level 
- Min Discharge Level 
- AC Charging Power 
- Backup Reserve Level 

*Selects*
- DC (12V) Charge Current 
- DC Mode 
- Screen Timeout 
- Unit Timeout 
- AC Timeout 

</p></details>

<details><summary> RIVER 2 Pro (API) <i>(sensors: 30, switches: 3, sliders: 3, selects: 5)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Main Design Capacity  _(disabled)_
- Main Full Capacity  _(disabled)_
- Main Remain Capacity  _(disabled)_
- State of Health
- Battery Level
- Battery Charging State
- Total In Power
- Total Out Power
- AC In Power
- AC Out Power
- AC In Volts
- AC Out Volts
- Type-C In Power
- Solar In Power
- DC Out Power
- Type-C Out Power
- USB Out Power
- Charge Remaining Time
- Discharge Remaining Time
- Remaining Time
- Inv Out Temperature
- Cycles
- Battery Temperature
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Status

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

<details><summary> Smart Plug (API) <i>(sensors: 4, switches: 1, sliders: 1, selects: 0)</i> </summary>
<p>

*Sensors*
- Temperature
- Volts
- Current
- Power

*Switches*
- On 

*Sliders (numbers)*
- Brightness 

*Selects*

</p></details>

<details><summary> PowerStream (API) <i>(sensors: 58, switches: 0, sliders: 4, selects: 1)</i> </summary>
<p>

*Sensors*
- ESP Temperature
- Solar 1 Watts
- Solar 1 Input Potential
- Solar 1 Op Potential
- Solar 1 Current
- Solar 1 Temperature
- Solar 1 Relay Status
- Solar 1 Error Code  _(disabled)_
- Solar 1 Warning Code  _(disabled)_
- Solar 1 Status  _(disabled)_
- Solar 2 Watts
- Solar 2 Input Potential
- Solar 2 Op Potential
- Solar 2 Current
- Solar 2 Temperature
- Solar 2 Relay Status
- Solar 2 Error Code  _(disabled)_
- Solar 2 Warning Code  _(disabled)_
- Solar 2 Status  _(disabled)_
- Battery Type  _(disabled)_
- Battery Charge
- Battery Input Watts
- Battery Input Potential
- Battery Op Potential
- Battery Input Current
- Battery Temperature
- Charge Time
- Discharge Time
- Battery Error Code  _(disabled)_
- Battery Warning Code  _(disabled)_
- Battery Status  _(disabled)_
- LLC Input Potential  _(disabled)_
- LLC Op Potential  _(disabled)_
- LLC Temperature
- LLC Error Code  _(disabled)_
- LLC Warning Code  _(disabled)_
- LLC Status  _(disabled)_
- Inverter On/Off Status
- Inverter Output Watts
- Inverter Output Potential  _(disabled)_
- Inverter Op Potential
- Inverter Output Current
- Inverter Frequency
- Inverter Temperature
- Inverter Relay Status
- Inverter Error Code  _(disabled)_
- Inverter Warning Code  _(disabled)_
- Inverter Status  _(disabled)_
- Other Loads
- Smart Plug Loads
- Rated Power
- Lower Battery Limit  _(disabled)_
- Upper Battery Limit  _(disabled)_
- Wireless Error Code  _(disabled)_
- Wireless Warning Code  _(disabled)_
- LED Brightness  _(disabled)_
- Heartbeat Frequency  _(disabled)_
- Status

*Switches*

*Sliders (numbers)*
- Min Discharge Level 
- Max Charge Level 
- Brightness 
- Custom load power settings 

*Selects*
- Power supply mode 

</p></details>

<details><summary> WAVE 2 (API) <i>(sensors: 27, switches: 0, sliders: 1, selects: 4)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Main Remain Capacity  _(disabled)_
- Battery Temperature
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Charge Remaining Time
- Discharge Remaining Time
- Condensation temperature  _(disabled)_
- Return air temperature in condensation zone  _(disabled)_
- Air outlet temperature  _(disabled)_
- Evaporation temperature  _(disabled)_
- Exhaust temperature  _(disabled)_
- Evaporation zone return air temperature  _(disabled)_
- Air outlet temperature  _(disabled)_
- Ambient temperature  _(disabled)_
- PV input power
- Battery output power
- PV charging power
- AC input power
- Power supply power
- System power
- Battery power
- Motor operating power
- Battery output power
- AC input power
- PV input power
- Status

*Switches*

*Sliders (numbers)*
- Set Temperature 

*Selects*
- Wind speed 
- Main mode 
- Remote startup/shutdown 
- Sub-mode 

</p></details>

<details><summary> Delta Pro 3 (API) <i>(sensors: 6, switches: 0, sliders: 1, selects: 0)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Main Design Capacity  _(disabled)_
- Battery Level
- Total In Power
- Total Out Power
- AC In Power

*Switches*

*Sliders (numbers)*
- AC Charging Power 

*Selects*

</p></details>

<details><summary> Power Kits (API) <i>(sensors: 161, switches: 10, sliders: 1, selects: 0)</i> </summary>
<p>

### bbcin

*Sensors*
- DC Work Mode 1  _(disabled)_
- DC Work Mode 2  _(disabled)_
- DC In Hardware Type
- DC Online Pos  _(disabled)_
- DC In Energy for Day  _(disabled)_
- Disable Shake Control  _(disabled)_
- Is Car Moving  _(disabled)_
- DC In Event Code  _(disabled)_
- DC In Warning Code
- DC In Error Code
- DC In Battery Power
- DC In Battery Current
- DC In Battery Voltage
- DC Allow Discharge
- DC Discharge Energy  _(disabled)_
- DC In State
- DC In Power
- DC In Current
- DC In Voltage
- DC Charge Paused
- DC Charge Type
- DC Charge Max Current
- DC Charge Mode
- DC In L1 Current  _(disabled)_
- DC In L2 Current  _(disabled)_
- DC In HS1 Temperature
- DC In HS2 Temperature
- DC In PCB Temperature
- Alt. Cable Unit
- Alt. Cable Length
- Alt. Cable Voltage Limit
- Alt. Voltage Limit En

*Switches*
- Main DC Output 

*Sliders (numbers)*

*Selects*

### bbcout

*Sensors*
- DC Out Current
- DC Out Power
- DC Out Battery Power
- DC 1 Out Battery Current  _(disabled)_
- DC 2 Out Battery Current  _(disabled)_
- DC Out Battery Voltage  _(disabled)_

*Switches*

*Sliders (numbers)*

*Selects*

### iclow

*Sensors*
- Main Battery Level
- BMS Error Code
- BMS Warning Code
- BMS Event Code  _(disabled)_
- BMS DC Temperature
- BMS Charge Discharge State  _(disabled)_
- BMS Charge Voltage  _(disabled)_
- BMS Charge Type  _(disabled)_
- BMS Charge In Type  _(disabled)_
- BMS Charge Flag  _(disabled)_
- BMS Max Charge Current  _(disabled)_
- BMS External Kit Type  _(disabled)_
- BMS Bus Current  _(disabled)_
- BMS Bus Voltage
- BMS LSPL Flag  _(disabled)_
- BMS Protect State
- BMS Battery Current  _(disabled)_
- Fan Level  _(disabled)_

*Switches*
- AC Output 
- AC Charging 

*Sliders (numbers)*
- AC Charging Power 

*Selects*

### bpxxx

*Sensors*
- Ampere battery (SN)
- max Capacity battery (SN)
- State of Charge (soc) battery (SN)
- minimal cell voltage battery (SN)
- full cycle count battery (SN)
- current voltage battery (SN)
- current Capacity battery (SN)
- Charing power battery (SN)
- temperatur battery (SN)
- remaining time battery (SN)
- maximum cell voltage battery (SN)
- discharing power battery (SN)

*Switches*

*Sliders (numbers)*

*Selects*

### kitscc

*Sensors*
- Total In Power
- Solar Battery Current
- Solar Battery Voltage
- Solar (2) In Power
- Solar (2) In Voltage
- Solar (2) In Current
- Solar (2) Error Code
- Solar (2) Hot Out  _(disabled)_
- Solar (2) Input Flag  _(disabled)_
- Solar (2) Work Mode  _(disabled)_
- Solar (2) Enabled
- Solar (2) Event Code  _(disabled)_
- Solar (2) Warn Code
- Solar (2) Temperature
- Solar (3) In Power
- Solar (3) In Voltage
- Solar (3) In Current
- Solar (3) Error Code
- Solar (3) Hot Out  _(disabled)_
- Solar (3) Input Flag  _(disabled)_
- Solar (3) Work Mode  _(disabled)_
- Solar (3) Enabled
- Solar (3) Event Code  _(disabled)_
- Solar (3) Warn Code
- Solar (3) Temperature
- Solar Total Charge Current  _(disabled)_
- Solar Energy for Day  _(disabled)_

*Switches*

*Sliders (numbers)*

*Selects*

### lddc

*Sensors*
- Distributer DC Out Power
- DC Out 1
- DC Out 2
- DC Out 3
- DC Out 4
- DC Out 5
- DC Out 6
- DC Out 7
- DC Out 8
- DC Out 9
- DC Out 10
- DC Out 11
- DC Out 12
- DC Ampere Out 1
- DC Ampere Out 2
- DC Ampere Out 3
- DC Ampere Out 4
- DC Ampere Out 5
- DC Ampere Out 6
- DC Ampere Out 7
- DC Ampere Out 8
- DC Ampere Out 9
- DC Ampere Out 10
- DC Ampere Out 11
- DC Ampere Out 12
- Distributer - DC Temperature 1
- Distributer - DC Temperature 2
- DC Out Ch Relay  _(disabled)_
- DC Out Enabled
- DC Out Set Ch State  _(disabled)_
- DC Out Voltage

*Switches*
- DC Switch 1 
- DC Switch 2 
- DC Switch 3 
- DC Switch 4 
- DC Switch 5 
- DC Switch 6 

*Sliders (numbers)*

*Selects*

### ichigh

*Sensors*
- AC Out Voltage
- AC Out Current
- AC Inverter Type  _(disabled)_
- AC In Frequency
- AC In Power
- AC In Current
- AC In Voltage
- AC Out Enabled
- AC Inverter Temperature
- AC Out Power
- AC Outlet Power
- AC Outlet Current
- AC Config Out Frequency  _(disabled)_
- AC Out Frequency
- AC Standby Time  _(disabled)_
- AC Input Day Power  _(disabled)_
- AC Output Day Power  _(disabled)_

*Switches*
- Prioretize grid 

*Sliders (numbers)*

*Selects*

### ldac

*Sensors*
- Distributer AC Out Power
- AC Out 1
- AC Out 2
- AC Out 3
- AC Out 4
- AC Out 5
- AC Out 6
- AC Ampere Out 1
- AC Ampere Out 2
- AC Ampere Out 3
- AC Ampere Out 4
- AC Ampere Out 5
- AC Ampere Out 6
- AC Inverter In Power
- AC Inverter In Voltage
- Distributer AC Temperature 1
- Distributer AC Temperature 2
- AC Charge State

*Switches*

*Sliders (numbers)*

*Selects*

</p></details>

<details><summary> Smart Meter (API) <i>(sensors: 20, switches: 0, sliders: 0, selects: 0)</i> </summary>
<p>

*Sensors*
- Power Grid Global
- Power Grid L1  _(disabled)_
- Power Grid L2  _(disabled)_
- Power Grid L3  _(disabled)_
- Power Grid (L1) In Amps  _(disabled)_
- Power Grid (L2) In Amps  _(disabled)_
- Power Grid (L3) In Amps  _(disabled)_
- Power Grid (L1) Volts  _(disabled)_
- Power Grid (L2) Volts  _(disabled)_
- Power Grid (L3) Volts  _(disabled)_
- Flag L1  _(disabled)_
- Flag L2  _(disabled)_
- Flag L3  _(disabled)_
- L1 Lifetime net usage  _(disabled)_
- L2 Lifetime net usage  _(disabled)_
- L3 Lifetime net usage  _(disabled)_
- Lifetime consumption
- Lifetime injection (2)  _(disabled)_
- Lifetime net usage
- Lifetime injection

*Switches*

*Sliders (numbers)*

*Selects*

</p></details>

<details><summary> Stream AC (API) <i>(sensors: 39, switches: 0, sliders: 0, selects: 0)</i> </summary>
<p>

*Sensors*
- Cumulative Capacity Charge (mAh)  _(disabled)_
- Cumulative Energy Charge (Wh)
- Cumulative Capacity Discharge (mAh)  _(disabled)_
- Cumulative Energy Discharge (Wh)
- Charge Remaining Time  _(disabled)_
- Discharge Remaining Time  _(disabled)_
- Cycles
- Design Capacity  _(disabled)_
- Power Battery SOC
- Full Capacity  _(disabled)_
- Power AC
- Power Volts  _(disabled)_
- In Power
- Max Cell Temperature  _(disabled)_
- Max Cell Volts  _(disabled)_
- Min Cell Temperature  _(disabled)_
- Min Cell Volts  _(disabled)_
- Out Power
- Power Battery
- Power PV 1  _(auto)_
- Power PV 2  _(auto)_
- Power PV 3  _(auto)_
- Power PV 4  _(auto)_
- Power PV Sum
- Power SCHUKO1  _(auto)_
- Power SCHUKO2  _(auto)_
- Power Grid
- Power Sys Load
- Power Sys Load From Battery
- Power Sys Load From Grid
- Power Sys Load From PV
- Real State of Health  _(disabled)_
- Remain Capacity  _(disabled)_
- Remaining Time
- Power Battery
- State of Health
- Power AC SYS
- Battery Temperature
- Battery Volts  _(disabled)_

*Switches*

*Sliders (numbers)*

*Selects*

</p></details>

<details><summary> Stream PRO (API) <i>(sensors: 39, switches: 0, sliders: 0, selects: 0)</i> </summary>
<p>

*Sensors*
- Cumulative Capacity Charge (mAh)  _(disabled)_
- Cumulative Energy Charge (Wh)
- Cumulative Capacity Discharge (mAh)  _(disabled)_
- Cumulative Energy Discharge (Wh)
- Charge Remaining Time  _(disabled)_
- Discharge Remaining Time  _(disabled)_
- Cycles
- Design Capacity  _(disabled)_
- Power Battery SOC
- Full Capacity  _(disabled)_
- Power AC
- Power Volts  _(disabled)_
- In Power
- Max Cell Temperature  _(disabled)_
- Max Cell Volts  _(disabled)_
- Min Cell Temperature  _(disabled)_
- Min Cell Volts  _(disabled)_
- Out Power
- Power Battery
- Power PV 1  _(auto)_
- Power PV 2  _(auto)_
- Power PV 3  _(auto)_
- Power PV 4  _(auto)_
- Power PV Sum
- Power SCHUKO1  _(auto)_
- Power SCHUKO2  _(auto)_
- Power Grid
- Power Sys Load
- Power Sys Load From Battery
- Power Sys Load From Grid
- Power Sys Load From PV
- Real State of Health  _(disabled)_
- Remain Capacity  _(disabled)_
- Remaining Time
- Power Battery
- State of Health
- Power AC SYS
- Battery Temperature
- Battery Volts  _(disabled)_

*Switches*

*Sliders (numbers)*

*Selects*

</p></details>

<details><summary> Stream Ultra (API) <i>(sensors: 39, switches: 0, sliders: 0, selects: 0)</i> </summary>
<p>

*Sensors*
- Cumulative Capacity Charge (mAh)  _(disabled)_
- Cumulative Energy Charge (Wh)
- Cumulative Capacity Discharge (mAh)  _(disabled)_
- Cumulative Energy Discharge (Wh)
- Charge Remaining Time  _(disabled)_
- Discharge Remaining Time  _(disabled)_
- Cycles
- Design Capacity  _(disabled)_
- Power Battery SOC
- Full Capacity  _(disabled)_
- Power AC
- Power Volts  _(disabled)_
- In Power
- Max Cell Temperature  _(disabled)_
- Max Cell Volts  _(disabled)_
- Min Cell Temperature  _(disabled)_
- Min Cell Volts  _(disabled)_
- Out Power
- Power Battery
- Power PV 1  _(auto)_
- Power PV 2  _(auto)_
- Power PV 3  _(auto)_
- Power PV 4  _(auto)_
- Power PV Sum
- Power SCHUKO1  _(auto)_
- Power SCHUKO2  _(auto)_
- Power Grid
- Power Sys Load
- Power Sys Load From Battery
- Power Sys Load From Grid
- Power Sys Load From PV
- Real State of Health  _(disabled)_
- Remain Capacity  _(disabled)_
- Remaining Time
- Power Battery
- State of Health
- Power AC SYS
- Battery Temperature
- Battery Volts  _(disabled)_

*Switches*

*Sliders (numbers)*

*Selects*

</p></details>

<details><summary> Stream Microinverter (API) <i>(sensors: 10, switches: 0, sliders: 0, selects: 0)</i> </summary>
<p>

*Sensors*
- Power AC
- Power PV 1  _(auto)_
- Power PV 2  _(auto)_
- Power Volts  _(disabled)_
- Power PV1 Volts  _(auto)_
- Power PV2 Volts  _(auto)_
- Power In Amps  _(disabled)_
- Power PV1 In Amps  _(auto)_
- Power PV2 In Amps  _(auto)_
- Status

*Switches*

*Sliders (numbers)*

*Selects*

</p></details>

<details><summary> Smart Home Panel 2 (API) <i>(sensors: 16, switches: 2, sliders: 3, selects: 7)</i> </summary>
<p>

*Sensors*
- AC In Power
- Breaker 0 Energy
- Breaker 1 Energy
- Breaker 2 Energy
- Breaker 3 Energy
- Breaker 4 Energy
- Breaker 5 Energy
- Breaker 6 Energy
- Breaker 7 Energy
- Breaker 8 Energy
- Breaker 9 Energy
- Breaker 10 Energy
- Breaker 11 Energy
- Battery Level 1
- Battery Level 2
- Battery Level 3

*Switches*
- EPS Mode 
- Storm Guard 

*Sliders (numbers)*
- Backup reserve level 
- Charging power 
- Charging limit 

*Selects*
- Batterie Status 1 
- Batterie Status 2 
- Batterie Status 3 
- Batterie Force Charge 1 
- Batterie Force Charge 2 
- Batterie Force Charge 3 
- Economic Mode 

</p></details>




## How to
- [Add/update device](docs/integration.md)
