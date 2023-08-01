## DELTA_2

*Sensors*
- Main Battery Level (`pd.soc`)
- Battery Level (`bms_emsStatus.lcdShowSoc`)
- Total In Power (`pd.wattsInSum`)
- Total Out Power (`pd.wattsOutSum`)
- AC In Power (`inv.inputWatts`)
- AC Out Power (`inv.outputWatts`)
- AC In Volts (`inv.acInVol`)
- AC Out Volts (`inv.invOutVol`)
- Solar In Power (`mppt.inWatts`)
- DC Out Power (`mppt.outWatts`)
- Type-C (1) Out Power (`pd.typec1Watts`)
- Type-C (2) Out Power (`pd.typec2Watts`)
- USB (1) Out Power (`pd.usb1Watts`)
- USB (2) Out Power (`pd.usb2Watts`)
- USB QC (1) Out Power (`pd.qcUsb1Watts`)
- USB QC (2) Out Power (`pd.qcUsb2Watts`)
- Charge Remaining Time (`bms_emsStatus.chgRemainTime`)
- Discharge Remaining Time (`bms_emsStatus.dsgRemainTime`)
- Inv Out Temperature (`inv.outTemp`)
- Cycles (`bms_bmsStatus.cycles`)
- Battery Temperature (`bms_bmsStatus.temp`)
- Min Cell Temperature (`bms_bmsStatus.minCellTemp`)   _(disabled)_
- Max Cell Temperature (`bms_bmsStatus.maxCellTemp`)   _(disabled)_
- Battery Volts (`bms_bmsStatus.vol`)   _(disabled)_
- Min Cell Volts (`bms_bmsStatus.minCellVol`)   _(disabled)_
- Max Cell Volts (`bms_bmsStatus.maxCellVol`)   _(disabled)_
- Slave Battery Level (`bms_slave.soc`)   _(auto)_
- Slave Battery Temperature (`bms_slave.temp`)   _(auto)_
- Slave Min Cell Temperature (`bms_slave.minCellTemp`)   _(disabled)_
- Slave Max Cell Temperature (`bms_slave.maxCellTemp`)   _(disabled)_
- Slave Battery Volts (`bms_slave.vol`)   _(disabled)_
- Slave Min Cell Volts (`bms_slave.minCellVol`)   _(disabled)_
- Slave Max Cell Volts (`bms_slave.maxCellVol`)   _(disabled)_
- Slave Cycles (`bms_slave.cycles`)   _(auto)_
- Slave In Power (`bms_slave.inputWatts`)   _(auto)_
- Slave Out Power (`bms_slave.outputWatts`)   _(auto)_
- Status

*Switches*
- Beeper (`mppt.beepState` -> `{"moduleType": 5, "operateType": "quietMode", "params": {"enabled": "VALUE"}}`)
- USB Enabled (`pd.dcOutState` -> `{"moduleType": 1, "operateType": "dcOutCfg", "params": {"enabled": "VALUE"}}`)
- AC Always On (`pd.acAutoOutConfig` -> `{"moduleType": 1, "operateType": "acAutoOutConfig", "params": {"acAutoOutConfig": "VALUE", "minAcOutSoc": 5}}`)
- Prio Solar Charging (`pd.pvChgPrioSet` -> `{"moduleType": 1, "operateType": "pvChangePrio", "params": {"pvChangeSet": "VALUE"}}`)
- AC Enabled (`mppt.cfgAcEnabled` -> `{"moduleType": 5, "operateType": "acOutCfg", "params": {"enabled": "VALUE", "out_voltage": -1, "out_freq": 255, "xboost": 255}}`)
- X-Boost Enabled (`mppt.cfgAcXboost` -> `{"moduleType": 5, "operateType": "acOutCfg", "params": {"enabled": 255, "out_voltage": -1, "out_freq": 255, "xboost": "VALUE"}}`)
- DC (12V) Enabled (`pd.carState` -> `{"moduleType": 5, "operateType": "mpptCar", "params": {"enabled": "VALUE"}}`)
- Backup Reserve Enabled (`pd.bpPowerSoc` -> `{"moduleType": 1, "operateType": "watthConfig", "params": {"isConfig": "VALUE"}}`)

*Sliders (numbers)*
- Max Charge Level (`bms_emsStatus.maxChargeSoc` -> `{"moduleType": 2, "operateType": "upsConfig", "params": {"maxChgSoc": "VALUE"}}` [50 - 100])
- Min Discharge Level (`bms_emsStatus.minDsgSoc` -> `{"moduleType": 2, "operateType": "dsgCfg", "params": {"minDsgSoc": "VALUE"}}` [0 - 30])
- Backup Reserve Level (`pd.bpPowerSoc` -> `{"moduleType": 1, "operateType": "watthConfig", "params": {"isConfig": 1, "bpPowerSoc": "VALUE", "minDsgSoc": 0, "minChgSoc": 0}}` [5 - 100])
- Generator Auto Start Level (`bms_emsStatus.minOpenOilEb` -> `{"moduleType": 2, "operateType": "closeOilSoc", "params": {"closeOilSoc": "VALUE"}}` [0 - 30])
- Generator Auto Stop Level (`bms_emsStatus.maxCloseOilEb` -> `{"moduleType": 2, "operateType": "openOilSoc", "params": {"openOilSoc": "VALUE"}}` [50 - 100])
- AC Charging Power (`mppt.cfgChgWatts` -> `{"moduleType": 5, "operateType": "acChgCfg", "params": {"chgWatts": "VALUE", "chgPauseFlag": 255}}` [200 - 1200])

*Selects*
- DC (12V) Charge Current (`mppt.dcChgCurrent` -> `{"moduleType": 5, "operateType": "dcChgCfg", "params": {"dcChgCfg": "VALUE"}}` [4A (4000), 6A (6000), 8A (8000)])
- Screen Timeout (`pd.lcdOffSec` -> `{"moduleType": 1, "operateType": "lcdCfg", "params": {"brighLevel": 255, "delayOff": "VALUE"}}` [Never (0), 10 sec (10), 30 sec (30), 1 min (60), 5 min (300), 30 min (1800)])
- Unit Timeout (`pd.standbyMin` -> `{"moduleType": 1, "operateType": "standbyTime", "params": {"standbyMin": "VALUE"}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])
- AC Timeout (`mppt.acStandbyMins` -> `{"moduleType": 5, "operateType": "standbyTime", "params": {"standbyMins": "VALUE"}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])
- DC (12V) Timeout (`mppt.carStandbyMin` -> `{"moduleType": 5, "operateType": "carStandby", "params": {"standbyMins": "VALUE"}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])


