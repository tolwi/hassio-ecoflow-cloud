## DELTA_MINI

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
- Battery Temperature (`bmsMaster.temp`)   _(disabled)_
- Main Battery Current (`bmsMaster.amp`)   _(disabled)_
- Battery Volts (`bmsMaster.vol`)   _(disabled)_
- Solar In Energy (`pd.chgSunPower`)
- Battery Charge Energy from AC (`pd.chgPowerAc`)
- Battery Charge Energy from DC (`pd.chgPowerDc`)
- Battery Discharge Energy to AC (`pd.dsgPowerAc`)
- Battery Discharge Energy to DC (`pd.dsgPowerDc`)
- Status

*Switches*
- Beeper (`mppt.beepState` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 38, "enabled": "VALUE"}}`)
- DC (12V) Enabled (`mppt.carState` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 81, "enabled": "VALUE"}}`)
- AC Enabled (`inv.cfgAcEnabled` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 66, "enabled": "VALUE"}}`)
- X-Boost Enabled (`inv.cfgAcXboost` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 66, "xboost": "VALUE"}}`)

*Sliders (numbers)*
- Max Charge Level (`ems.maxChargeSoc` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 49, "maxChgSoc": "VALUE"}}` [50 - 100])
- Min Discharge Level (`ems.minDsgSoc` -> `{"moduleType": 0, "operateType": "TCP", "params": {"id": 51, "minDsgSoc": "VALUE"}}` [0 - 30])
- AC Charging Power (`inv.cfgSlowChgWatts` -> `{"moduleType": 0, "operateType": "TCP", "params": {"slowChgPower": "VALUE", "id": 69}}` [200 - 900])

*Selects*
- DC (12V) Charge Current (`mppt.cfgDcChgCurrent` -> `{"moduleType": 0, "operateType": "TCP", "params": {"currMa": "VALUE", "id": 71}}` [4A (4000), 6A (6000), 8A (8000)])
- Screen Timeout (`pd.lcdOffSec` -> `{"moduleType": 0, "operateType": "TCP", "params": {"lcdTime": "VALUE", "id": 39}}` [Never (0), 10 sec (10), 30 sec (30), 1 min (60), 5 min (300), 30 min (1800)])
- Unit Timeout (`pd.standByMode` -> `{"moduleType": 0, "operateType": "TCP", "params": {"standByMode": "VALUE", "id": 33}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 6 hr (360), 12 hr (720)])
- AC Timeout (`inv.cfgStandbyMin` -> `{"moduleType": 0, "operateType": "TCP", "params": {"standByMins": "VALUE", "id": 153}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])


