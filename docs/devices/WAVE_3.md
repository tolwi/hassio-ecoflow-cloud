## WAVE_3

*Sensors*
- Total In Power (`pow_in_sum_w`)
- Total Out Power (`pow_out_sum_w`)
- AC Out Power (`pow_get_ac`)
- AC In Power (`pow_get_ac_in`)
- DC Battery Power (`pow_get_bms`)
- Solar In Power (`pow_get_pv`)
- Self Consumption Power (`pow_get_self_consume`)   _(disabled)_
- Main Battery Level (`bms_batt_soc`)
- Water Level (`condensate_water_level`)
- Discharge Remaining Time (`bms_dsg_rem_time`)
- Charge Remaining Time (`bms_chg_rem_time`)
- Power Off Delay Remaining (`power_off_delay_remaining`)
- Ambient Temperature (`temp_ambient`)
- Indoor Supply Air Temp (`temp_indoor_supply_air`)   _(disabled)_
- Condenser Temp (`temp_condenser`)   _(disabled)_
- Evaporator Temp (`temp_evaporator`)   _(disabled)_
- BMS Error Code (`bms_err_code`)   _(disabled)_

*Switches*
- Beeper (`en_beep` -> `{"Wave3SetMessage": {"header": {"pdata": {"Wave3ConfigWrite": {"enBeep": 0}}, "src": 32, "dest": 66, "d_src": 1, "d_dest": 1, "enc_type": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 2, "need_ack": 1, "version": 3, "payload_ver": 1, "is_rw_cmd": 1, "from": "Android", "device_sn": "SN"}}}`)
- Auto Drain (`drainage_mode` -> `{"Wave3SetMessage": {"header": {"pdata": {"Wave3ConfigWrite": {"cfg_drainage_mode": 1}}, "src": 32, "dest": 66, "d_src": 1, "d_dest": 1, "enc_type": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 3, "need_ack": 1, "version": 3, "payload_ver": 1, "is_rw_cmd": 1, "from": "Android", "device_sn": "SN"}}}`)

*Sliders (numbers)*
- Screen Brightness (`lcd_light` -> `{"Wave3SetMessage": {"header": {"pdata": {"Wave3ConfigWrite": {"lcdLight": 6666}}, "src": 32, "dest": 66, "d_src": 1, "d_dest": 1, "enc_type": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 3, "need_ack": 1, "version": 3, "payload_ver": 1, "is_rw_cmd": 1, "from": "Android", "device_sn": "SN"}}}` [0 - 100])

*Selects*
- Screen Timeout (`screen_off_time` -> `{"Wave3SetMessage": {"header": {"pdata": {"Wave3ConfigWrite": {"screenOffTime": 6666}}, "src": 32, "dest": 66, "d_src": 1, "d_dest": 1, "enc_type": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 3, "need_ack": 1, "version": 3, "payload_ver": 1, "is_rw_cmd": 1, "from": "Android", "device_sn": "SN"}}}` [Nie (0), 10 s (10), 30 s (30), 1 min (60), 5 min (300), 10 min (600)])
- Unit Timeout (`dev_standby_time` -> `{"Wave3SetMessage": {"header": {"pdata": {"Wave3ConfigWrite": {"devStandbyTime": 6666}}, "src": 32, "dest": 66, "d_src": 1, "d_dest": 1, "enc_type": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 3, "need_ack": 1, "version": 3, "payload_ver": 1, "is_rw_cmd": 1, "from": "Android", "device_sn": "SN"}}}` [Nie (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])
- Auto-Off Timeout (`power_off_delay_set` -> `{"Wave3SetMessage": {"header": {"pdata": {"Wave3ConfigWrite": {"cfg_power_off_delay_set": 6666}}, "src": 32, "dest": 66, "d_src": 1, "d_dest": 1, "enc_type": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 4, "need_ack": 1, "version": 3, "payload_ver": 1, "is_rw_cmd": 1, "from": "Android", "device_sn": "SN"}}}` [Nie (0), 30 min (30), 1 hr (60), 2 hr (120), 3 hr (180), 4 hr (240), 6 hr (360), 8 hr (480), 12 hr (720), 24 hr (1440)])


