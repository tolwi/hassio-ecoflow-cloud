## Stream_5000

*Sensors*
- Battery Level (`sysEnergyStreamReport.bpSoc`)
- Power PV Sum (`sysEnergyStreamReport.pvPwr`)
- Power Battery (`sysEnergyStreamReport.bpPwr`)
- Power Sys Load (`sysEnergyStreamReport.loadPwr`)
- Power Grid (`sysEnergyStreamReport.gridPwr`)
- Power AC SYS (`sysEnergyStreamReport.onGridPwr`)
- Status

*Switches*
- Backup Reserve (`bpBackupConfig.backupSocOnOff` -> `{"sn": "SN", "cmdId": 38, "cmdFunc": 254, "dirDest": 1, "dirSrc": 1, "dest": 2, "needAck": true, "params": {"bpBackupConfig": {"backupSocOnOff": true}}}`)
- Feed-in Limit (`powerParameterConfig.feedToGridLimitOnOff` -> `{"sn": "SN", "cmdId": 38, "cmdFunc": 254, "dirDest": 1, "dirSrc": 1, "dest": 2, "needAck": true, "params": {"powerParameterConfig": {"feedToGridLimitOnOff": true}}}`)
- AC Socket (`devSwitch.acSocketOnoff` -> `{"sn": "SN", "cmdId": 38, "cmdFunc": 254, "dirDest": 1, "dirSrc": 1, "dest": 2, "needAck": true, "params": {"devSwitch": {"acSocketOnoff": true}}}`)

*Sliders (numbers)*
- Backup Reserve Level (`bpBackupConfig.backupSoc` -> `{"sn": "SN", "cmdId": 38, "cmdFunc": 254, "dirDest": 1, "dirSrc": 1, "dest": 2, "needAck": true, "params": {"bpBackupConfig": {"backupSocOnOff": true, "backupSoc": 6666}}}` [0 - 100])

*Selects*
- Operating Mode (`workMode` -> `{"sn": "SN", "cmdId": 38, "cmdFunc": 254, "dirDest": 1, "dirSrc": 1, "dest": 2, "needAck": true, "params": {"workMode": "VALUE"}}` [Self consumption (SELF_CONSUMPTION), AI mode (AI_MODE), Timer task (TIMER_TASK), Time of use (POU_MODE), Emergency stop (EMERGENCY_STOP)])


