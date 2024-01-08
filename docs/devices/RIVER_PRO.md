## RIVER_PRO

*Sensors*
- Main Battery Level (`bmsMaster.soc`)
- Main Design Capacity (`bmsMaster.designCap`)   _(disabled)_
- Main Full Capacity (`bmsMaster.fullCap`)   _(disabled)_
- Main Remain Capacity (`bmsMaster.remainCap`)   _(disabled)_
- Total In Power (`pd.wattsInSum`)
- Total Out Power (`pd.wattsOutSum`)
- Solar In Current (`inv.dcInAmp`)
- Solar In Voltage (`inv.dcInVol`)
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
- Battery Temperature (`bmsMaster.temp`)
- Min Cell Temperature (`bmsMaster.minCellTemp`)   _(disabled)_
- Max Cell Temperature (`bmsMaster.maxCellTemp`)   _(disabled)_
- Battery Current (`bmsMaster.amp`)   _(disabled)_
- Battery Volts (`bmsMaster.vol`)   _(disabled)_
- Min Cell Volts (`bmsMaster.minCellVol`)   _(disabled)_
- Max Cell Volts (`bmsMaster.maxCellVol`)   _(disabled)_
- Cycles (`bmsMaster.cycles`)
- Slave Battery Level (`bmsSlave1.soc`)   _(auto)_
- Slave Design Capacity (`bmsSlave1.designCap`)   _(disabled)_
- Slave Full Capacity (`bmsSlave1.fullCap`)   _(disabled)_
- Slave Remain Capacity (`bmsSlave1.remainCap`)   _(disabled)_
- Slave Cycles (`bmsSlave1.cycles`)   _(auto)_
- Slave Battery Temperature (`bmsSlave1.temp`)   _(auto)_
- Slave Battery Current (`bmsSlave1.amp`)   _(disabled)_
- Slave Battery Volts (`bmsSlave1.vol`)   _(disabled)_
- Slave Min Cell Volts (`bmsSlave1.minCellVol`)   _(disabled)_
- Slave Max Cell Volts (`bmsSlave1.maxCellVol`)   _(disabled)_
- Status

*Switches*
- Beeper (`pd.beepState` -> `_ command not available _`)
- AC Enabled (`inv.cfgAcEnabled` -> `_ command not available _`)
- X-Boost Enabled (`inv.cfgAcXboost` -> `_ command not available _`)

*Sliders (numbers)*
- Max Charge Level (`bmsMaster.maxChargeSoc` -> `_ command not available _` [50 - 100])

*Selects*
- Unit Timeout (`pd.standByMode` -> `_ command not available _` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])
- AC Timeout (`inv.cfgStandbyMin` -> `_ command not available _` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])


