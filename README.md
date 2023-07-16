# EcoFlow Cloud Integration for Home Assistant
Inspired by [hassio-ecoflow](https://github.com/vwt12eh8/hassio-ecoflow) and [ecoflow-mqtt-prometheus-exporter](https://github.com/berezhinskiy/ecoflow-mqtt-prometheus-exporter) this integration uses EcoFlow MQTT Broker `mqtt.ecoflow.com` to monitor and control the device.

## Installation

- Install as a custom repository via HACS
- Manually download and extract to the custom_components directory

Once installed, use Add Integration -> Ecoflow Cloud.

## Disclaimers

⚠️ Originally developed for personal use without a goal to cover all available device attributes

## Current state
<details><summary> DELTA_2 <i>(sensors: 35, switches: 8, sliders: 6, selects: 5)</i> </summary>
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
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Slave Battery Level  _(auto)_
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

<details><summary> RIVER_2 <i>(sensors: 21, switches: 3, sliders: 3, selects: 5)</i> </summary>
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

<details><summary> RIVER_2_MAX <i>(sensors: 24, switches: 3, sliders: 3, selects: 5)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Total In Power
- Total Out Power
- Solar In Current
- Solar In Voltage
- AC In Power
- Type-C In Power
- Solar In Power
- AC Out Power
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

<details><summary> RIVER_2_PRO <i>(sensors: 22, switches: 3, sliders: 3, selects: 5)</i> </summary>
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

<details><summary> DELTA_PRO <i>(sensors: 38, switches: 6, sliders: 6, selects: 4)</i> </summary>
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
- Slave 1 Battery Temperature  _(auto)_
- Slave 1 In Power  _(auto)_
- Slave 1 Out Power  _(auto)_
- Slave 2 Battery Level  _(auto)_
- Slave 2 Battery Temperature  _(auto)_
- Slave 2 In Power  _(auto)_
- Slave 2 Out Power  _(auto)_
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

<details><summary> RIVER_MAX <i>(sensors: 27, switches: 4, sliders: 1, selects: 2)</i> </summary>
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
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Slave Battery Level  _(auto)_
- Slave Battery Temperature  _(auto)_
- Slave Min Cell Temperature  _(disabled)_
- Slave Max Cell Temperature  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Slave Cycles  _(auto)_
- Status

*Switches*
- Beeper
- AC Enabled
- DC (12V) Enabled
- X-Boost Enabled

*Sliders (numbers)*
- Max Charge Level  _(read-only)_

*Selects*
- Unit Timeout
- AC Timeout

</p></details>

<details><summary> RIVER_PRO <i>(sensors: 29, switches: 3, sliders: 1, selects: 2)</i> </summary>
<p>

*Sensors*
- Main Battery Level
- Total In Power
- Total Out Power
- Solar In Current
- Solar In Voltage
- AC In Power
- AC Out Power
- DC Out Power
- Type-C Out Power
- USB (1) Out Power
- USB (2) Out Power
- USB (3) Out Power
- Remaining Time
- Battery Temperature
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Battery Volts  _(disabled)_
- Battery Current  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Cycles
- Slave Battery Level  _(auto)_
- Slave Cycles  _(auto)_
- Slave Battery Temperature  _(auto)_
- Slave Battery Volts  _(disabled)_
- Slave Battery Current  _(disabled)_
- Slave Min Cell Volts  _(disabled)_
- Slave Max Cell Volts  _(disabled)_
- Status

*Switches*
- Beeper  _(read-only)_
- AC Enabled  _(read-only)_
- X-Boost Enabled  _(read-only)_

*Sliders (numbers)*
- Max Charge Level  _(read-only)_

*Selects*
- Unit Timeout  _(read-only)_
- AC Timeout  _(read-only)_

</p></details>

<details><summary> DELTA_MAX <i>(sensors: 25, switches: 7, sliders: 5, selects: 0)</i> </summary>
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
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
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

<details><summary> DELTA_2_MAX <i>(sensors: 25, switches: 5, sliders: 5, selects: 3)</i> </summary>
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
- Min Cell Temperature  _(disabled)_
- Max Cell Temperature  _(disabled)_
- Battery Volts  _(disabled)_
- Min Cell Volts  _(disabled)_
- Max Cell Volts  _(disabled)_
- Status

*Switches*
- Beeper
- USB Enabled
- AC Always On
- AC Enabled
- X-Boost Enabled

*Sliders (numbers)*
- Max Charge Level
- Min Discharge Level
- Generator Auto Start Level
- Generator Auto Stop Level
- AC Charging Power

*Selects*
- Screen Timeout
- Unit Timeout
- AC Timeout

</p></details>

<details><summary> POWERSTREAM <i>(sensors: 25, switches: 0, sliders: 0, selects: 0)</i> </summary>
<p>

*Sensors*
- Solar 1 Watts
- Solar 1 Input Potential
- Solar 1 Op Potential
- Solar 1 Currrent
- Solar 1 Tempurature
- Solar 2 Watts
- Solar 2 Input Potential
- Solar 2 Op Potential
- Solar 2 Current
- Solar 2 Tempurature
- Battery Charge
- Battery Input Watts
- Battery Input Potential
- Battery Op Potential
- Battery Input Current
- Battery Tempurature
- Charge Time
- Discharge Time
- LLC Input Potential _(disabled)_
- LLC Op Potential _(disabled)_
- Inverter Output Watts
- Inverter Output Potential _(disabled)_
- Inverter Op Potential
- Inverter Output Current
- Inverter DC Current
- Inverter Frequency
- Inverter Tempurature
- Other Loads
- Smart Plug Loads
- Rated Power

*Switches*
None

*Sliders (numbers)*
None

*Selects*
None

</p></details>

## How to
- [Add/update device](docs/integration.md)
