## DELTA_PRO_3

*Sensors*
- Main Battery Level (`bms_batt_soc`)
- Main Design Capacity (`bms_design_cap`)   _(disabled)_
- Main Full Capacity (`bms_full_cap_mah`)   _(disabled)_
- Main Remain Capacity (`bms_remain_cap_mah`)   _(disabled)_
- State of Health (`bms_batt_soh`)
- Cycles (`cycles`)
- Battery Volts (`bms_batt_vol`)   _(disabled)_
- Min Cell Volts (`bms_min_cell_vol`)   _(disabled)_
- Max Cell Volts (`bms_max_cell_vol`)   _(disabled)_
- Main Battery Current (`bms_batt_amp`)   _(disabled)_
- Max Cell Temperature (`bms_max_cell_temp`)   _(disabled)_
- Min Cell Temperature (`bms_min_cell_temp`)   _(disabled)_
- Battery Temperature (`bms_max_mos_temp`)
- Charge Remaining Time (`bms_chg_rem_time`)
- Discharge Remaining Time (`bms_dsg_rem_time`)
- Battery Level (`cms_batt_soc`)
- Total In Power (`pow_in_sum_w`)
- Total Out Power (`pow_out_sum_w`)
- AC In Power (`pow_get_ac_in`)
- AC Out Power (`pow_get_ac`)
- AC HV Output Power (`pow_get_ac_hv_out`)
- AC LV Output Power (`pow_get_ac_lv_out`)
- AC In Volts (`plug_in_info_ac_in_vol`)
- AC In Current (`plug_in_info_ac_in_amp`)
- 12V DC Output Power (`pow_get_12v`)
- 24V DC Output Power (`pow_get_24v`)
- 12V DC Output Voltage (`pow_get_12v_vol`)
- 24V DC Output Voltage (`pow_get_24v_vol`)
- Solar High Voltage Input Power (`pow_get_pv_h`)
- Solar Low Voltage Input Power (`pow_get_pv_l`)
- Solar HV Input Voltage (`pow_get_pv_h_vol`)
- Solar LV Input Voltage (`pow_get_pv_l_vol`)
- Solar HV Input Current (`pow_get_pv_h_amp`)
- Solar LV Input Current (`pow_get_pv_l_amp`)
- USB QC (1) Out Power (`pow_get_qcusb1`)
- USB QC (2) Out Power (`pow_get_qcusb2`)
- Type-C (1) Out Power (`pow_get_typec1`)
- Type-C (2) Out Power (`pow_get_typec2`)
- 5P8 Power I/O Port Power (`pow_get_5p8`)
- 4P8 Extra Battery Port 1 Power (`pow_get_4p8_1`)
- 4P8 Extra Battery Port 2 Power (`pow_get_4p8_2`)
- AC Output Frequency (`ac_out_freq`)
- Max Charge SOC Setting (`cms_max_chg_soc`)
- Min Discharge SOC Setting (`cms_min_dsg_soc`)
- Total Charge Energy (`accuChgEnergy`)
- Total Discharge Energy (`accuDsgEnergy`)
- Status

*Switches*
- Beeper (`en_beep` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 38, "enBeep": "VALUE"}}`)
- AC HV Output Enabled (`cfg_hv_ac_out_open` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 66, "cfgHvAcOutOpen": "VALUE"}}`)
- AC LV Output Enabled (`cfg_lv_ac_out_open` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 66, "cfgLvAcOutOpen": "VALUE"}}`)
- 12V DC Output Enabled (`cfg_dc_12v_out_open` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 81, "cfgDc12vOutOpen": "VALUE"}}`)
- 24V DC Output Enabled (`cfg_dc_24v_out_open` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 81, "cfgDc24vOutOpen": "VALUE"}}`)
- X-Boost Enabled (`xboost_en` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 66, "xboostEn": "VALUE"}}`)
- AC Energy Saving Enabled (`ac_energy_saving_open` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 95, "acEnergySavingOpen": "VALUE"}}`)
- GFCI Protection Enabled (`llc_gfci_flag` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 153, "llcGFCIFlag": "VALUE"}}`)

*Sliders (numbers)*
- Max Charge Level (`cms_max_chg_soc` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 49, "cmsMaxChgSoc": "VALUE"}}` [50 - 100])
- Min Discharge Level (`cms_min_dsg_soc` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 51, "cmsMinDsgSoc": "VALUE"}}` [0 - 30])
- AC Charging Power (`plug_in_info_ac_in_chg_pow_max` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 69, "plugInInfoAcInChgPowMax": "VALUE"}}` [200 - 3000])

*Selects*
- Screen Timeout (`screen_off_time` -> `{"moduleType": 0, "operateType": "TCP", "params": {"screenOffTime": "VALUE", "id": 39}}` [Never (0), 10 sec (10), 30 sec (30), 1 min (60), 5 min (300), 30 min (1800)])
- AC Timeout (`ac_standby_time` -> `{"moduleType": 0, "operateType": "TCP", "params": {"acStandbyTime": "VALUE", "id": 10}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])
- DC Timeout (`dc_standby_time` -> `{"moduleType": 0, "operateType": "TCP", "params": {"dcStandbyTime": "VALUE", "id": 33}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 6 hr (360), 12 hr (720)])
- AC Output Type (`plug_in_info_ac_out_type` -> `{"moduleType": 0, "operateType": "TCP", "params": {"plugInInfoAcOutType": "VALUE", "id": 59}}` [HV+LV (0), HV Only (1), LV Only (2)])


