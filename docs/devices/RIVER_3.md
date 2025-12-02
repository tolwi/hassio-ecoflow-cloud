## RIVER_3

*Sensors*
- Main Battery Level (`bms_batt_soc`, field 242, DisplayPropertyUpload)
- Main Design Capacity (`bms_design_cap`, field 248, DisplayPropertyUpload)   _(disabled)_
- Main Full Capacity (`bms_full_cap`, field 247, RuntimePropertyUpload)   _(disabled)_
- Main Remain Capacity (`bms_remain_cap`, field 249, RuntimePropertyUpload)   _(disabled)_
- State of Health (`bms_batt_soh`, field 243, DisplayPropertyUpload)
- Battery Level (`cms_batt_soc`, field 262, DisplayPropertyUpload)
- Battery Charging State (`bms_chg_dsg_state`, field 281, DisplayPropertyUpload)
- Total In Power (`pow_in_sum_w`, field 3, DisplayPropertyUpload) (energy:  _[Device Name]_ Total In  Energy)
- Total Out Power (`pow_out_sum_w`, field 4, DisplayPropertyUpload) (energy:  _[Device Name]_ Total Out  Energy)
- Solar In Power (`pow_get_pv`, field 361, DisplayPropertyUpload)
- Solar In Current (`plug_in_info_pv_amp`, field 381, RuntimePropertyUpload)
- AC In Power (`pow_get_ac_in`, field 54, DisplayPropertyUpload)
- AC Out Power (`pow_get_ac_out`, field 368, DisplayPropertyUpload)
- AC In Volts (`plug_in_info_ac_in_vol`, field 68, RuntimePropertyUpload)
- DC Out Power (`pow_get_12v`, field 37, DisplayPropertyUpload)
- Type-C (1) Out Power (`pow_get_typec1`, field 11, DisplayPropertyUpload)
- USB QC (1) Out Power (`pow_get_qcusb1`, field 9, DisplayPropertyUpload)
- USB QC (2) Out Power (`pow_get_qcusb2`, field 10, DisplayPropertyUpload)
- Charge Remaining Time (`bms_chg_rem_time`, field 255, DisplayPropertyUpload)
- Discharge Remaining Time (`bms_dsg_rem_time`, field 254, DisplayPropertyUpload)
- Remaining Time (`cms_chg_rem_time`, field 269, DisplayPropertyUpload)
- PCS DC Temperature (`temp_pcs_dc`, field 26, RuntimePropertyUpload)
- PCS AC Temperature (`temp_pcs_ac`, field 27, RuntimePropertyUpload)
- Battery Temperature (`bms_min_cell_temp`, field 258, DisplayPropertyUpload)
- Max Cell Temperature (`bms_max_cell_temp`, field 259, DisplayPropertyUpload)   _(disabled)_
- Battery Volts (`bms_batt_vol`, field 244, RuntimePropertyUpload)   _(disabled)_
- Min Cell Volts (`bms_min_cell_vol`, field 256, RuntimePropertyUpload)   _(disabled)_
- Max Cell Volts (`bms_max_cell_vol`, field 257, RuntimePropertyUpload)   _(disabled)_
- Cycles (`cycles`, field 14, BMSHeartBeatReport)
- AC Output Energy (`ac_out_energy`, field 2, StatisticsObject.AC_OUT_ENERGY)
- AC Input Energy (`ac_in_energy`, field 6, StatisticsObject.AC_IN_ENERGY)
- Solar In Energy (`pv_in_energy`, field 7, StatisticsObject.PV_IN_ENERGY)
- DC 12V Output Energy (`dc12v_out_energy`, field 3, StatisticsObject.DC12V_OUT_ENERGY)   _(disabled)_
- Type-C Output Energy (`typec_out_energy`, field 4, StatisticsObject.TYPEC_OUT_ENERGY)   _(disabled)_
- USB-A Output Energy (`usba_out_energy`, field 5, StatisticsObject.USBA_OUT_ENERGY)   _(disabled)_
- Status

*Switches*
- Beeper (`en_beep`, field 9, SetCommand)
- AC Enabled (`cfg_ac_out_open`, field 76, SetCommand)
- X-Boost Enabled (`xboost_en`, field 25, SetCommand)
- DC (12V) Enabled (`cfg_dc12v_out_open`, field 18, SetCommand)
- AC Always On (`output_power_off_memory`, field 141, SetCommand)
- Backup Reserve Enabled (`energy_backup_en`, field 1 in cfg_energy_backup, SetCommand)

*Sliders (numbers)*
- Max Charge Level (`cms_max_chg_soc`, field 33, SetCommand [50 - 100])
- Min Discharge Level (`cms_min_dsg_soc`, field 34, SetCommand [0 - 30])
- AC Charging Power (`plug_in_info_ac_in_chg_pow_max`, field 54, SetCommand [50 - 305])
- Backup Reserve Level (`energy_backup_start_soc`, field 2 in cfg_energy_backup, SetCommand [5 - 100])

*Selects*
- DC (12V) Charge Current (`plug_in_info_pv_dc_amp_max`, field 87, SetCommand [4A (4), 6A (6), 8A (8)])
- DC Mode (`pv_chg_type`, field 90, SetCommand [Auto (0), Solar Recharging (1), Car Recharging (2)])
- Screen Timeout (`screen_off_time`, field 12, SetCommand [Never (0), 10 sec (10), 30 sec (30), 1 min (60), 5 min (300), 30 min (1800)])
- Unit Timeout (`dev_standby_time`, field 13, SetCommand [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])
- AC Timeout (`ac_standby_time`, field 10, SetCommand [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])

