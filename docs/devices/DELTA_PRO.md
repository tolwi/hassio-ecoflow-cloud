## DELTA_PRO

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
- AC In Power (`inv.inputWatts`)
- AC Out Power (`inv.outputWatts`)
- AC In Volts (`inv.acInVol`)
- AC Out Volts (`inv.invOutVol`)
- Solar In Power (`mppt.inWatts`)
- Solar In Voltage (`mppt.inVol`)
- Solar In Current (`mppt.inAmp`)
- DC Out Power (`mppt.outWatts`)
- DC Out Voltage (`mppt.outVol`)
- DC Car Out Power (`mppt.carOutWatts`)
- DC Anderson Out Power (`mppt.dcdc12vWatts`)
- Type-C (1) Out Power (`pd.typec1Watts`)
- Type-C (2) Out Power (`pd.typec2Watts`)
- USB (1) Out Power (`pd.usb1Watts`)
- USB (2) Out Power (`pd.usb2Watts`)
- USB QC (1) Out Power (`pd.qcUsb1Watts`)
- USB QC (2) Out Power (`pd.qcUsb2Watts`)
- Charge Remaining Time (`ems.chgRemainTime`)
- Discharge Remaining Time (`ems.dsgRemainTime`)
- Cycles (`bmsMaster.cycles`)
- Battery Temperature (`bmsMaster.temp`)
- Min Cell Temperature (`bmsMaster.minCellTemp`)   _(disabled)_
- Max Cell Temperature (`bmsMaster.maxCellTemp`)   _(disabled)_
- Main Battery Current (`bmsMaster.amp`)   _(disabled)_
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
- Beeper (`pd.beepState` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 38, "enabled": "VALUE"}}`)
- DC (12V) Enabled (`mppt.carState` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 81, "enabled": "VALUE"}}`)
- AC Enabled (`inv.cfgAcEnabled` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 66, "enabled": "VALUE"}}`)
- X-Boost Enabled (`inv.cfgAcXboost` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 66, "xboost": "VALUE"}}`)
- AC Always On (`pd.acautooutConfig` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 95, "acautooutConfig": "VALUE"}}`)
- Backup Reserve Enabled (`pd.watthisconfig` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 94, "isConfig": "VALUE", "bpPowerSoc": -3333300, "minDsgSoc": 0, "maxChgSoc": 0}}`)

*Sliders (numbers)*
- Max Charge Level (`ems.maxChargeSoc` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 49, "maxChgSoc": "VALUE"}}` [50 - 100])
- Min Discharge Level (`ems.minDsgSoc` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 51, "minDsgSoc": "VALUE"}}` [0 - 30])
- Backup Reserve Level (`pd.bppowerSoc` -> `{"moduleType": 0, "operateType": "TCP", "params": {"isConfig": 1, "bpPowerSoc": "VALUE", "minDsgSoc": 0, "maxChgSoc": 0, "id": 94}}` [5 - 100])
- Generator Auto Start Level (`ems.minOpenOilEbSoc` -> `{"moduleType": 0, "operateType": "TCP", "params": {"openOilSoc": "VALUE", "id": 52}}` [0 - 30])
- Generator Auto Stop Level (`ems.maxCloseOilEbSoc` -> `{"moduleType": 0, "operateType": "TCP", "params": {"closeOilSoc": "VALUE", "id": 53}}` [50 - 100])
- AC Charging Power (`inv.cfgSlowChgWatts` -> `{"moduleType": 0, "operateType": "TCP", "params": {"slowChgPower": "VALUE", "id": 69}}` [200 - 2900])

*Selects*
- DC (12V) Charge Current (`mppt.cfgDcChgCurrent` -> `{"moduleType": 0, "operateType": "TCP", "params": {"currMa": "VALUE", "id": 71}}` [4A (4000), 6A (6000), 8A (8000)])
- Screen Timeout (`pd.lcdOffSec` -> `{"moduleType": 0, "operateType": "TCP", "params": {"lcdTime": "VALUE", "id": 39}}` [Never (0), 10 sec (10), 30 sec (30), 1 min (60), 5 min (300), 30 min (1800)])
- Unit Timeout (`pd.standByMode` -> `{"moduleType": 0, "operateType": "TCP", "params": {"standByMode": "VALUE", "id": 33}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 6 hr (360), 12 hr (720)])
- AC Timeout (`inv.cfgStandbyMin` -> `{"moduleType": 0, "operateType": "TCP", "params": {"standByMins": "VALUE", "id": 153}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])


