FREQS = {
    "50Hz": 1,
    "60Hz": 2,
}

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
    "10sec": 10,
    "30sec": 30,
    "1min": 60,
    "5min": 300,
    "30min": 1800,
}

UNIT_TIMEOUT_OPTIONS = {
    "Never": 0,
    "30min": 30,
    "1hour": 60,
    "2hour": 120,
    "6hour": 360,
    "12hour": 720,
}

AC_TIMEOUT_OPTIONS = {
    "Never": 0,
    "2hour": 120,
    "4hour": 240,
    "6hour": 360,
    "12hour": 720,
    "24hour": 1440,
}

DC_TIMEOUT_OPTIONS = {
    "Never": 0,
    "2hour": 120,
    "4hour": 240,
    "6hour": 360,
    "12hour": 720,
    "24hour": 1440,
}

DC_CHARGE_CURRENT_OPTIONS = {
    "4A": 4000,
    "6A": 6000,
    "8A": 8000
}

MAIN_BATTERY_LEVEL = "Main Battery Level"
TOTAL_IN_POWER = "Total In Power"
TOTAL_OUT_POWER = "Total Out Power"
CHARGE_REMAINING_TIME = "Charge Remaining Time"
DISCHARGE_REMAINING_TIME = "Discharge Remaining Time"

BATTERY_TEMP = "Battery Temperature"
CYCLES = "Cycles"

SLAVE_BATTERY_LEVEL = "Slave Battery Level"
SLAVE_BATTERY_TEMP = "Slave Battery Temperature"
SLAVE_CYCLES = "Slave Cycles"

MAX_CHARGE_LEVEL = "Max Charge Level"
MIN_DISCHARGE_LEVEL = "Min Discharge Level"
AC_CHARGING_POWER = "AC Charging Power"
SCREEN_TIMEOUT = "Screen Timeout"
UNIT_TIMEOUT = "Unit Timeout"
AC_TIMEOUT = "AC Timeout"
DC_TIMEOUT = "DC (12V) Timeout"
DC_CHARGE_CURRENT = "DC (12V) Charge Current"

BEEPER = "Beeper"
USB_ENABLED = "USB Enabled"
AC_ENABLED = "AC Enabled"
DC_ENABLED = "DC (12V) Enabled"
XBOOST_ENABLED = "X-Boost Enabled"
AC_ALWAYS_ENABLED = "AC Always On"


