## SMART_PLUG

*Sensors*
- Temperature (`temp`)
- Volts (`volt`)
- Current (`current`)
- Power (`watts`)
- Status (`status`)

*Switches*
- On (`switchSta` -> `{"SendSmartPlugHeaderMsg": {"msg": [{"pdata": {"WnPlugSwitchMessage": {"switchSta": true}}, "dataLen": 2, "src": 32, "dest": 2, "cmdFunc": 2, "cmdId": 129, "needAck": 1, "deviceSn": "SN"}]}}`)

*Sliders (numbers)*
- Brightness (`brightness` -> `{"SendSmartPlugHeaderMsg": {"msg": [{"pdata": {"WnBrightnessPack": {"brightness": 6666}}, "dataLen": 3, "src": 32, "dest": 2, "cmdFunc": 2, "cmdId": 130, "needAck": 1, "deviceSn": "SN"}]}}` [0 - 1023])
- Max Power (`maxWatts` -> `{"SendSmartPlugHeaderMsg": {"msg": [{"pdata": {"WnMaxWattsPack": {"maxWatts": 6666}}, "dataLen": 3, "src": 32, "dest": 2, "cmdFunc": 2, "cmdId": 137, "needAck": 1, "deviceSn": "SN"}]}}` [0 - 2500])


