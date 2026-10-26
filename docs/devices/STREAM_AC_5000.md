## STREAM_AC_5000

*Sensors*
- Battery Level (`soc`)
- Power Battery SOC (`f32ShowSoc`)   _(disabled)_
- Battery Level (BMS) (`bmsBattSoc`)   _(disabled)_
- Battery Level (pack) (`packSoc`)   _(disabled)_
- Stored Energy (`storedEnergy_cmsBattFullEnergy`)
- Remaining Time (`remainTime`)
- Charge Remaining Time (`bmsChgRemTime`)   _(disabled)_
- Discharge Remaining Time (`bmsDsgRemTime`)   _(disabled)_
- Grid Port Power (`gridPortPower`)
- Battery Power (`bpPower`)
- Charge Power Limit (`maxChgPow`)   _(disabled)_
- Max Discharge Power (`maxDsgPow`)   _(disabled)_
- Feed-in Power Max (`feedGridModePowMax`)   _(disabled)_
- Power Grid Global (`meterTotalPower`)
- Power Grid L1 (`meterPhaseAPower`)
- Power Grid L2 (`meterPhaseBPower`)
- Power Grid L3 (`meterPhaseCPower`)
- Power Grid (L1) Volts (`meterPhaseAVol`)   _(disabled)_
- Power Grid (L2) Volts (`meterPhaseBVol`)   _(disabled)_
- Power Grid (L3) Volts (`meterPhaseCVol`)   _(disabled)_
- Power Grid Frequency (`meterFreq`)   _(disabled)_
- Min Cell Volts (`minCellVol`)   _(disabled)_
- Max Cell Volts (`maxCellVol`)   _(disabled)_
- Real State of Health (`realSoh`)   _(disabled)_
- State of Health (`cycleSoh`)   _(disabled)_
- Cumulative Capacity Charge (mAh) (`accuChgCap`)   _(disabled)_
- Cumulative Capacity Discharge (mAh) (`accuDsgCap`)   _(disabled)_
- Cumulative Energy Charge (Wh) (`accuChgEnergy`)
- Cumulative Energy Discharge (Wh) (`accuDsgEnergy`)
- Status

*Binary sensors*
- P1 Meter Link (`meterLinkUp`)

*Switches*
- AC Output (`acOutEnabled` -> `{"StreamAC5000SendCommandMsg": {"msg": {"pdata": {"StreamAC5000SetCommand": {"propertyId": 19, "acOut": {"enabled": 6666}}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 38, "data_len": 8, "need_ack": 1, "version": 4, "from_": "HomeAssistant", "device_sn": "SN", "device_sn_2": "SN", "device_sn_3": "SN"}}}`)
- X-Boost (`xboostEnabled` -> `{"StreamAC5000SendCommandMsg": {"msg": {"pdata": {"StreamAC5000SetCommand": {"propertyId": 23, "deviceCfg": {"xboostEnabled": 6666}}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 38, "data_len": 8, "need_ack": 1, "version": 4, "from_": "HomeAssistant", "device_sn": "SN", "device_sn_2": "SN", "device_sn_3": "SN"}}}`)
- UPS Mode (`upsEnabled` -> `{"StreamAC5000SendCommandMsg": {"msg": {"pdata": {"StreamAC5000SetCommand": {"propertyId": 23, "deviceCfg": {"upsEnabled": 6666}}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 38, "data_len": 8, "need_ack": 1, "version": 4, "from_": "HomeAssistant", "device_sn": "SN", "device_sn_2": "SN", "device_sn_3": "SN"}}}`)

*Sliders (numbers)*
- Max Charge Level (`cmsMaxChgSoc` -> `{"StreamAC5000SendCommandMsg": {"msg": {"pdata": {"StreamAC5000SetCommand": {"propertyId": 29, "socLimits": {"cmsMaxChgSoc": 6666, "cmsMinDsgSoc": 5}}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 38, "data_len": 10, "need_ack": 1, "version": 4, "from_": "HomeAssistant", "device_sn": "SN", "device_sn_2": "SN", "device_sn_3": "SN"}}}` [50 - 100])
- Min Discharge Level (`cmsMinDsgSoc` -> `{"StreamAC5000SendCommandMsg": {"msg": {"pdata": {"StreamAC5000SetCommand": {"propertyId": 29, "socLimits": {"cmsMaxChgSoc": 100, "cmsMinDsgSoc": 6666}}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 38, "data_len": 10, "need_ack": 1, "version": 4, "from_": "HomeAssistant", "device_sn": "SN", "device_sn_2": "SN", "device_sn_3": "SN"}}}` [0 - 30])
- Net Power Out Limit (`feedGridModePowLimit` -> `{"StreamAC5000SendCommandMsg": {"msg": {"pdata": {"StreamAC5000SetCommand": {"propertyId": 10, "powerLimits": {"feedGridModePowLimit": 6666, "outLimitField4": 4, "outLimitMax": 800}}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 38, "data_len": 12, "need_ack": 1, "version": 4, "from_": "HomeAssistant", "device_sn": "SN", "device_sn_2": "SN", "device_sn_3": "SN"}}}` [0 - 2500])
- Net Power In Limit (`chgPowLimit` -> `{"StreamAC5000SendCommandMsg": {"msg": {"pdata": {"StreamAC5000SetCommand": {"propertyId": 10, "powerLimits": {"chgPowLimit": 6666}}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 38, "data_len": 7, "need_ack": 1, "version": 4, "from_": "HomeAssistant", "device_sn": "SN", "device_sn_2": "SN", "device_sn_3": "SN"}}}` [0 - 3000])

*Selects*
- Work Mode (`workMode` -> `{"StreamAC5000SendCommandMsg": {"msg": {"pdata": {"StreamAC5000SetCommand": {"propertyId": 25, "workMode": 6666}}, "src": 32, "dest": 2, "d_src": 1, "d_dest": 1, "check_type": 3, "cmd_func": 254, "cmd_id": 38, "data_len": 6, "need_ack": 1, "version": 4, "from_": "HomeAssistant", "device_sn": "SN", "device_sn_2": "SN", "device_sn_3": "SN"}}}` [Self-powered (0), Intelligent (1), Scheduled (2)])


