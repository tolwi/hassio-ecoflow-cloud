DC_IMPUTS = {
    "Auto": 0,
    "Solar": 1,
    "Car": 2,
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
    "4 hr": 240,
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

DC_CHARGE_CURRENT_OPTIONS = {
    "4A": 4000,
    "6A": 6000,
    "8A": 8000
}

COMBINED_BATTERY_LEVEL = "Battery Level"

MAIN_BATTERY_LEVEL = "Main Battery Level"
TOTAL_IN_POWER = "Total In Power"
SOLAR_IN_POWER = "Solar In Power"
AC_IN_POWER = "AC In Power"
TYPE_C_IN_POWER = "Type-C In Power"

TOTAL_OUT_POWER = "Total Out Power"
AC_OUT_POWER = "AC Out Power"
DC_OUT_POWER = "DC Out Power"
DC_CAR_OUT_POWER = "DC Car Out Power"
DC_ANDERSON_OUT_POWER = "DC Anderson Out Power"

TYPEC_OUT_POWER = "Type-C Out Power"
TYPEC_1_OUT_POWER = "Type-C (1) Out Power"
TYPEC_2_OUT_POWER = "Type-C (2) Out Power"
USB_1_OUT_POWER = "USB (1) Out Power"
USB_2_OUT_POWER = "USB (2) Out Power"
USB_3_OUT_POWER = "USB (3) Out Power"

USB_QC_1_OUT_POWER = "USB QC (1) Out Power"
USB_QC_2_OUT_POWER = "USB QC (2) Out Power"


REMAINING_TIME = "Remaining Time"
CHARGE_REMAINING_TIME = "Charge Remaining Time"
DISCHARGE_REMAINING_TIME = "Discharge Remaining Time"

BATTERY_TEMP = "Battery Temperature"
CYCLES = "Cycles"

SLAVE_BATTERY_LEVEL = "Slave Battery Level"
SLAVE_BATTERY_TEMP = "Slave Battery Temperature"
SLAVE_CYCLES = "Slave Cycles"
SLAVE_IN_POWER = "Slave In Power"
SLAVE_OUT_POWER = "Slave Out Power"

MAX_CHARGE_LEVEL = "Max Charge Level"
MIN_DISCHARGE_LEVEL = "Min Discharge Level"
AC_CHARGING_POWER = "AC Charging Power"
SCREEN_TIMEOUT = "Screen Timeout"
UNIT_TIMEOUT = "Unit Timeout"
AC_TIMEOUT = "AC Timeout"
DC_TIMEOUT = "DC (12V) Timeout"
DC_CHARGE_CURRENT = "DC (12V) Charge Current"
GEN_AUTO_START_LEVEL = "Generator Auto Start Level"
GEN_AUTO_STOP_LEVEL = "Generator Auto Stop Level"

BEEPER = "Beeper"
USB_ENABLED = "USB Enabled"
AC_ENABLED = "AC Enabled"
DC_ENABLED = "DC (12V) Enabled"
XBOOST_ENABLED = "X-Boost Enabled"
AC_ALWAYS_ENABLED = "AC Always On"
PV_PRIO = "Prio Solar Charging"

