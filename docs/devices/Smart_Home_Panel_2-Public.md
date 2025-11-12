## Smart_Home_Panel_2

*Sensors*
- Status (Scheduled)
- AC In Power (`'wattInfo.gridWatt'`) (energy:  _[Device Name]_ AC In  Energy)
- AC Out Power (`'wattInfo.allHallWatt'`) (energy:  _[Device Name]_ AC Out  Energy)
- Battery Level (`'backupIncreInfo.backupBatPer'`)
- Discharge Remaining Time (`'backupInfo.backupDischargeTime'`)
- Breaker 1 Power (`'loadInfo.hall1Watt'[0]`) (energy:  _[Device Name]_ Breaker 1  Energy)
- Breaker 2 Power (`'loadInfo.hall1Watt'[1]`) (energy:  _[Device Name]_ Breaker 2  Energy)
- Breaker 3 Power (`'loadInfo.hall1Watt'[2]`) (energy:  _[Device Name]_ Breaker 3  Energy)
- Breaker 4 Power (`'loadInfo.hall1Watt'[3]`) (energy:  _[Device Name]_ Breaker 4  Energy)
- Breaker 5 Power (`'loadInfo.hall1Watt'[4]`) (energy:  _[Device Name]_ Breaker 5  Energy)
- Breaker 6 Power (`'loadInfo.hall1Watt'[5]`) (energy:  _[Device Name]_ Breaker 6  Energy)
- Breaker 7 Power (`'loadInfo.hall1Watt'[6]`) (energy:  _[Device Name]_ Breaker 7  Energy)
- Breaker 8 Power (`'loadInfo.hall1Watt'[7]`) (energy:  _[Device Name]_ Breaker 8  Energy)
- Breaker 9 Power (`'loadInfo.hall1Watt'[8]`) (energy:  _[Device Name]_ Breaker 9  Energy)
- Breaker 10 Power (`'loadInfo.hall1Watt'[9]`) (energy:  _[Device Name]_ Breaker 10  Energy)
- Breaker 11 Power (`'loadInfo.hall1Watt'[10]`) (energy:  _[Device Name]_ Breaker 11  Energy)
- Breaker 12 Power (`'loadInfo.hall1Watt'[11]`) (energy:  _[Device Name]_ Breaker 12  Energy)
- Power Grid (`'pd303_mc.masterIncreInfo.gridSta'`)
- Power Grid Voltage (`'pd303_mc.masterIncreInfo.gridVol'`)   _(disabled)_
- In Storm Mode (`'pd303_mc.inStormMode'`)
- Relay 1 Operation Count (`'pd303_mc.masterIncreInfo.masterRly1Cnt'`)   _(disabled)_
- Relay 2 Operation Count (`'pd303_mc.masterIncreInfo.masterRly2Cnt'`)   _(disabled)_
- Relay 3 Operation Count (`'pd303_mc.masterIncreInfo.masterRly3Cnt'`)   _(disabled)_
- Relay 4 Operation Count (`'pd303_mc.masterIncreInfo.masterRly4Cnt'`)   _(disabled)_
- Battery 1 Level (`'backupIncreInfo.Energy1Info.batteryPercentage'`)   _(disabled)_
- Battery 2 Level (`'backupIncreInfo.Energy2Info.batteryPercentage'`)   _(disabled)_
- Battery 3 Level (`'backupIncreInfo.Energy3Info.batteryPercentage'`)   _(disabled)_
- Battery 1 Power (`'wattInfo.chWatt'[0]`)   _(disabled)_
- Battery 2 Power (`'wattInfo.chWatt'[1]`)   _(disabled)_
- Battery 3 Power (`'wattInfo.chWatt'[2]`)   _(disabled)_

*Switches*
- EPS Mode (`epsModeInfo` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"epsModeInfo": false, "smartBackupMode": 0}}`)
- Storm Guard (`stormIsEnable` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"stormIsEnable": false}}`)
- Battery 1 (`'ch1EnableSet'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"ch1EnableSet": "VALUE"}}`)
- Battery 2 (`'ch2EnableSet'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"ch2EnableSet": "VALUE"}}`)
- Battery 3 (`'ch3EnableSet'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"ch3EnableSet": "VALUE"}}`)
- Battery 1 Force Charge (`ch1ForceCharge` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"ch1ForceCharge": "VALUE"}}`)
- Battery 2 Force Charge (`ch2ForceCharge` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"ch2ForceCharge": "VALUE"}}`)
- Battery 3 Force Charge (`ch3ForceCharge` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"ch3ForceCharge": "VALUE"}}`)

*Sliders (numbers)*
- Backup Reserve Level (`'backupReserveSoc'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"backupReserveSoc": "VALUE"}}` [10 - 50])
- AC Charging Power (`'chargeWattPower'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"chargeWattPower": "VALUE"}}` [500 - 7200])
- Max Charge Level (`'foceChargeHight'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"foceChargeHight": "VALUE"}}` [80 - 100])
- Generator Battery Charging Power (`'pd303_mc.oilEngineWatt'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"oilEngineWatt": "VALUE"}}` [500 - 3000])
- Generator Max Output Power (`'oilMaxOutputWatt'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"oilMaxOutputWatt": "VALUE"}}` [3000 - 12000])

*Selects*
- Operating Mode (`'smartBackupMode'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"smartBackupMode": "VALUE", "epsModeInfo": false}}` [None (0), TOU (1), Self-powered (2), Scheduled tasks (3)])
- Generator Type (`'pd303_mc.oilType'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"oilType": "VALUE"}}` [Not Set (0), Single-Phase (120V) (1), Split-Phase (240V) (2)])


