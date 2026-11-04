## SMART_GATEWAY

*Sensors*
- Battery Level (`cms_batt_soc`)
- Home Load Power (`shp_load_pwr`) (energy:  _[Device Name]_ Home Load Energy)
- Grid Power (`shp_grid_pwr`) (energy:  _[Device Name]_ Grid Energy)
- Storage Output Power (`shp_batt_pwr`)
- Status
- Grid L1 Power (`shp_grid_l1_pwr`)   _(disabled)_
- Grid L2 Power (`shp_grid_l2_pwr`)   _(disabled)_
- Grid L1 Voltage (`shp_l1_vol`)   _(disabled)_
- Grid L2 Voltage (`shp_l2_vol`)   _(disabled)_
- Grid L1 Current (`shp_grid_l1_amp`)   _(disabled)_
- Grid L2 Current (`shp_grid_l2_amp`)   _(disabled)_
- Circuit 1 Power (`ch_1_pwr`) (energy:  _[Device Name]_ Circuit 1 Energy)
- Circuit 1 Voltage (`ch_1_vol`)   _(disabled)_
- Circuit 1 Current (`ch_1_amp`)   _(disabled)_
- Circuit 2 Power (`ch_2_pwr`) (energy:  _[Device Name]_ Circuit 2 Energy)
- Circuit 2 Voltage (`ch_2_vol`)   _(disabled)_
- Circuit 2 Current (`ch_2_amp`)   _(disabled)_
- Circuit 3 Power (`ch_3_pwr`) (energy:  _[Device Name]_ Circuit 3 Energy)
- Circuit 3 Voltage (`ch_3_vol`)   _(disabled)_
- Circuit 3 Current (`ch_3_amp`)   _(disabled)_
- Circuit 4 Power (`ch_4_pwr`) (energy:  _[Device Name]_ Circuit 4 Energy)
- Circuit 4 Voltage (`ch_4_vol`)   _(disabled)_
- Circuit 4 Current (`ch_4_amp`)   _(disabled)_
- Circuit 5 Power (`ch_5_pwr`) (energy:  _[Device Name]_ Circuit 5 Energy)
- Circuit 5 Voltage (`ch_5_vol`)   _(disabled)_
- Circuit 5 Current (`ch_5_amp`)   _(disabled)_
- Circuit 6 Power (`ch_6_pwr`) (energy:  _[Device Name]_ Circuit 6 Energy)
- Circuit 6 Voltage (`ch_6_vol`)   _(disabled)_
- Circuit 6 Current (`ch_6_amp`)   _(disabled)_
- Circuit 7 Power (`ch_7_pwr`) (energy:  _[Device Name]_ Circuit 7 Energy)
- Circuit 7 Voltage (`ch_7_vol`)   _(disabled)_
- Circuit 7 Current (`ch_7_amp`)   _(disabled)_
- Circuit 8 Power (`ch_8_pwr`) (energy:  _[Device Name]_ Circuit 8 Energy)
- Circuit 8 Voltage (`ch_8_vol`)   _(disabled)_
- Circuit 8 Current (`ch_8_amp`)   _(disabled)_
- Grid Import Power (`shp_grid_in_pwr`) (energy:  _[Device Name]_ Grid Import Energy)
- Grid Export Power (`shp_grid_out_pwr`) (energy:  _[Device Name]_ Grid Export Energy)
- Battery Charge Power (`shp_batt_chg_pwr`) (energy:  _[Device Name]_ Battery Charge Energy)
- Battery Discharge Power (`shp_batt_dsg_pwr`) (energy:  _[Device Name]_ Battery Discharge Energy)
- Battery Charging State (`cms_chg_dsg_state`)
- Discharge Remaining Time (`cms_dsg_rem_time`)
- Charge Remaining Time (`cms_chg_rem_time`)
- Target Charge Level (`shp_target_soc`)
- Active Scheduled Task (`current_time_task_v2_item_task_type`)
- Panel L1 Voltage (`shp_panel_l1_vol`)   _(disabled)_
- Panel L2 Voltage (`shp_panel_l2_vol`)   _(disabled)_
- Circuit 1 Breaker State (`ch_1_state`)
- Circuit 2 Breaker State (`ch_2_state`)
- Circuit 3 Breaker State (`ch_3_state`)
- Circuit 4 Breaker State (`ch_4_state`)
- Circuit 5 Breaker State (`ch_5_state`)
- Circuit 6 Breaker State (`ch_6_state`)

*Switches*
- EPS Mode (`shp_eps_mode`)
- Storm Guard (`shp_storm_guard`)
- Emergency Charge (`shp_force_charge`)

*Selects*
- Operating Mode (`shp_operating_mode` [Self-Powered (1), Scheduled Tasks (2), Custom (5), AI Mode (6)])

*Sliders (numbers)*
- Backup Reserve Level (`shp_backup_reserve_soc` [10 - 50])
- Max Charge Level (`cms_max_chg_soc` [50 - 100])
- Max Charge Rate (`shp_max_chg_pwr` [500 - 10000])
- Generator Charge Rate (`shp_gen_chg_pwr` [500 - 10000])
