## Smart_Home_Panel

*Sensors*
- Battery Level (`heartbeat.backupBatPer`)
- Battery 1 Level (`heartbeat.energyInfos[0].batteryPercentage`)
- Battery 2 Level (`heartbeat.energyInfos[1].batteryPercentage`)   _(disabled)_
- Remaining Time (`heartbeat.backupChaTime`)
- Battery 1 Charge Remaining Time (`heartbeat.energyInfos[0].chargeTime`)   _(disabled)_
- Battery 2 Charge Remaining Time (`heartbeat.energyInfos[1].chargeTime`)   _(disabled)_
- Battery 1 Discharge Remaining Time (`heartbeat.energyInfos[0].dischargeTime`)   _(disabled)_
- Battery 2 Discharge Remaining Time (`heartbeat.energyInfos[1].dischargeTime`)   _(disabled)_
- Battery 1 Temperature (`heartbeat.energyInfos[0].emsBatTemp`)
- Battery 2 Temperature (`heartbeat.energyInfos[1].emsBatTemp`)   _(disabled)_
- Battery 1 Input Power (`heartbeat.energyInfos[0].lcdInputWatts`) (energy:  _[Device Name]_ Battery 1 Input  Energy)
- Battery 2 Input Power (`heartbeat.energyInfos[1].lcdInputWatts`)   _(disabled)_ (energy:  _[Device Name]_ Battery 2 Input  Energy)
- Battery 1 Output Power (`heartbeat.energyInfos[0].outputPower`) (energy:  _[Device Name]_ Battery 1 Output  Energy)
- Battery 2 Output Power (`heartbeat.energyInfos[1].outputPower`)   _(disabled)_ (energy:  _[Device Name]_ Battery 2 Output  Energy)
- Power Grid Today (`heartbeat.gridDayWatth`)
- Battery Today (`heartbeat.backupDayWatth`)
- Power Grid Voltage (`'gridInfo.gridVol'`)
- Power Grid Frequency (`'gridInfo.gridFreq'`)
- Battery 1 Current (`'loadChCurInfo.cur'[10]`)   _(disabled)_
- Battery 2 Current (`'loadChCurInfo.cur'[11]`)   _(disabled)_
- Circuit 1 Current (`'loadChCurInfo.cur'[0]`)   _(disabled)_
- Circuit 2 Current (`'loadChCurInfo.cur'[1]`)   _(disabled)_
- Circuit 3 Current (`'loadChCurInfo.cur'[2]`)   _(disabled)_
- Circuit 4 Current (`'loadChCurInfo.cur'[3]`)   _(disabled)_
- Circuit 5 Current (`'loadChCurInfo.cur'[4]`)   _(disabled)_
- Circuit 6 Current (`'loadChCurInfo.cur'[5]`)   _(disabled)_
- Circuit 7 Current (`'loadChCurInfo.cur'[6]`)   _(disabled)_
- Circuit 8 Current (`'loadChCurInfo.cur'[7]`)   _(disabled)_
- Circuit 9 Current (`'loadChCurInfo.cur'[8]`)   _(disabled)_
- Circuit 10 Current (`'loadChCurInfo.cur'[9]`)   _(disabled)_

*Binary sensors*
- Power Grid (`heartbeat.gridSta`)

*Switches*
- EPS Mode (`'epsModeInfo.eps'` -> `{"operateType": "TCP", "params": {"cmdSet": 11, "id": 24, "eps": "VALUE"}}`)
- Battery 1 Charge (`heartbeat.backupCmdChCtrlInfos[0].ctrlSta` -> `{"operateType": "TCP", "params": {"cmdSet": 11, "id": 17, "sta": 2, "ctrlMode": 1, "ch": 10}}`)
- Battery 2 Charge (`heartbeat.backupCmdChCtrlInfos[1].ctrlSta` -> `{"operateType": "TCP", "params": {"cmdSet": 11, "id": 17, "sta": 2, "ctrlMode": 1, "ch": 11}}`)

*Sliders (numbers)*
- Min Discharge Level (`'backupChaDiscCfg.discLower'` -> `{"operateType": "TCP", "params": {"cmdSet": 11, "id": 29, "discLower": "VALUE", "forceChargeHigh": 100}}` [0 - 30])
- Max Charge Level (`'backupChaDiscCfg.forceChargeHigh'` -> `{"operateType": "TCP", "params": {"cmdSet": 11, "id": 29, "forceChargeHigh": "VALUE", "discLower": 0}}` [50 - 100])


