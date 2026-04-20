## Stream_PRO

*Sensors*
- Cumulative Capacity Charge (mAh) (`accuChgCap`)   _(disabled)_
- Cumulative Energy Charge (Wh) (`accuChgEnergy`)
- Cumulative Capacity Discharge (mAh) (`accuDsgCap`)   _(disabled)_
- Cumulative Energy Discharge (Wh) (`accuDsgEnergy`)
- Charge Remaining Time (`bmsChgRemTime`)   _(disabled)_
- Discharge Remaining Time (`bmsDsgRemTime`)   _(disabled)_
- Max Charge Level (`cmsMaxChgSoc`)
- Min Discharge Level (`cmsMinDsgSoc`)
- Cycles (`cycles`)
- Design Capacity (`designCap`)   _(disabled)_
- Power Battery SOC (`f32ShowSoc`)
- Full Capacity (`fullCap`)   _(disabled)_
- Power AC (`gridConnectionPower`)
- Power Volts (`gridConnectionVol`)   _(disabled)_
- In Power (`inputWatts`)
- Max Cell Temperature (`maxCellTemp`)   _(disabled)_
- Max Cell Volts (`maxCellVol`)   _(disabled)_
- Min Cell Temperature (`minCellTemp`)   _(disabled)_
- Min Cell Volts (`minCellVol`)   _(disabled)_
- Out Power (`outputWatts`)
- Power Battery (`powGetBpCms`)
- Power PV 1 (`pvWatts_plugInInfoPvAmp`)   _(auto)_
- Power PV 2 (`pvWatts_plugInInfoPv2Amp`)   _(auto)_
- Power PV 3 (`pvWatts_plugInInfoPv3Amp`)   _(auto)_
- Power PV 4 (`pvWatts_plugInInfoPv4Amp`)   _(auto)_
- Power PV 1 (`powGetPv`)   _(auto)_
- Power PV 2 (`powGetPv2`)   _(auto)_
- Power PV 3 (`powGetPv3`)   _(auto)_
- Power PV 4 (`powGetPv4`)   _(auto)_
- Power PV1 Volts (`plugInInfoPvVol`)   _(auto)_
- Power PV2 Volts (`plugInInfoPv2Vol`)   _(auto)_
- Power PV3 Volts (`plugInInfoPv3Vol`)   _(auto)_
- Power PV4 Volts (`plugInInfoPv4Vol`)   _(auto)_
- Power PV1 In Amps (`plugInInfoPvAmp`)   _(auto)_
- Power PV2 In Amps (`plugInInfoPv2Amp`)   _(auto)_
- Power PV3 In Amps (`plugInInfoPv3Amp`)   _(auto)_
- Power PV4 In Amps (`plugInInfoPv4Amp`)   _(auto)_
- Power PV Sum (`powGetPvSum`)
- Power SCHUKO1 (`powGetSchuko1`)   _(auto)_
- Power SCHUKO2 (`powGetSchuko2`)   _(auto)_
- Power Grid (`powGetSysGrid`)
- Power Sys Load (`powGetSysLoad`)
- Power Sys Load From Battery (`powGetSysLoadFromBp`)
- Power Sys Load From Grid (`powGetSysLoadFromGrid`)
- Power Sys Load From PV (`powGetSysLoadFromPv`)
- Real State of Health (`realSoh`)   _(disabled)_
- Remain Capacity (`remainCap`)   _(disabled)_
- Remaining Time (`remainTime`)
- Power Battery (`soc`)
- State of Health (`soh`)
- Power AC SYS (`sysGridConnectionPower`)
- Battery Temperature (`temp`)
- Battery Volts (`vol`)   _(disabled)_

*Switches*
- AC 1 On (`relay2Onoff` -> `{"sn": "SN", "cmdId": 17, "cmdFunc": 254, "dirDest": 1, "dirSrc": 1, "dest": 2, "needAck": true, "params": {"cfgRelay2Onoff": "VALUE"}}`)
- AC 2 On (`relay3Onoff` -> `{"sn": "SN", "cmdId": 17, "cmdFunc": 254, "dirDest": 1, "dirSrc": 1, "dest": 2, "needAck": true, "params": {"cfgRelay3Onoff": "VALUE"}}`)
- Operating mode - Self-powered (`energyStrategyOperateMode.operateSelfPoweredOpen` -> `{"sn": "SN", "cmdId": 17, "cmdFunc": 254, "dirDest": 1, "dirSrc": 1, "dest": 2, "needAck": true, "params": {"cfgEnergyStrategyOperateMode": {"operateSelfPoweredOpen": 6666}}}`)
- Operating mode - AI Mode (`energyStrategyOperateMode.operateIntelligentScheduleModeOpen` -> `{"sn": "SN", "cmdId": 17, "cmdFunc": 254, "dirDest": 1, "dirSrc": 1, "dest": 2, "needAck": true, "params": {"cfgEnergyStrategyOperateMode": {"operateIntelligentScheduleModeOpen": 6666}}}`)
- Feed-in control (`feedGridMode` -> `{"sn": "SN", "cmdId": 17, "cmdFunc": 254, "dirDest": 1, "dirSrc": 1, "dest": 2, "needAck": true, "params": {"cfgFeedGridMode": "VALUE"}}`)

*Sliders (numbers)*
- Backup Reserve Level (`backupReverseSoc` -> `{"sn": "SN", "cmdId": 17, "cmdFunc": 254, "dirDest": 1, "dirSrc": 1, "dest": 2, "needAck": true, "params": {"cfgBackupReverseSoc": "VALUE"}}` [3 - 95])


