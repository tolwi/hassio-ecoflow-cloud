## DELTA_3_Max_Plus

*Sensors*
- Main Battery Level (`cmsBattSoc`)
- Battery Charging State (`cmsChgDsgState`)
- Total In Power (`powInSumW`) (energy:  _[Device Name]_ Total In  Energy)
- Total Out Power (`powOutSumW`) (energy:  _[Device Name]_ Total Out  Energy)
- AC In Power (`powGetAcIn`)
- Solar In Power (`powGetPv`)
- Solar 2 In Power (`powGetPv2`)
- DC Out Power (`powGet12v`)
- Type-C (1) Out Power (`powGetTypec1`)
- Type-C (2) Out Power (`powGetTypec2`)
- Type-C (3) Out Power (`powGetTypec3`)
- USB QC (1) Out Power (`powGetQcusb1`)
- USB QC (2) Out Power (`powGetQcusb2`)
- Charge Remaining Time (`cmsChgRemTime`)
- Discharge Remaining Time (`cmsDsgRemTime`)
- Status (Scheduled)

*Switches*
- AC Output (`flowInfoAcOut` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgAcOutOpen": true}}`)
- AC2 Output (`flowInfoAc2Out` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgAc2OutOpen": true}}`)
- DC Output (`flowInfo12v` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgDc12vOutOpen": true}}`)
- X-Boost Enabled (`xboostEn` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgXboostEn": true}}`)
- Beeper (`enBeep` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgBeepEn": true}}`)
- Backup Reserve Enabled (`energyBackupEn` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgEnergyBackup": {"energyBackupEn": true}}}`)
- Bypass Output Disabled (`bypassOutDisable` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgBypassOutDisable": true}}`)

*Sliders (numbers)*
- Max Charge Level (`cmsMaxChgSoc` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgMaxChgSoc": "VALUE"}}` [50 - 100])
- Min Discharge Level (`cmsMinDsgSoc` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgMinDsgSoc": "VALUE"}}` [0 - 30])
- Backup Reserve Level (`backupReverseSoc` -> `{"sn": "SN", "cmdId": 17, "dirDest": 1, "dirSrc": 1, "cmdFunc": 254, "dest": 2, "params": {"cfgBackupReverseSoc": "VALUE"}}` [0 - 50])


