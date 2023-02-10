## RIVER_2_MAX

*Sensors*
- Main Battery Level (`pd.soc`)
- Total In Power (`pd.wattsInSum`)
- Total Out Power (`pd.wattsOutSum`)
- AC In Power (`inv.inputWatts`)
- Type-C In Power (`pd.typecChaWatts`)
- Solar In Power (`mppt.inWatts`)
- AC Out Power (`inv.outputWatts`)
- DC Out Power (`pd.carWatts`)
- Type-C (1) Out Power (`pd.typec1Watts`)
- USB (1) Out Power (`pd.usb1Watts`)
- USB (2) Out Power (`pd.usb2Watts`)
- Charge Remaining Time (`bms_emsStatus.chgRemainTime`)
- Discharge Remaining Time (`bms_emsStatus.dsgRemainTime`)
- Inv Out Temperature (`inv.outTemp`)
- Battery Temperature (`bms_bmsStatus.temp`)
- Cycles (`bms_bmsStatus.cycles`)

*Switches*
- AC Enabled (`mppt.cfgAcEnabled` -> `{"moduleType": 5, "operateType": "acOutCfg", "params": {"enabled": "VALUE", "out_voltage": -1, "out_freq": 255, "xboost": 255}}`)
- DC (12V) Enabled (`pd.carState` -> `{"moduleType": 5, "operateType": "mpptCar", "params": {"enabled": "VALUE"}}`)

*Sliders (numbers)*
- Max Charge Level (`bms_emsStatus.maxChargeSoc` -> `{"moduleType": 2, "operateType": "upsConfig", "params": {"maxChgSoc": "VALUE"}}` [50 - 100])
- Min Discharge Level (`bms_emsStatus.minDsgSoc` -> `{"moduleType": 2, "operateType": "upsConfig", "params": {"minDsgSoc": "VALUE"}}` [0 - 30])
- AC Charging Power (`mppt.cfgChgWatts` -> `{"moduleType": 5, "operateType": "acChgCfg", "params": {"chgWatts": "VALUE", "chgPauseFlag": 255}}` [100 - 660])

*Selects*
- DC (12V) Charge Current (`mppt.dcChgCurrent` -> `{"moduleType": 5, "operateType": "dcChgCfg", "params": {"dcChgCfg": "VALUE"}}` [4A (4000), 6A (6000), 8A (8000)])
- Screen Timeout (`mppt.scrStandbyMin` -> `{"moduleType": 5, "operateType": "lcdCfg", "params": {"brighLevel": 255, "delayOff": "VALUE"}}` [Never (0), 10 sec (10), 30 sec (30), 1 min (60), 5 min (300), 30 min (1800)])
- Unit Timeout (`mppt.powStandbyMin` -> `{"moduleType": 5, "operateType": "standby", "params": {"standbyMins": "VALUE"}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])
- AC Timeout (`mppt.acStandbyMins` -> `{"moduleType": 5, "operateType": "acStandby", "params": {"standbyMins": "VALUE"}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])


