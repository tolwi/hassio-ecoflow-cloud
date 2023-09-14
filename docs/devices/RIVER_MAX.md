## RIVER_MAX

*Sensors*
- Main Battery Level (`bmsMaster.soc`)
- Total In Power (`pd.wattsInSum`)
- Total Out Power (`pd.wattsOutSum`)
- AC In Power (`inv.inputWatts`)
- AC Out Power (`inv.outputWatts`)
- AC In Volts (`inv.acInVol`)
- AC Out Volts (`inv.invOutVol`)
- DC Out Power (`pd.carWatts`)
- Type-C Out Power (`pd.typecWatts`)
- USB (1) Out Power (`pd.usb1Watts`)
- USB (2) Out Power (`pd.usb2Watts`)
- USB (3) Out Power (`pd.usb3Watts`)
- Remaining Time (`pd.remainTime`)
- Cycles (`bmsMaster.cycles`)
- Battery Temperature (`bmsMaster.temp`)
- Min Cell Temperature (`bmsMaster.minCellTemp`)   _(disabled)_
- Max Cell Temperature (`bmsMaster.maxCellTemp`)   _(disabled)_
- Battery Volts (`bmsMaster.vol`)   _(disabled)_
- Min Cell Volts (`bmsMaster.minCellVol`)   _(disabled)_
- Max Cell Volts (`bmsMaster.maxCellVol`)   _(disabled)_
- Solar In Energy (`pd.chgSunPower`)
- Battery Charge Energy from AC (`pd.chgPowerAC`)
- Battery Charge Energy from DC (`pd.chgPowerDC`)
- Battery Discharge Energy to AC (`pd.dsgPowerAC`)
- Battery Discharge Energy to DC (`pd.dsgPowerDC`)
- Slave Battery Level (`bmsSlave1.soc`)   _(auto)_
- Slave Battery Temperature (`bmsSlave1.temp`)   _(auto)_
- Slave Min Cell Temperature (`bmsSlave1.minCellTemp`)   _(disabled)_
- Slave Max Cell Temperature (`bmsSlave1.maxCellTemp`)   _(disabled)_
- Battery Volts (`bmsSlave1.vol`)   _(disabled)_
- Min Cell Volts (`bmsSlave1.minCellVol`)   _(disabled)_
- Max Cell Volts (`bmsSlave1.maxCellVol`)   _(disabled)_
- Slave Cycles (`bmsSlave1.cycles`)   _(auto)_
- Status

*Switches*
- Beeper (`pd.beepState` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 38, "enabled": "VALUE"}}`)
- AC Enabled (`inv.cfgAcEnabled` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 66, "enabled": "VALUE"}}`)
- DC (12V) Enabled (`pd.carSwitch` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 34, "enabled": "VALUE"}}`)
- X-Boost Enabled (`inv.cfgAcXboost` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 66, "xboost": "VALUE"}}`)

*Sliders (numbers)*
- Max Charge Level (`bmsMaster.maxChargeSoc` -> `_ command not available _` [30 - 100])

*Selects*
- Unit Timeout (`pd.standByMode` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 33, "standByMode": "VALUE"}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])
- AC Timeout (`inv.cfgStandbyMin` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 153, "standByMins": "VALUE"}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])


