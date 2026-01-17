## DELTA_3

*Sensors*
- Main Battery Level (`bms_batt_soc`)
- Main Design Capacity (`bms_design_cap`)   _(disabled)_
- Main Full Capacity (`bms_full_cap`)   _(disabled)_
- Main Remain Capacity (`bms_remain_cap`)   _(disabled)_
- State of Health (`bms_batt_soh`)
- Battery Level (`cms_batt_soc`)
- Battery Charging State (`bms_chg_dsg_state`)
- Total In Power (`pow_in_sum_w`) (energy:  _[Device Name]_ Total In  Energy)
- Total Out Power (`pow_out_sum_w`) (energy:  _[Device Name]_ Total Out  Energy)
- Solar In Power (`pow_get_pv`)
- Solar In Current (`plug_in_info_pv_amp`)
- AC In Power (`pow_get_ac_in`)
- AC Out Power (`pow_get_ac_out`)
- AC In Volts (`plug_in_info_ac_in_vol`)
- AC Out Volts (`plug_in_info_ac_out_vol`)
- DC Out Power (`pow_get_12v`)
- Type-C (1) Out Power (`pow_get_typec1`)
- USB QC (1) Out Power (`pow_get_qcusb1`)
- USB QC (2) Out Power (`pow_get_qcusb2`)
- Charge Remaining Time (`bms_chg_rem_time`)
- Discharge Remaining Time (`bms_dsg_rem_time`)
- Remaining Time (`cms_chg_rem_time`)
- PCS DC Temperature (`temp_pcs_dc`)
- PCS AC Temperature (`temp_pcs_ac`)
- Battery Temperature (`bms_min_cell_temp`)
- Max Cell Temperature (`bms_max_cell_temp`)   _(disabled)_
- Battery Volts (`bms_batt_vol`)   _(disabled)_
- Min Cell Volts (`bms_min_cell_vol`)   _(disabled)_
- Max Cell Volts (`bms_max_cell_vol`)   _(disabled)_
- Cycles (`cycles`)
- Solar In Energy (`pv_in_energy`)
- Status

*Switches*
- Beeper (`en_beep` -> `{"Delta3SendHeaderMsg": {"msg": [{"pdata": {"Delta3SetCommand": {"en_beep": 1}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "cmd_func": 254, "cmd_id": 17, "data_len": 2, "need_ack": 1, "product_id": 1, "version": 19, "payload_ver": 1, "device_sn": "SN"}]}}`)
- AC Enabled (`cfg_ac_out_open` -> `{"Delta3SendHeaderMsg": {"msg": [{"pdata": {"Delta3SetCommand": {"cfg_ac_out_open": 1}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "cmd_func": 254, "cmd_id": 17, "data_len": 3, "need_ack": 1, "product_id": 1, "version": 19, "payload_ver": 1, "device_sn": "SN"}]}}`)
- X-Boost Enabled (`xboost_en` -> `{"Delta3SendHeaderMsg": {"msg": [{"pdata": {"Delta3SetCommand": {"xboost_en": 1}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "cmd_func": 254, "cmd_id": 17, "data_len": 3, "need_ack": 1, "product_id": 1, "version": 19, "payload_ver": 1, "device_sn": "SN"}]}}`)
- DC (12V) Enabled (`cfg_dc12v_out_open` -> `{"Delta3SendHeaderMsg": {"msg": [{"pdata": {"Delta3SetCommand": {"cfg_dc12v_out_open": 1}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "cmd_func": 254, "cmd_id": 17, "data_len": 3, "need_ack": 1, "product_id": 1, "version": 19, "payload_ver": 1, "device_sn": "SN"}]}}`)
- AC Always On (`output_power_off_memory` -> `{"Delta3SendHeaderMsg": {"msg": [{"pdata": {"Delta3SetCommand": {"output_power_off_memory": 1}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "cmd_func": 254, "cmd_id": 17, "data_len": 3, "need_ack": 1, "product_id": 1, "version": 19, "payload_ver": 1, "device_sn": "SN"}]}}`)
- Backup Reserve Enabled (`energy_backup_en` -> `{"Delta3SendHeaderMsg": {"msg": [{"pdata": {"Delta3SetCommand": {"cfg_energy_backup": {"energy_backup_en": 1, "energy_backup_start_soc": 5}}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "cmd_func": 254, "cmd_id": 17, "data_len": 7, "need_ack": 1, "product_id": 1, "version": 19, "payload_ver": 1, "device_sn": "SN"}]}}`)

*Sliders (numbers)*
- Max Charge Level (`cms_max_chg_soc` -> `{"Delta3SendHeaderMsg": {"msg": [{"pdata": {"Delta3SetCommand": {"cms_max_chg_soc": 6666}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "cmd_func": 254, "cmd_id": 17, "data_len": 4, "need_ack": 1, "product_id": 1, "version": 19, "payload_ver": 1, "device_sn": "SN"}]}}` [50 - 100])
- Min Discharge Level (`cms_min_dsg_soc` -> `{"Delta3SendHeaderMsg": {"msg": [{"pdata": {"Delta3SetCommand": {"cms_min_dsg_soc": 6666}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "cmd_func": 254, "cmd_id": 17, "data_len": 4, "need_ack": 1, "product_id": 1, "version": 19, "payload_ver": 1, "device_sn": "SN"}]}}` [0 - 30])
- AC Charging Power (`plug_in_info_ac_in_chg_pow_max` -> `{"Delta3SendHeaderMsg": {"msg": [{"pdata": {"Delta3SetCommand": {"plug_in_info_ac_in_chg_pow_max": 6666}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "cmd_func": 254, "cmd_id": 17, "data_len": 4, "need_ack": 1, "product_id": 1, "version": 19, "payload_ver": 1, "device_sn": "SN"}]}}` [50 - 305])
- Backup Reserve Level (`energy_backup_start_soc` -> `{"Delta3SendHeaderMsg": {"msg": [{"pdata": {"Delta3SetCommand": {"cfg_energy_backup": {"energy_backup_en": 1, "energy_backup_start_soc": 6666}}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "cmd_func": 254, "cmd_id": 17, "data_len": 8, "need_ack": 1, "product_id": 1, "version": 19, "payload_ver": 1, "device_sn": "SN"}]}}` [5 - 100])

*Selects*
- DC (12V) Charge Current (`plug_in_info_pv_dc_amp_max` -> `{"Delta3SendHeaderMsg": {"msg": [{"pdata": {"Delta3SetCommand": {"plug_in_info_pv_dc_amp_max": 6666}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "cmd_func": 254, "cmd_id": 17, "data_len": 4, "need_ack": 1, "product_id": 1, "version": 19, "payload_ver": 1, "device_sn": "SN"}]}}` [4A (4), 5A (5), 6A (6), 7A (7), 8A (8)])
- Screen Timeout (`screen_off_time` -> `{"Delta3SendHeaderMsg": {"msg": [{"pdata": {"Delta3SetCommand": {"screen_off_time": 6666}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "cmd_func": 254, "cmd_id": 17, "data_len": 3, "need_ack": 1, "product_id": 1, "version": 19, "payload_ver": 1, "device_sn": "SN"}]}}` [Never (0), 10 sec (10), 30 sec (30), 1 min (60), 5 min (300), 30 min (1800)])
- Unit Timeout (`dev_standby_time` -> `{"Delta3SendHeaderMsg": {"msg": [{"pdata": {"Delta3SetCommand": {"dev_standby_time": 6666}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "cmd_func": 254, "cmd_id": 17, "data_len": 3, "need_ack": 1, "product_id": 1, "version": 19, "payload_ver": 1, "device_sn": "SN"}]}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])
- AC Timeout (`ac_standby_time` -> `{"Delta3SendHeaderMsg": {"msg": [{"pdata": {"Delta3SetCommand": {"ac_standby_time": 6666}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "cmd_func": 254, "cmd_id": 17, "data_len": 3, "need_ack": 1, "product_id": 1, "version": 19, "payload_ver": 1, "device_sn": "SN"}]}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])
- DC (12V) Timeout (`dc_standby_time` -> `{"Delta3SendHeaderMsg": {"msg": [{"pdata": {"Delta3SetCommand": {"dc_standby_time": 6666}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "cmd_func": 254, "cmd_id": 17, "data_len": 3, "need_ack": 1, "product_id": 1, "version": 19, "payload_ver": 1, "device_sn": "SN"}]}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])


