## Smart_Home_Panel_2

*Sensors*
- AC In Power (`'wattInfo.gridWatt'`)
- Breaker 0 Energy (`'loadInfo.hall1Watt'[0]`)
- Breaker 1 Energy (`'loadInfo.hall1Watt'[1]`)
- Breaker 2 Energy (`'loadInfo.hall1Watt'[2]`)
- Breaker 3 Energy (`'loadInfo.hall1Watt'[3]`)
- Breaker 4 Energy (`'loadInfo.hall1Watt'[4]`)
- Breaker 5 Energy (`'loadInfo.hall1Watt'[5]`)
- Breaker 6 Energy (`'loadInfo.hall1Watt'[6]`)
- Breaker 7 Energy (`'loadInfo.hall1Watt'[7]`)
- Breaker 8 Energy (`'loadInfo.hall1Watt'[8]`)
- Breaker 9 Energy (`'loadInfo.hall1Watt'[9]`)
- Breaker 10 Energy (`'loadInfo.hall1Watt'[10]`)
- Breaker 11 Energy (`'loadInfo.hall1Watt'[11]`)
- Battery Level 1 (`'backupIncreInfo.Energy1Info.batteryPercentage'`)
- Battery Level 2 (`'backupIncreInfo.Energy2Info.batteryPercentage'`)
- Battery Level 3 (`'backupIncreInfo.Energy3Info.batteryPercentage'`)

*Switches*
- EPS Mode (`epsModeInfo` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"epsModeInfo": false}}`)
- Storm Guard (`stormIsEnable` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"stormIsEnable": false}}`)

*Sliders (numbers)*
- Backup reserve level (`'backupReserveSoc'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"backupReserveSoc": "VALUE"}}` [10 - 50])
- Charging power (`'chargeWattPower'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"chargeWattPower": "VALUE"}}` [500 - 7200])
- Charging limit (`'foceChargeHight'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"foceChargeHight": "VALUE"}}` [80 - 100])

*Selects*
- Batterie Status 1 (`'ch1EnableSet'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"ch1EnableSet": "VALUE"}}` [No operation (0), Enabled (1), Disabled (2)])
- Batterie Status 2 (`'ch2EnableSet'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"ch2EnableSet": "VALUE"}}` [No operation (0), Enabled (1), Disabled (2)])
- Batterie Status 3 (`'ch3EnableSet'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"ch3EnableSet": "VALUE"}}` [No operation (0), Enabled (1), Disabled (2)])
- Batterie Force Charge 1 (`'ch1ForceCharge'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"ch1ForceCharge": "VALUE"}}` [Off (FORCE_CHARGE_OFF), On (FORCE_CHARGE_ON)])
- Batterie Force Charge 2 (`'ch2ForceCharge'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"ch2ForceCharge": "VALUE"}}` [Off (FORCE_CHARGE_OFF), On (FORCE_CHARGE_ON)])
- Batterie Force Charge 3 (`'ch3ForceCharge'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"ch3ForceCharge": "VALUE"}}` [Off (FORCE_CHARGE_OFF), On (FORCE_CHARGE_ON)])
- Economic Mode (`'smartBackupMode'` -> `{"sn": "SN", "cmdCode": "PD303_APP_SET", "params": {"smartBackupMode": "VALUE"}}` [None (0), TOU (1), Self-service (2), Timed task (3)])


