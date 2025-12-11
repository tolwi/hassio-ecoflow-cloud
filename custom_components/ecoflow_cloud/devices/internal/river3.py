import logging
import time
from typing import Any, override

from homeassistant.components.binary_sensor import BinarySensorDeviceClass  # pyright: ignore[reportMissingImports]
from homeassistant.helpers.entity import EntityCategory  # pyright: ignore[reportMissingImports]

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.api.private_api import PrivateAPIMessageProtocol
from custom_components.ecoflow_cloud.devices import BaseDevice, const
from custom_components.ecoflow_cloud.devices.internal.proto import (
    ef_river3_pb2 as ef_river3_pb2,
)

from custom_components.ecoflow_cloud.entities import (
    BaseNumberEntity,
    BaseSelectEntity,
    BaseSensorEntity,
    BaseSwitchEntity,
)
from custom_components.ecoflow_cloud.number import (
    BatteryBackupLevel,
    ChargingPowerEntity,
    MaxBatteryLevelEntity,
    MinBatteryLevelEntity,
)
from custom_components.ecoflow_cloud.select import (
    DictSelectEntity,
    TimeoutDictSelectEntity,
)
from custom_components.ecoflow_cloud.sensor import (
    CapacitySensorEntity,
    CyclesSensorEntity,
    InEnergySensorEntity,
    InEnergySolarSensorEntity,
    InMilliampSensorEntity,
    InVoltSensorEntity,
    InWattsSensorEntity,
    LevelSensorEntity,
    MilliVoltSensorEntity,
    OutEnergySensorEntity,
    OutWattsSensorEntity,
    QuotaStatusSensorEntity,
    RemainSensorEntity,
    TempSensorEntity,
    VoltSensorEntity,
)
from custom_components.ecoflow_cloud.switch import BeeperEntity, EnabledEntity

_LOGGER = logging.getLogger(__name__)


class River3CommandMessage(PrivateAPIMessageProtocol):
    """Message wrapper for River 3 protobuf commands."""

    def __init__(self, packet: ef_river3_pb2.River3SendHeaderMsg):
        self._packet = packet

    def private_api_to_mqtt_payload(self):
        return self._packet.SerializeToString()


def _create_river3_proto_command(
    field_name: str, value: int, device_sn: str, data_len: int | None = None
):
    """Create a protobuf command for River 3."""
    # Build the command using the generated protobuf class
    cmd = ef_river3_pb2.River3SetCommand()
    try:
        setattr(cmd, field_name, int(value))
    except AttributeError:
        _LOGGER.error("Unknown River3 set field: %s", field_name)
        return None

    pdata = cmd.SerializeToString()

    packet = ef_river3_pb2.River3SendHeaderMsg()
    message = packet.msg.add()

    message.src = 32
    message.dest = 2
    message.d_src = 1
    message.d_dest = 1
    message.cmd_func = 254
    message.cmd_id = 17
    message.need_ack = 1
    message.seq = int(time.time() * 1000) % 2147483647
    message.product_id = 1
    message.version = 19
    message.payload_ver = 1
    message.device_sn = device_sn
    message.data_len = data_len if data_len is not None else len(pdata)
    message.pdata = pdata

    return River3CommandMessage(packet)


def _create_river3_energy_backup_command(
    energy_backup_en: int | None, energy_backup_start_soc: int, device_sn: str
):
    """Create a protobuf command for River 3 energy backup settings."""
    # Build the command using the generated protobuf classes
    cmd = ef_river3_pb2.River3SetCommand()
    cmd.cfg_energy_backup.energy_backup_start_soc = int(energy_backup_start_soc)
    if energy_backup_en is not None:
        cmd.cfg_energy_backup.energy_backup_en = int(energy_backup_en)

    pdata = cmd.SerializeToString()

    packet = ef_river3_pb2.River3SendHeaderMsg()
    message = packet.msg.add()

    message.src = 32
    message.dest = 2
    message.d_src = 1
    message.d_dest = 1
    message.cmd_func = 254
    message.cmd_id = 17
    message.need_ack = 1
    message.seq = int(time.time() * 1000) % 2147483647
    message.product_id = 1
    message.version = 19
    message.payload_ver = 1
    message.device_sn = device_sn
    message.data_len = len(pdata)
    message.pdata = pdata

    return River3CommandMessage(packet)


BMS_HEARTBEAT_COMMANDS: set[tuple[int, int]] = {
    (3, 1),
    (3, 2),
    (3, 30),
    (3, 50),
    (32, 1),
    (32, 3),
    (32, 50),
    (32, 51),
    (32, 52),
    (254, 24),
    (254, 25),
    (254, 26),
    (254, 27),
    (254, 28),
    (254, 29),
    (254, 30),
}


class River3ChargingStateSensorEntity(BaseSensorEntity):
    """Sensor for battery charging state."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:battery-charging"
    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING

    def _update_value(self, val: Any) -> bool:
        if val == 0:
            return super()._update_value("idle")
        elif val == 1:
            return super()._update_value("discharging")
        elif val == 2:
            return super()._update_value("charging")
        else:
            return False


class OutWattsAbsSensorEntity(OutWattsSensorEntity):
    """Output power sensor that uses absolute value."""

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(abs(int(val)))


class River3(BaseDevice):
    """EcoFlow River 3 device implementation using protobuf decoding."""

    @staticmethod
    def default_charging_power_step() -> int:
        return 50

    @override
    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [
            LevelSensorEntity(client, self, "bms_batt_soc", const.MAIN_BATTERY_LEVEL)
            .attr("bms_design_cap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("bms_full_cap", const.ATTR_FULL_CAPACITY, 0)
            .attr("bms_remain_cap", const.ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(
                client, self, "bms_design_cap", const.MAIN_DESIGN_CAPACITY, False
            ),
            CapacitySensorEntity(
                client, self, "bms_full_cap", const.MAIN_FULL_CAPACITY, False
            ),
            CapacitySensorEntity(
                client, self, "bms_remain_cap", const.MAIN_REMAIN_CAPACITY, False
            ),
            LevelSensorEntity(client, self, "bms_batt_soh", const.SOH),
            LevelSensorEntity(
                client, self, "cms_batt_soc", const.COMBINED_BATTERY_LEVEL
            ),
            River3ChargingStateSensorEntity(
                client, self, "bms_chg_dsg_state", const.BATTERY_CHARGING_STATE
            ),
            InWattsSensorEntity(
                client, self, "pow_in_sum_w", const.TOTAL_IN_POWER
            ).with_energy(),
            OutWattsSensorEntity(
                client, self, "pow_out_sum_w", const.TOTAL_OUT_POWER
            ).with_energy(),
            InWattsSensorEntity(client, self, "pow_get_pv", const.SOLAR_IN_POWER),
            InMilliampSensorEntity(
                client, self, "plug_in_info_pv_amp", const.SOLAR_IN_CURRENT
            ),
            InWattsSensorEntity(client, self, "pow_get_ac_in", const.AC_IN_POWER),
            OutWattsAbsSensorEntity(client, self, "pow_get_ac_out", const.AC_OUT_POWER),
            InVoltSensorEntity(
                client, self, "plug_in_info_ac_in_vol", const.AC_IN_VOLT
            ),
            # AC output voltage not available in proto
            OutWattsSensorEntity(client, self, "pow_get_12v", const.DC_OUT_POWER),
            OutWattsAbsSensorEntity(
                client, self, "pow_get_typec1", const.TYPEC_1_OUT_POWER
            ),
            OutWattsAbsSensorEntity(
                client, self, "pow_get_qcusb1", const.USB_QC_1_OUT_POWER
            ),
            OutWattsAbsSensorEntity(
                client, self, "pow_get_qcusb2", const.USB_QC_2_OUT_POWER
            ),
            RemainSensorEntity(
                client, self, "bms_chg_rem_time", const.CHARGE_REMAINING_TIME
            ),
            RemainSensorEntity(
                client, self, "bms_dsg_rem_time", const.DISCHARGE_REMAINING_TIME
            ),
            RemainSensorEntity(client, self, "cms_chg_rem_time", const.REMAINING_TIME),
            TempSensorEntity(client, self, "temp_pcs_dc", "PCS DC Temperature"),
            TempSensorEntity(client, self, "temp_pcs_ac", "PCS AC Temperature"),
            TempSensorEntity(
                client, self, "bms_min_cell_temp", const.BATTERY_TEMP
            ).attr("bms_max_cell_temp", const.ATTR_MAX_CELL_TEMP, 0),
            TempSensorEntity(
                client, self, "bms_max_cell_temp", const.MAX_CELL_TEMP, False
            ),
            VoltSensorEntity(client, self, "bms_batt_vol", const.BATTERY_VOLT, False)
            .attr("bms_min_cell_vol", const.ATTR_MIN_CELL_VOLT, 0)
            .attr("bms_max_cell_vol", const.ATTR_MAX_CELL_VOLT, 0),
            MilliVoltSensorEntity(
                client, self, "bms_min_cell_vol", const.MIN_CELL_VOLT, False
            ),
            MilliVoltSensorEntity(
                client, self, "bms_max_cell_vol", const.MAX_CELL_VOLT, False
            ),
            CyclesSensorEntity(client, self, "cycles", const.CYCLES),
            OutEnergySensorEntity(client, self, "ac_out_energy", "AC Output Energy"),
            InEnergySensorEntity(client, self, "ac_in_energy", "AC Input Energy"),
            InEnergySolarSensorEntity(
                client, self, "pv_in_energy", const.SOLAR_IN_ENERGY
            ),
            OutEnergySensorEntity(
                client, self, "dc12v_out_energy", "DC 12V Output Energy", False
            ),
            OutEnergySensorEntity(
                client, self, "typec_out_energy", "Type-C Output Energy", False
            ),
            OutEnergySensorEntity(
                client, self, "usba_out_energy", "USB-A Output Energy", False
            ),
            QuotaStatusSensorEntity(client, self),
        ]

    @override
    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        device = self
        return [
            MaxBatteryLevelEntity(
                client,
                self,
                "cms_max_chg_soc",
                const.MAX_CHARGE_LEVEL,
                50,
                100,
                lambda value: _create_river3_proto_command(
                    "cms_max_chg_soc", int(value), device.device_data.sn
                ),
            ),
            MinBatteryLevelEntity(
                client,
                self,
                "cms_min_dsg_soc",
                const.MIN_DISCHARGE_LEVEL,
                0,
                30,
                lambda value: _create_river3_proto_command(
                    "cms_min_dsg_soc", int(value), device.device_data.sn
                ),
            ),
            ChargingPowerEntity(
                client,
                self,
                "plug_in_info_ac_in_chg_pow_max",
                const.AC_CHARGING_POWER,
                50,
                305,
                lambda value: _create_river3_proto_command(
                    "plug_in_info_ac_in_chg_pow_max", int(value), device.device_data.sn
                ),
            ),
            BatteryBackupLevel(
                client,
                self,
                "energy_backup_start_soc",
                const.BACKUP_RESERVE_LEVEL,
                5,
                100,
                "cms_min_dsg_soc",
                "cms_max_chg_soc",
                5,
                lambda value: _create_river3_energy_backup_command(
                    1, int(value), device.device_data.sn
                ),
            ),
        ]

    @override
    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        device = self
        return [
            BeeperEntity(
                client,
                self,
                "en_beep",
                const.BEEPER,
                lambda value: _create_river3_proto_command(
                    "en_beep", 1 if value else 0, device.device_data.sn, data_len=2
                ),
            ),
            EnabledEntity(
                client,
                self,
                "cfg_ac_out_open",
                const.AC_ENABLED,
                lambda value, params=None: _create_river3_proto_command(
                    "cfg_ac_out_open", 1 if value else 0, device.device_data.sn
                ),
            ),
            EnabledEntity(
                client,
                self,
                "xboost_en",
                const.XBOOST_ENABLED,
                lambda value, params=None: _create_river3_proto_command(
                    "xboost_en", 1 if value else 0, device.device_data.sn
                ),
            ),
            EnabledEntity(
                client,
                self,
                "cfg_dc12v_out_open",
                const.DC_ENABLED,
                lambda value, params=None: _create_river3_proto_command(
                    "cfg_dc12v_out_open", 1 if value else 0, device.device_data.sn
                ),
            ),
            EnabledEntity(
                client,
                self,
                "output_power_off_memory",
                const.AC_ALWAYS_ENABLED,
                lambda value, params=None: _create_river3_proto_command(
                    "output_power_off_memory", 1 if value else 0, device.device_data.sn
                ),
            ),
            EnabledEntity(
                client,
                self,
                "energy_backup_en",
                const.BP_ENABLED,
                lambda value, params=None: _create_river3_energy_backup_command(
                    1 if value else None,
                    params.get("energy_backup_start_soc", 5) if params else 5,
                    device.device_data.sn,
                ),
            ),
        ]

    @override
    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        device = self
        dc_charge_current_options = {"4A": 4, "6A": 6, "8A": 8}
        return [
            DictSelectEntity(
                client,
                self,
                "plug_in_info_pv_dc_amp_max",
                const.DC_CHARGE_CURRENT,
                dc_charge_current_options,
                lambda value: _create_river3_proto_command(
                    "plug_in_info_pv_dc_amp_max", int(value), device.device_data.sn
                ),
            ),
            DictSelectEntity(
                client,
                self,
                "pv_chg_type",
                const.DC_MODE,
                const.DC_MODE_OPTIONS,
                lambda value: _create_river3_proto_command(
                    "pv_chg_type", int(value), device.device_data.sn
                ),
            ),
            TimeoutDictSelectEntity(
                client,
                self,
                "screen_off_time",
                const.SCREEN_TIMEOUT,
                const.SCREEN_TIMEOUT_OPTIONS,
                lambda value: _create_river3_proto_command(
                    "screen_off_time", int(value), device.device_data.sn
                ),
            ),
            TimeoutDictSelectEntity(
                client,
                self,
                "dev_standby_time",
                const.UNIT_TIMEOUT,
                const.UNIT_TIMEOUT_OPTIONS,
                lambda value: _create_river3_proto_command(
                    "dev_standby_time", int(value), device.device_data.sn
                ),
            ),
            TimeoutDictSelectEntity(
                client,
                self,
                "ac_standby_time",
                const.AC_TIMEOUT,
                const.AC_TIMEOUT_OPTIONS,
                lambda value: _create_river3_proto_command(
                    "ac_standby_time", int(value), device.device_data.sn
                ),
            ),
        ]

    @override
    def _prepare_data(self, raw_data: bytes) -> dict[str, Any]:
        """Prepare River 3 data by decoding protobuf and flattening fields."""
        flat_dict: dict[str, Any] | None = None
        decoded_data: dict[str, Any] | None = None
        try:
            header_info = self._decode_header_message(raw_data)
            if not header_info:
                return super()._prepare_data(raw_data)

            pdata = self._extract_payload_data(header_info.get("header_obj"))
            if not pdata:
                return {}

            decoded_pdata = self._perform_xor_decode(pdata, header_info)
            decoded_data = self._decode_message_by_type(decoded_pdata, header_info)
            if not decoded_data:
                return {}

            flat_dict = self._flatten_dict(decoded_data)
        except Exception as e:
            _LOGGER.debug(f"[River3] Data processing failed: {e}")
            return super()._prepare_data(raw_data)

        return {
            "params": flat_dict or {},
            "all_fields": decoded_data or {},
        }

    def _decode_header_message(self, raw_data: bytes) -> dict[str, Any] | None:
        """Decode HeaderMessage and extract header info."""
        try:
            import base64

            try:
                decoded_payload = base64.b64decode(raw_data, validate=True)
                raw_data = decoded_payload
            except Exception as e:
                # If base64 decoding fails, proceed with the original raw_data (it may not be base64 encoded)
                _LOGGER.debug("[River3] base64 decode failed: %s", e)

            try:
                header_msg = ef_river3_pb2.River3HeaderMessage()
                header_msg.ParseFromString(raw_data)
            except Exception as e:
                _LOGGER.debug("[River3] Failed to parse header message: %s", e)
                return None

            if not header_msg.header:
                return None

            header = header_msg.header[0]
            return {
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
        except Exception as e:
            _LOGGER.debug("[River3] Failed to decode header message: %s", e)
            return None

    def _extract_payload_data(self, header_obj: Any) -> bytes | None:
        """Extract payload bytes from header."""
        try:
            pdata = getattr(header_obj, "pdata", b"")
            return pdata if pdata else None
        except Exception as e:
            _LOGGER.debug("[River3] Failed to extract payload data: %s", e)
            return None

    def _perform_xor_decode(self, pdata: bytes, header_info: dict[str, Any]) -> bytes:
        """Perform XOR decoding if required by header info."""
        enc_type = header_info.get("encType", 0)
        src = header_info.get("src", 0)
        seq = header_info.get("seq", 0)
        if enc_type == 1 and src != 32:
            return self._xor_decode_pdata(pdata, seq)
        return pdata

    def _xor_decode_pdata(self, pdata: bytes, seq: int) -> bytes:
        """Apply XOR over payload with sequence value."""
        if not pdata:
            return b""

        decoded_payload = bytearray()
        for byte_val in pdata:
            decoded_payload.append((byte_val ^ seq) & 0xFF)

        return bytes(decoded_payload)

    def _decode_message_by_type(
        self, pdata: bytes, header_info: dict[str, Any]
    ) -> dict[str, Any]:
        """Decode protobuf message based on cmdFunc/cmdId.
        - cmdFunc=254, cmdId=21: DisplayPropertyUpload
        - cmdFunc=254, cmdId=22: RuntimePropertyUpload
        - cmdFunc=254, cmdId=17: Set command
        - cmdFunc=254, cmdId=18: Set reply
        """
        cmd_func = header_info.get("cmdFunc", 0)
        cmd_id = header_info.get("cmdId", 0)

        try:
            if cmd_func == 254 and cmd_id == 21:
                msg = ef_river3_pb2.River3DisplayPropertyUpload()
                msg.ParseFromString(pdata)
                result = self._protobuf_to_dict(msg)
                return self._extract_statistics(result)

            elif cmd_func == 254 and cmd_id == 22:
                msg = ef_river3_pb2.River3RuntimePropertyUpload()
                msg.ParseFromString(pdata)
                return self._protobuf_to_dict(msg)

            elif cmd_func == 254 and cmd_id == 17:
                try:
                    msg = ef_river3_pb2.River3SetCommand()
                    msg.ParseFromString(pdata)
                    return self._protobuf_to_dict(msg)
                except Exception as e:
                    _LOGGER.debug("Failed to decode as River3SetCommand: %s", e)
                    return {}

            elif cmd_func == 254 and cmd_id == 18:
                try:
                    msg = ef_river3_pb2.River3SetReply()
                    msg.ParseFromString(pdata)
                    result = self._protobuf_to_dict(msg)
                    return result if result.get("config_ok", False) else {}
                except Exception as e:
                    _LOGGER.debug(f"Failed to decode as setReply_dp3: {e}")
                    return {}

            elif cmd_func == 32 and cmd_id == 2:
                try:
                    msg = ef_river3_pb2.River3CMSHeartBeatReport()
                    msg.ParseFromString(pdata)
                    return self._protobuf_to_dict(msg)
                except Exception as e:
                    _LOGGER.debug(f"Failed to decode as cmdFunc32_cmdId2_Report: {e}")
                    return {}

            elif self._is_bms_heartbeat(cmd_func, cmd_id):
                try:
                    msg = ef_river3_pb2.River3BMSHeartBeatReport()
                    msg.ParseFromString(pdata)
                    return self._protobuf_to_dict(msg)
                except Exception as e:
                    _LOGGER.debug(
                        f"Failed to decode as BMSHeartBeatReport (cmdFunc={cmd_func}, cmdId={cmd_id}): {e}"
                    )
                    return {}

            # Unknown message type - try BMSHeartBeatReport as fallback
            try:
                msg = ef_river3_pb2.River3BMSHeartBeatReport()
                msg.ParseFromString(pdata)
                result = self._protobuf_to_dict(msg)
                if (
                    "cycles" in result
                    or "accu_chg_energy" in result
                    or "accu_dsg_energy" in result
                ):
                    return result
            except Exception as e:
                _LOGGER.debug("Failed to decode as fallback BMSHeartBeatReport: %s", e)

            return {}
        except Exception as e:
            _LOGGER.debug(
                f"Message decode error for cmdFunc={cmd_func}, cmdId={cmd_id}: {e}"
            )
            return {}

    def _is_bms_heartbeat(self, cmd_func: int, cmd_id: int) -> bool:
        """Return True if the pair maps to a BMSHeartBeatReport message."""
        return (cmd_func, cmd_id) in BMS_HEARTBEAT_COMMANDS

    def _flatten_dict(self, d: dict, parent_key: str = "", sep: str = "_") -> dict:
        """Flatten nested dict with underscore separator."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def _protobuf_to_dict(self, protobuf_obj: Any) -> dict[str, Any]:
        """Convert protobuf message to dictionary."""
        try:
            from google.protobuf.json_format import MessageToDict

            return MessageToDict(protobuf_obj, preserving_proto_field_name=True)
        except ImportError:
            return self._manual_protobuf_to_dict(protobuf_obj)

    def _extract_statistics(self, data: dict[str, Any]) -> dict[str, Any]:
        """Extract statistics from display_statistics_sum into flat fields."""
        stats_sum = data.get("display_statistics_sum", {})
        list_info = stats_sum.get("list_info", [])

        if not list_info:
            return data

        for item in list_info:
            stat_obj = item.get("statistics_object") or item.get("statisticsObject")
            stat_content = item.get("statistics_content") or item.get(
                "statisticsContent"
            )

            if stat_obj is not None and stat_content is not None:
                if isinstance(stat_obj, str) and stat_obj.startswith(
                    "STATISTICS_OBJECT_"
                ):
                    field_name = stat_obj.replace("STATISTICS_OBJECT_", "").lower()
                    data[field_name] = stat_content
                elif isinstance(stat_obj, int):
                    try:
                        enum_name = ef_river3_pb2.River3StatisticsObject.Name(stat_obj)
                        if enum_name.startswith("STATISTICS_OBJECT_"):
                            field_name = enum_name.replace(
                                "STATISTICS_OBJECT_", ""
                            ).lower()
                            data[field_name] = stat_content
                    except ValueError as e:
                        _LOGGER.debug(
                            "Failed to get enum name for statistics object %s: %s",
                            stat_obj,
                            e,
                        )

        return data

    def _manual_protobuf_to_dict(self, protobuf_obj: Any) -> dict[str, Any]:
        """Convert protobuf object to dict manually (fallback)."""
        result = {}
        for field, value in protobuf_obj.ListFields():
            if field.label == field.LABEL_REPEATED:
                result[field.name] = list(value)
            elif hasattr(value, "ListFields"):  # nested message
                result[field.name] = self._manual_protobuf_to_dict(value)
            else:
                result[field.name] = value
        return result

    @override
    def update_data(self, raw_data, data_type: str) -> bool:
        """Decode protobuf for data_topic; silently handle other topics."""
        if data_type == self.device_info.data_topic:
            raw = self._prepare_data(raw_data)
            self.data.update_data(raw)
        elif data_type == self.device_info.set_topic:
            pass
        elif data_type == self.device_info.set_reply_topic:
            raw = self._prepare_set_reply_data(raw_data)
            if raw:
                self.data.update_data(raw)
            self.data.add_set_reply_message(raw)
        elif data_type == self.device_info.get_topic:
            pass
        elif data_type == self.device_info.get_reply_topic:
            raw = self._prepare_set_reply_data(raw_data)
            if raw:
                self.data.update_data(raw)
            self.data.add_get_reply_message(raw)
        else:
            return False
        return True

    def _prepare_set_reply_data(self, raw_data: bytes) -> dict[str, Any]:
        """Parse set/get reply data - try protobuf, fall back to quiet JSON."""
        try:
            import base64

            try:
                decoded_payload = base64.b64decode(raw_data, validate=True)
                raw_data = decoded_payload
            except Exception as e:
                # If base64 decoding fails, proceed with the original raw_data (it may not be base64 encoded)
                _LOGGER.debug("[River3] base64 decode failed: %s", e)

            header_msg = ef_river3_pb2.River3HeaderMessage()
            header_msg.ParseFromString(raw_data)

            if header_msg.header:
                header = header_msg.header[0]
                pdata = getattr(header, "pdata", b"")
                if pdata:
                    try:
                        enc_type = getattr(header, "enc_type", 0)
                        src = getattr(header, "src", 0)
                        seq = getattr(header, "seq", 0)
                        if enc_type == 1 and src != 32:
                            pdata = self._xor_decode_pdata(pdata, seq)

                        reply_msg = ef_river3_pb2.River3SetReply()
                        reply_msg.ParseFromString(pdata)
                        result = self._protobuf_to_dict(reply_msg)
                        return {"params": self._flatten_dict(result)}
                    except Exception as e:
                        _LOGGER.debug(f"Failed to parse as River3SetReply: {e}")
        except Exception as e:
            _LOGGER.debug(f"Protobuf parse failed for set_reply: {e}")

        return super()._prepare_data(raw_data)
