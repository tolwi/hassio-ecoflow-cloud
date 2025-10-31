import logging
from typing import Any, override

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import BaseDevice, const

# Protocol Buffers modules are imported lazily in _prepare_data method
from custom_components.ecoflow_cloud.entities import (
    BaseNumberEntity,
    BaseSelectEntity,
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
    OutVoltDcSensorEntity,
    OutWattsDcSensorEntity,
    OutWattsSensorEntity,
    QuotaStatusSensorEntity,
    RemainSensorEntity,
    TempSensorEntity,
)
from custom_components.ecoflow_cloud.switch import BeeperEntity, EnabledEntity

_LOGGER = logging.getLogger(__name__)

# Message type mapping for BMS heartbeat related reports
# These (cmdFunc, cmdId) pairs are known to map to BMSHeartBeatReport
BMS_HEARTBEAT_COMMANDS: set[tuple[int, int]] = {
    (3, 1),
    (3, 2),
    (3, 30),
    (3, 50),
    (254, 24),
    (254, 25),
    (254, 26),
    (254, 27),
    (254, 28),
    (254, 29),
    (254, 30),
    (32, 1),
    (32, 3),
    (32, 50),
    (32, 51),
    (32, 52),
}


class DeltaPro3(BaseDevice):
    @override
    def sensors(self, client: EcoflowApiClient) -> list[Any]:
        return [
            # Main Battery System - using actual protobuf field names
            LevelSensorEntity(client, self, "bms_batt_soc", const.MAIN_BATTERY_LEVEL)
            .attr("bms_design_cap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("bms_full_cap_mah", const.ATTR_FULL_CAPACITY, 0)
            .attr("bms_remain_cap_mah", const.ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, self, "bms_design_cap", const.MAIN_DESIGN_CAPACITY, False),
            CapacitySensorEntity(client, self, "bms_full_cap_mah", const.MAIN_FULL_CAPACITY, False),
            CapacitySensorEntity(client, self, "bms_remain_cap_mah", const.MAIN_REMAIN_CAPACITY, False),
            LevelSensorEntity(client, self, "bms_batt_soh", const.SOH),
            # Cycles from BMSHeartBeatReport (not DisplayPropertyUpload)
            CyclesSensorEntity(client, self, "cycles", const.CYCLES),
            MilliVoltSensorEntity(client, self, "bms_batt_vol", const.BATTERY_VOLT, False)
            .attr("bms_min_cell_vol", const.ATTR_MIN_CELL_VOLT, 0)
            .attr("bms_max_cell_vol", const.ATTR_MAX_CELL_VOLT, 0),
            MilliVoltSensorEntity(client, self, "bms_min_cell_vol", const.MIN_CELL_VOLT, False),
            MilliVoltSensorEntity(client, self, "bms_max_cell_vol", const.MAX_CELL_VOLT, False),
            AmpSensorEntity(client, self, "bms_batt_amp", const.MAIN_BATTERY_CURRENT, False),
            TempSensorEntity(client, self, "bms_max_cell_temp", const.MAX_CELL_TEMP, False),
            TempSensorEntity(client, self, "bms_min_cell_temp", const.MIN_CELL_TEMP, False),
            TempSensorEntity(client, self, "bms_max_mos_temp", const.BATTERY_TEMP)
            .attr("bms_min_cell_temp", const.ATTR_MIN_CELL_TEMP, 0)
            .attr("bms_max_cell_temp", const.ATTR_MAX_CELL_TEMP, 0),
            RemainSensorEntity(client, self, "bms_chg_rem_time", const.CHARGE_REMAINING_TIME),
            RemainSensorEntity(client, self, "bms_dsg_rem_time", const.DISCHARGE_REMAINING_TIME),
            LevelSensorEntity(client, self, "cms_batt_soc", const.COMBINED_BATTERY_LEVEL),
            OutWattsSensorEntity(client, self, "pow_out_sum_w", const.TOTAL_OUT_POWER),
            InWattsSensorEntity(client, self, "pow_in_sum_w", const.TOTAL_IN_POWER),
            InWattsSensorEntity(client, self, "pow_get_ac_in", const.AC_IN_POWER),
            OutWattsSensorEntity(client, self, "pow_get_ac", const.AC_OUT_POWER),
            OutWattsSensorEntity(client, self, "pow_get_ac_hv_out", "AC HV Output Power"),
            OutWattsSensorEntity(client, self, "pow_get_ac_lv_out", "AC LV Output Power"),
            InMilliVoltSensorEntity(client, self, "plug_in_info_ac_in_vol", const.AC_IN_VOLT),
            InMilliampSolarSensorEntity(client, self, "plug_in_info_ac_in_amp", "AC Input Current"),
            OutWattsDcSensorEntity(client, self, "pow_get_12v", "12V DC Output Power"),
            OutWattsDcSensorEntity(client, self, "pow_get_24v", "24V DC Output Power"),
            OutVoltDcSensorEntity(client, self, "pow_get_12v_vol", "12V DC Output Voltage"),
            OutVoltDcSensorEntity(client, self, "pow_get_24v_vol", "24V DC Output Voltage"),
            InWattsSolarSensorEntity(client, self, "pow_get_pv_h", "Solar High Voltage Input Power"),
            InWattsSolarSensorEntity(client, self, "pow_get_pv_l", "Solar Low Voltage Input Power"),
            InVoltSolarSensorEntity(client, self, "pow_get_pv_h_vol", "Solar HV Input Voltage"),
            InVoltSolarSensorEntity(client, self, "pow_get_pv_l_vol", "Solar LV Input Voltage"),
            InMilliampSolarSensorEntity(client, self, "pow_get_pv_h_amp", "Solar HV Input Current"),
            InMilliampSolarSensorEntity(client, self, "pow_get_pv_l_amp", "Solar LV Input Current"),
            OutWattsSensorEntity(client, self, "pow_get_qcusb1", const.USB_QC_1_OUT_POWER),
            OutWattsSensorEntity(client, self, "pow_get_qcusb2", const.USB_QC_2_OUT_POWER),
            OutWattsSensorEntity(client, self, "pow_get_typec1", const.TYPEC_1_OUT_POWER),
            OutWattsSensorEntity(client, self, "pow_get_typec2", const.TYPEC_2_OUT_POWER),
            OutWattsDcSensorEntity(client, self, "pow_get_5p8", "5P8 Power I/O Port Power"),
            OutWattsDcSensorEntity(client, self, "pow_get_4p8_1", "4P8 Extra Battery Port 1 Power"),
            OutWattsDcSensorEntity(client, self, "pow_get_4p8_2", "4P8 Extra Battery Port 2 Power"),
            OutWattsSensorEntity(client, self, "ac_out_freq", "AC Output Frequency"),
            LevelSensorEntity(client, self, "cms_max_chg_soc", "Max Charge SOC Setting"),
            LevelSensorEntity(client, self, "cms_min_dsg_soc", "Min Discharge SOC Setting"),
            # Energy sensors from BMSHeartBeatReport
            # Note: accuChgEnergy and accuDsgEnergy are in Wh, multiply by 0.001 for kWh display
            # These fields do not exist in DisplayPropertyUpload - they come from BMSHeartBeatReport
            # Using camelCase to match upstream pattern (see stream_ac.py)
            InEnergySensorEntity(client, self, "accuChgEnergy", "Total Charge Energy"),
            OutEnergySensorEntity(client, self, "accuDsgEnergy", "Total Discharge Energy"),
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
        """Prepare Delta Pro 3 data by decoding protobuf and flattening fields."""
        _LOGGER.debug(f"[DeltaPro3] _prepare_data called with {len(raw_data)} bytes")

        # Lazy import of Protocol Buffers modules to avoid blocking calls
        try:
            from .proto import ef_dp3_iobroker_pb2 as pb2
        except Exception as e:
            # protobuf generated modules can raise non-ImportError exceptions
            # (for example descriptor build errors when duplicate symbols exist).
            # Catch all exceptions here and fall back to JSON processing so
            # the integration doesn't crash Home Assistant.
            _LOGGER.error("Failed to import ef_dp3_iobroker_pb2: %s: %s", type(e).__name__, e)
            _LOGGER.debug("Falling back to parent JSON processing due to pb2 import error")
            return super()._prepare_data(raw_data)

        flat_dict: dict[str, Any] | None = None
        decoded_data: dict[str, Any] | None = None
        try:
            _LOGGER.debug(f"Processing {len(raw_data)} bytes of raw data")

            # 1. Decode HeaderMessage
            header_info = self._decode_header_message(raw_data)
            if not header_info:
                _LOGGER.warning("HeaderMessage decoding failed, trying JSON fallback")
                return super()._prepare_data(raw_data)

            # 2. Extract payload data
            pdata = self._extract_payload_data(header_info.get("header_obj"))
            if not pdata:
                _LOGGER.warning("No payload data found")
                return {}

            # 3. XOR decode (if needed)
            decoded_pdata = self._perform_xor_decode(pdata, header_info)

            # 4. Protobuf message decode
            decoded_data = self._decode_message_by_type(decoded_pdata, header_info)
            if not decoded_data:
                _LOGGER.warning("Message decoding failed")
                return {}

            # 5. Flatten all fields for params
            flat_dict = self._flatten_dict(decoded_data)
            _LOGGER.debug(f"Flat dict for params (all fields): {flat_dict}")  # noqa: G004
        except Exception as e:
            _LOGGER.error(f"[DeltaPro3] Data processing failed: {e}", exc_info=True)
            _LOGGER.debug("[DeltaPro3] Attempting JSON fallback after protobuf failure")
            # Fallback to parent's JSON processing for compatibility
            try:
                return super()._prepare_data(raw_data)
            except Exception as e2:
                _LOGGER.error(f"[DeltaPro3] JSON fallback also failed: {e2}")
                return {}

        # Home Assistant expects a dict with 'params' on success
        _LOGGER.debug(f"[DeltaPro3] Successfully processed protobuf data, returning {len(flat_dict or {})} fields")
        return {
            "params": flat_dict or {},
            "all_fields": decoded_data or {},
        }

    def _decode_header_message(self, raw_data: bytes) -> dict[str, Any] | None:
        """Decode HeaderMessage and extract header info."""
        try:
            # Try Base64 decode
            import base64

            try:
                decoded_payload = base64.b64decode(raw_data, validate=True)
                _LOGGER.debug("Base64 decode successful")
                raw_data = decoded_payload
            except Exception:
                _LOGGER.debug("Data is not Base64 encoded, using as-is")

            # Try to decode as HeaderMessage
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

            # Use the first header (usually single)
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

            _LOGGER.debug(f"Header decoded: cmdFunc={header_info['cmdFunc']}, cmdId={header_info['cmdId']}")
            return header_info

        except Exception as e:
            _LOGGER.debug(f"HeaderMessage decode failed: {e}")
            return None

    def _extract_payload_data(self, header_obj: Any) -> bytes | None:
        """Extract payload bytes from header."""
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
        """Perform XOR decoding if required by header info."""
        enc_type = header_info.get("encType", 0)
        src = header_info.get("src", 0)
        seq = header_info.get("seq", 0)

        # XOR decode condition: enc_type == 1 and src != 32
        if enc_type == 1 and src != 32:
            return self._xor_decode_pdata(pdata, seq)
        else:
            return pdata

    def _xor_decode_pdata(self, pdata: bytes, seq: int) -> bytes:
        """Apply XOR over payload with sequence value."""
        if not pdata:
            return b""

        decoded_payload = bytearray()
        for byte_val in pdata:
            decoded_payload.append((byte_val ^ seq) & 0xFF)

        return bytes(decoded_payload)

    def _decode_message_by_type(self, pdata: bytes, header_info: dict[str, Any]) -> dict[str, Any]:
        """Decode protobuf message based on cmdFunc/cmdId."""
        cmd_func = header_info.get("cmdFunc", 0)
        cmd_id = header_info.get("cmdId", 0)

        try:
            _LOGGER.debug(f"Decoding message: cmdFunc={cmd_func}, cmdId={cmd_id}, size={len(pdata)} bytes")

            # Import pb2 module
            from .proto import ef_dp3_iobroker_pb2 as pb2

            if cmd_func == 254 and cmd_id == 21:
                # DisplayPropertyUpload
                msg = pb2.DisplayPropertyUpload()
                msg.ParseFromString(pdata)
                return self._protobuf_to_dict(msg)

            elif cmd_func == 32 and cmd_id == 2:
                # cmdFunc32_cmdId2_Report (CMSHeartBeatReport)
                msg = pb2.cmdFunc32_cmdId2_Report()
                msg.ParseFromString(pdata)
                return self._protobuf_to_dict(msg)

            elif cmd_func == 254 and cmd_id == 22:
                # RuntimePropertyUpload - frequently updated runtime properties
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
                            timestamp = int.from_bytes(pdata[:4], byteorder="little", signed=True)
                            return {
                                "cmdFunc": cmd_func,
                                "cmdId": cmd_id,
                                "report_timestamp": timestamp,
                                "raw_data_length": len(pdata),
                            }
                    except Exception:
                        pass
                    return {"cmdFunc": cmd_func, "cmdId": cmd_id, "raw_data_length": len(pdata)}

            elif cmd_func == 254 and cmd_id == 23:
                # cmdFunc254_cmdId23_Report - report with timestamp
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
                            timestamp = int.from_bytes(pdata[:4], byteorder="little", signed=True)
                            return {
                                "cmdFunc": cmd_func,
                                "cmdId": cmd_id,
                                "report_timestamp": timestamp,
                                "raw_data_length": len(pdata),
                            }
                    except Exception:
                        pass
                    return {"cmdFunc": cmd_func, "cmdId": cmd_id, "raw_data_length": len(pdata)}

            # BMSHeartBeatReport - Battery heartbeat with cycles and energy data
            # Verified from ioBroker implementation: cmdFunc=32, cmdId=50
            # Reference: https://github.com/foxthefox/ioBroker.ecoflow-mqtt/blob/main/lib/dict_data/ef_deltapro3_data.js#L4958
            elif self._is_bms_heartbeat(cmd_func, cmd_id):
                # BMSHeartBeatReport - contains cycles, input_watts, output_watts, accu_chg_energy, accu_dsg_energy
                try:
                    msg = pb2.BMSHeartBeatReport()
                    msg.ParseFromString(pdata)
                    _LOGGER.info(f"Successfully decoded BMSHeartBeatReport: cmdFunc={cmd_func}, cmdId={cmd_id}")
                    return self._protobuf_to_dict(msg)
                except Exception as e:
                    _LOGGER.debug(f"Failed to decode as BMSHeartBeatReport (cmdFunc={cmd_func}, cmdId={cmd_id}): {e}")
                    # Fall through to unknown message type

            # Unknown message type - try BMSHeartBeatReport as fallback
            _LOGGER.warning(f"Unknown message type: cmdFunc={cmd_func}, cmdId={cmd_id}, size={len(pdata)} bytes")

            # Try to decode as BMSHeartBeatReport since that's a common case
            try:
                msg = pb2.BMSHeartBeatReport()
                msg.ParseFromString(pdata)
                result = self._protobuf_to_dict(msg)
                # Check if we got meaningful data (cycles or energy fields)
                if "cycles" in result or "accu_chg_energy" in result or "accu_dsg_energy" in result:
                    _LOGGER.warning(
                        f"Found BMSHeartBeatReport at unexpected cmdFunc={cmd_func}, cmdId={cmd_id}. "
                        f"Consider updating mapping in _decode_message_by_type."
                    )
                    return result
            except Exception as e:
                _LOGGER.debug(f"Failed fallback BMSHeartBeatReport decode: {e}")

            return {}

        except Exception as e:
            _LOGGER.error(f"Message decode error for cmdFunc={cmd_func}, cmdId={cmd_id}: {e}")
            return {}

    def _is_bms_heartbeat(self, cmd_func: int, cmd_id: int) -> bool:
        """Return True if the pair maps to a BMSHeartBeatReport message."""
        return (cmd_func, cmd_id) in BMS_HEARTBEAT_COMMANDS

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
            _LOGGER.debug(f"MessageToDict result fields: {len(result)}")
            return result
        except ImportError:
            result = self._manual_protobuf_to_dict(protobuf_obj)
            _LOGGER.debug(f"Manual conversion result fields: {len(result)}")
            return result

    def _manual_protobuf_to_dict(self, protobuf_obj: Any) -> dict[str, Any]:
        """Convert protobuf object to dict manually."""
        result = {}
        for field, value in protobuf_obj.ListFields():
            if field.label == field.LABEL_REPEATED:
                result[field.name] = list(value)
            elif hasattr(value, "ListFields"):  # nested message
                result[field.name] = self._manual_protobuf_to_dict(value)
            else:
                result[field.name] = value
        return result

    def _transform_data_fields(self, decoded_data: dict[str, Any], header_info: dict[str, Any]) -> dict[str, Any]:
        # Flatten and return all fields
        flat = self._flatten_dict(decoded_data)
        _LOGGER.debug(f"Flat dict (all fields to params): {flat}")
        return flat

    def _extract_unknown_fields(self, decoded_data: dict[str, Any]) -> dict[str, Any]:
        """Extract fields that look like 'unknown*' (flattened)."""
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
        """Decode protobuf only for data_topic; otherwise use BaseDevice JSON path."""
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
