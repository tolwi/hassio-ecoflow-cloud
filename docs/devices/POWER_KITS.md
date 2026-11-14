## POWER_KITS

### hub

*Sensors*
- Battery Level (`totalSoc`)
- Total In Power (`totalInWatts`)
- Total Out Power (`totalOutWatts`)
- Total Current (`totalAmp`)
- Remaining Time (`totalRemainTime`)
- Total Full Capacity (`totalFullCap`)   _(disabled)_
- Total Charge Discharge State (`totalChgDsgState`)   _(disabled)_
- Charge Upper Limit (`bmsChgUpline`)   _(disabled)_
- Discharge Lower Limit (`bmsDsgDownline`)   _(disabled)_
- Generator Start Level (`oilStartDownline`)   _(disabled)_
- Generator Stop Level (`oilStopUpline`)   _(disabled)_
- Scene (`scenes`)   _(disabled)_
- GPS Enabled (`gpsOn`)   _(disabled)_
- GPS Connected (`gpsCon`)   _(disabled)_
- Status

*Sliders (numbers)*
- Min Discharge Level (`bmsDsgDownline` -> `{"id": 123456789, "version": "1.0", "moduleSn": "0000000000000000", "moduleType": 0, "operateType": "socLowerLimit", "params": {"minDsgSoc": "VALUE"}}` [0 - 30])
- Max Charge Level (`bmsChgUpline` -> `{"id": 123456789, "version": "1.0", "moduleSn": "0000000000000000", "moduleType": 0, "operateType": "socUpperLimit", "params": {"maxChgSoc": "VALUE"}}` [50 - 100])

### bbcin

*Sensors*
- DC Work Mode 1 (`workMode`)   _(disabled)_
- DC Work Mode 2 (`workMode2`)   _(disabled)_
- DC In Hardware Type (`inHwTpe`)
- DC Online Pos (`bpOnlinePos`)   _(disabled)_
- DC In Energy for Day (`dayEnergy`)   _(disabled)_
- Disable Shake Control (`shakeCtrlDisable`)   _(disabled)_
- Is Car Moving (`isCarMoving`)   _(disabled)_
- DC In Event Code (`eventCode`)   _(disabled)_
- DC In Warning Code (`warnCode`)
- DC In Error Code (`errCode`)
- DC In Battery Power (`batWatts`)
- DC In Battery Current (`batCurr`)
- DC In Battery Voltage (`batVol`)
- DC Allow Discharge (`allowDsgOn`)
- DC Discharge Energy (`dsgEnergy`)   _(disabled)_
- DC In State (`dcInState`)
- DC In Power (`dcInWatts`)
- DC In Current (`dcInCurr`)
- DC In Voltage (`dcInVol`)
- DC Charge Paused (`chgPause`)
- DC Charge Type (`chgType`)
- DC Charge Max Current (`chgMaxCurr`)
- DC Charge Mode (`chargeMode`)
- DC In L1 Current (`l1Curr`)   _(disabled)_
- DC In L2 Current (`l2Curr`)   _(disabled)_
- DC In HS1 Temperature (`hs1Temp`)
- DC In HS2 Temperature (`hs2Temp`)
- DC In PCB Temperature (`pcbTemp`)
- Alt. Cable Unit (`altCableUnit`)
- Alt. Cable Length (`altCableLen`)
- Alt. Cable Voltage Limit (`altVoltLmt`)
- Alt. Voltage Limit En (`altVoltLmtEn`)
- Alternator Mode (`alternatorMode`)   _(disabled)_
- Third Input Power (`thirdWatts`)   _(disabled)_
- Input Port Type (`setPortType`)   _(disabled)_

*Switches*
- Port 1 Charging (`chgPause` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15362, "operateType": "chgParaSet", "params": {"chgPause": 1, "maxChgCurr": -1, "altCableLen": -1, "altCableUnit": 255, "altVoltLmt": 65535, "altVoltLmtEn": 255, "shakeCtrlDisable": 255, "setPortType": 255}}`)

*Selects*
- Port 1 Charging Mode (`setPortType` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15362, "operateType": "chgParaSet", "params": {"chgPause": 255, "maxChgCurr": -1, "altCableLen": -1, "altCableUnit": 255, "altVoltLmt": 65535, "altVoltLmtEn": 255, "shakeCtrlDisable": 255, "setPortType": "VALUE"}}` [Auto (0), Alternator (1), Solar (2)])
- Port 1 Alternator Type (`alternatorMode` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15362, "operateType": "chgDsgAltmodeSet", "params": {"rsvd": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"], "alternatorMode": "VALUE"}}` [Generic (0), 48V Excited (1)])

### bbcout

*Sensors*
- DC Out Current (`ldOutCurr`)
- DC Out Power (`ldOutWatts`)
- DC Out Battery Power (`batWatts`)
- DC 1 Out Battery Current (`l1Curr`)   _(disabled)_
- DC 2 Out Battery Current (`l2Curr`)   _(disabled)_
- DC Out Battery Voltage (`batVol`)   _(disabled)_
- DC Output Enabled (`dcOutSta`)
- Beeper (`beepEn`)   _(disabled)_
- DC Always On (`dcAlwaysOn`)   _(disabled)_
- No Load Power (`noLoadPwr`)   _(disabled)_
- Hub Work Mode (`hubWorkMode`)   _(disabled)_
- DC Out Energy Today (`dayEnergy`)   _(disabled)_

*Switches*
- Main DC Output (`dcOutSta` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15363, "operateType": "dischgParaSet", "params": {"swSta": 0, "beepEn": 255, "volTag": 255, "hubExitLsp": 255, "bbcInExitLsp": 255, "icExitLsp": 255, "sccExitLsp": 255, "noLoadPwr": 65535, "standbyTime": 65535}}`)
- Beeper (`beepEn` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15363, "operateType": "dischgParaSet", "params": {"swSta": 255, "beepEn": 0, "volTag": 255, "hubExitLsp": 255, "bbcInExitLsp": 255, "icExitLsp": 255, "sccExitLsp": 255, "noLoadPwr": 65535, "standbyTime": 65535}}`)

*Selects*
- DC Output Voltage (`cfgVolTag` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15363, "operateType": "dischgParaSet", "params": {"swSta": 255, "beepEn": 255, "volTag": "VALUE", "hubExitLsp": 255, "bbcInExitLsp": 255, "icExitLsp": 255, "sccExitLsp": 255, "noLoadPwr": 65535, "standbyTime": 65535}}` [12V (0), 24V (1)])

### iclow

*Sensors*
- Main Battery Level (`realSoc`)
- BMS Error Code (`errCode`)
- BMS Warning Code (`warn_code`)
- BMS Event Code (`event_code`)   _(disabled)_
- BMS DC Temperature (`dcTemp`)
- BMS Charge Discharge State (`chgDsgState`)   _(disabled)_
- BMS Charge Voltage (`chgBatVol`)   _(disabled)_
- BMS Charge Type (`chgType`)   _(disabled)_
- BMS Charge In Type (`chgInType`)   _(disabled)_
- BMS Charge Flag (`chrgFlag`)   _(disabled)_
- BMS Max Charge Current (`maxChgCurr`)   _(disabled)_
- BMS External Kit Type (`extKitType`)   _(disabled)_
- BMS Bus Current (`bmsChgCurr`)   _(disabled)_
- BMS Bus Voltage (`busVol`)
- BMS LSPL Flag (`lsplFlag`)   _(disabled)_
- BMS Protect State (`protectState`)
- BMS Battery Current (`batCurr`)   _(disabled)_
- Fan Level (`fanLevel`)   _(disabled)_
- AC Always On (`acAlwaysOn`)   _(disabled)_
- Inverter No Load Power (`invNoLoadPwr`)   _(disabled)_

### bpxxx

*Sensors*
- Ampere battery (SN) (`amp`)
- max Capacity battery (SN) (`fullCap`)
- State of Charge (soc) battery (SN) (`soc`)
- minimal cell voltage battery (SN) (`minCellVol`)
- full cycle count battery (SN) (`cycles`)
- current voltage battery (SN) (`vol`)
- current Capacity battery (SN) (`remainCap`)
- Charing power battery (SN) (`inWatts`)
- temperatur battery (SN) (`temp`)
- remaining time battery (SN) (`remainTime`)
- maximum cell voltage battery (SN) (`maxCellVol`)
- discharing power battery (SN) (`outWatts`)
- State of Health (`soh`)
- Design Capacity (`designCap`)   _(disabled)_
- Cumulative Energy Charge (Wh) (`accuChgEnergy`)
- Cumulative Energy Discharge (Wh) (`accuDsgEnergy`)
- Cumulative Capacity Charge (mAh) (`accuChgCap`)   _(disabled)_
- Cumulative Capacity Discharge (mAh) (`accuDsgCap`)   _(disabled)_
- Max Cell Temperature (`maxCellTemp`)   _(disabled)_
- Min Cell Temperature (`minCellTemp`)   _(disabled)_
- Charge Limit (`chgSetSoc`)   _(disabled)_
- Discharge Limit (`dsgSetSoc`)   _(disabled)_
- Kit Number (`kitNum`)   _(disabled)_
- Warning Code (`warnCode`)   _(disabled)_
- BMS Fault (`bmsFault`)   _(disabled)_

### kitscc

*Sensors*
- Total In Power (`batWatts`)
- Solar Battery Current (`batCurr`)
- Solar Battery Voltage (`batVol`)
- Solar (2) In Power (`pv1InWatts`)
- Solar (2) In Voltage (`pv1InVol`)
- Solar (2) In Current (`pv1InCurr`)
- Solar (2) Error Code (`pv1ErrCode`)
- Solar (2) Hot Out (`pv1_hot_out`)   _(disabled)_
- Solar (2) Input Flag (`pv1InputFlag`)   _(disabled)_
- Solar (2) Work Mode (`pv1WorkMode`)   _(disabled)_
- Solar (2) Enabled (`mppt1SwSta`)
- Solar (2) Event Code (`eventCode1`)   _(disabled)_
- Solar (2) Warn Code (`warnCode1`)
- Solar (2) Temperature (`hs1Temp`)
- Solar (3) In Power (`pv2InWatts`)
- Solar (3) In Voltage (`pv2InVol`)
- Solar (3) In Current (`pv2InCurr`)
- Solar (3) Error Code (`pv2ErrCode`)
- Solar (3) Hot Out (`pv2_hot_out`)   _(disabled)_
- Solar (3) Input Flag (`pv2InputFlag`)   _(disabled)_
- Solar (3) Work Mode (`pv2WorkMode`)   _(disabled)_
- Solar (3) Enabled (`mppt2SwSta`)
- Solar (3) Event Code (`eventCode2`)   _(disabled)_
- Solar (3) Warn Code (`warnCode2`)
- Solar (3) Temperature (`hs2Temp`)
- Solar Total Charge Current (`chgEnergy`)   _(disabled)_
- Solar Energy for Day (`dayEnergy`)   _(disabled)_

*Switches*
- Port 2 Charging (`mppt1SwSta` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15364, "operateType": "pvSwitch", "params": {"mpptt1": 0, "mpptt2": 255, "alt1CableLen": -1, "alt2CableLen": -1, "alt1CableUnit": 255, "alt2CableUnit": 255, "alt1VoltLmt": 65535, "alt2VoltLmt": 65535, "alt1VoltLmtEn": 255, "alt2VoltLmtEn": 255, "setPort1Type": 255, "setPort2Type": 255}}`)
- Port 3 Charging (`mppt2SwSta` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15364, "operateType": "pvSwitch", "params": {"mpptt1": 255, "mpptt2": 0, "alt1CableLen": -1, "alt2CableLen": -1, "alt1CableUnit": 255, "alt2CableUnit": 255, "alt1VoltLmt": 65535, "alt2VoltLmt": 65535, "alt1VoltLmtEn": 255, "alt2VoltLmtEn": 255, "setPort1Type": 255, "setPort2Type": 255}}`)

*Selects*
- Port 2 Charging Mode (`setPort1Type` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15364, "operateType": "pvSwitch", "params": {"mpptt1": 255, "mpptt2": 255, "alt1CableLen": -1, "alt2CableLen": -1, "alt1CableUnit": 255, "alt2CableUnit": 255, "alt1VoltLmt": 65535, "alt2VoltLmt": 65535, "alt1VoltLmtEn": 255, "alt2VoltLmtEn": 255, "setPort1Type": "VALUE", "setPort2Type": 255}}` [Auto (0), Alternator (1), Solar (2)])
- Port 3 Charging Mode (`setPort2Type` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15364, "operateType": "pvSwitch", "params": {"mpptt1": 255, "mpptt2": 255, "alt1CableLen": -1, "alt2CableLen": -1, "alt1CableUnit": 255, "alt2CableUnit": 255, "alt1VoltLmt": 65535, "alt2VoltLmt": 65535, "alt1VoltLmtEn": 255, "alt2VoltLmtEn": 255, "setPort1Type": 255, "setPort2Type": "VALUE"}}` [Auto (0), Alternator (1), Solar (2)])

### lddc

*Sensors*
- Distributer DC Out Power (`dcTotalWatts`)
- DC Out 1 (`dcChWatt[0]`)
- DC Out 2 (`dcChWatt[1]`)
- DC Out 3 (`dcChWatt[2]`)
- DC Out 4 (`dcChWatt[3]`)
- DC Out 5 (`dcChWatt[4]`)
- DC Out 6 (`dcChWatt[5]`)
- DC Out 7 (`dcChWatt[6]`)
- DC Out 8 (`dcChWatt[7]`)
- DC Out 9 (`dcChWatt[8]`)
- DC Out 10 (`dcChWatt[9]`)
- DC Out 11 (`dcChWatt[10]`)
- DC Out 12 (`dcChWatt[11]`)
- DC Ampere Out 1 (`dcChCur[0]`)
- DC Ampere Out 2 (`dcChCur[1]`)
- DC Ampere Out 3 (`dcChCur[2]`)
- DC Ampere Out 4 (`dcChCur[3]`)
- DC Ampere Out 5 (`dcChCur[4]`)
- DC Ampere Out 6 (`dcChCur[5]`)
- DC Ampere Out 7 (`dcChCur[6]`)
- DC Ampere Out 8 (`dcChCur[7]`)
- DC Ampere Out 9 (`dcChCur[8]`)
- DC Ampere Out 10 (`dcChCur[9]`)
- DC Ampere Out 11 (`dcChCur[10]`)
- DC Ampere Out 12 (`dcChCur[11]`)
- Distributer - DC Temperature 1 (`dcTemp1`)
- Distributer - DC Temperature 2 (`dcTemp2`)
- DC Out Ch Relay (`dcChRelay`)   _(disabled)_
- DC Out Enabled (`dcChSta`)
- DC Out Set Ch State (`dcSetChSta`)   _(disabled)_
- DC Out Voltage (`dcInVol`)
- DC Out 13 (`dcChWattV2[0]`)
- DC Out 14 (`dcChWattV2[1]`)
- DC Out 15 (`dcChWattV2[2]`)
- DC Out 16 (`dcChWattV2[3]`)
- DC Ampere Out 13 (`dcChCurV2[0]`)
- DC Ampere Out 14 (`dcChCurV2[1]`)
- DC Ampere Out 15 (`dcChCurV2[2]`)
- DC Ampere Out 16 (`dcChCurV2[3]`)
- DC Out 13-16 Ch Relay (`dcChRelayV2`)   _(disabled)_

*Switches*
- DC Switch 1 (`dcChRelay` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)
- DC Switch 2 (`dcChRelay` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)
- DC Switch 3 (`dcChRelay` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)
- DC Switch 4 (`dcChRelay` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)
- DC Switch 5 (`dcChRelay` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)
- DC Switch 6 (`dcChRelay` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)
- DC Switch 7 (`dcChRelay` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)
- DC Switch 8 (`dcChRelay` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)
- DC Switch 9 (`dcChRelay` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)
- DC Switch 10 (`dcChRelay` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)
- DC Switch 11 (`dcChRelay` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)
- DC Switch 12 (`dcChRelay` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)
- DC Switch 13 (`dcChRelayV2` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)
- DC Switch 14 (`dcChRelayV2` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)
- DC Switch 15 (`dcChRelayV2` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)
- DC Switch 16 (`dcChRelayV2` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)

*Texts*
- DC Out 1 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "setDcChAlias", "params": {"id": 0, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)
- DC Out 2 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "setDcChAlias", "params": {"id": 1, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)
- DC Out 3 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "setDcChAlias", "params": {"id": 2, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)
- DC Out 4 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "setDcChAlias", "params": {"id": 3, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)
- DC Out 5 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "setDcChAlias", "params": {"id": 4, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)
- DC Out 6 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "setDcChAlias", "params": {"id": 5, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)
- DC Out 7 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "setDcChAlias", "params": {"id": 6, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)
- DC Out 8 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "setDcChAlias", "params": {"id": 7, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)
- DC Out 9 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "setDcChAlias", "params": {"id": 8, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)
- DC Out 10 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "setDcChAlias", "params": {"id": 9, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)
- DC Out 11 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "setDcChAlias", "params": {"id": 10, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)
- DC Out 12 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "setDcChAlias", "params": {"id": 11, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)
- DC Out 13 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "setDcChAlias", "params": {"id": 12, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)
- DC Out 14 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "setDcChAlias", "params": {"id": 13, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)
- DC Out 15 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "setDcChAlias", "params": {"id": 14, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)
- DC Out 16 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15368, "operateType": "setDcChAlias", "params": {"id": 15, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)

### ichigh

*Sensors*
- AC Out Voltage (`outVol`)
- AC Out Current (`outCurr`)
- AC Inverter Type (`invType`)   _(disabled)_
- AC In Frequency (`inFreq`)
- AC In Power (`inWatts`)
- AC In Current (`inCurr`)
- AC In Voltage (`inVol`)
- AC Out Enabled (`invSwSta`)
- AC Inverter Temperature (`acTemp`)
- AC Out Power (`outWatts`)
- AC Outlet Power (`ch2Watt`)
- AC Outlet Current (`outAmp2`)
- AC Config Out Frequency (`cfgOutFreq`)   _(disabled)_
- AC Out Frequency (`outFreq`)
- AC Standby Time (`standbyTime`)   _(disabled)_
- AC Input Day Power (`inputWhInDay`)   _(disabled)_
- AC Output Day Power (`outputWhInDay`)   _(disabled)_
- AC Out Apparent Power (`outVa`)
- AC Charge Power (`chgWatts`)
- AC Out Voltage Setting (`appCfg.acVolSet`)   _(disabled)_
- AC Out Frequency Setting (`appCfg.acFreqSet`)   _(disabled)_

*Switches*
- Grid Priority (`passByModeEn` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15365, "operateType": "dsgIcParaSet", "params": {"invNoLoadPwr": 65535, "dsgLowPwrEn": 255, "setInvTag": 255, "pfcDsgModeEn": 255, "passByCurrMax": 255, "passByModeEn": 2}}`)
- AC Output (`invSwSta` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15365, "operateType": "dischgIcParaSet", "params": {"powerOn": 0, "acCurrMaxSet": 255, "acChgDisa": 255, "acFrequencySet": 255, "acVolSet": 255}}`)
- AC Charging (`appCfg.acChgDisable` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15365, "operateType": "dischgIcParaSet", "params": {"acCurrMaxSet": 255, "powerOn": 255, "acChgDisa": 1, "acFrequencySet": 255, "wakeup": 1, "standbyTime": 255, "acRlyCtrlDisable": 255, "acVolSet": 255, "passByMaxCurr": 255}}`)

*Sliders (numbers)*
- AC Charging Current (`appCfg.acMaxCurrSer` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15365, "operateType": "dischgIcParaSet", "params": {"wakeup": 1, "powerOn": 255, "acChgDisa": 255, "acRlyCtrlDisable": 255, "acCurrMaxSet": "VALUE", "passByMaxCurr": 255, "acVolSet": 255, "acFrequencySet": 255, "standbyTime": 255}}` [2 - 20])
- AC Input Current (`appCfg.passByMaxCurr` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15365, "operateType": "dischgIcParaSet", "params": {"wakeup": 1, "powerOn": 255, "acChgDisa": 255, "acRlyCtrlDisable": 255, "acCurrMaxSet": 255, "passByMaxCurr": "VALUE", "acVolSet": 255, "acFrequencySet": 255, "standbyTime": 255}}` [2 - 50])

### ldac

*Sensors*
- Distributer AC Out Power (`acTotalWatts`)
- AC Out 1 (`acChWatt[0]`)
- AC Out 2 (`acChWatt[1]`)
- AC Out 3 (`acChWatt[2]`)
- AC Out 4 (`acChWatt[3]`)
- AC Out 5 (`acChWatt[4]`)
- AC Out 6 (`acChWatt[5]`)
- AC Ampere Out 1 (`acChCur[0]`)
- AC Ampere Out 2 (`acChCur[1]`)
- AC Ampere Out 3 (`acChCur[2]`)
- AC Ampere Out 4 (`acChCur[3]`)
- AC Ampere Out 5 (`acChCur[4]`)
- AC Ampere Out 6 (`acChCur[5]`)
- AC Inverter In Power (`outWatts`)
- AC Inverter In Voltage (`acInVol`)
- Distributer AC Temperature 1 (`acTemp1`)
- Distributer AC Temperature 2 (`acTemp2`)
- AC Charge State (`acChSta`)
- AC L1 Power (`acTotalWatts1`)
- AC L2 Power (`acTotalWatts2`)
- AC L2 In Voltage (`acInVol2`)

*Texts*
- AC Out 1 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15367, "operateType": "setAcChAlias", "params": {"id": 0, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)
- AC Out 2 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15367, "operateType": "setAcChAlias", "params": {"id": 1, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)
- AC Out 3 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15367, "operateType": "setAcChAlias", "params": {"id": 2, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)
- AC Out 4 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15367, "operateType": "setAcChAlias", "params": {"id": 3, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)
- AC Out 5 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15367, "operateType": "setAcChAlias", "params": {"id": 4, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)
- AC Out 6 Name (`{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15367, "operateType": "setAcChAlias", "params": {"id": 5, "chAlias": {"logoNum": 0, "alias": "VALUE"}}}`)


