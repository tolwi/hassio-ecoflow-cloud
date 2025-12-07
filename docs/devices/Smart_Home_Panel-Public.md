## Smart_Home_Panel

*Sensors*
- Power Grid (`heartbeat.gridSta`)
- Battery Level (`heartbeat.backupBatPer`)
- Discharge Remaining Time (`heartbeat.backupChaTime`)
- Main Battery Level (`heartbeat.energyInfos[0].batteryPercentage`)
- Main Charge Remaining Time (`heartbeat.energyInfos[0].chargeTime`)
- Main Discharge Remaining Time (`heartbeat.energyInfos[0].dischargeTime`)
- Main Battery Temperature (`heartbeat.energyInfos[0].emsBatTemp`)
- Main Battery Output Power (`heartbeat.energyInfos[0].outputPower`)

*Switches*
- EPS Mode (`'epsModeInfo.eps'` -> `{"operateType": "TCP", "params": {"cmdSet": 11, "id": 24, "eps": "VALUE"}}`)

*Sliders (numbers)*
- Backup Discharge Lower Limit (`'backupChaDiscCfg.discLower'` -> `{"operateType": "TCP", "params": {"cmdSet": 11, "id": 29, "discLower": "VALUE", "forceChargeHigh": 100}}` [0 - 30])
- Backup Force Charge High Limit (`'backupChaDiscCfg.forceChargeHigh'` -> `{"operateType": "TCP", "params": {"cmdSet": 11, "id": 29, "forceChargeHigh": "VALUE", "discLower": 0}}` [50 - 100])

*Selects*


