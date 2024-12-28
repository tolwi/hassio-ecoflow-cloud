## RIVER_MINI

*Sensors*
- Main Battery Level (`inv.soc`)
- AC In Power (`inv.inputWatts`)
- AC Out Power (`inv.outputWatts`)
- AC In Volts (`inv.invInVol`)
- AC Out Volts (`inv.invOutVol`)
- Solar In Voltage (`inv.dcInVol`)
- Solar In Current (`inv.dcInAmp`)
- Inverter Inside Temperature (`inv.inTemp`)
- Inverter Outside Temperature (`inv.outTemp`)
- Solar In Energy (`pd.chgSunPower`)
- Battery Charge Energy from AC (`pd.chgPowerAC`)
- Battery Charge Energy from DC (`pd.chgPowerDC`)
- Battery Discharge Energy to AC (`pd.dsgPowerAC`)
- Battery Discharge Energy to DC (`pd.dsgPowerDC`)
- Total In Power (`pd.wattsInSum`)
- Total Out Power (`pd.wattsOutSum`)
- Cycles (`inv.cycles`)

*Switches*
- AC Enabled (`inv.cfgAcEnabled` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 66, "enabled": "VALUE"}}`)
- X-Boost Enabled (`inv.cfgAcXboost` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 66, "xboost": "VALUE"}}`)

*Sliders (numbers)*
- Max Charge Level (`inv.maxChargeSoc` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 0, "maxChgSoc": "VALUE"}}` [30 - 100])

*Selects*


