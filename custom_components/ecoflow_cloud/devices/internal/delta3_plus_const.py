"""EcoFlow DELTA 3 Plus-specific constants."""

SOLAR_CAR_INPUT_1_POWER = "Solar/Car Input 1 Power"
SOLAR_CAR_INPUT_1_VOLTAGE = "Solar/Car Input 1 Voltage"
SOLAR_CAR_INPUT_1_CURRENT = "Solar/Car Input 1 Current"
SOLAR_CAR_INPUT_1_TEMP = "Solar/Car Input 1 Temperature"
SOLAR_CAR_INPUT_2_POWER = "Solar/Car Input 2 Power"
SOLAR_CAR_INPUT_2_VOLTAGE = "Solar/Car Input 2 Voltage"
SOLAR_CAR_INPUT_2_CURRENT = "Solar/Car Input 2 Current"
SOLAR_CAR_INPUT_2_TEMP = "Solar/Car Input 2 Temperature"

EXTRA_BATTERY_LEVEL = "Extra Battery Level"
EXTRA_BATTERY_IN_POWER = "Extra Battery Input Power"
EXTRA_BATTERY_OUT_POWER = "Extra Battery Output Power"
EXTRA_BATTERY_CHARGING_STATE_RAW = "Extra Battery Charging State (Raw)"
EXTRA_BATTERY_REMAIN_CAPACITY = "Extra Battery Remaining Capacity"
EXTRA_BATTERY_FULL_CAPACITY = "Extra Battery Full Capacity"
EXTRA_BATTERY_DESIGN_CAPACITY = "Extra Battery Design Capacity"
EXTRA_BATTERY_SOH = "Extra Battery State of Health"
EXTRA_BATTERY_CYCLES = "Extra Battery Cycles"
EXTRA_BATTERY_TEMP = "Extra Battery Temperature"
EXTRA_BATTERY_MIN_CELL_TEMP = "Extra Battery Minimum Cell Temperature"
EXTRA_BATTERY_MAX_CELL_TEMP = "Extra Battery Maximum Cell Temperature"
EXTRA_BATTERY_MIN_CELL_VOLT = "Extra Battery Minimum Cell Voltage"
EXTRA_BATTERY_MAX_CELL_VOLT = "Extra Battery Maximum Cell Voltage"
EXTRA_BATTERY_FIRMWARE_VERSION = "Extra Battery Firmware Version"

TYPEC_2_OUT_POWER = "Type-C (2) Out Power"
STORM_GUARD = "Storm Guard"

# Main battery and power telemetry.
MAIN_BATTERY_LEVEL = "Main Battery Level"
COMBINED_BATTERY_LEVEL = "Battery Level"
BATTERY_CHARGING_STATE = "Battery Charging State"
ATTR_DESIGN_CAPACITY = "Design Capacity (mAh)"
ATTR_FULL_CAPACITY = "Full Capacity (mAh)"
ATTR_REMAIN_CAPACITY = "Remain Capacity (mAh)"
MAIN_DESIGN_CAPACITY = "Main Design Capacity"
MAIN_FULL_CAPACITY = "Main Full Capacity"
MAIN_REMAIN_CAPACITY = "Main Remain Capacity"
SOH = "State of Health"
TOTAL_IN_POWER = "Total In Power"
TOTAL_OUT_POWER = "Total Out Power"
AC_IN_POWER = "AC In Power"
AC_OUT_POWER = "AC Out Power"
AC_IN_VOLT = "AC In Volts"
AC_OUT_VOLT = "AC Out Volts"
DC_OUT_POWER = "DC Out Power"
TYPEC_1_OUT_POWER = "Type-C (1) Out Power"
USB_QC_1_OUT_POWER = "USB QC (1) Out Power"
USB_QC_2_OUT_POWER = "USB QC (2) Out Power"
REMAINING_TIME = "Remaining Time"
CHARGE_REMAINING_TIME = "Charge Remaining Time"
DISCHARGE_REMAINING_TIME = "Discharge Remaining Time"
PCS_DC_TEMP = "PCS DC Temperature"
PCS_AC_TEMP = "PCS AC Temperature"
BATTERY_TEMP = "Battery Temperature"
MIN_CELL_TEMP = "Min Cell Temperature"
MAX_CELL_TEMP = "Max Cell Temperature"
BATTERY_VOLT = "Battery Volts"
MIN_CELL_VOLT = "Min Cell Volts"
MAX_CELL_VOLT = "Max Cell Volts"
CYCLES = "Cycles"

# Numbers, switches and selects.
MAX_CHARGE_LEVEL = "Max Charge Level"
MIN_DISCHARGE_LEVEL = "Min Discharge Level"
AC_CHARGING_POWER = "AC Charging Power"
BACKUP_RESERVE_LEVEL = "Backup Reserve Level"
BACKUP_RESERVE_SOC = "Backup Reserve SOC"
BEEPER = "Beeper"
AC_ENABLED = "AC Enabled"
XBOOST_ENABLED = "X-Boost Enabled"
DC_ENABLED = "DC (12V) Enabled"
USB_ENABLED = "USB Enabled"
AC_ALWAYS_ENABLED = "AC Always On"
BP_ENABLED = "Backup Reserve Enabled"
GRID_BYPASS = "Grid Bypass"
DC_CHARGE_CURRENT = "DC (12V) Charge Current"
ENERGY_STRATEGY = "Energy Strategy"
AC_CHARGE_MODE = "AC Charging Mode"
SCREEN_TIMEOUT = "Screen Timeout"
UNIT_TIMEOUT = "Unit Timeout"
AC_TIMEOUT = "AC Timeout"
DC_TIMEOUT = "DC (12V) Timeout"

DC_CHARGE_CURRENT_OPTIONS = {"4A": 4, "5A": 5, "6A": 6, "7A": 7, "8A": 8}
ENERGY_STRATEGY_OPTIONS = {"Standard": 0, "Self-Powered": 1, "Scheduled": 2, "TOU": 3}
AC_CHARGE_MODE_OPTIONS = {"Auto": 1, "Silent": 2, "Custom": 0}
SCREEN_TIMEOUT_OPTIONS = {"Never": 0, "10 sec": 10, "30 sec": 30, "1 min": 60, "5 min": 300, "30 min": 1800}
UNIT_TIMEOUT_OPTIONS = {
    "Never": 0,
    "30 min": 30,
    "1 hr": 60,
    "2 hr": 120,
    "4 hr": 240,
    "6 hr": 360,
    "12 hr": 720,
    "24 hr": 1440,
}
AC_TIMEOUT_OPTIONS = dict(UNIT_TIMEOUT_OPTIONS)
DC_TIMEOUT_OPTIONS = dict(UNIT_TIMEOUT_OPTIONS)
