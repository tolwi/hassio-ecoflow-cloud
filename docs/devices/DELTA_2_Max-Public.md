## DELTA_2_Max

*Sensors*
- Cumulative Capacity Charge (mAh) (`bms_bmsInfo.accuChgCap`)   _(disabled)_
- Cumulative Energy Charge (Wh) (`bms_bmsInfo.accuChgEnergy`)
- Cumulative Capacity Discharge (mAh) (`bms_bmsInfo.accuDsgCap`)   _(disabled)_
- Cumulative Energy Discharge (Wh) (`bms_bmsInfo.accuDsgEnergy`)
- Main Battery Level (`bms_bmsStatus.soc`)
- Main Design Capacity (`bms_bmsStatus.designCap`)   _(disabled)_
- Main Full Capacity (`bms_bmsStatus.fullCap`)   _(disabled)_
- Main Remain Capacity (`bms_bmsStatus.remainCap`)   _(disabled)_
- State of Health (`bms_bmsStatus.soh`)
- Battery Level (`bms_emsStatus.lcdShowSoc`)
- Total In Power (`pd.wattsInSum`)
- Total Out Power (`pd.wattsOutSum`)
- AC In Power (`inv.inputWatts`)
- AC Out Power (`inv.outputWatts`)
- AC In Volts (`inv.acInVol`)
- AC Out Volts (`inv.invOutVol`)
- Solar (1) In Power (`mppt.inWatts`)
- Solar (2) In Power (`mppt.pv2InWatts`)
- Solar (1) In Volts (`mppt.inVol`)
- Solar (2) In Volts (`mppt.pv2InVol`)
- Solar (1) In Amps (`mppt.inAmp`)
- Solar (2) In Amps (`mppt.pv2InAmp`)
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
- Battery level SOC (`bms_bmsStatus.f32ShowSoc`)   _(auto)_
- Slave 1 Cumulative Capacity Charge (mAh) (`bms_slave_bmsSlaveInfo_1.accuChgCap`)   _(auto)_
- Slave 1 Cumulative Energy Charge (Wh) (`bms_slave_bmsSlaveInfo_1.accuChgEnergy`)   _(disabled)_
- Slave 1 Cumulative Capacity Discharge (mAh) (`bms_slave_bmsSlaveInfo_1.accuDsgCap`)   _(auto)_
- Slave 1 Cumulative Energy Discharge (Wh) (`bms_slave_bmsSlaveInfo_1.accuDsgEnergy`)   _(disabled)_
- Slave 1 Battery Level (`bms_slave_bmsSlaveStatus_1.soc`)   _(auto)_
- Slave 1 Design Capacity (`bms_slave_bmsSlaveStatus_1.designCap`)   _(disabled)_
- Slave 1 Full Capacity (`bms_slave_bmsSlaveStatus_1.fullCap`)   _(disabled)_
- Slave 1 Remain Capacity (`bms_slave_bmsSlaveStatus_1.remainCap`)   _(disabled)_
- Slave 1 Battery Temperature (`bms_slave_bmsSlaveStatus_1.temp`)   _(auto)_
- Slave 1 Min Cell Temperature (`bms_slave_bmsSlaveStatus_1.minCellTemp`)   _(disabled)_
- Slave 1 Max Cell Temperature (`bms_slave_bmsSlaveStatus_1.maxCellTemp`)   _(disabled)_
- Slave 1 Battery Volts (`bms_slave_bmsSlaveStatus_1.vol`)   _(disabled)_
- Slave 1 Min Cell Volts (`bms_slave_bmsSlaveStatus_1.minCellVol`)   _(disabled)_
- Slave 1 Max Cell Volts (`bms_slave_bmsSlaveStatus_1.maxCellVol`)   _(disabled)_
- Slave 1 Cycles (`bms_slave_bmsSlaveStatus_1.cycles`)   _(auto)_
- Slave 1 State of Health (`bms_slave_bmsSlaveStatus_1.soh`)   _(auto)_
- Slave 1 In Power (`bms_slave_bmsSlaveStatus_1.inputWatts`)   _(auto)_
- Slave 1 Out Power (`bms_slave_bmsSlaveStatus_1.outputWatts`)   _(auto)_
- Slave 1 Battery level SOC (`bms_slave_bmsSlaveStatus_1.f32ShowSoc`)   _(auto)_
- Slave 2 Cumulative Capacity Charge (mAh) (`bms_slave_bmsSlaveInfo_2.accuChgCap`)   _(disabled)_
- Slave 2 Cumulative Energy Charge (Wh) (`bms_slave_bmsSlaveInfo_2.accuChgEnergy`)   _(auto)_
- Slave 2 Cumulative Capacity Discharge (mAh) (`bms_slave_bmsSlaveInfo_2.accuDsgCap`)   _(disabled)_
- Slave 2 Cumulative Energy Discharge (Wh) (`bms_slave_bmsSlaveInfo_2.accuDsgEnergy`)   _(auto)_
- Slave 2 Battery Level (`bms_slave_bmsSlaveStatus_2.soc`)   _(auto)_
- Slave 2 Design Capacity (`bms_slave_bmsSlaveStatus_2.designCap`)   _(disabled)_
- Slave 2 Full Capacity (`bms_slave_bmsSlaveStatus_2.fullCap`)   _(disabled)_
- Slave 2 Remain Capacity (`bms_slave_bmsSlaveStatus_2.remainCap`)   _(disabled)_
- Slave 2 Battery Temperature (`bms_slave_bmsSlaveStatus_2.temp`)   _(auto)_
- Slave 2 Min Cell Temperature (`bms_slave_bmsSlaveStatus_2.minCellTemp`)   _(disabled)_
- Slave 2 Max Cell Temperature (`bms_slave_bmsSlaveStatus_2.maxCellTemp`)   _(disabled)_
- Slave 2 Battery Volts (`bms_slave_bmsSlaveStatus_2.vol`)   _(disabled)_
- Slave 2 Min Cell Volts (`bms_slave_bmsSlaveStatus_2.minCellVol`)   _(disabled)_
- Slave 2 Max Cell Volts (`bms_slave_bmsSlaveStatus_2.maxCellVol`)   _(disabled)_
- Slave 2 Cycles (`bms_slave_bmsSlaveStatus_2.cycles`)   _(auto)_
- Slave 2 State of Health (`bms_slave_bmsSlaveStatus_2.soh`)   _(auto)_
- Slave 2 In Power (`bms_slave_bmsSlaveStatus_2.inputWatts`)   _(auto)_
- Slave 2 Out Power (`bms_slave_bmsaSlaveStatus_2.outputWatts`)   _(auto)_
- Slave 2 Battery level SOC (`bms_slave_bmsSlaveStatus_2.f32ShowSoc`)   _(auto)_
- Status
- Status (Scheduled)

*Switches*
- Beeper (`pd.beepMode` -> `{"moduleType": 1, "operateType": "quietCfg", "moduleSn": "SN", "params": {"enabled": "VALUE"}}`)
- USB Enabled (`pd.dcOutState` -> `{"moduleType": 1, "operateType": "dcOutCfg", "moduleSn": "SN", "params": {"enabled": "VALUE"}}`)
- AC Always On (`pd.newAcAutoOnCfg` -> `{"moduleType": 1, "operateType": "newAcAutoOnCfg", "moduleSn": "SN", "params": {"enabled": "VALUE", "minAcSoc": 5}}`)
- AC Enabled (`inv.cfgAcEnabled` -> `{"moduleType": 3, "operateType": "acOutCfg", "moduleSn": "SN", "params": {"enabled": "VALUE", "out_voltage": -1, "out_freq": 255, "xboost": 255}}`)
- X-Boost Enabled (`inv.cfgAcXboost` -> `{"moduleType": 3, "operateType": "acOutCfg", "moduleSn": "SN", "params": {"xboost": "VALUE"}}`)
- DC (12V) Enabled (`pd.carState` -> `{"moduleType": 5, "operateType": "mpptCar", "params": {"enabled": "VALUE"}}`)
- Backup Reserve Enabled (`pd.watchIsConfig` -> `{"moduleType": 1, "operateType": "watthConfig", "params": {"bpPowerSoc": 333300, "minChgSoc": 0, "isConfig": "VALUE", "minDsgSoc": 0}}`)

*Sliders (numbers)*
- Max Charge Level (`bms_emsStatus.maxChargeSoc` -> `{"moduleType": 2, "operateType": "upsConfig", "moduleSn": "SN", "params": {"maxChgSoc": "VALUE"}}` [50 - 100])
- Min Discharge Level (`bms_emsStatus.minDsgSoc` -> `{"moduleType": 2, "operateType": "dsgCfg", "moduleSn": "SN", "params": {"minDsgSoc": "VALUE"}}` [0 - 30])
- Backup Reserve Level (`pd.bpPowerSoc` -> `{"moduleType": 1, "operateType": "watthConfig", "params": {"isConfig": 1, "bpPowerSoc": "VALUE", "minDsgSoc": 0, "minChgSoc": 0}}` [5 - 100])
- Generator Auto Start Level (`bms_emsStatus.minOpenOilEbSoc` -> `{"moduleType": 2, "operateType": "openOilSoc", "moduleSn": "SN", "params": {"openOilSoc": "VALUE"}}` [0 - 30])
- Generator Auto Stop Level (`bms_emsStatus.maxCloseOilEbSoc` -> `{"moduleType": 2, "operateType": "closeOilSoc", "moduleSn": "SN", "params": {"closeOilSoc": "VALUE"}}` [50 - 100])
- AC Charging Power (`inv.SlowChgWatts` -> `{"moduleType": 3, "operateType": "acChgCfg", "moduleSn": "SN", "params": {"slowChgWatts": "VALUE", "fastChgWatts": 2000, "chgPauseFlag": 0}}` [200 - 2400])

*Selects*
- Screen Timeout (`pd.lcdOffSec` -> `{"moduleType": 1, "operateType": "lcdCfg", "moduleSn": "SN", "params": {"brighLevel": 255, "delayOff": "VALUE"}}` [Never (0), 10 sec (10), 30 sec (30), 1 min (60), 5 min (300), 30 min (1800)])
- Unit Timeout (`inv.standbyMin` -> `{"moduleType": 1, "operateType": "standbyTime", "moduleSn": "SN", "params": {"standbyMin": "VALUE"}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])
- AC Timeout (`mppt.carStandbyMin` -> `{"moduleType": 5, "operateType": "standbyTime", "moduleSn": "SN", "params": {"standbyMins": "VALUE"}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])


