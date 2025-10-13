import logging
from typing import Any, override

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import BaseDevice, const
# Protocol Buffers modules are imported lazily in _prepare_data method
from custom_components.ecoflow_cloud.entities import (
    BaseNumberEntity,
    BaseSelectEntity,
    BaseSensorEntity,
    BaseSwitchEntity,
)
from custom_components.ecoflow_cloud.number import (
    ChargingPowerEntity,
    MaxBatteryLevelEntity,
    MinBatteryLevelEntity,
)
from custom_components.ecoflow_cloud.select import (
    DictSelectEntity,
    TimeoutDictSelectEntity,
)
from custom_components.ecoflow_cloud.sensor import (
    AmpSensorEntity,
    CapacitySensorEntity,
    CyclesSensorEntity,
    InMilliampSolarSensorEntity,
    InEnergySensorEntity,
    InMilliVoltSensorEntity,
    InVoltSolarSensorEntity,
    InWattsSensorEntity,
    InWattsSolarSensorEntity,
    LevelSensorEntity,
    MilliVoltSensorEntity,
    OutEnergySensorEntity,
    OutMilliVoltSensorEntity,
    OutVoltDcSensorEntity,
    OutWattsDcSensorEntity,
    OutWattsSensorEntity,
    QuotaStatusSensorEntity,
    RemainSensorEntity,
    TempSensorEntity,
    WattsSensorEntity,
)
from custom_components.ecoflow_cloud.switch import BeeperEntity, EnabledEntity

_LOGGER = logging.getLogger(__name__)


class DeltaPro3(BaseDevice):
    @override
    def sensors(self, client: EcoflowApiClient) -> list[Any]:
        return [
            # Main Battery System - using actual protobuf field names
            LevelSensorEntity(client, self, "bms_batt_soc", const.MAIN_BATTERY_LEVEL)
            .attr("bms_design_cap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("bms_full_cap_mah", const.ATTR_FULL_CAPACITY, 0)
            .attr("bms_remain_cap_mah", const.ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(
                client, self, "bms_design_cap", const.MAIN_DESIGN_CAPACITY, False
            ),
            CapacitySensorEntity(
                client, self, "bms_full_cap_mah", const.MAIN_FULL_CAPACITY, False
            ),
            CapacitySensorEntity(
                client, self, "bms_remain_cap_mah", const.MAIN_REMAIN_CAPACITY, False
            ),
            LevelSensorEntity(client, self, "bms_batt_soh", const.SOH),
            # Cycles from BMSHeartBeatReport (not DisplayPropertyUpload)
            CyclesSensorEntity(client, self, "cycles", const.CYCLES),
            MilliVoltSensorEntity(
                client, self, "bms_batt_vol", const.BATTERY_VOLT, False
            )
            .attr("bms_min_cell_vol", const.ATTR_MIN_CELL_VOLT, 0)
            .attr("bms_max_cell_vol", const.ATTR_MAX_CELL_VOLT, 0),
            MilliVoltSensorEntity(
                client, self, "bms_min_cell_vol", const.MIN_CELL_VOLT, False
            ),
            MilliVoltSensorEntity(
                client, self, "bms_max_cell_vol", const.MAX_CELL_VOLT, False
            ),
            AmpSensorEntity(
                client, self, "bms_batt_amp", const.MAIN_BATTERY_CURRENT, False
            ),
            TempSensorEntity(
                client, self, "bms_max_cell_temp", const.MAX_CELL_TEMP, False
            ),
            TempSensorEntity(
                client, self, "bms_min_cell_temp", const.MIN_CELL_TEMP, False
            ),
            TempSensorEntity(client, self, "bms_max_mos_temp", const.BATTERY_TEMP)
            .attr("bms_min_cell_temp", const.ATTR_MIN_CELL_TEMP, 0)
            .attr("bms_max_cell_temp", const.ATTR_MAX_CELL_TEMP, 0),
            RemainSensorEntity(
                client, self, "bms_chg_rem_time", const.CHARGE_REMAINING_TIME
            ),
            RemainSensorEntity(
                client, self, "bms_dsg_rem_time", const.DISCHARGE_REMAINING_TIME
            ),
            LevelSensorEntity(
                client, self, "cms_batt_soc", const.COMBINED_BATTERY_LEVEL
            ),
            OutWattsSensorEntity(client, self, "pow_out_sum_w", const.TOTAL_OUT_POWER),
            InWattsSensorEntity(client, self, "pow_in_sum_w", const.TOTAL_IN_POWER),
            InWattsSensorEntity(client, self, "pow_get_ac_in", const.AC_IN_POWER),
            OutWattsSensorEntity(client, self, "pow_get_ac", const.AC_OUT_POWER),
            OutWattsSensorEntity(
                client, self, "pow_get_ac_hv_out", "AC HV Output Power"
            ),
            OutWattsSensorEntity(
                client, self, "pow_get_ac_lv_out", "AC LV Output Power"
            ),
            InMilliVoltSensorEntity(
                client, self, "plug_in_info_ac_in_vol", const.AC_IN_VOLT
            ),
            InMilliampSolarSensorEntity(
                client, self, "plug_in_info_ac_in_amp", "AC Input Current"
            ),
            OutWattsDcSensorEntity(client, self, "pow_get_12v", "12V DC Output Power"),
            OutWattsDcSensorEntity(client, self, "pow_get_24v", "24V DC Output Power"),
            OutVoltDcSensorEntity(
                client, self, "pow_get_12v_vol", "12V DC Output Voltage"
            ),
            OutVoltDcSensorEntity(
                client, self, "pow_get_24v_vol", "24V DC Output Voltage"
            ),
            InWattsSolarSensorEntity(
                client, self, "pow_get_pv_h", "Solar High Voltage Input Power"
            ),
            InWattsSolarSensorEntity(
                client, self, "pow_get_pv_l", "Solar Low Voltage Input Power"
            ),
            InVoltSolarSensorEntity(
                client, self, "pow_get_pv_h_vol", "Solar HV Input Voltage"
            ),
            InVoltSolarSensorEntity(
                client, self, "pow_get_pv_l_vol", "Solar LV Input Voltage"
            ),
            InMilliampSolarSensorEntity(
                client, self, "pow_get_pv_h_amp", "Solar HV Input Current"
            ),
            InMilliampSolarSensorEntity(
                client, self, "pow_get_pv_l_amp", "Solar LV Input Current"
            ),
            OutWattsSensorEntity(
                client, self, "pow_get_qcusb1", const.USB_QC_1_OUT_POWER
            ),
            OutWattsSensorEntity(
                client, self, "pow_get_qcusb2", const.USB_QC_2_OUT_POWER
            ),
            OutWattsSensorEntity(
                client, self, "pow_get_typec1", const.TYPEC_1_OUT_POWER
            ),
            OutWattsSensorEntity(
                client, self, "pow_get_typec2", const.TYPEC_2_OUT_POWER
            ),
            OutWattsDcSensorEntity(
                client, self, "pow_get_5p8", "5P8 Power I/O Port Power"
            ),
            OutWattsDcSensorEntity(
                client, self, "pow_get_4p8_1", "4P8 Extra Battery Port 1 Power"
            ),
            OutWattsDcSensorEntity(
                client, self, "pow_get_4p8_2", "4P8 Extra Battery Port 2 Power"
            ),
            OutWattsSensorEntity(client, self, "ac_out_freq", "AC Output Frequency"),
            LevelSensorEntity(
                client, self, "cms_max_chg_soc", "Max Charge SOC Setting"
            ),
            LevelSensorEntity(
                client, self, "cms_min_dsg_soc", "Min Discharge SOC Setting"
            ),
            # Energy sensors from BMSHeartBeatReport
            # Note: accu_chg_energy and accu_dsg_energy are in Wh, multiply by 0.001 for kWh display
            # These fields do not exist in DisplayPropertyUpload - they come from BMSHeartBeatReport
            InEnergySensorEntity(
                client, self, "accu_chg_energy", "Total Charge Energy"
            ),
            OutEnergySensorEntity(
                client, self, "accu_dsg_energy", "Total Discharge Energy"
            ),
            # Note: The following fields do not exist in any Delta Pro 3 protobuf messages:
            # - pow_in_sum_energy (Total Input Energy)
            # - pow_out_sum_energy (Total Output Energy)
            # - ac_in_energy_total (AC Charge Energy)
            # - ac_out_energy_total (AC Discharge Energy)
            # - pv_in_energy_total (Solar In Energy)
            # - dc_out_energy_total (DC Discharge Energy)
            # Alternative: Use .with_energy() on power sensors for HA integration sensor
            QuotaStatusSensorEntity(client, self),
        ]

    @override
    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return [
            # Battery Management
            MaxBatteryLevelEntity(
                client,
                self,
                "cms_max_chg_soc",
                const.MAX_CHARGE_LEVEL,
                50,
                100,
                lambda value: {
                    "moduleType": 0,
                    "operateType": "TCP",
                    "params": {"id": 49, "cmsMaxChgSoc": value},
                },
            ),
            MinBatteryLevelEntity(
                client,
                self,
                "cms_min_dsg_soc",
                const.MIN_DISCHARGE_LEVEL,
                0,
                30,
                lambda value: {
                    "moduleType": 0,
                    "operateType": "TCP",
                    "params": {"id": 51, "cmsMinDsgSoc": value},
                },
            ),
            # AC Charging Power
            ChargingPowerEntity(
                client,
                self,
                "plug_in_info_ac_in_chg_pow_max",
                const.AC_CHARGING_POWER,
                200,
                3000,
                lambda value: {
                    "moduleType": 0,
                    "operateType": "TCP",
                    "params": {"id": 69, "plugInInfoAcInChgPowMax": value},
                },
            ),
        ]

    @override
    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        return [
            # Audio Control
            BeeperEntity(
                client,
                self,
                "en_beep",
                const.BEEPER,
                lambda value: {
                    "moduleType": 0,
                    "operateType": "TCP",
                    "params": {"id": 38, "enBeep": value},
                },
            ),
            # AC Output Control
            EnabledEntity(
                client,
                self,
                "cfg_hv_ac_out_open",
                "AC HV Output Enabled",
                lambda value, params=None: {
                    "moduleType": 0,
                    "operateType": "TCP",
                    "params": {"id": 66, "cfgHvAcOutOpen": value},
                },
            ),
            EnabledEntity(
                client,
                self,
                "cfg_lv_ac_out_open",
                "AC LV Output Enabled",
                lambda value, params=None: {
                    "moduleType": 0,
                    "operateType": "TCP",
                    "params": {"id": 66, "cfgLvAcOutOpen": value},
                },
            ),
            # DC Output Control
            EnabledEntity(
                client,
                self,
                "cfg_dc_12v_out_open",
                "12V DC Output Enabled",
                lambda value, params=None: {
                    "moduleType": 0,
                    "operateType": "TCP",
                    "params": {"id": 81, "cfgDc12vOutOpen": value},
                },
            ),
            EnabledEntity(
                client,
                self,
                "cfg_dc_24v_out_open",
                "24V DC Output Enabled",
                lambda value, params=None: {
                    "moduleType": 0,
                    "operateType": "TCP",
                    "params": {"id": 81, "cfgDc24vOutOpen": value},
                },
            ),
            # Xboost Control
            EnabledEntity(
                client,
                self,
                "xboost_en",
                const.XBOOST_ENABLED,
                lambda value, params=None: {
                    "moduleType": 0,
                    "operateType": "TCP",
                    "params": {"id": 66, "xboostEn": value},
                },
            ),
            # Energy Saving
            EnabledEntity(
                client,
                self,
                "ac_energy_saving_open",
                "AC Energy Saving Enabled",
                lambda value, params=None: {
                    "moduleType": 0,
                    "operateType": "TCP",
                    "params": {"id": 95, "acEnergySavingOpen": value},
                },
            ),
            # GFCI Control
            EnabledEntity(
                client,
                self,
                "llc_gfci_flag",
                "GFCI Protection Enabled",
                lambda value, params=None: {
                    "moduleType": 0,
                    "operateType": "TCP",
                    "params": {"id": 153, "llcGFCIFlag": value},
                },
            ),
        ]

    @override
    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return [
            # Screen Timeout
            TimeoutDictSelectEntity(
                client,
                self,
                "screen_off_time",
                const.SCREEN_TIMEOUT,
                const.SCREEN_TIMEOUT_OPTIONS,
                lambda value: {
                    "moduleType": 0,
                    "operateType": "TCP",
                    "params": {"screenOffTime": value, "id": 39},
                },
            ),
            # AC Standby Timeout
            TimeoutDictSelectEntity(
                client,
                self,
                "ac_standby_time",
                const.AC_TIMEOUT,
                const.AC_TIMEOUT_OPTIONS,
                lambda value: {
                    "moduleType": 0,
                    "operateType": "TCP",
                    "params": {"acStandbyTime": value, "id": 10},
                },
            ),
            # DC Standby Timeout
            TimeoutDictSelectEntity(
                client,
                self,
                "dc_standby_time",
                "DC Timeout",
                const.UNIT_TIMEOUT_OPTIONS_LIMITED,
                lambda value: {
                    "moduleType": 0,
                    "operateType": "TCP",
                    "params": {"dcStandbyTime": value, "id": 33},
                },
            ),
            # AC Output Type
            DictSelectEntity(
                client,
                self,
                "plug_in_info_ac_out_type",
                "AC Output Type",
                {"HV+LV": 0, "HV Only": 1, "LV Only": 2},
                lambda value: {
                    "moduleType": 0,
                    "operateType": "TCP",
                    "params": {"plugInInfoAcOutType": int(value), "id": 59},
                },
            ),
        ]

    @override
    def _prepare_data(self, raw_data: bytes) -> dict[str, Any]:
        """Delta Pro 3専用のデータ準備メソッド.
        Protobufバイナリデータをデコードして辞書形式に変換し、全フィールドをflat化してparamsに100%格納する."""
        # Lazy import of Protocol Buffers modules to avoid blocking calls
        try:
            from .proto import ef_dp3_iobroker_pb2 as pb2
        except ImportError as e:
            _LOGGER.error(f"Failed to import ef_dp3_iobroker_pb2: {e}")
            return {}
        
        try:
            _LOGGER.debug(f"Processing {len(raw_data)} bytes of raw data")

            # 1. HeaderMessageのデコード
            header_info = self._decode_header_message(raw_data)
            if not header_info:
                _LOGGER.warning("HeaderMessage decoding failed")
                return {}

            # 2. ペイロードデータの抽出
            pdata = self._extract_payload_data(header_info.get("header_obj"))
            if not pdata:
                _LOGGER.warning("No payload data found")
                return {}

            # 3. XORデコード (必要に応じて)
            decoded_pdata = self._perform_xor_decode(pdata, header_info)

            # 4. Protobufメッセージのデコード
            decoded_data = self._decode_message_by_type(decoded_pdata, header_info)
            if not decoded_data:
                _LOGGER.warning("Message decoding failed")
                return {}

            # 5. flat化して全フィールドをparamsに格納
            flat_dict = self._flatten_dict(decoded_data)
            _LOGGER.debug(f"Flat dict for params (all fields): {flat_dict}")  # noqa: G004
            for k, v in flat_dict.items():
                _LOGGER.debug(f"flat_dict[{k!r}] = {v!r} (type: {type(v).__name__})")  # noqa: G004

            # Home Assistant反映用に必ず'params'キーで返す
            return {  # noqa: TRY300
                "params": flat_dict,
                "all_fields": decoded_data,
            }
        except Exception as e:
            _LOGGER.error(f"Data processing failed: {e}", exc_info=True)
            return {}

    def _decode_header_message(self, raw_data: bytes) -> dict[str, Any] | None:
        """HeaderMessageをデコードしてヘッダー情報を抽出."""
        try:
            # Base64デコードを試行
            import base64

            try:
                decoded_payload = base64.b64decode(raw_data, validate=True)
                _LOGGER.debug("Base64 decode successful")
                raw_data = decoded_payload
            except Exception:
                _LOGGER.debug("Data is not Base64 encoded, using as-is")

            # HeaderMessageとしてデコードを試行
            try:
                from .proto import ef_dp3_iobroker_pb2 as pb2
                header_msg = pb2.HeaderMessage()
                header_msg.ParseFromString(raw_data)
            except AttributeError as e:
                _LOGGER.error(f"HeaderMessage class not found in pb2 module: {e}")
                _LOGGER.debug(f"Available classes in pb2: {[attr for attr in dir(pb2) if not attr.startswith('_')]}")
                return None
            except Exception as e:
                _LOGGER.error(f"Failed to parse HeaderMessage: {e}")
                _LOGGER.debug(f"Raw data length: {len(raw_data)}, first 20 bytes: {raw_data[:20].hex()}")
                return None

            if not header_msg.header:
                _LOGGER.debug("No headers found in HeaderMessage")
                return None

            # 最初のヘッダーを使用 (通常は1つ)
            header = header_msg.header[0]
            header_info = {
                "src": getattr(header, "src", 0),
                "dest": getattr(header, "dest", 0),
                "dSrc": getattr(header, "d_src", 0),
                "dDest": getattr(header, "d_dest", 0),
                "encType": getattr(header, "enc_type", 0),
                "checkType": getattr(header, "check_type", 0),
                "cmdFunc": getattr(header, "cmd_func", 0),
                "cmdId": getattr(header, "cmd_id", 0),
                "dataLen": getattr(header, "data_len", 0),
                "needAck": getattr(header, "need_ack", 0),
                "seq": getattr(header, "seq", 0),
                "productId": getattr(header, "product_id", 0),
                "version": getattr(header, "version", 0),
                "payloadVer": getattr(header, "payload_ver", 0),
                "header_obj": header,
            }

            _LOGGER.debug(
                f"Header decoded: cmdFunc={header_info['cmdFunc']}, cmdId={header_info['cmdId']}"
            )
            return header_info

        except Exception as e:
            _LOGGER.debug(f"HeaderMessage decode failed: {e}")
            return None

    def _extract_payload_data(self, header_obj: Any) -> bytes | None:
        """ヘッダーからペイロードデータを抽出."""
        try:
            pdata = getattr(header_obj, "pdata", b"")
            if pdata:
                _LOGGER.debug(f"Extracted {len(pdata)} bytes of payload data")
                return pdata
            else:
                _LOGGER.warning("No pdata found in header")
                return None
        except Exception as e:
            _LOGGER.error(f"Payload extraction error: {e}")
            return None

    def _perform_xor_decode(self, pdata: bytes, header_info: dict[str, Any]) -> bytes:
        """必要に応じてXORデコードを実行."""
        enc_type = header_info.get("encType", 0)
        src = header_info.get("src", 0)
        seq = header_info.get("seq", 0)

        # XOR decode condition: enc_type == 1 and src != 32
        if enc_type == 1 and src != 32:
            return self._xor_decode_pdata(pdata, seq)
        else:
            return pdata

    def _xor_decode_pdata(self, pdata: bytes, seq: int) -> bytes:
        """XORデコード処理"""
        if not pdata:
            return b""

        decoded_payload = bytearray()
        for byte_val in pdata:
            decoded_payload.append((byte_val ^ seq) & 0xFF)

        return bytes(decoded_payload)

    def _decode_message_by_type(
        self, pdata: bytes, header_info: dict[str, Any]
    ) -> dict[str, Any]:
        """cmdFunc/cmdIdに基づいてProtobufメッセージをデコード."""
        cmd_func = header_info.get("cmdFunc", 0)
        cmd_id = header_info.get("cmdId", 0)

        try:
            _LOGGER.debug(f"Decoding message: cmdFunc={cmd_func}, cmdId={cmd_id}")
            
            # Import pb2 module
            from .proto import ef_dp3_iobroker_pb2 as pb2

            if cmd_func == 254 and cmd_id == 21:
                # DisplayPropertyUpload
                msg = pb2.DisplayPropertyUpload()
                msg.ParseFromString(pdata)
                return self._protobuf_to_dict(msg)

            elif cmd_func == 32 and cmd_id == 2:
                # cmdFunc32_cmdId2_Report
                msg = pb2.cmdFunc32_cmdId2_Report()
                msg.ParseFromString(pdata)
                return self._protobuf_to_dict(msg)

            elif cmd_func == 32 and cmd_id == 50:
                # RuntimePropertyUpload
                msg = pb2.RuntimePropertyUpload()
                msg.ParseFromString(pdata)
                return self._protobuf_to_dict(msg)

            elif cmd_func == 254 and cmd_id == 22:
                # RuntimePropertyUpload - ランタイムプロパティ（頻繁更新データ）
                try:
                    msg = pb2.RuntimePropertyUpload()
                    msg.ParseFromString(pdata)
                    return self._protobuf_to_dict(msg)
                except AttributeError:
                    # RuntimePropertyUpload class not found, use generic handling
                    _LOGGER.debug("RuntimePropertyUpload class not found, using generic handling")
                    # Try to parse as raw data and extract basic information
                    try:
                        # Basic timestamp extraction (assuming first 4 bytes are timestamp)
                        if len(pdata) >= 4:
                            timestamp = int.from_bytes(pdata[:4], byteorder='little', signed=True)
                            return {
                                "cmdFunc": cmd_func, 
                                "cmdId": cmd_id, 
                                "report_timestamp": timestamp,
                                "raw_data_length": len(pdata)
                            }
                    except Exception:
                        pass
                    return {"cmdFunc": cmd_func, "cmdId": cmd_id, "raw_data_length": len(pdata)}

            elif cmd_func == 254 and cmd_id == 23:
                # cmdFunc254_cmdId23_Report - タイムスタンプ付きレポート
                try:
                    msg = pb2.cmdFunc254_cmdId23_Report()
                    msg.ParseFromString(pdata)
                    return self._protobuf_to_dict(msg)
                except AttributeError:
                    # cmdFunc254_cmdId23_Report class not found, use generic handling
                    _LOGGER.debug("cmdFunc254_cmdId23_Report class not found, using generic handling")
                    # Try to parse as raw data and extract basic information
                    try:
                        # Basic timestamp extraction (assuming first 4 bytes are timestamp)
                        if len(pdata) >= 4:
                            timestamp = int.from_bytes(pdata[:4], byteorder='little', signed=True)
                            return {
                                "cmdFunc": cmd_func,
                                "cmdId": cmd_id,
                                "report_timestamp": timestamp,
                                "raw_data_length": len(pdata)
                            }
                    except Exception:
                        pass
                    return {"cmdFunc": cmd_func, "cmdId": cmd_id, "raw_data_length": len(pdata)}

            # BMSHeartBeatReport - Battery heartbeat with cycles and energy data
            # Note: cmdFunc/cmdId mapping needs verification from actual MQTT logs
            # Trying multiple potential combinations based on ioBroker implementation
            elif (cmd_func == 3 and cmd_id in [1, 2, 30, 50]) or \
                 (cmd_func == 254 and cmd_id in [24, 25, 26, 27, 28, 29, 30]) or \
                 (cmd_func == 32 and cmd_id in [1, 3, 51, 52]):
                # BMSHeartBeatReport - contains cycles, input_watts, output_watts, accu_chg_energy, accu_dsg_energy
                try:
                    msg = pb2.BMSHeartBeatReport()
                    msg.ParseFromString(pdata)
                    _LOGGER.info(f"✅ Successfully decoded BMSHeartBeatReport: cmdFunc={cmd_func}, cmdId={cmd_id}")
                    return self._protobuf_to_dict(msg)
                except Exception as e:
                    _LOGGER.debug(f"Failed to decode as BMSHeartBeatReport (cmdFunc={cmd_func}, cmdId={cmd_id}): {e}")
                    # Fall through to unknown message type

            else:
                _LOGGER.warning(
                    f"Unknown message type: cmdFunc={cmd_func}, cmdId={cmd_id}"
                )
                return {}

        except Exception as e:
            _LOGGER.error(
                f"Message decode error for cmdFunc={cmd_func}, cmdId={cmd_id}: {e}"
            )
            return {}

    def _flatten_dict(self, d: dict, parent_key: str = "", sep: str = "_") -> dict:
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def _protobuf_to_dict(self, protobuf_obj: Any) -> dict[str, Any]:
        try:
            from google.protobuf.json_format import MessageToDict

            result = MessageToDict(protobuf_obj, preserving_proto_field_name=True)
            _LOGGER.debug(f"MessageToDict result: {len(result)} fields: {result}")
            return result
        except ImportError:
            result = self._manual_protobuf_to_dict(protobuf_obj)
            _LOGGER.debug(f"Manual conversion result: {len(result)} fields: {result}")
            return result

    def _manual_protobuf_to_dict(self, protobuf_obj: Any) -> dict[str, Any]:
        """手動でProtobufオブジェクトを辞書に変換."""
        result = {}
        for field, value in protobuf_obj.ListFields():
            if field.label == field.LABEL_REPEATED:
                result[field.name] = list(value)
            elif hasattr(value, "ListFields"):  # ネストしたメッセージ
                result[field.name] = self._manual_protobuf_to_dict(value)
            else:
                result[field.name] = value
        return result

    def _transform_data_fields(
        self, decoded_data: dict[str, Any], header_info: dict[str, Any]
    ) -> dict[str, Any]:
        # flat化して全フィールドを展開し、そのまま返す
        flat = self._flatten_dict(decoded_data)
        _LOGGER.debug(f"Flat dict (all fields to params): {flat}")
        return flat

    def _extract_unknown_fields(self, decoded_data: dict[str, Any]) -> dict[str, Any]:
        """unknown, 未定義, unknownXX_s1/s2 などを抽出 (flat)."""
        result = {}

        def _recurse(d, prefix=""):
            for k, v in d.items():
                if "unknown" in k:
                    result[prefix + k] = v
                elif isinstance(v, dict):
                    _recurse(v, prefix + k + ".")

        _recurse(decoded_data)
        return result

    @override
    def update_data(self, raw_data, data_type: str) -> bool:
        """DeltaPro3専用: data_topicのみProtobufデコード、それ以外はBaseDeviceのJSONデコード."""
        if data_type == self.device_info.data_topic:
            raw = self._prepare_data(raw_data)
            self.data.update_data(raw)
        elif data_type == self.device_info.set_topic:
            raw = BaseDevice._prepare_data(self, raw_data)
            self.data.add_set_message(raw)
        elif data_type == self.device_info.set_reply_topic:
            raw = BaseDevice._prepare_data(self, raw_data)
            self.data.add_set_reply_message(raw)
        elif data_type == self.device_info.get_topic:
            raw = BaseDevice._prepare_data(self, raw_data)
            self.data.add_get_message(raw)
        elif data_type == self.device_info.get_reply_topic:
            raw = BaseDevice._prepare_data(self, raw_data)
            self.data.add_get_reply_message(raw)
        else:
            return False
        return True
