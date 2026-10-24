## Smart_Home_Panel_2

*Sensors*
- Status (Scheduled)
- AC In Power (`'wattInfo.gridWatt'`) (energy:  _[Device Name]_ AC In  Energy)
- AC Out Power (`'wattInfo.allHallWatt'`) (energy:  _[Device Name]_ AC Out  Energy)
- Battery Level (`'backupIncreInfo.backupBatPer'`)
- Discharge Remaining Time (`'backupInfo.backupDischargeTime'`)
- Power Grid Voltage (`'pd303_mc.masterIncreInfo.gridVol'`)   _(disabled)_
- Relay 1 Operation Count (`'pd303_mc.masterIncreInfo.masterRly1Cnt'`)   _(disabled)_
- Relay 2 Operation Count (`'pd303_mc.masterIncreInfo.masterRly2Cnt'`)   _(disabled)_
- Relay 3 Operation Count (`'pd303_mc.masterIncreInfo.masterRly3Cnt'`)   _(disabled)_
- Relay 4 Operation Count (`'pd303_mc.masterIncreInfo.masterRly4Cnt'`)   _(disabled)_
- Battery 1 Level (`'backupIncreInfo.Energy1Info.batteryPercentage'`)   _(disabled)_
- Battery 2 Level (`'backupIncreInfo.Energy2Info.batteryPercentage'`)   _(disabled)_
- Battery 3 Level (`'backupIncreInfo.Energy3Info.batteryPercentage'`)   _(disabled)_
- Battery 1 Power (`'wattInfo.chWatt'[0]`)   _(disabled)_ (energy:  _[Device Name]_ Battery 1  Energy)
- Battery 2 Power (`'wattInfo.chWatt'[1]`)   _(disabled)_ (energy:  _[Device Name]_ Battery 2  Energy)
- Battery 3 Power (`'wattInfo.chWatt'[2]`)   _(disabled)_ (energy:  _[Device Name]_ Battery 3  Energy)
- Breaker1 Power (`'loadInfo.hall1Watt'[0]`) (energy:  _[Device Name]_ Breaker1  Energy)
- Breaker2 Power (`'loadInfo.hall1Watt'[1]`) (energy:  _[Device Name]_ Breaker2  Energy)
- Breaker3 Power (`'loadInfo.hall1Watt'[2]`) (energy:  _[Device Name]_ Breaker3  Energy)
- Breaker4 Power (`'loadInfo.hall1Watt'[3]`) (energy:  _[Device Name]_ Breaker4  Energy)
- Breaker5 Power (`'loadInfo.hall1Watt'[4]`) (energy:  _[Device Name]_ Breaker5  Energy)
- Breaker6 Power (`'loadInfo.hall1Watt'[5]`) (energy:  _[Device Name]_ Breaker6  Energy)
- Breaker7 Power (`'loadInfo.hall1Watt'[6]`) (energy:  _[Device Name]_ Breaker7  Energy)
- Breaker8 Power (`'loadInfo.hall1Watt'[7]`) (energy:  _[Device Name]_ Breaker8  Energy)
- Breaker9 Power (`'loadInfo.hall1Watt'[8]`) (energy:  _[Device Name]_ Breaker9  Energy)
- Breaker10 Power (`'loadInfo.hall1Watt'[9]`) (energy:  _[Device Name]_ Breaker10  Energy)
- Breaker11 Power (`'loadInfo.hall1Watt'[10]`) (energy:  _[Device Name]_ Breaker11  Energy)
- Breaker12 Power (`'loadInfo.hall1Watt'[11]`) (energy:  _[Device Name]_ Breaker12  Energy)

*Binary sensors*
- Power Grid (`'pd303_mc.masterIncreInfo.gridSta'`)
- In Storm Mode (`'pd303_mc.inStormMode'`)

*Switches*
- EPS Mode (`epsModeInfo` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"epsModeInfo": false, "smartBackupMode": 0}}`)
- Storm Guard (`stormIsEnable` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"stormIsEnable": false}}`)
- Battery 1 (`'ch1EnableSet'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"ch1EnableSet": "VALUE"}}`)
- Battery 2 (`'ch2EnableSet'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"ch2EnableSet": "VALUE"}}`)
- Battery 3 (`'ch3EnableSet'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"ch3EnableSet": "VALUE"}}`)
- Battery 1 Force Charge (`ch1ForceCharge` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"ch1ForceCharge": "VALUE"}}`)
- Battery 2 Force Charge (`ch2ForceCharge` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"ch2ForceCharge": "VALUE"}}`)
- Battery 3 Force Charge (`ch3ForceCharge` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"ch3ForceCharge": "VALUE"}}`)
- Breaker 1 (`'pd303_mc.loadIncreInfo.hall1IncreInfo.ch1Sta.loadSta'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"loadIncreInfo": {"hall1IncreInfo": {"ch1Sta": {"loadSta": 6666}}}}}`)
- Breaker 2 (`'pd303_mc.loadIncreInfo.hall1IncreInfo.ch2Sta.loadSta'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"loadIncreInfo": {"hall1IncreInfo": {"ch2Sta": {"loadSta": 6666}}}}}`)
- Breaker 3 (`'pd303_mc.loadIncreInfo.hall1IncreInfo.ch3Sta.loadSta'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"loadIncreInfo": {"hall1IncreInfo": {"ch3Sta": {"loadSta": 6666}}}}}`)
- Breaker 4 (`'pd303_mc.loadIncreInfo.hall1IncreInfo.ch4Sta.loadSta'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"loadIncreInfo": {"hall1IncreInfo": {"ch4Sta": {"loadSta": 6666}}}}}`)
- Breaker 5 (`'pd303_mc.loadIncreInfo.hall1IncreInfo.ch5Sta.loadSta'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"loadIncreInfo": {"hall1IncreInfo": {"ch5Sta": {"loadSta": 6666}}}}}`)
- Breaker 6 (`'pd303_mc.loadIncreInfo.hall1IncreInfo.ch6Sta.loadSta'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"loadIncreInfo": {"hall1IncreInfo": {"ch6Sta": {"loadSta": 6666}}}}}`)
- Breaker 7 (`'pd303_mc.loadIncreInfo.hall1IncreInfo.ch7Sta.loadSta'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"loadIncreInfo": {"hall1IncreInfo": {"ch7Sta": {"loadSta": 6666}}}}}`)
- Breaker 8 (`'pd303_mc.loadIncreInfo.hall1IncreInfo.ch8Sta.loadSta'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"loadIncreInfo": {"hall1IncreInfo": {"ch8Sta": {"loadSta": 6666}}}}}`)
- Breaker 9 (`'pd303_mc.loadIncreInfo.hall1IncreInfo.ch9Sta.loadSta'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"loadIncreInfo": {"hall1IncreInfo": {"ch9Sta": {"loadSta": 6666}}}}}`)
- Breaker 10 (`'pd303_mc.loadIncreInfo.hall1IncreInfo.ch10Sta.loadSta'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"loadIncreInfo": {"hall1IncreInfo": {"ch10Sta": {"loadSta": 6666}}}}}`)
- Breaker 11 (`'pd303_mc.loadIncreInfo.hall1IncreInfo.ch11Sta.loadSta'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"loadIncreInfo": {"hall1IncreInfo": {"ch11Sta": {"loadSta": 6666}}}}}`)
- Breaker 12 (`'pd303_mc.loadIncreInfo.hall1IncreInfo.ch12Sta.loadSta'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"loadIncreInfo": {"hall1IncreInfo": {"ch12Sta": {"loadSta": 6666}}}}}`)

*Sliders (numbers)*
- Backup Reserve Level (`'backupReserveSoc'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"backupReserveSoc": "VALUE"}}` [10 - 50])
- AC Charging Power (`'chargeWattPower'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"chargeWattPower": "VALUE"}}` [500 - 7200])
- Max Charge Level (`'foceChargeHight'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"foceChargeHight": "VALUE"}}` [80 - 100])
- Generator Battery Charging Power (`'pd303_mc.oilEngineWatt'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"oilEngineWatt": "VALUE"}}` [500 - 3000])
- Generator Max Output Power (`'oilMaxOutputWatt'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"oilMaxOutputWatt": "VALUE"}}` [3000 - 12000])

*Selects*
- Operating Mode (`'smartBackupMode'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"smartBackupMode": "VALUE", "epsModeInfo": false}}` [None (0), TOU (1), Self-powered (2), Scheduled tasks (3)])
- Generator Type (`'pd303_mc.oilType'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"oilType": "VALUE"}}` [Not Set (0), Single-Phase (120V) (1), Split-Phase (240V) (2)])


