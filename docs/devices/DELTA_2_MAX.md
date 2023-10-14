## DELTA_2_MAX

*Sensors*
- Main Battery Level (`bms_bmsStatus.soc`)
- Battery Level (`bms_emsStatus.lcdShowSoc`)
- Total In Power (`pd.wattsInSum`)
- Total Out Power (`pd.wattsOutSum`)
- AC In Power (`inv.inputWatts`)
- AC Out Power (`inv.outputWatts`)
- AC In Volts (`inv.acInVol`)
- AC Out Volts (`inv.invOutVol`)
- Solar (1) In Power (`mppt.inWatts`)
- Solar (2) In Power (`mppt.pv2InWatts`)
- DC Out Power (`mppt.outWatts`)
- Type-C (1) Out Power (`pd.typec1Watts`)
- Type-C (2) Out Power (`pd.typec2Watts`)
- USB (1) Out Power (`pd.usb1Watts`)
- USB (2) Out Power (`pd.usb2Watts`)
- USB QC (1) Out Power (`pd.qcUsb1Watts`)
- USB QC (2) Out Power (`pd.qcUsb2Watts`)
- Charge Remaining Time (`bms_emsStatus.chgRemainTime`)
- Discharge Remaining Time (`bms_emsStatus.dsgRemainTime`)
- Inv Out Temperature (`inv.outTemp`)
- Cycles (`bms_bmsStatus.cycles`)
- Battery Temperature (`bms_bmsStatus.temp`)
- Min Cell Temperature (`bms_bmsStatus.minCellTemp`)   _(disabled)_
- Max Cell Temperature (`bms_bmsStatus.maxCellTemp`)   _(disabled)_
- Battery Volts (`bms_bmsStatus.vol`)   _(disabled)_
- Min Cell Volts (`bms_bmsStatus.minCellVol`)   _(disabled)_
- Max Cell Volts (`bms_bmsStatus.maxCellVol`)   _(disabled)_
- Status

*Switches*
- Beeper (`pd.beepMode` -> `{"moduleType": 1, "operateType": "quietCfg", "moduleSn": "MOCK", "params": {"enabled": "VALUE"}}`)
- USB Enabled (`pd.dcOutState` -> `{"moduleType": 1, "operateType": "dcOutCfg", "moduleSn": "MOCK", "params": {"enabled": "VALUE"}}`)
- AC Always On (`pd.newAcAutoOnCfg` -> `{"moduleType": 1, "operateType": "newAcAutoOnCfg", "moduleSn": "MOCK", "params": {"enabled": "VALUE", "minAcSoc": 5}}`)
- AC Enabled (`inv.cfgAcEnabled` -> `{"moduleType": 3, "operateType": "acOutCfg", "moduleSn": "MOCK", "params": {"enabled": "VALUE"}}`)
- X-Boost Enabled (`inv.cfgAcXboost` -> `{"moduleType": 3, "operateType": "acOutCfg", "moduleSn": "MOCK", "params": {"xboost": "VALUE"}}`)

*Sliders (numbers)*
- Max Charge Level (`bms_emsStatus.maxChargeSoc` -> `{"moduleType": 2, "operateType": "upsConfig", "moduleSn": "MOCK", "params": {"maxChgSoc": "VALUE"}}` [50 - 100])
- Min Discharge Level (`bms_emsStatus.minDsgSoc` -> `{"moduleType": 2, "operateType": "dsgCfg", "moduleSn": "MOCK", "params": {"minDsgSoc": "VALUE"}}` [0 - 30])
- Generator Auto Start Level (`bms_emsStatus.minOpenOilEbSoc` -> `{"moduleType": 2, "operateType": "closeOilSoc", "moduleSn": "MOCK", "params": {"closeOilSoc": "VALUE"}}` [0 - 30])
- Generator Auto Stop Level (`bms_emsStatus.maxCloseOilEbSoc` -> `{"moduleType": 2, "operateType": "openOilSoc", "moduleSn": "MOCK", "params": {"openOilSoc": "VALUE"}}` [50 - 100])
- AC Charging Power (`inv.SlowChgWatts` -> `{"moduleType": 3, "operateType": "acChgCfg", "moduleSn": "MOCK", "params": {"slowChgWatts": "VALUE", "fastChgWatts": 255, "chgPauseFlag": 0}}` [200 - 2400])

*Selects*
- Screen Timeout (`pd.lcdOffSec` -> `{"moduleType": 1, "operateType": "lcdCfg", "moduleSn": "MOCK", "params": {"brighLevel": 255, "delayOff": "VALUE"}}` [Never (0), 10 sec (10), 30 sec (30), 1 min (60), 5 min (300), 30 min (1800)])
- Unit Timeout (`inv.standbyMin` -> `{"moduleType": 1, "operateType": "standbyTime", "moduleSn": "MOCK", "params": {"standbyMin": "VALUE"}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])
- AC Timeout (`mppt.carStandbyMin` -> `{"moduleType": 5, "operateType": "standbyTime", "moduleSn": "MOCK", "params": {"standbyMins": "VALUE"}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])


