## GLACIER

*Sensors*
- Main Battery Level (`bms_bmsStatus.soc`)
- Main Design Capacity (`bms_bmsStatus.designCap`)   _(disabled)_
- Main Full Capacity (`bms_bmsStatus.fullCap`)   _(disabled)_
- Main Remain Capacity (`bms_bmsStatus.remainCap`)   _(disabled)_
- Battery Level (`bms_emsStatus.f32LcdSoc`)
- Battery Charging State (`bms_emsStatus.chgState`)
- Total In Power (`bms_bmsStatus.inWatts`)
- Total Out Power (`bms_bmsStatus.outWatts`)
- Motor Power (`pd.motorWat`)
- Charge Remaining Time (`bms_emsStatus.chgRemain`)
- Discharge Remaining Time (`bms_emsStatus.dsgRemain`)
- Cycles (`bms_bmsStatus.cycles`)
- Battery Temperature (`bms_bmsStatus.tmp`)
- Min Cell Temperature (`bms_bmsStatus.minCellTmp`)   _(disabled)_
- Max Cell Temperature (`bms_bmsStatus.maxCellTmp`)   _(disabled)_
- Battery Volts (`bms_bmsStatus.vol`)   _(disabled)_
- Min Cell Volts (`bms_bmsStatus.minCellVol`)   _(disabled)_
- Max Cell Volts (`bms_bmsStatus.maxCellVol`)   _(disabled)_
- Battery Present (`pd.batFlag`)
- XT60 State (`pd.xt60InState`)
- Fan Level (`bms_emsStatus.fanLvl`)
- Ambient Temperature (`pd.ambientTmp`)
- Exhaust Temperature (`pd.exhaustTmp`)
- Water Temperature (`pd.tempWater`)
- Left Temperature (`pd.tmpL`)
- Right Temperature (`pd.tmpR`)
- Dual Zone Mode (`pd.flagTwoZone`)
- Ice Time Remain (`pd.iceTm`)
- Ice Percentage (`pd.icePercent`)
- Ice Make Mode (`pd.iceMkMode`)
- Ice Alert (`pd.iceAlert`)
- Ice Water Level OK (`pd.waterLine`)
- Status

*Switches*
- Beeper (`pd.beepEn` -> `{"moduleType": 1, "operateType": "beepEn", "params": {"flag": "VALUE"}}`)
- Eco Mode (`pd.coolMode` -> `{"moduleType": 1, "operateType": "ecoMode", "params": {"mode": "VALUE"}}`)
- Power (`pd.pwrState` -> `{"moduleType": 1, "operateType": "powerOff", "params": {"enable": "VALUE"}}`)

*Sliders (numbers)*
- Left Set Temperature (`pd.tmpLSet` -> `{"moduleType": 1, "operateType": "temp", "params": {"tmpM": 0, "tmpL": "VALUE", "tmpR": 0}}` [-25 - 10])
- Combined Set Temperature (`pd.tmpMSet` -> `{"moduleType": 1, "operateType": "temp", "params": {"tmpM": "VALUE", "tmpL": 0, "tmpR": 0}}` [-25 - 10])
- Right Set Temperature (`pd.tmpRSet` -> `{"moduleType": 1, "operateType": "temp", "params": {"tmpM": 0, "tmpL": 0, "tmpR": "VALUE"}}` [-25 - 10])

*Selects*


