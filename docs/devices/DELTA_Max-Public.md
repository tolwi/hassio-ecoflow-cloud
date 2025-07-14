## DELTA_Max

*Sensors*
- Main Battery Level (`bmsMaster.soc`)
- Main Battery Level (Precise) (`bmsMaster.f32ShowSoc`)   _(disabled)_
- Main Design Capacity (`bmsMaster.designCap`)   _(disabled)_
- Main Full Capacity (`bmsMaster.fullCap`)   _(disabled)_
- Main Remain Capacity (`bmsMaster.remainCap`)   _(disabled)_
- State of Health (`bmsMaster.soh`)
- Battery Level (`ems.lcdShowSoc`)
- Battery Level (Precise) (`ems.f32LcdShowSoc`)   _(disabled)_
- Total In Power (`pd.wattsInSum`)
- Total Out Power (`pd.wattsOutSum`)
- Main Battery Current (`bmsMaster.amp`)
- AC In Power (`inv.inputWatts`)
- AC Out Power (`inv.outputWatts`)
- AC In Volts (`inv.acInVol`)
- AC Out Volts (`inv.invOutVol`)
- Solar In Power (`mppt.inWatts`)
- Solar In Voltage (`mppt.inVol`)
- Solar In Current (`mppt.inAmp`)
- DC Out Power (`mppt.outWatts`)
- DC Out Voltage (`mppt.outVol`)
- Type-C (1) Out Power (`pd.typec1Watts`)
- Type-C (2) Out Power (`pd.typec2Watts`)
- USB (1) Out Power (`pd.usb1Watts`)
- USB (2) Out Power (`pd.usb2Watts`)
- USB QC (1) Out Power (`pd.qcUsb1Watts`)
- USB QC (2) Out Power (`pd.qcUsb2Watts`)
- Charge Remaining Time (`ems.chgRemainTime`)
- Discharge Remaining Time (`ems.dsgRemainTime`)
- Inv Out Temperature (`inv.outTemp`)
- Cycles (`bmsMaster.cycles`)
- Battery Temperature (`bmsMaster.temp`)
- Min Cell Temperature (`bmsMaster.minCellTemp`)   _(disabled)_
- Max Cell Temperature (`bmsMaster.maxCellTemp`)   _(disabled)_
- Battery Volts (`bmsMaster.vol`)   _(disabled)_
- Min Cell Volts (`bmsMaster.minCellVol`)   _(disabled)_
- Max Cell Volts (`bmsMaster.maxCellVol`)   _(disabled)_
- Solar In Energy (`pd.chgSunPower`)
- Battery Charge Energy from AC (`pd.chgPowerAc`)
- Battery Charge Energy from DC (`pd.chgPowerDc`)
- Battery Discharge Energy to AC (`pd.dsgPowerAc`)
- Battery Discharge Energy to DC (`pd.dsgPowerDc`)
- Slave 1 Battery Level (`bmsSlave1.soc`)   _(auto)_
- Slave 1 Battery Level (Precise) (`bmsSlave1.f32ShowSoc`)   _(disabled)_
- Slave 1 Design Capacity (`bmsSlave1.designCap`)   _(disabled)_
- Slave 1 Full Capacity (`bmsSlave1.fullCap`)   _(disabled)_
- Slave 1 Remain Capacity (`bmsSlave1.remainCap`)   _(disabled)_
- Slave 1 State of Health (`bmsSlave1.soh`)
- Slave 1 Battery Temperature (`bmsSlave1.temp`)   _(auto)_
- Slave 1 In Power (`bmsSlave1.inputWatts`)   _(auto)_
- Slave 1 Out Power (`bmsSlave1.outputWatts`)   _(auto)_
- Slave 2 Battery Level (`bmsSlave2.soc`)   _(auto)_
- Slave 2 Battery Level (Precise) (`bmsSlave2.f32ShowSoc`)   _(disabled)_
- Slave 2 Design Capacity (`bmsSlave2.designCap`)   _(disabled)_
- Slave 2 Full Capacity (`bmsSlave2.fullCap`)   _(disabled)_
- Slave 2 Remain Capacity (`bmsSlave2.remainCap`)   _(disabled)_
- Slave 2 State of Health (`bmsSlave2.soh`)
- Slave 1 Battery Volts (`bmsSlave1.vol`)   _(disabled)_
- Slave 1 Min Cell Volts (`bmsSlave1.minCellVol`)   _(disabled)_
- Slave 1 Max Cell Volts (`bmsSlave1.maxCellVol`)   _(disabled)_
- Slave 1 Battery Current (`bmsSlave1.amp`)   _(disabled)_
- Slave 2 Battery Volts (`bmsSlave2.vol`)   _(disabled)_
- Slave 2 Min Cell Volts (`bmsSlave2.minCellVol`)   _(disabled)_
- Slave 2 Max Cell Volts (`bmsSlave2.maxCellVol`)   _(disabled)_
- Slave 2 Battery Current (`bmsSlave2.amp`)   _(disabled)_
- Slave 2 Battery Temperature (`bmsSlave2.temp`)   _(auto)_
- Slave 2 In Power (`bmsSlave2.inputWatts`)   _(auto)_
- Slave 2 Out Power (`bmsSlave2.outputWatts`)   _(auto)_
- Slave 1 Cycles (`bmsSlave1.cycles`)   _(disabled)_
- Slave 2 Cycles (`bmsSlave2.cycles`)   _(disabled)_
- Status

*Switches*
- Beeper (`pd.beepState` -> `{"moduleType": 5, "operateType": "TCP", "params": {"id": 38, "enabled": "VALUE"}}`)
- USB Enabled (`pd.dcOutState` -> `{"moduleType": 0, "operateType": "TCP", "params": {"enabled": "VALUE", "id": 34}}`)
- AC Always On (`pd.acAutoOnCfg` -> `{"moduleType": 1, "operateType": "acAutoOn", "params": {"cfg": "VALUE"}}`)
- Prio Solar Charging (`pd.pvChgPrioSet` -> `{"moduleType": 1, "operateType": "pvChangePrio", "params": {"pvChangeSet": "VALUE"}}`)
- AC Enabled (`inv.cfgAcEnabled` -> `{"moduleType": 0, "operateType": "TCP", "params": {"enabled": "VALUE", "id": 66}}`)
- X-Boost Enabled (`inv.cfgAcXboost` -> `{"moduleType": 5, "operateType": "TCP", "params": {"id": 66, "xboost": "VALUE"}}`)
- DC (12V) Enabled (`mppt.carState` -> `{"moduleType": 0, "operateType": "TCP", "params": {"enabled": "VALUE", "id": 81}}`)

*Sliders (numbers)*
- Max Charge Level (`ems.maxChargeSoc` -> `{"moduleType": 2, "operateType": "TCP", "params": {"id": 49, "maxChgSoc": "VALUE"}}` [50 - 100])
- Min Discharge Level (`ems.minDsgSoc` -> `{"moduleType": 2, "operateType": "TCP", "params": {"id": 51, "minDsgSoc": "VALUE"}}` [0 - 30])
- Generator Auto Start Level (`ems.minOpenOilEbSoc` -> `{"moduleType": 2, "operateType": "TCP", "params": {"id": 52, "openOilSoc": "VALUE"}}` [0 - 30])
- Generator Auto Stop Level (`ems.maxCloseOilEbSoc` -> `{"moduleType": 2, "operateType": "TCP", "params": {"id": 53, "closeOilSoc": "VALUE"}}` [50 - 100])
- AC Charging Power (`inv.cfgSlowChgWatts` -> `{"moduleType": 0, "operateType": "TCP", "params": {"slowChgPower": "VALUE", "id": 69}}` [100 - 2000])

*Selects*


