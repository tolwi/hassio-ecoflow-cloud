## SMART_PLUG

*Sensors*
- Temperature (`temp`)
- Volts (`volt`)
- Current (`current`)
- Power (`watts`)
- Status

*Switches*
- On (`switchSta` -> `{"SendSmartPlugHeaderMsg": {"msg": [{"pdata": {"WnPlugSwitchMessage": {"switchSta": true}}, "src": 32, "dest": 53, "cmdFunc": 2, "cmdId": 129, "dataLen": 2, "needAck": 1, "deviceSn": "SN"}]}}`)

*Sliders (numbers)*
- Brightness (`brightness` -> `{"SendSmartPlugHeaderMsg": {"msg": [{"pdata": {"WnBrightnessPack": {"brightness": 6666}}, "src": 32, "dest": 53, "cmdFunc": 2, "cmdId": 130, "dataLen": 3, "needAck": 1, "deviceSn": "SN"}]}}` [0 - 1023])
- Max Power (`maxWatts` -> `{"SendSmartPlugHeaderMsg": {"msg": [{"pdata": {"WnMaxWattsPack": {"maxWatts": 6666}}, "src": 32, "dest": 53, "cmdFunc": 2, "cmdId": 137, "dataLen": 3, "needAck": 1, "deviceSn": "SN"}]}}` [0 - 2500])


