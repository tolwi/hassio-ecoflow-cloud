## WAVE_2

*Sensors*
- Main Battery Level (`bms.soc`)
- Main Remain Capacity (`bms.remainCap`)   _(disabled)_
- Battery Temperature (`bms.tmp`)
- Min Cell Temperature (`bms.minCellTmp`)   _(disabled)_
- Max Cell Temperature (`bms.maxCellTmp`)   _(disabled)_
- Charge Remaining Time (`pd.batChgRemain`)
- Discharge Remaining Time (`pd.batDsgRemain`)
- Condensation temperature (`pd.condTemp`)   _(disabled)_
- Return air temperature in condensation zone (`pd.heatEnv`)   _(disabled)_
- Air outlet temperature (`pd.coolEnv`)   _(disabled)_
- Evaporation temperature (`pd.evapTemp`)   _(disabled)_
- Exhaust temperature (`pd.motorOutTemp`)   _(disabled)_
- Evaporation zone return air temperature (`pd.airInTemp`)   _(disabled)_
- Air outlet temperature (`pd.coolTemp`)   _(disabled)_
- Ambient temperature (`pd.envTemp`)   _(disabled)_
- PV input power (`pd.mpptPwr`)
- Battery output power (`pd.batPwrOut`)
- PV charging power (`pd.pvPower`)
- AC input power (`pd.acPwrIn`)
- Power supply power (`pd.psdrPower `)
- System power (`pd.sysPowerWatts`)
- Battery power (`pd.batPower `)
- Motor operating power (`motor.power`)
- Battery output power (`power.batPwrOut`)
- AC input power (`power.acPwrI`)
- PV input power (`power.mpptPwr `)
- Status

*Sliders (numbers)*
- Set Temperature (`pd.setTemp` -> `{"moduleType": 1, "operateType": "setTemp", "sn": "SN", "params": {"setTemp": "VALUE"}}` [0 - 40])

*Selects*
- Wind speed (`pd.fanValue` -> `{"moduleType": 1, "operateType": "fanValue", "sn": "SN", "params": {"fanValue": "VALUE"}}` [Low (0), Medium (1), High (2)])
- Main mode (`pd.mainMode` -> `{"moduleType": 1, "operateType": "mainMode", "sn": "SN", "params": {"mainMode": "VALUE"}}` [Cool (0), Heat (1), Fan (2)])
- Remote startup/shutdown (`pd.powerMode` -> `{"moduleType": 1, "operateType": "powerMode", "sn": "SN", "params": {"powerMode": "VALUE"}}` [Startup (1), Standby (2), Shutdown (3)])
- Sub-mode (`pd.subMode` -> `{"moduleType": 1, "operateType": "subMode", "sn": "SN", "params": {"subMode": "VALUE"}}` [Max (0), Sleep (1), Eco (2), Manual (3)])


