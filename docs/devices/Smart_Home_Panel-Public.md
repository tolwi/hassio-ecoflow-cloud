## Smart_Home_Panel

*Sensors*
- Power Grid (`heartbeat.gridSta`)
- Battery Level (`heartbeat.backupBatPer`)
- Remaining Time (`heartbeat.backupChaTime`)
- Main Battery Temperature (`heartbeat.energyInfos[0].emsBatTemp`)
- Main Battery Input Power (`heartbeat.energyInfos[0].lcdInputWatts`) (energy:  _[Device Name]_ Main Battery Input  Energy)
- Main Battery Output Power (`heartbeat.energyInfos[0].outputPower`) (energy:  _[Device Name]_ Main Battery Output  Energy)
- Power Grid Today (`heartbeat.gridDayWatth`)
- Battery Today (`heartbeat.backupDayWatth`)

*Switches*
- EPS Mode (`'epsModeInfo.eps'` -> `{"operateType": "TCP", "params": {"cmdSet": 11, "id": 24, "eps": "VALUE"}}`)
- Main Battery Charge (`heartbeat.backupCmdChCtrlInfos[0].ctrlSta` -> `{"operateType": "TCP", "params": {"cmdSet": 11, "id": 17, "sta": 2, "ctrlMode": 1, "ch": 10}}`)

*Sliders (numbers)*
- Min Discharge Level (`'backupChaDiscCfg.discLower'` -> `{"operateType": "TCP", "params": {"cmdSet": 11, "id": 29, "discLower": "VALUE", "forceChargeHigh": 100}}` [0 - 30])
- Max Charge Level (`'backupChaDiscCfg.forceChargeHigh'` -> `{"operateType": "TCP", "params": {"cmdSet": 11, "id": 29, "forceChargeHigh": "VALUE", "discLower": 0}}` [50 - 100])

*Selects*


