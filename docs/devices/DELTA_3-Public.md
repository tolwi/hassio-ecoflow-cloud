## DELTA_3

*Sensors*
- Main Battery Level (`soc`)
- Main Design Capacity (`designCap`)   _(disabled)_
- Main Full Capacity (`fullCap`)   _(disabled)_
- Main Remain Capacity (`remainCap`)   _(disabled)_
- State of Health (`soh`)
- Battery Level (`v1p0.lcdShowSoc`)
- Total In Power (`powInSumW`)
- Total Out Power (`powOutSumW`)
- AC In Power (`powGetAcIn`)
- AC Out Power (`powGetAcOut`)
- AC In Volts (`plugInInfoAcInVol`)
- AC Out Volts (`plugInInfoAcOutVol`)
- Solar In Power (`powGetPv`)
- DC Out Power (`powGetDc`)
- Type-C (1) Out Power (`powGetTypec1`)
- Type-C (2) Out Power (`powGetTypec2`)
- USB QC (1) Out Power (`powGetQcusb1`)
- USB QC (2) Out Power (`powGetQcusb2`)
- Charge Remaining Time (`v1p0.chgRemainTime`)
- Discharge Remaining Time (`v1p0.dsgRemainTime`)
- Cycles (`cycles`)
- Battery Temperature (`temp`)
- Min Cell Temperature (`minCellTemp`)   _(disabled)_
- Max Cell Temperature (`maxCellTemp`)   _(disabled)_
- Battery Volts (`vol`)   _(disabled)_
- Min Cell Volts (`minCellVol`)   _(disabled)_
- Max Cell Volts (`maxCellVol`)   _(disabled)_
- Status

*Switches*
- Beeper (`enBeep` -> `{"moduleType": 5, "operateType": "quietMode", "params": {"enabled": "VALUE"}}`)
- X-Boost Enabled (`xboostEn` -> `{"moduleType": 5, "operateType": "acOutCfg", "params": {"enabled": 255, "out_voltage": -1, "out_freq": 255, "xboost": "VALUE"}}`)

*Sliders (numbers)*
- Max Charge Level (`v1p0.maxChargeSoc` -> `{"moduleType": 2, "operateType": "upsConfig", "params": {"maxChgSoc": "VALUE"}}` [50 - 100])
- Min Discharge Level (`v1p0.minDsgSoc` -> `{"moduleType": 2, "operateType": "dsgCfg", "params": {"minDsgSoc": "VALUE"}}` [0 - 30])
- Backup Reserve Level (`backupReverseSoc` -> `{"moduleType": 1, "operateType": "watthConfig", "params": {"isConfig": 1, "backupReverseSoc": "VALUE", "minDsgSoc": 0, "minChgSoc": 0}}` [5 - 100])
- Generator Auto Start Level (`v1p0.minOpenOilEbSoc` -> `{"moduleType": 2, "operateType": "openOilSoc", "params": {"openOilSoc": "VALUE"}}` [0 - 30])
- Generator Auto Stop Level (`v1p0.maxCloseOilEbSoc` -> `{"moduleType": 2, "operateType": "closeOilSoc", "params": {"closeOilSoc": "VALUE"}}` [50 - 100])
- AC Charging Power (`plugInInfoAcInChgPowMax` -> `{"moduleType": 5, "operateType": "acChgCfg", "params": {"chgWatts": "VALUE", "chgPauseFlag": 255}}` [200 - 1200])

*Selects*
- Screen Timeout (`screenOffTime` -> `{"moduleType": 1, "operateType": "lcdCfg", "params": {"brighLevel": 255, "delayOff": "VALUE"}}` [Never (0), 10 sec (10), 30 sec (30), 1 min (60), 5 min (300), 30 min (1800)])
- Unit Timeout (`devStandbyTime` -> `{"moduleType": 1, "operateType": "standbyTime", "params": {"standbyMin": "VALUE"}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])
- AC Timeout (`acStandbyTime` -> `{"moduleType": 5, "operateType": "standbyTime", "params": {"standbyMins": "VALUE"}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])
- DC (12V) Timeout (`dcStandbyTime` -> `{"moduleType": 5, "operateType": "carStandby", "params": {"standbyMins": "VALUE"}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])


