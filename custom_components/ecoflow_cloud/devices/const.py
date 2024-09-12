DC_MODE_OPTIONS = {
    "Auto": 0,
    "Solar Recharging": 1,
    "Car Recharging": 2,
}

DC_ICONS = {
    "Auto": None,
    "MPPT": "mdi:solar-power",
    "DC": "mdi:current-dc",
}

SCREEN_TIMEOUT_OPTIONS = {
    "Never": 0,
    "10 sec": 10,
    "30 sec": 30,
    "1 min": 60,
    "5 min": 300,
    "30 min": 1800,
}

UNIT_TIMEOUT_OPTIONS = {
    "Never": 0,
    "30 min": 30,
    "1 hr": 60,
    "2 hr": 120,
    "4 hr": 240,
    "6 hr": 360,
    "12 hr": 720,
    "24 hr": 1440
}

UNIT_TIMEOUT_OPTIONS_LIMITED = {
    "Never": 0,
    "30 min": 30,
    "1 hr": 60,
    "2 hr": 120,
    "6 hr": 360,
    "12 hr": 720
}

AC_TIMEOUT_OPTIONS = {
    "Never": 0,
    "30 min": 30,
    "1 hr": 60,
    "2 hr": 120,
    "4 hr": 240,
    "6 hr": 360,
    "12 hr": 720,
    "24 hr": 1440,
}

AC_TIMEOUT_OPTIONS_LIMITED = {
    "Never": 0,
    "2 hr": 120,
    "4 hr": 240,
    "6 hr": 360,
    "12 hr": 720,
    "24 hr": 1440,
}

DC_TIMEOUT_OPTIONS = {
    "Never": 0,
    "30 min": 30,
    "1 hr": 60,
    "2 hr": 120,
    "4 hr": 240,
    "6 hr": 360,
    "12 hr": 720,
    "24 hr": 1440,
}

DC_TIMEOUT_OPTIONS_LIMITED = {
    "Never": 0,
    "2 hr": 120,
    "4 hr": 240,
    "6 hr": 360,
    "12 hr": 720,
    "24 hr": 1440,
}

DC_CHARGE_CURRENT_OPTIONS = {
    "4A": 4000,
    "6A": 6000,
    "8A": 8000
}

MAIN_MODE_OPTIONS = {
    "Cool": 0,
    "Heat": 1,
    "Fan": 2
}

FAN_MODE_OPTIONS = {
    "Low": 0,
    "Medium": 1,
    "High": 2
}

REMOTE_MODE_OPTIONS = {
    "Startup": 1,
    "Standby": 2,
    "Shutdown": 3
}

POWER_SUB_MODE_OPTIONS = {
    "Max": 0,
    "Sleep": 1,
    "Eco": 2,
    "Manual": 3
}

POWER_SUPPLY_PRIORITY_OPTIONS = {
    "Prioritize power supply": 0,
    "Prioritize power storage": 1
}

COMBINED_BATTERY_LEVEL = "Battery Level"
COMBINED_BATTERY_LEVEL_F32 = "Battery Level (Precise)"
BATTERY_CHARGING_STATE = "Battery Charging State"

ATTR_DESIGN_CAPACITY = "Design Capacity (mAh)"
ATTR_FULL_CAPACITY = "Full Capacity (mAh)"
ATTR_REMAIN_CAPACITY = "Remain Capacity (mAh)"
MAIN_DESIGN_CAPACITY = "Main Design Capacity"
MAIN_FULL_CAPACITY = "Main Full Capacity"
MAIN_REMAIN_CAPACITY = "Main Remain Capacity"
SLAVE_DESIGN_CAPACITY = "Slave Design Capacity"
SLAVE_FULL_CAPACITY = "Slave Full Capacity"
SLAVE_REMAIN_CAPACITY = "Slave Remain Capacity"
SLAVE_N_DESIGN_CAPACITY = "Slave %i Design Capacity"
SLAVE_N_FULL_CAPACITY = "Slave %i Full Capacity"
SLAVE_N_REMAIN_CAPACITY = "Slave %i Remain Capacity"

MAIN_BATTERY_LEVEL = "Main Battery Level"
MAIN_BATTERY_LEVEL_F32 = "Main Battery Level (Precise)"
MAIN_BATTERY_CURRENT = "Main Battery Current"
TOTAL_IN_POWER = "Total In Power"
SOLAR_IN_POWER = "Solar In Power"
SOLAR_1_IN_POWER = "Solar (1) In Power"
SOLAR_2_IN_POWER = "Solar (2) In Power"
SOLAR_1_IN_VOLTS = "Solar (1) In Volts"
SOLAR_2_IN_VOLTS = "Solar (2) In Volts"
SOLAR_1_IN_AMPS = "Solar (1) In Amps"
SOLAR_2_IN_AMPS = "Solar (2) In Amps"
AC_IN_POWER = "AC In Power"
AC_IN_VOLT = "AC In Volts"
AC_OUT_VOLT = "AC Out Volts"

TYPE_C_IN_POWER = "Type-C In Power"
SOLAR_IN_CURRENT = "Solar In Current"
SOLAR_IN_VOLTAGE = "Solar In Voltage"
SOLAR_IN_ENERGY = "Solar In Energy"
CHARGE_AC_ENERGY = "Battery Charge Energy from AC"
CHARGE_DC_ENERGY = "Battery Charge Energy from DC"
DISCHARGE_AC_ENERGY = "Battery Discharge Energy to AC"
DISCHARGE_DC_ENERGY = "Battery Discharge Energy to DC"

TOTAL_OUT_POWER = "Total Out Power"
AC_OUT_POWER = "AC Out Power"
DC_OUT_POWER = "DC Out Power"
DC_OUT_VOLTAGE = "DC Out Voltage"
DC_CAR_OUT_POWER = "DC Car Out Power"
DC_ANDERSON_OUT_POWER = "DC Anderson Out Power"

TYPEC_OUT_POWER = "Type-C Out Power"
TYPEC_1_OUT_POWER = "Type-C (1) Out Power"
TYPEC_2_OUT_POWER = "Type-C (2) Out Power"
USB_OUT_POWER = "USB Out Power"
USB_1_OUT_POWER = "USB (1) Out Power"
USB_2_OUT_POWER = "USB (2) Out Power"
USB_3_OUT_POWER = "USB (3) Out Power"

USB_QC_1_OUT_POWER = "USB QC (1) Out Power"
USB_QC_2_OUT_POWER = "USB QC (2) Out Power"

REMAINING_TIME = "Remaining Time"
CHARGE_REMAINING_TIME = "Charge Remaining Time"
DISCHARGE_REMAINING_TIME = "Discharge Remaining Time"

CYCLES = "Cycles"
SOH = "State of Health"

SLAVE_BATTERY_LEVEL = "Slave Battery Level"
SLAVE_N_BATTERY_LEVEL = "Slave %i Battery Level"
SLAVE_N_BATTERY_LEVEL_F32 = "Slave %i Battery Level (Precise)"

SLAVE_BATTERY_TEMP = "Slave Battery Temperature"
SLAVE_N_BATTERY_TEMP = "Slave %i Battery Temperature"

SLAVE_MIN_CELL_TEMP = "Slave Min Cell Temperature"
SLAVE_MAX_CELL_TEMP = "Slave Max Cell Temperature"

SLAVE_N_MIN_CELL_TEMP = "Slave %i Min Cell Temperature"
SLAVE_N_MAX_CELL_TEMP = "Slave %i Max Cell Temperature"

SLAVE_CYCLES = "Slave Cycles"
SLAVE_N_CYCLES = "Slave %i Cycles"
SLAVE_SOH = "Slave State of Health"
SLAVE_N_SOH = "Slave %i State of Health"

SLAVE_IN_POWER = "Slave In Power"
SLAVE_N_IN_POWER = "Slave %i In Power"

SLAVE_OUT_POWER = "Slave Out Power"
SLAVE_N_OUT_POWER = "Slave %i Out Power"

SLAVE_BATTERY_VOLT = "Slave Battery Volts"
SLAVE_MIN_CELL_VOLT = "Slave Min Cell Volts"
SLAVE_MAX_CELL_VOLT = "Slave Max Cell Volts"

SLAVE_N_BATTERY_VOLT = "Slave %i Battery Volts"
SLAVE_N_MIN_CELL_VOLT = "Slave %i Min Cell Volts"
SLAVE_N_MAX_CELL_VOLT = "Slave %i Max Cell Volts"
SLAVE_N_BATTERY_CURRENT = "Slave %i Battery Current"
SLAVE_N_BATTERY_LEVEL_SOC = "Slave %i Battery level SOC"

MAX_CHARGE_LEVEL = "Max Charge Level"
MIN_DISCHARGE_LEVEL = "Min Discharge Level"
BACKUP_RESERVE_LEVEL = "Backup Reserve Level"
AC_CHARGING_POWER = "AC Charging Power"
SCREEN_TIMEOUT = "Screen Timeout"
UNIT_TIMEOUT = "Unit Timeout"
AC_TIMEOUT = "AC Timeout"
DC_TIMEOUT = "DC (12V) Timeout"
DC_CHARGE_CURRENT = "DC (12V) Charge Current"
GEN_AUTO_START_LEVEL = "Generator Auto Start Level"
GEN_AUTO_STOP_LEVEL = "Generator Auto Stop Level"

POWER = "Power"
CURRENT = "Current"
MAX_CURRENT = "Max Current"
MODE_ON = "On"
BRIGHTNESS = "Brightness"
BEEPER = "Beeper"
USB_ENABLED = "USB Enabled"
AC_ENABLED = "AC Enabled"
BYPASS_AC = "Bypass AC auto start"
DC_ENABLED = "DC (12V) Enabled"
XBOOST_ENABLED = "X-Boost Enabled"
AC_ALWAYS_ENABLED = "AC Always On"
PV_PRIO = "Prio Solar Charging"
BP_ENABLED = "Backup Reserve Enabled"
AUTO_FAN_SPEED = "Auto Fan Speed"
AC_SLOW_CHARGE = "AC Slow Charging"

DC_MODE = "DC Mode"

TEMPERATURE = "Temperature"
BATTERY_TEMP = "Battery Temperature"
MIN_CELL_TEMP = "Min Cell Temperature"
MAX_CELL_TEMP = "Max Cell Temperature"
INV_IN_TEMP = "Inverter Inside Temperature"
INV_OUT_TEMP = "Inverter Outside Temperature"
DC_CAR_OUT_TEMP = "DC Temperature"
USB_C_TEMP = "USB C Temperature"
ATTR_MIN_CELL_TEMP = MIN_CELL_TEMP
ATTR_MAX_CELL_TEMP = MAX_CELL_TEMP

VOLT = "Volts"
BATTERY_VOLT = "Battery Volts"
MIN_CELL_VOLT = "Min Cell Volts"
MAX_CELL_VOLT = "Max Cell Volts"
ATTR_MIN_CELL_VOLT = MIN_CELL_VOLT
ATTR_MAX_CELL_VOLT = MAX_CELL_VOLT

BATTERY_AMP = "Battery Current"
SLAVE_BATTERY_AMP = "Slave Battery Current"
BATTERY_LEVEL_SOC = "Battery level SOC"

FAN_MODE = "Wind speed"
MAIN_MODE = "Main mode"
REMOTE_MODE = "Remote startup/shutdown"
POWER_SUB_MODE = "Sub-mode"
