## Power_Kits

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

*Switches*
- Main DC Output (`not_existing` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15362, "operateType": "dischgParaSet", "params": {"swSta": 0}}`)

### bbcout

*Sensors*
- DC Out Current (`ldOutCurr`)
- DC Out Power (`ldOutWatts`)
- DC Out Battery Power (`batWatts`)
- DC 1 Out Battery Current (`l1Curr`)   _(disabled)_
- DC 2 Out Battery Current (`l2Curr`)   _(disabled)_
- DC Out Battery Voltage (`batVol`)   _(disabled)_

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

*Switches*
- AC Output (`invSwSta` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15365, "operateType": "dischgIcParaSet", "params": {"powerOn": 0, "acCurrMaxSet": 255, "acChgDisa": 255, "acFrequencySet": 255, "acVolSet": 255}}`)
- AC Charging (`chgDsgState` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15365, "operateType": "dischgIcParaSet", "params": {"acCurrMaxSet": 255, "powerOn": 255, "acChgDisa": 1, "acFrequencySet": 255, "wakeup": 1, "standbyTime": 255, "acRlyCtrlDisable": 255, "acVolSet": 255, "passByMaxCurr": 255}}`)

*Sliders (numbers)*
- AC Charging Power (`NotExisting` -> `{"id": 123456789, "version": "1.0", "sn": "SN", "moduleSn": "SN", "moduleType": 15365, "operateType": "dischgIcParaSet", "params": {"acCurrMaxSet": "VALUE"}}` [0 - 16])

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

*Switches*
- DC Switch 1 (`dcChRelay` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15362, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)
- DC Switch 2 (`dcChRelay` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15362, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)
- DC Switch 3 (`dcChRelay` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15362, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)
- DC Switch 4 (`dcChRelay` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15362, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)
- DC Switch 5 (`dcChRelay` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15362, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)
- DC Switch 6 (`dcChRelay` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15362, "operateType": "chSwitch", "params": {"bitsSwSta": "VALUE"}}`)

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

*Switches*
- Prioretize grid (`passByModeEn` -> `{"id": 123456789, "version": "1.0", "moduleSn": "SN", "moduleType": 15365, "operateType": "dsgIcParaSet", "params": {"dsgLowPwrEn": 255, "pfcDsgModeEn": 255, "passByCurrMax": 255, "passByModeEn": 2}}`)

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


