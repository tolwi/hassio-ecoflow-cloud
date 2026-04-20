## GLACIER_CLASSIC

*Sensors*
- Main Battery Level (`bms_bmsStatus.soc`)
- Main Design Capacity (`bms_bmsStatus.designCap`)   _(disabled)_
- Main Full Capacity (`bms_bmsStatus.fullCap`)   _(disabled)_
- Main Remain Capacity (`bms_bmsStatus.remainCap`)   _(disabled)_
- Battery Level (`bms_emsStatus.f32LcdSoc`)
- Battery Charging State (`bms_emsStatus.chgState`)
- Total In Power (`bms_bmsStatus.inWatts`)
- Total Out Power (`bms_bmsStatus.outWatts`)
- Charge Remaining Time (`bms_emsStatus.chgRemain`)
- Discharge Remaining Time (`bms_emsStatus.dsgRemain`)
- Battery Remaining Time (`bms_bmsStatus.remainTime`)   _(disabled)_
- Cycles (`bms_bmsStatus.cycles`)
- Battery Temperature (`bms_bmsStatus.tmp`)
- Min MOS Temperature (`bms_bmsStatus.minMosTmp`)   _(disabled)_
- Max MOS Temperature (`bms_bmsStatus.maxMosTmp`)   _(disabled)_
- Left Temperature (`pd.tmpL`)   _(disabled)_
- Right Temperature (`pd.tmpR`)   _(disabled)_
- Combined Temperature (`pd.tmpM`)   _(disabled)_
- Battery Pack Temperature (`pd.batTemp`)   _(disabled)_
- Input Voltage (`pd.inputVolts`)   _(disabled)_
- Battery Volts (`bms_bmsStatus.vol`)   _(disabled)_
- Min Cell Volts (`bms_bmsStatus.minCellVol`)   _(disabled)_
- Max Cell Volts (`bms_bmsStatus.maxCellVol`)   _(disabled)_
- Battery Current (`bms_bmsStatus.amp`)   _(disabled)_
- Target Charge Current (`bms_bmsStatus.tagChgAmp`)   _(disabled)_
- Actual Battery SOC (`bms_bmsStatus.actSoc`)   _(disabled)_
- Battery SOC Delta (`bms_bmsStatus.diffSoc`)   _(disabled)_
- Target Battery SOC (`bms_bmsStatus.targetSoc`)   _(disabled)_
- Screen Off Time (`pd.blTime`)
- Device Standby Time (`pd.devStandbyTime`)   _(disabled)_
- Runtime Full Upload Period (`runtime.runtime_property_full_upload_period`)   _(disabled)_
- Runtime Incremental Upload Period (`runtime.runtime_property_incremental_upload_period`)   _(disabled)_
- Display Full Upload Period (`runtime.display_property_full_upload_period`)   _(disabled)_
- Display Incremental Upload Period (`runtime.display_property_incremental_upload_period`)   _(disabled)_
- BMS Fault Code (`diag.bmsFault`)   _(disabled)_
- BMS Error Code (`diag.bmsErrorCode`)   _(disabled)_
- PD Error Code (`diag.pdErrorCode`)   _(disabled)_
- All Error Code (`diag.allErrorCode`)   _(disabled)_
- All BMS Fault (`diag.allBmsFault`)   _(disabled)_
- BQ System Status Register (`diag.bqSysStatReg`)   _(disabled)_
- BMS Serial (`diag.bmsSn`)   _(disabled)_
- Main BMS Serial (`diag.bmsMainSn`)   _(disabled)_
- BMS Hardware Version (`diag.hwVer`)   _(disabled)_
- BMS Warning State (`diag.bmsWarningState`)   _(disabled)_
- Open BMS Index (`diag.openBmsIdx`)   _(disabled)_
- Max Available Modules (`diag.maxAvailableNum`)   _(disabled)_
- Temperature Unit (`pd.tmpUnit`)   _(disabled)_
- Temperature Unit Raw (`pd.tmpUnit`)   _(disabled)_
- Status
- Protobuf Debug (`debug.packet_ts`)   _(disabled)_

*Binary sensors*
- Dual Zone Mode (`pd.flagTwoZone`)
- Lid Status (`pd.lidStatus`)
- External Supply Connected (`pd.pvFlag`)

*Switches*
- Beeper (`pd.beepEn` -> `{"GlacierClassicSendHeaderMsg": {"msg": [{"pdata": {"GlacierClassicSetCommand": {"en_beep": 6666}}, "src": 32, "dest": 66, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 3, "need_ack": 1, "version": 19, "payload_ver": 1, "from": "Android", "device_sn": "SN"}]}}`)
- Eco Mode (`pd.coolMode` -> `{"GlacierClassicSendHeaderMsg": {"msg": [{"pdata": {"GlacierClassicSetCommand": {"cooling_mode": 6666}}, "src": 32, "dest": 66, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 4, "need_ack": 1, "version": 19, "payload_ver": 1, "from": "Android", "device_sn": "SN"}]}}`)
- Child Lock (`pd.childLock` -> `{"GlacierClassicSendHeaderMsg": {"msg": [{"pdata": {"GlacierClassicSetCommand": {"child_lock": 6666}}, "src": 32, "dest": 66, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 4, "need_ack": 1, "version": 19, "payload_ver": 1, "from": "Android", "device_sn": "SN"}]}}`)
- Simple Mode (`pd.simpleMode` -> `{"GlacierClassicSendHeaderMsg": {"msg": [{"pdata": {"GlacierClassicSetCommand": {"simple_mode": 6666}}, "src": 32, "dest": 66, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 4, "need_ack": 1, "version": 19, "payload_ver": 1, "from": "Android", "device_sn": "SN"}]}}`)
- Temperature Alert (`pd.tempAlert` -> `{"GlacierClassicSendHeaderMsg": {"msg": [{"pdata": {"GlacierClassicSetCommand": {"temp_alert": 6666}}, "src": 32, "dest": 66, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 4, "need_ack": 1, "version": 19, "payload_ver": 1, "from": "Android", "device_sn": "SN"}]}}`)

*Sliders (numbers)*
- Left Set Temperature (`pd.tmpLSet` -> `{"GlacierClassicSendHeaderMsg": {"msg": [{"pdata": {"GlacierClassicSetCommand": {"set_point_left": 6666.0}}, "src": 32, "dest": 66, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 6, "need_ack": 1, "version": 19, "payload_ver": 1, "from": "Android", "device_sn": "SN"}]}}` [-20 - 20])
- Right Set Temperature (`pd.tmpRSet` -> `{"GlacierClassicSendHeaderMsg": {"msg": [{"pdata": {"GlacierClassicSetCommand": {"set_point_right": 6666.0}}, "src": 32, "dest": 66, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 6, "need_ack": 1, "version": 19, "payload_ver": 1, "from": "Android", "device_sn": "SN"}]}}` [-20 - 20])
- Max Charge Level (`bms_emsStatus.maxChargeSoc` -> `{"GlacierClassicSendHeaderMsg": {"msg": [{"pdata": {"GlacierClassicSetCommand": {"cms_max_chg_soc": 6666}}, "src": 32, "dest": 66, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 4, "need_ack": 1, "version": 19, "payload_ver": 1, "from": "Android", "device_sn": "SN"}]}}` [50 - 100])
- Min Discharge Level (`bms_emsStatus.minDischargeSoc` -> `{"GlacierClassicSendHeaderMsg": {"msg": [{"pdata": {"GlacierClassicSetCommand": {"cms_min_dsg_soc": 6666}}, "src": 32, "dest": 66, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 4, "need_ack": 1, "version": 19, "payload_ver": 1, "from": "Android", "device_sn": "SN"}]}}` [0 - 50])

*Selects*
- Battery Protection (`pd.powerPbLevel` -> `{"GlacierClassicSendHeaderMsg": {"msg": [{"pdata": {"GlacierClassicSetCommand": {"bat_protect": 6666}}, "src": 32, "dest": 66, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 4, "need_ack": 1, "version": 19, "payload_ver": 1, "from": "Android", "device_sn": "SN"}]}}` [Off (0), Low (3), Medium (2), High (1)])
- Device Standby Time (`pd.devStandbyTime` -> `{"GlacierClassicSendHeaderMsg": {"msg": [{"pdata": {"GlacierClassicSetCommand": {"dev_standby_time": 6666}}, "src": 32, "dest": 66, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 3, "need_ack": 1, "version": 19, "payload_ver": 1, "from": "Android", "device_sn": "SN"}]}}` [30 min (1800), 1 hr (3600), 2 hr (7200), 4 hr (14400), 12 hr (43200), 24 hr (86400), Never (0)])


