## RIVER_2_MAX

*Sensors*
- Main Battery Level (`bms_bmsStatus.soc`)
- Main Design Capacity (`bms_bmsStatus.designCap`)   _(disabled)_
- Main Full Capacity (`bms_bmsStatus.fullCap`)   _(disabled)_
- Main Remain Capacity (`bms_bmsStatus.remainCap`)   _(disabled)_
- State of Health (`bms_bmsStatus.soh`)
- Battery Level (`bms_emsStatus.lcdShowSoc`)
- Battery Charging State (`bms_emsStatus.chgState`)
- Total In Power (`pd.wattsInSum`) (energy:  _[Device Name]_ Total In  Energy)
- Total Out Power (`pd.wattsOutSum`) (energy:  _[Device Name]_ Total Out  Energy)
- Solar In Current (`inv.dcInAmp`)
- Solar In Voltage (`inv.dcInVol`)
- AC In Power (`inv.inputWatts`) (energy:  _[Device Name]_ AC In  Energy)
- AC Out Power (`inv.outputWatts`) (energy:  _[Device Name]_ AC Out  Energy)
- AC In Volts (`inv.acInVol`)
- AC Out Volts (`inv.invOutVol`)
- Type-C In Power (`pd.typecChaWatts`)
- Solar In Power (`mppt.inWatts`) (energy:  _[Device Name]_ Solar In  Energy)
- DC Out Power (`pd.carWatts`)
- Type-C Out Power (`pd.typec1Watts`)
- USB Out Power (`pd.usb1Watts`)
- Charge Remaining Time (`bms_emsStatus.chgRemainTime`)
- Discharge Remaining Time (`bms_emsStatus.dsgRemainTime`)
- Remaining Time (`pd.remainTime`)
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
- AC Enabled (`mppt.cfgAcEnabled` -> `{"moduleType": 5, "operateType": "acOutCfg", "params": {"enabled": "VALUE", "out_voltage": -1, "out_freq": 255, "xboost": 255}}`)
- AC Always On (`pd.acAutoOutConfig` -> `{"moduleType": 1, "operateType": "acAutoOutConfig", "params": {"acAutoOutConfig": "VALUE", "minAcOutSoc": 5}}`)
- X-Boost Enabled (`mppt.cfgAcXboost` -> `{"moduleType": 5, "operateType": "acOutCfg", "params": {"enabled": 255, "out_voltage": -1, "out_freq": 255, "xboost": "VALUE"}}`)
- DC (12V) Enabled (`pd.carState` -> `{"moduleType": 5, "operateType": "mpptCar", "params": {"enabled": "VALUE"}}`)
- Backup Reserve Enabled (`pd.watchIsConfig` -> `{"moduleType": 1, "operateType": "watthConfig", "params": {"isConfig": "VALUE", "bpPowerSoc": 333300, "minDsgSoc": 0, "minChgSoc": 0}}`)

*Sliders (numbers)*
- Max Charge Level (`bms_emsStatus.maxChargeSoc` -> `{"moduleType": 2, "operateType": "upsConfig", "params": {"maxChgSoc": "VALUE"}}` [50 - 100])
- Min Discharge Level (`bms_emsStatus.minDsgSoc` -> `{"moduleType": 2, "operateType": "dsgCfg", "params": {"minDsgSoc": "VALUE"}}` [0 - 30])
- AC Charging Power (`mppt.cfgChgWatts` -> `{"moduleType": 5, "operateType": "acChgCfg", "params": {"chgWatts": "VALUE", "chgPauseFlag": 255}}` [50 - 660])
- Backup Reserve Level (`pd.bpPowerSoc` -> `{"moduleType": 1, "operateType": "watthConfig", "params": {"isConfig": 1, "bpPowerSoc": "VALUE", "minDsgSoc": 0, "minChgSoc": 0}}` [5 - 100])

*Selects*
- DC (12V) Charge Current (`mppt.dcChgCurrent` -> `{"moduleType": 5, "operateType": "dcChgCfg", "params": {"dcChgCfg": "VALUE"}}` [4A (4000), 6A (6000), 8A (8000)])
- DC Mode (`mppt.cfgChgType` -> `{"moduleType": 5, "operateType": "chaType", "params": {"chaType": "VALUE"}}` [Auto (0), Solar Recharging (1), Car Recharging (2)])
- Screen Timeout (`mppt.scrStandbyMin` -> `{"moduleType": 5, "operateType": "lcdCfg", "params": {"brighLevel": 255, "delayOff": "VALUE"}}` [Never (0), 10 sec (10), 30 sec (30), 1 min (60), 5 min (300), 30 min (1800)])
- Unit Timeout (`mppt.powStandbyMin` -> `{"moduleType": 5, "operateType": "standby", "params": {"standbyMins": "VALUE"}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])
- AC Timeout (`mppt.acStandbyMins` -> `{"moduleType": 5, "operateType": "acStandby", "params": {"standbyMins": "VALUE"}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])


