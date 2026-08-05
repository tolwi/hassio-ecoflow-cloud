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
- Breaker 1 Power (`'infoList'[0].chWatt`) (energy:  _[Device Name]_ Breaker 1  Energy)
- Breaker 2 Power (`'infoList'[1].chWatt`) (energy:  _[Device Name]_ Breaker 2  Energy)
- Breaker 3 Power (`'infoList'[2].chWatt`) (energy:  _[Device Name]_ Breaker 3  Energy)
- Breaker 4 Power (`'infoList'[3].chWatt`) (energy:  _[Device Name]_ Breaker 4  Energy)
- Breaker 5 Power (`'infoList'[4].chWatt`) (energy:  _[Device Name]_ Breaker 5  Energy)
- Breaker 6 Power (`'infoList'[5].chWatt`) (energy:  _[Device Name]_ Breaker 6  Energy)
- Breaker 7 Power (`'infoList'[6].chWatt`) (energy:  _[Device Name]_ Breaker 7  Energy)
- Breaker 8 Power (`'infoList'[7].chWatt`) (energy:  _[Device Name]_ Breaker 8  Energy)
- Breaker 9 Power (`'infoList'[8].chWatt`) (energy:  _[Device Name]_ Breaker 9  Energy)
- Breaker 10 Power (`'infoList'[9].chWatt`) (energy:  _[Device Name]_ Breaker 10  Energy)
- Breaker 1 Battery Power (`infoList.breaker1.battery`) (energy:  _[Device Name]_ Breaker 1 Battery  Energy)
- Breaker 1 Grid Power (`infoList.breaker1.grid`) (energy:  _[Device Name]_ Breaker 1 Grid  Energy)
- Breaker 2 Battery Power (`infoList.breaker2.battery`) (energy:  _[Device Name]_ Breaker 2 Battery  Energy)
- Breaker 2 Grid Power (`infoList.breaker2.grid`) (energy:  _[Device Name]_ Breaker 2 Grid  Energy)
- Breaker 3 Battery Power (`infoList.breaker3.battery`) (energy:  _[Device Name]_ Breaker 3 Battery  Energy)
- Breaker 3 Grid Power (`infoList.breaker3.grid`) (energy:  _[Device Name]_ Breaker 3 Grid  Energy)
- Breaker 4 Battery Power (`infoList.breaker4.battery`) (energy:  _[Device Name]_ Breaker 4 Battery  Energy)
- Breaker 4 Grid Power (`infoList.breaker4.grid`) (energy:  _[Device Name]_ Breaker 4 Grid  Energy)
- Breaker 5 Battery Power (`infoList.breaker5.battery`) (energy:  _[Device Name]_ Breaker 5 Battery  Energy)
- Breaker 5 Grid Power (`infoList.breaker5.grid`) (energy:  _[Device Name]_ Breaker 5 Grid  Energy)
- Breaker 6 Battery Power (`infoList.breaker6.battery`) (energy:  _[Device Name]_ Breaker 6 Battery  Energy)
- Breaker 6 Grid Power (`infoList.breaker6.grid`) (energy:  _[Device Name]_ Breaker 6 Grid  Energy)
- Breaker 7 Battery Power (`infoList.breaker7.battery`) (energy:  _[Device Name]_ Breaker 7 Battery  Energy)
- Breaker 7 Grid Power (`infoList.breaker7.grid`) (energy:  _[Device Name]_ Breaker 7 Grid  Energy)
- Breaker 8 Battery Power (`infoList.breaker8.battery`) (energy:  _[Device Name]_ Breaker 8 Battery  Energy)
- Breaker 8 Grid Power (`infoList.breaker8.grid`) (energy:  _[Device Name]_ Breaker 8 Grid  Energy)
- Breaker 9 Battery Power (`infoList.breaker9.battery`) (energy:  _[Device Name]_ Breaker 9 Battery  Energy)
- Breaker 9 Grid Power (`infoList.breaker9.grid`) (energy:  _[Device Name]_ Breaker 9 Grid  Energy)
- Breaker 10 Battery Power (`infoList.breaker10.battery`) (energy:  _[Device Name]_ Breaker 10 Battery  Energy)
- Breaker 10 Grid Power (`infoList.breaker10.grid`) (energy:  _[Device Name]_ Breaker 10 Grid  Energy)
- Battery 1 Power (`'infoList'[10].chWatt`) (energy:  _[Device Name]_ Battery 1  Energy)
- Battery 2 Power (`'infoList'[11].chWatt`) (energy:  _[Device Name]_ Battery 2  Energy)
- Circuits Combined Power (`infoList.total_circuits`) (energy:  _[Device Name]_ Circuits Combined  Energy)
- Circuits Battery Demand Power (`infoList.total_circuits_battery`) (energy:  _[Device Name]_ Circuits Battery Demand  Energy)
- Circuits Grid Demand Power (`infoList.total_circuits_grid`) (energy:  _[Device Name]_ Circuits Grid Demand  Energy)
- Battery Combined Power (`infoList.total_battery_combined`) (energy:  _[Device Name]_ Battery Combined  Energy)
- Status

*Binary sensors*
- Power Grid (`heartbeat.gridSta`)

*Switches*
- EPS Mode (`'epsModeInfo.eps'` -> `{"operateType": "TCP", "params": {"cmdSet": 11, "id": 24, "eps": "VALUE"}}`)
- Scheduled Charge (`timeTask.cfg.comCfg.isEnable` -> `{"operateType": "TCP", "params": {"cfg": {"param": {"lowBattery": 95, "hightBattery": 100, "chChargeWatt": 2000, "chSta": [1, 1]}, "comCfg": {"timeScale": [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], "isCfg": 1, "type": 1, "timeRange": {"isCfg": 1, "isEnable": 1, "timeMode": 0, "startTime": {"sec": 0, "min": 0, "week": 1, "hour": 0, "month": 1, "year": 2020, "day": 1}, "endTime": {"sec": 0, "min": 0, "week": 1, "hour": 0, "month": 1, "year": 2030, "day": 1}}, "setTime": {"sec": 0, "min": 0, "week": 1, "hour": 0, "month": 1, "year": 2020, "day": 1}, "isEnable": 6666}}, "cfgIndex": 10, "cmdSet": 11, "id": 81}}`)
- Battery 1 Charge (`heartbeat.backupCmdChCtrlInfos[0].ctrlSta` -> `{"operateType": "TCP", "params": {"cmdSet": 11, "id": 17, "sta": 2, "ctrlMode": 1, "ch": 10}}`)
- Battery 2 Charge (`heartbeat.backupCmdChCtrlInfos[1].ctrlSta` -> `{"operateType": "TCP", "params": {"cmdSet": 11, "id": 17, "sta": 2, "ctrlMode": 1, "ch": 11}}`)

*Sliders (numbers)*
- Min Discharge Level (`'backupChaDiscCfg.discLower'` -> `{"operateType": "TCP", "params": {"cmdSet": 11, "id": 29, "discLower": "VALUE", "forceChargeHigh": 100}}` [0 - 30])
- Max Charge Level (`'backupChaDiscCfg.forceChargeHigh'` -> `{"operateType": "TCP", "params": {"cmdSet": 11, "id": 29, "forceChargeHigh": "VALUE", "discLower": 0}}` [50 - 100])
- Scheduled Charge Battery Level (`timeTask.cfg.param.hightBattery` -> `{"operateType": "TCP", "params": {"cfg": {"param": {"lowBattery": 6661, "hightBattery": 6666, "chChargeWatt": 2000, "chSta": [1, 1]}, "comCfg": {"timeScale": [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], "isCfg": 1, "type": 1, "timeRange": {"isCfg": 1, "isEnable": 1, "timeMode": 0, "startTime": {"sec": 0, "min": 0, "week": 1, "hour": 0, "month": 1, "year": 2020, "day": 1}, "endTime": {"sec": 0, "min": 0, "week": 1, "hour": 0, "month": 1, "year": 2030, "day": 1}}, "setTime": {"sec": 0, "min": 0, "week": 1, "hour": 0, "month": 1, "year": 2020, "day": 1}, "isEnable": 0}}, "cfgIndex": 10, "cmdSet": 11, "id": 81}}` [50 - 100])
- Scheduled Charge Power (`timeTask.cfg.param.chChargeWatt` -> `{"operateType": "TCP", "params": {"cfg": {"param": {"lowBattery": 95, "hightBattery": 100, "chChargeWatt": 6666, "chSta": [1, 1]}, "comCfg": {"timeScale": [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], "isCfg": 1, "type": 1, "timeRange": {"isCfg": 1, "isEnable": 1, "timeMode": 0, "startTime": {"sec": 0, "min": 0, "week": 1, "hour": 0, "month": 1, "year": 2020, "day": 1}, "endTime": {"sec": 0, "min": 0, "week": 1, "hour": 0, "month": 1, "year": 2030, "day": 1}}, "setTime": {"sec": 0, "min": 0, "week": 1, "hour": 0, "month": 1, "year": 2020, "day": 1}, "isEnable": 0}}, "cfgIndex": 10, "cmdSet": 11, "id": 81}}` [200 - 3400])

*Selects*
- Circuit 1 Mode (`heartbeat.loadCmdChCtrlInfos[0].ctrlSta` -> `_ command not available _` [Auto (0), Grid (0), Battery (1), Off (2)])
- Circuit 2 Mode (`heartbeat.loadCmdChCtrlInfos[1].ctrlSta` -> `_ command not available _` [Auto (0), Grid (0), Battery (1), Off (2)])
- Circuit 3 Mode (`heartbeat.loadCmdChCtrlInfos[2].ctrlSta` -> `_ command not available _` [Auto (0), Grid (0), Battery (1), Off (2)])
- Circuit 4 Mode (`heartbeat.loadCmdChCtrlInfos[3].ctrlSta` -> `_ command not available _` [Auto (0), Grid (0), Battery (1), Off (2)])
- Circuit 5 Mode (`heartbeat.loadCmdChCtrlInfos[4].ctrlSta` -> `_ command not available _` [Auto (0), Grid (0), Battery (1), Off (2)])
- Circuit 6 Mode (`heartbeat.loadCmdChCtrlInfos[5].ctrlSta` -> `_ command not available _` [Auto (0), Grid (0), Battery (1), Off (2)])
- Circuit 7 Mode (`heartbeat.loadCmdChCtrlInfos[6].ctrlSta` -> `_ command not available _` [Auto (0), Grid (0), Battery (1), Off (2)])
- Circuit 8 Mode (`heartbeat.loadCmdChCtrlInfos[7].ctrlSta` -> `_ command not available _` [Auto (0), Grid (0), Battery (1), Off (2)])
- Circuit 9 Mode (`heartbeat.loadCmdChCtrlInfos[8].ctrlSta` -> `_ command not available _` [Auto (0), Grid (0), Battery (1), Off (2)])
- Circuit 10 Mode (`heartbeat.loadCmdChCtrlInfos[9].ctrlSta` -> `_ command not available _` [Auto (0), Grid (0), Battery (1), Off (2)])
- Scheduled Charge Battery (`timeTask.cfg.param.chSta` -> `{"operateType": "TCP", "params": {"cfg": {"param": {"lowBattery": 95, "hightBattery": 100, "chChargeWatt": 2000, "chSta": 6666}, "comCfg": {"timeScale": [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], "isCfg": 1, "type": 1, "timeRange": {"isCfg": 1, "isEnable": 1, "timeMode": 0, "startTime": {"sec": 0, "min": 0, "week": 1, "hour": 0, "month": 1, "year": 2020, "day": 1}, "endTime": {"sec": 0, "min": 0, "week": 1, "hour": 0, "month": 1, "year": 2030, "day": 1}}, "setTime": {"sec": 0, "min": 0, "week": 1, "hour": 0, "month": 1, "year": 2020, "day": 1}, "isEnable": 0}}, "cfgIndex": 10, "cmdSet": 11, "id": 81}}` [Battery 1 ([1, 0]), Battery 2 ([0, 1]), Both ([1, 1])])


