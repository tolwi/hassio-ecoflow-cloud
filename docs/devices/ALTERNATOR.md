## ALTERNATOR

*Sensors*
- Alternator In Power (`254_21.alternatorPower`)
- Station Power (`254_21.stationPower`)
- Alternator Rated Power (`254_21.ratedPower`)   _(disabled)_
- Charging Power Limit (`254_21.permanentWatts`)   _(disabled)_
- Station Battery Charge (`254_21.batSoc`)
- Discharge Remaining Time (`254_21.chargeToFull268`)
- Charge Remaining Time (`254_21.unknown269`)
- Car Battery Voltage (`254_21.carBatVolt`)
- Alternator Temperature (`254_21.temp`)
- WiFi Signal Strength (`254_21.wifiRssi`)   _(disabled)_
- Alternator Status Code (`254_21.status1`)   _(disabled)_
- Operation Mode (`254_21.operationMode`)   _(disabled)_
- Charge Current Limit (`254_21.spChargerDevBattChgAmpLimit`)   _(disabled)_
- Reverse Charge Current Limit (`254_21.spChargerCarBattChgAmpLimit`)   _(disabled)_
- Charge Current Max (`254_21.spChargerDevBattChgAmpMax`)   _(disabled)_
- Reverse Charge Current Max (`254_21.spChargerCarBattChgAmpMax`)   _(disabled)_
- Status

*Switches*
- Charging Enabled (`254_21.startStop` -> `{"AlternatorMessage": {"msg": [{"pdata": {"AlternatorSet": {"start_stop": 6666}}, "src": 32, "dest": 20, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 4, "need_ack": 1, "version": 19, "payload_ver": 1, "from_": "HomeAssistant", "device_sn": "SN"}]}}`)

*Sliders (numbers)*
- Charge Current Limit (`254_21.spChargerDevBattChgAmpLimit` -> `{"AlternatorMessage": {"msg": [{"pdata": {"AlternatorSet": {"cfg_sp_charger_dev_batt_chg_amp_limit": 6666.0}}, "src": 32, "dest": 20, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 6, "need_ack": 1, "version": 19, "payload_ver": 1, "from_": "HomeAssistant", "device_sn": "SN"}]}}` [1 - 70])
- Reverse Charge Current Limit (`254_21.spChargerCarBattChgAmpLimit` -> `{"AlternatorMessage": {"msg": [{"pdata": {"AlternatorSet": {"cfg_sp_charger_car_batt_chg_amp_limit": 6666.0}}, "src": 32, "dest": 20, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 6, "need_ack": 1, "version": 19, "payload_ver": 1, "from_": "HomeAssistant", "device_sn": "SN"}]}}` [1 - 70])
- Car Battery Start Voltage (`254_21.startVoltage` -> `{"AlternatorMessage": {"msg": [{"pdata": {"AlternatorSet": {"start_voltage": 6666}}, "src": 32, "dest": 20, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 4, "need_ack": 1, "version": 19, "payload_ver": 1, "from_": "HomeAssistant", "device_sn": "SN"}]}}` [11 - 30])
- Extension Cable Length (`254_21.cableLength608` -> `{"AlternatorMessage": {"msg": [{"pdata": {"AlternatorSet": {"cable_length": 6666.0}}, "src": 32, "dest": 20, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 6, "need_ack": 1, "version": 19, "payload_ver": 1, "from_": "HomeAssistant", "device_sn": "SN"}]}}` [0 - 10])

*Selects*
- Operation Mode (`254_21.operationMode` -> `{"AlternatorMessage": {"msg": [{"pdata": {"AlternatorSet": {"operation_mode": 6666}}, "src": 32, "dest": 20, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 17, "data_len": 4, "need_ack": 1, "version": 19, "payload_ver": 1, "from_": "HomeAssistant", "device_sn": "SN"}]}}` [Charge (1), Battery Maintenance (2), Reverse Charge (3)])


