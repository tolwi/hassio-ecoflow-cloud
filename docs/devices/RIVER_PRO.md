## RIVER_PRO

*Sensors*
- Main Battery Level (`pd.soc`)
- Total In Power (`pd.wattsInSum`)
- Total Out Power (`pd.wattsOutSum`)
- AC In Power (`inv.inputWatts`)
- AC Out Power (`inv.outputWatts`)
- DC Out Power (`pd.carWatts`)
- Type-C Out Power (`pd.typecWatts`)
- USB (1) Out Power (`pd.usb1Watts`)
- USB (2) Out Power (`pd.usb2Watts`)
- USB (3) Out Power (`pd.usb3Watts`)
- Remaining Time (`pd.remainTime`)
- Battery Temperature (`bmsMaster.temp`)
- Cycles (`bmsMaster.cycles`)

*Switches*
- Beeper (`pd.beepState` -> `_ command not available _`)
- AC Enabled (`inv.cfgAcEnabled` -> `_ command not available _`)
- X-Boost Enabled (`inv.cfgAcXboost` -> `_ command not available _`)

*Sliders (numbers)*
- Max Charge Level (`bmsMaster.maxChargeSoc` -> `_ command not available _` [50 - 100])

*Selects*
- Unit Timeout (`pd.standByMode` -> `_ command not available _` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])
- AC Timeout (`inv.cfgStandbyMin` -> `_ command not available _` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])


