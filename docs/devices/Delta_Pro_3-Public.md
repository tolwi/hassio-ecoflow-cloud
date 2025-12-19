## Delta_Pro_3

*Sensors*
- Main Battery Level (`bmsBattSoc`)
- Main Design Capacity (`bmsDesignCap`)   _(disabled)_
- Charging/Discharging State (`cmsChgDsgState`)   _(disabled)_
- BMS Run State (`cmsBmsRunState`)   _(disabled)_
- Battery Level (`cmsBattSoc`)
- Max Cell Temperature (`bmsMaxCellTemp`)   _(disabled)_
- Min Cell Temperature (`bmsMinCellTemp`)   _(disabled)_
- Charge Remaining Time (`bmsChgRemTime`)
- Discharge Remaining Time (`bmsDsgRemTime`)
- Total Charging Time (`cmsChgRemTime`)
- Total Discharging Time (`cmsDsgRemTime`)
- Total In Power (`powInSumW`) (energy:  _[Device Name]_ Total In  Energy)
- Total Out Power (`powOutSumW`) (energy:  _[Device Name]_ Total Out  Energy)
- AC In Power (`powGetAcIn`)
- Real-time grid power (`powGetAcHvOut`)
- AC Out Power (`powGetAc`)
- 12V DC Output Power (`powGet12v`)
- 24V DC Output Power (`powGet24v`)
- Real-time low-voltage AC output power (`powGetAcLvOut`)
- Real-time power of the low-voltage AC output port (`powGetAcLvTt30Out`)
- Solar High Voltage Input Power (`powGetPvH`)
- Solar Low Voltage Input Power (`powGetPvL`)
- USB QC (1) Out Power (`powGetQcusb1`)
- USB QC (2) Out Power (`powGetQcusb2`)
- Type-C (1) Out Power (`powGetTypec1`)
- Type-C (2) Out Power (`powGetTypec2`)
- 5P8 Power I/O Port Power (`powGet5p8`)
- 4P8 Extra Battery Port 1 Power (`powGet4p81`)   _(auto)_
- 4P8 Extra Battery Port 2 Power (`powGet4p82`)   _(auto)_
- AC Input Frequency (`plugInInfoAcInFeq`)
- Status

*Switches*
- Beeper (`enBeep` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgBeepEn": "VALUE"}}`)
- AC HV Output Enabled (`cfgHvAcOutOpen` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgHvAcOutOpen": "VALUE"}}`)
- AC LV Output Enabled (`cfgLvAcOutOpen` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgLvAcOutOpen": "VALUE"}}`)
- 12V DC Output Enabled (`cfgDc12vOutOpen` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgDc12vOutOpen": "VALUE"}}`)
- 24V DC Output Enabled (`cfgDc24vOutOpen` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgDc24vOutOpen": "VALUE"}}`)
- X-Boost Enabled (`xboostEn` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgXboostEn": "VALUE"}}`)
- AC Energy Saving Enabled (`acEnergySavingOpen` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgAcEnergySavingOpen": "VALUE"}}`)
- Smart Generator Auto Start/Stop (`cmsOilSelfStart` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgCmsOilSelfStart": "VALUE"}}`)

*Sliders (numbers)*
- Max Charge Level (`cmsMaxChgSoc` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgMaxChgSoc": "VALUE"}}` [50 - 100])
- Min Discharge Level (`cmsMinDsgSoc` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgMinDsgSoc": "VALUE"}}` [0 - 30])
- Smart Generator Start SOC (`cmsOilOnSoc` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgCmsOilOnSoc": "VALUE"}}` [0 - 100])
- Smart Generator Stop SOC (`cmsOilOffSoc` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgCmsOilOffSoc": "VALUE"}}` [0 - 100])
- AC Charging Power (`cfgPlugInInfoAcInChgPowMax` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgPlugInInfoAcInChgPowMax": "VALUE"}}` [400 - 2900])

*Selects*
- Screen Timeout (`screenOffTime` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgScreenOffTime": "VALUE"}}` [Never (0), 10 sec (10), 30 sec (30), 1 min (60), 5 min (300), 30 min (1800)])
- AC Timeout (`acStandbyTime` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgAcStandbyTime": "VALUE"}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 4 hr (240), 6 hr (360), 12 hr (720), 24 hr (1440)])
- DC Timeout (`dcStandbyTime` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgDcStandbyTime": "VALUE"}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 6 hr (360), 12 hr (720)])
- Bluetooth Timeout (`bleStandbyTime` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgBleStandbyTime": "VALUE"}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 6 hr (360), 12 hr (720)])
- Device Timeout (`devStandbyTime` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgDevStandbyTime": "VALUE"}}` [Never (0), 30 min (30), 1 hr (60), 2 hr (120), 6 hr (360), 12 hr (720)])
- AC Output Type (`plugInInfoAcOutType` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgPlugInInfoAcOutType": "VALUE"}}` [HV+LV (0), HV Only (1), LV Only (2)])


