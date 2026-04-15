from homeassistant.components.select import SelectEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.number import NumberEntity
from custom_components.ecoflow_cloud.entities import BaseSensorEntity
from homeassistant.components.sensor import SensorEntity
from custom_components.ecoflow_cloud.devices.data_holder import PreparedData
from custom_components.ecoflow_cloud.api.message import Message
from custom_components.ecoflow_cloud.api.message import PrivateAPIMessageProtocol
import logging
import time
from typing import Any, override

from google.protobuf.json_format import MessageToDict
from homeassistant.helpers.entity import EntityCategory  # pyright: ignore[reportMissingImports]

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import BaseInternalDevice, const
from custom_components.ecoflow_cloud.devices.internal.proto import (
    ef_delta3_pb2 as delta3_pb2,
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
    InEnergySolarSensorEntity,
    InMilliampSensorEntity,
    InVoltSensorEntity,
    InWattsSensorEntity,
    LevelSensorEntity,
    MilliVoltSensorEntity,
    OutVoltSensorEntity,
    OutWattsSensorEntity,
    QuotaStatusSensorEntity,
    RemainSensorEntity,
    TempSensorEntity,
    VoltSensorEntity,
)
from custom_components.ecoflow_cloud.switch import (
    BeeperEntity,
    BypassBanScalarSwitch,
    EnabledEntity,
)

_LOGGER = logging.getLogger(__name__)


class Delta3CommandMessage(PrivateAPIMessageProtocol):
    """Message wrapper for Delta 3 protobuf commands."""

    def __init__(
        self,
        payload: delta3_pb2.Delta3SetCommand,
        packet: delta3_pb2.Delta3SendHeaderMsg,
    ):
        self._packet = packet
        self._payload = payload

    @override
    def to_mqtt_payload(self):
        return self._packet.SerializeToString()

    @override
    def to_dict(self) -> dict:
        payload_dict = MessageToDict(self._payload, preserving_proto_field_name=True)

        result = MessageToDict(self._packet, preserving_proto_field_name=True)
        result["msg"][0]["pdata"] = {type(self._payload).__name__: payload_dict}
        result["msg"][0].pop("seq", None)
        return {type(self._packet).__name__: result}


def _create_delta3_proto_command(field_name: str, value: int, device_sn: str, data_len: int | None = None):
    """Create a protobuf command for Delta 3."""
    # Build the command using the generated protobuf class
    payload = delta3_pb2.Delta3SetCommand()
    try:
        setattr(payload, field_name, int(value))
    except AttributeError:
        _LOGGER.error("Unknown Delta3 set field: %s", field_name)
        return None

    pdata = payload.SerializeToString()

    packet = delta3_pb2.Delta3SendHeaderMsg()
    message = packet.msg.add()

    message.src = 32
    message.dest = 2
    message.d_src = 1
    message.d_dest = 1
    message.cmd_func = 254
    message.cmd_id = 17
    message.need_ack = 1
    message.seq = Message.gen_seq()
    message.product_id = 1
    message.version = 19
    message.payload_ver = 1
    message.device_sn = device_sn
    message.data_len = data_len if data_len is not None else len(pdata)
    message.pdata = pdata

    return Delta3CommandMessage(payload, packet)


def _create_delta3_bypass_ban_command(value: int, device_sn: str) -> "Delta3CommandMessage":
    """Create a protobuf command for bypassBan / ban_bypass_en on DELTA 3.

    Field 26 of ``Delta3SetCommand`` — discovered via MQTT sniffing, not
    yet defined in the generated ``ef_delta3_pb2`` schema, so the pdata
    is crafted manually as a 3-byte varint encoding:

      tag   = (26 << 3) | 0 = 208 -> varint "d0 01"
      value = 0 or 1              (1 byte varint)

    Semantics match DELTA 3 1500 ``banBypassEn``:
      value=0 -> grid bypass enabled  (battery charges from AC input)
      value=1 -> grid bypass disabled (battery runs standalone, no charging)
    """
    pdata = bytes([0xD0, 0x01, 1 if value else 0])

    packet = delta3_pb2.Delta3SendHeaderMsg()
    message = packet.msg.add()
    message.src = 32
    message.dest = 2
    message.d_src = 1
    message.d_dest = 1
    message.cmd_func = 254
    message.cmd_id = 17
    message.need_ack = 1
    message.seq = Message.gen_seq()
    message.product_id = 1
    message.version = 19
    message.payload_ver = 1
    message.device_sn = device_sn
    message.data_len = len(pdata)
    message.pdata = pdata

    # Empty Delta3SetCommand as "payload" placeholder for MessageToDict
    # logging in Delta3CommandMessage.to_dict. The real wire bytes live
    # in packet.msg[0].pdata.
    dummy_payload = delta3_pb2.Delta3SetCommand()
    return Delta3CommandMessage(dummy_payload, packet)


def _create_delta3_ac_charging_power_command(value: int, device_sn: str) -> "Delta3CommandMessage":
    """Create a protobuf command for AC charging power on DELTA 3.

    The EcoFlow DELTA 3 firmware silently ignores SET commands that only
    carry field 54 (``plug_in_info_ac_in_chg_pow_max``), even though the
    proto declares field 54 as the standalone attribute for this setting.
    Capturing traffic from the mobile app shows the app always sends
    field 54 together with ``field 125 = 0`` — an undeclared companion
    field that appears to act as a commit/apply flag. Without it, the
    device ACKs the command but does not actually update its internal
    setpoint, so tolwi's generic ``_create_delta3_proto_command`` path
    is read-only for this entity.

    Field 125 is not declared in the generated ``ef_delta3_pb2`` schema,
    so pdata is crafted manually. The resulting wire bytes match the
    app's captured packets exactly: ``b0 03 <value_varint> e8 07 00``.
    """
    def _encode_varint(v: int) -> bytes:
        out = bytearray()
        while True:
            byte = v & 0x7F
            v >>= 7
            if v:
                out.append(byte | 0x80)
            else:
                out.append(byte)
                break
        return bytes(out)

    # Field 54 varint tag: (54 << 3) | 0 = 432 -> varint "b0 03"
    # Field 125 varint tag: (125 << 3) | 0 = 1000 -> varint "e8 07"
    pdata = bytes([0xB0, 0x03]) + _encode_varint(int(value)) + bytes([0xE8, 0x07, 0x00])

    packet = delta3_pb2.Delta3SendHeaderMsg()
    message = packet.msg.add()
    message.src = 32
    message.dest = 2
    message.d_src = 1
    message.d_dest = 1
    message.cmd_func = 254
    message.cmd_id = 17
    message.need_ack = 1
    message.seq = Message.gen_seq()
    message.product_id = 1
    message.version = 19
    message.payload_ver = 1
    message.device_sn = device_sn
    message.data_len = len(pdata)
    message.pdata = pdata

    # Empty Delta3SetCommand as placeholder payload for logging.
    dummy_payload = delta3_pb2.Delta3SetCommand()
    return Delta3CommandMessage(dummy_payload, packet)


def _extract_proto_varint_field(data: bytes, target_field: int) -> int | None:
    """Extract a single varint field from raw protobuf bytes by tag number.

    Used to read fields that are present on the wire but not declared in
    the generated ``ef_delta3_pb2`` schema (e.g. field 146 =
    ``ban_bypass_en`` in ``Delta3DisplayPropertyUpload``).

    Returns the int value or ``None`` if the field is not present.
    """
    pos = 0
    n = len(data)
    while pos < n:
        # Read tag varint
        tag = 0
        shift = 0
        while pos < n:
            b = data[pos]
            pos += 1
            tag |= (b & 0x7F) << shift
            if not (b & 0x80):
                break
            shift += 7
        fn = tag >> 3
        wt = tag & 0x7
        if wt == 0:  # varint
            v = 0
            shift = 0
            while pos < n:
                b = data[pos]
                pos += 1
                v |= (b & 0x7F) << shift
                if not (b & 0x80):
                    break
                shift += 7
            if fn == target_field:
                return v
        elif wt == 1:  # 64-bit
            pos += 8
        elif wt == 2:  # length-delimited
            length = 0
            shift = 0
            while pos < n:
                b = data[pos]
                pos += 1
                length |= (b & 0x7F) << shift
                if not (b & 0x80):
                    break
                shift += 7
            pos += length
        elif wt == 5:  # 32-bit
            pos += 4
        else:
            return None
    return None


def _create_delta3_get_quota_command() -> "Delta3CommandMessage":
    """Build a protobuf 'get all' request that fetches the full device snapshot.

    Mirrors the EcoFlow mobile app behavior when opening the device page:
    publishes a ``Delta3SendHeaderMsg`` containing a single empty
    ``Delta3Header`` with only ``src``/``dest``/``seq``/``from`` set. The
    device firmware interprets this as "send everything you have" and
    replies on the ``thing/property/get_reply`` topic with a multi-header
    snapshot (Display + Runtime + BMS + CMS reports).

    This is the only path that delivers sparse-delta-only fields like
    ``ban_bypass_en`` (Display field 146) at HA startup, without waiting
    for the user to toggle the bypass from the app or from HA.

    Tolwi's ``PrivateAPIClient.quota_all`` calls
    :meth:`Delta3.get_quota_message` during integration setup
    (``custom_components/ecoflow_cloud/__init__.py``), so the snapshot is
    fetched automatically on every HA restart.
    """
    packet = delta3_pb2.Delta3SendHeaderMsg()
    header = packet.msg.add()
    header.src = 32
    header.dest = 32
    header.seq = Message.gen_seq()
    # ``from`` is a Python reserved word; Delta3Header field 23 is named
    # "from" in the proto, so we set it via setattr.
    setattr(header, "from", "HomeAssistant")

    # Empty Delta3SetCommand acts as a placeholder payload for
    # Delta3CommandMessage.to_dict() diagnostics. The wire payload is
    # the serialized packet, which contains no pdata for this request.
    dummy_payload = delta3_pb2.Delta3SetCommand()
    return Delta3CommandMessage(dummy_payload, packet)


def _create_delta3_energy_backup_command(energy_backup_en: int | None, energy_backup_start_soc: int, device_sn: str):
    """Create a protobuf command for Delta 3 energy backup settings."""
    # Build the command using the generated protobuf classes
    payload = delta3_pb2.Delta3SetCommand()
    payload.cfg_energy_backup.energy_backup_start_soc = int(energy_backup_start_soc)
    if energy_backup_en is not None:
        payload.cfg_energy_backup.energy_backup_en = int(energy_backup_en)

    pdata = payload.SerializeToString()

    packet = delta3_pb2.Delta3SendHeaderMsg()
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

    return Delta3CommandMessage(payload, packet)


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


class Delta3ChargingStateSensorEntity(BaseSensorEntity):
    """Sensor for battery charging state."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:battery-charging"

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


class Delta3(BaseInternalDevice):
    """EcoFlow Delta 3 device implementation using protobuf decoding."""

    @staticmethod
    def default_charging_power_step() -> int:
        return 50

    @override
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            LevelSensorEntity(client, self, "bms_batt_soc", const.MAIN_BATTERY_LEVEL)
            .attr("bms_design_cap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("bms_full_cap", const.ATTR_FULL_CAPACITY, 0)
            .attr("bms_remain_cap", const.ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, self, "bms_design_cap", const.MAIN_DESIGN_CAPACITY, False),
            CapacitySensorEntity(client, self, "bms_full_cap", const.MAIN_FULL_CAPACITY, False),
            CapacitySensorEntity(client, self, "bms_remain_cap", const.MAIN_REMAIN_CAPACITY, False),
            LevelSensorEntity(client, self, "bms_batt_soh", const.SOH),
            LevelSensorEntity(client, self, "cms_batt_soc", const.COMBINED_BATTERY_LEVEL),
            Delta3ChargingStateSensorEntity(client, self, "bms_chg_dsg_state", const.BATTERY_CHARGING_STATE),
            InWattsSensorEntity(client, self, "pow_in_sum_w", const.TOTAL_IN_POWER).with_energy(),
            OutWattsSensorEntity(client, self, "pow_out_sum_w", const.TOTAL_OUT_POWER).with_energy(),
            InWattsSensorEntity(client, self, "pow_get_pv", const.SOLAR_IN_POWER),
            InMilliampSensorEntity(client, self, "plug_in_info_pv_amp", const.SOLAR_IN_CURRENT),
            InWattsSensorEntity(client, self, "pow_get_ac_in", const.AC_IN_POWER),
            OutWattsAbsSensorEntity(client, self, "pow_get_ac_out", const.AC_OUT_POWER),
            InVoltSensorEntity(client, self, "plug_in_info_ac_in_vol", const.AC_IN_VOLT),
            OutVoltSensorEntity(client, self, "plug_in_info_ac_out_vol", const.AC_OUT_VOLT),
            OutWattsSensorEntity(client, self, "pow_get_12v", const.DC_OUT_POWER),
            OutWattsAbsSensorEntity(client, self, "pow_get_typec1", const.TYPEC_1_OUT_POWER),
            OutWattsAbsSensorEntity(client, self, "pow_get_qcusb1", const.USB_QC_1_OUT_POWER),
            OutWattsAbsSensorEntity(client, self, "pow_get_qcusb2", const.USB_QC_2_OUT_POWER),
            RemainSensorEntity(client, self, "bms_chg_rem_time", const.CHARGE_REMAINING_TIME),
            RemainSensorEntity(client, self, "bms_dsg_rem_time", const.DISCHARGE_REMAINING_TIME),
            RemainSensorEntity(client, self, "cms_chg_rem_time", const.REMAINING_TIME),
            TempSensorEntity(client, self, "temp_pcs_dc", "PCS DC Temperature"),
            TempSensorEntity(client, self, "temp_pcs_ac", "PCS AC Temperature"),
            TempSensorEntity(client, self, "bms_min_cell_temp", const.BATTERY_TEMP).attr(
                "bms_max_cell_temp", const.ATTR_MAX_CELL_TEMP, 0
            ),
            TempSensorEntity(client, self, "bms_max_cell_temp", const.MAX_CELL_TEMP, False),
            VoltSensorEntity(client, self, "bms_batt_vol", const.BATTERY_VOLT, False)
            .attr("bms_min_cell_vol", const.ATTR_MIN_CELL_VOLT, 0)
            .attr("bms_max_cell_vol", const.ATTR_MAX_CELL_VOLT, 0),
            MilliVoltSensorEntity(client, self, "bms_min_cell_vol", const.MIN_CELL_VOLT, False),
            MilliVoltSensorEntity(client, self, "bms_max_cell_vol", const.MAX_CELL_VOLT, False),
            CyclesSensorEntity(client, self, "cycles", const.CYCLES),
            InEnergySolarSensorEntity(client, self, "pv_in_energy", const.SOLAR_IN_ENERGY),
            QuotaStatusSensorEntity(client, self),
        ]

    @override
    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        device = self
        return [
            MaxBatteryLevelEntity(
                client,
                self,
                "cms_max_chg_soc",
                const.MAX_CHARGE_LEVEL,
                50,
                100,
                lambda value: _create_delta3_proto_command("cms_max_chg_soc", int(value), device.device_data.sn),
            ),
            MinBatteryLevelEntity(
                client,
                self,
                "cms_min_dsg_soc",
                const.MIN_DISCHARGE_LEVEL,
                0,
                30,
                lambda value: _create_delta3_proto_command("cms_min_dsg_soc", int(value), device.device_data.sn),
            ),
            ChargingPowerEntity(
                client,
                self,
                "plug_in_info_ac_in_chg_pow_max",
                const.AC_CHARGING_POWER,
                100,
                1500,
                lambda value: _create_delta3_ac_charging_power_command(
                    int(value), device.device_data.sn
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
                lambda value: _create_delta3_energy_backup_command(1, int(value), device.device_data.sn),
            ),
        ]

    @override
    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        device = self
        return [
            BeeperEntity(
                client,
                self,
                "en_beep",
                const.BEEPER,
                lambda value: _create_delta3_proto_command(
                    "en_beep", 1 if value else 0, device.device_data.sn, data_len=2
                ),
            ),
            EnabledEntity(
                client,
                self,
                "cfg_ac_out_open",
                const.AC_ENABLED,
                lambda value, params=None: _create_delta3_proto_command(
                    "cfg_ac_out_open", 1 if value else 0, device.device_data.sn
                ),
            ),
            EnabledEntity(
                client,
                self,
                "xboost_en",
                const.XBOOST_ENABLED,
                lambda value, params=None: _create_delta3_proto_command(
                    "xboost_en", 1 if value else 0, device.device_data.sn
                ),
            ),
            EnabledEntity(
                client,
                self,
                "cfg_dc12v_out_open",
                const.DC_ENABLED,
                lambda value, params=None: _create_delta3_proto_command(
                    "cfg_dc12v_out_open", 1 if value else 0, device.device_data.sn
                ),
            ),
            EnabledEntity(
                client,
                self,
                "output_power_off_memory",
                const.AC_ALWAYS_ENABLED,
                lambda value, params=None: _create_delta3_proto_command(
                    "output_power_off_memory", 1 if value else 0, device.device_data.sn
                ),
            ),
            EnabledEntity(
                client,
                self,
                "energy_backup_en",
                const.BP_ENABLED,
                lambda value, params=None: _create_delta3_energy_backup_command(
                    1 if value else None,
                    params.get("energy_backup_start_soc", 5) if params else 5,
                    device.device_data.sn,
                ),
            ),
            BypassBanScalarSwitch(
                client,
                self,
                "ban_bypass_en",
                const.GRID_BYPASS,
                lambda value, params=None: _create_delta3_bypass_ban_command(
                    int(value), device.device_data.sn
                ),
                enableValue=1,
                disableValue=0,
            ),
        ]

    @override
    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        device = self
        dc_charge_current_options = {"4A": 4, "5A": 5, "6A": 6, "7A": 7, "8A": 8}
        return [
            DictSelectEntity(
                client,
                self,
                "plug_in_info_pv_dc_amp_max",
                const.DC_CHARGE_CURRENT,
                dc_charge_current_options,
                lambda value: _create_delta3_proto_command(
                    "plug_in_info_pv_dc_amp_max", int(value), device.device_data.sn
                ),
            ),
            TimeoutDictSelectEntity(
                client,
                self,
                "screen_off_time",
                const.SCREEN_TIMEOUT,
                const.SCREEN_TIMEOUT_OPTIONS,
                lambda value: _create_delta3_proto_command("screen_off_time", int(value), device.device_data.sn),
            ),
            TimeoutDictSelectEntity(
                client,
                self,
                "dev_standby_time",
                const.UNIT_TIMEOUT,
                const.UNIT_TIMEOUT_OPTIONS,
                lambda value: _create_delta3_proto_command("dev_standby_time", int(value), device.device_data.sn),
            ),
            TimeoutDictSelectEntity(
                client,
                self,
                "ac_standby_time",
                const.AC_TIMEOUT,
                const.AC_TIMEOUT_OPTIONS,
                lambda value: _create_delta3_proto_command("ac_standby_time", int(value), device.device_data.sn),
            ),
            TimeoutDictSelectEntity(
                client,
                self,
                "dc_standby_time",
                const.DC_TIMEOUT,
                const.DC_TIMEOUT_OPTIONS,
                lambda value: _create_delta3_proto_command("dc_standby_time", int(value), device.device_data.sn),
            ),
        ]

    @override
    def _prepare_data(self, raw_data: bytes) -> dict[str, Any]:
        """Prepare Delta 3 data by decoding protobuf and flattening fields."""
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
            _LOGGER.debug(f"[Delta] Data processing failed: {e}")
            return super()._prepare_data(raw_data)

        return {
            "params": flat_dict or {},
            "all_fields": decoded_data or {},
        }

    @override
    def get_quota_message(self) -> "Delta3CommandMessage":
        """Return the protobuf 'get all' request used by quota_all().

        The base ``BaseInternalDevice`` returns a JSON ``latestQuotas``
        message which the protobuf-only DELTA 3 firmware silently ignores.
        Overriding here lets HA proactively fetch the full device snapshot
        at integration setup (and on every quota refresh), populating
        sparse-delta-only fields such as ``ban_bypass_en`` before the
        first user interaction.
        """
        return _create_delta3_get_quota_command()

    @override
    def _prepare_data_get_reply_topic(self, raw_data: bytes) -> PreparedData:
        """Decode a multi-header ``thing/property/get_reply`` snapshot.

        EcoFlow's get_reply contains a full state dump as a
        ``Delta3HeaderMessage`` with several headers (Display, Runtime,
        BMS heartbeat, CMS heartbeat). The base class ``_prepare_data``
        path only handles a single header, so this override iterates
        every header, decodes it via :meth:`_decode_message_by_type`,
        and merges the resulting dicts.

        This is the path that delivers ``ban_bypass_en`` (Display field
        146) right after HA setup, without requiring the user to open
        the EcoFlow mobile app or toggle anything.
        """
        try:
            import base64

            try:
                raw_data = base64.b64decode(raw_data, validate=True)
            except Exception as e:
                _LOGGER.debug("[Delta3] get_reply base64 decode failed: %s", e)

            header_msg = delta3_pb2.Delta3HeaderMessage()
            header_msg.ParseFromString(raw_data)
        except Exception as e:
            _LOGGER.debug("[Delta3] get_reply parse failed: %s", e)
            return PreparedData(None, None, {"proto": raw_data.hex()})

        merged: dict[str, Any] = {}
        for header in header_msg.header:
            try:
                header_info = {
                    "src": getattr(header, "src", 0),
                    "encType": getattr(header, "enc_type", 0),
                    "seq": getattr(header, "seq", 0),
                    "cmdFunc": getattr(header, "cmd_func", 0),
                    "cmdId": getattr(header, "cmd_id", 0),
                }
                pdata = getattr(header, "pdata", b"")
                if not pdata:
                    continue
                decoded_pdata = self._perform_xor_decode(pdata, header_info)
                decoded = self._decode_message_by_type(decoded_pdata, header_info)
                if decoded:
                    merged.update(decoded)
            except Exception as e:
                _LOGGER.debug("[Delta3] get_reply header decode failed: %s", e)
                continue

        if not merged:
            return PreparedData(None, None, {"proto": raw_data.hex()})

        flat = self._flatten_dict(merged)
        return PreparedData(None, {"params": flat, "all_fields": merged}, {"proto": raw_data.hex()})

    def _decode_header_message(self, raw_data: bytes) -> dict[str, Any] | None:
        """Decode HeaderMessage and extract header info."""
        try:
            import base64

            try:
                decoded_payload = base64.b64decode(raw_data, validate=True)
                raw_data = decoded_payload
            except Exception as e:
                # If base64 decoding fails, proceed with the original raw_data (it may not be base64 encoded)
                _LOGGER.debug("[Delta3] base64 decode failed: %s", e)

            try:
                header_msg = delta3_pb2.Delta3HeaderMessage()
                header_msg.ParseFromString(raw_data)
            except Exception as e:
                _LOGGER.debug("[Delta3] Failed to parse header message: %s", e)
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
            _LOGGER.debug("[Delta3] Failed to decode header message: %s", e)
            return None

    def _extract_payload_data(self, header_obj: Any) -> bytes | None:
        """Extract payload bytes from header."""
        try:
            pdata = getattr(header_obj, "pdata", b"")
            return pdata if pdata else None
        except Exception as e:
            _LOGGER.debug("[Delta3] Failed to extract payload data: %s", e)
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

    def _decode_message_by_type(self, pdata: bytes, header_info: dict[str, Any]) -> dict[str, Any]:
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
                msg_display_upload = delta3_pb2.Delta3DisplayPropertyUpload()
                msg_display_upload.ParseFromString(pdata)
                result = self._protobuf_to_dict(msg_display_upload)
                # Inject ban_bypass_en (proto field 146) which is not declared
                # in the tolwi ef_delta3.proto schema. The device only sends
                # this field when the bypass state changes (push delta) or in
                # full snapshots (get_reply), so its absence in a delta must
                # not overwrite the previously known value.
                ban_bypass = _extract_proto_varint_field(pdata, 146)
                if ban_bypass is not None:
                    result["ban_bypass_en"] = ban_bypass
                return result

            elif cmd_func == 254 and cmd_id == 22:
                msg_runtime_upload = delta3_pb2.Delta3RuntimePropertyUpload()
                msg_runtime_upload.ParseFromString(pdata)
                return self._protobuf_to_dict(msg_runtime_upload)

            elif cmd_func == 254 and cmd_id == 17:
                try:
                    msg_set_command = delta3_pb2.Delta3SetCommand()
                    msg_set_command.ParseFromString(pdata)
                    return self._protobuf_to_dict(msg_set_command)
                except Exception as e:
                    _LOGGER.debug("Failed to decode as Delta3SetCommand: %s", e)
                    return {}

            elif cmd_func == 254 and cmd_id == 18:
                try:
                    msg_set_reply = delta3_pb2.Delta3SetReply()
                    msg_set_reply.ParseFromString(pdata)
                    result = self._protobuf_to_dict(msg_set_reply)
                    return result if result.get("config_ok", False) else {}
                except Exception as e:
                    _LOGGER.debug(f"Failed to decode as setReply_dp3: {e}")
                    return {}

            elif cmd_func == 32 and cmd_id == 2:
                try:
                    msg_cms_heartbeat = delta3_pb2.Delta3CMSHeartBeatReport()
                    msg_cms_heartbeat.ParseFromString(pdata)
                    return self._protobuf_to_dict(msg_cms_heartbeat)
                except Exception as e:
                    _LOGGER.debug(f"Failed to decode as cmdFunc32_cmdId2_Report: {e}")
                    return {}

            elif self._is_bms_heartbeat(cmd_func, cmd_id):
                try:
                    msg_bms_heartbeat = delta3_pb2.Delta3BMSHeartBeatReport()
                    msg_bms_heartbeat.ParseFromString(pdata)
                    return self._protobuf_to_dict(msg_bms_heartbeat)
                except Exception as e:
                    _LOGGER.debug(f"Failed to decode as BMSHeartBeatReport (cmdFunc={cmd_func}, cmdId={cmd_id}): {e}")
                    return {}

            # Unknown message type - try BMSHeartBeatReport as fallback
            try:
                msg_bms_heartbeat = delta3_pb2.Delta3BMSHeartBeatReport()
                msg_bms_heartbeat.ParseFromString(pdata)
                result = self._protobuf_to_dict(msg_bms_heartbeat)
                if "cycles" in result or "accu_chg_energy" in result or "accu_dsg_energy" in result:
                    return result
            except Exception as e:
                _LOGGER.debug("Failed to decode as fallback BMSHeartBeatReport: %s", e)

            return {}
        except Exception as e:
            _LOGGER.debug(f"Message decode error for cmdFunc={cmd_func}, cmdId={cmd_id}: {e}")
            return {}

    def _is_bms_heartbeat(self, cmd_func: int, cmd_id: int) -> bool:
        """Return True if the pair maps to a BMSHeartBeatReport message."""
        return (cmd_func, cmd_id) in BMS_HEARTBEAT_COMMANDS

    def _flatten_dict(self, d: dict, parent_key: str = "", sep: str = "_") -> dict:
        """Flatten nested dict with underscore separator."""
        items: list[tuple[str, Any]] = []
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

    def _manual_protobuf_to_dict(self, protobuf_obj: Any) -> dict[str, Any]:
        """Convert protobuf object to dict manually (fallback)."""
        result: dict[str, Any] = {}
        for field, value in protobuf_obj.ListFields():
            if field.label == field.LABEL_REPEATED:
                result[field.name] = list(value)
            elif hasattr(value, "ListFields"):  # nested message
                result[field.name] = self._manual_protobuf_to_dict(value)
            else:
                result[field.name] = value
        return result

    @override
    def _prepare_data_set_reply_topic(self, raw_data: bytes) -> PreparedData:
        """Parse set/get reply data - try protobuf, fall back to quiet JSON."""
        try:
            import base64

            try:
                decoded_payload = base64.b64decode(raw_data, validate=True)
                raw_data = decoded_payload
            except Exception as e:
                # If base64 decoding fails, proceed with the original raw_data (it may not be base64 encoded)
                _LOGGER.debug("[Delta3] base64 decode failed: %s", e)

            header_msg = delta3_pb2.Delta3SendHeaderMsg()
            header_msg.ParseFromString(raw_data)

            if header_msg.msg:
                header = header_msg.msg[0]
                pdata = getattr(header, "pdata", b"")
                if pdata:
                    try:
                        enc_type = getattr(header, "enc_type", 0)
                        src = getattr(header, "src", 0)
                        seq = getattr(header, "seq", 0)
                        if enc_type == 1 and src != 32:
                            pdata = self._xor_decode_pdata(pdata, seq)

                        reply_msg = delta3_pb2.Delta3SetReply()
                        reply_msg.ParseFromString(pdata)
                        result = self._protobuf_to_dict(reply_msg)
                        return PreparedData(None, {"params": self._flatten_dict(result)}, {"proto": raw_data.hex()})
                    except Exception as e:
                        _LOGGER.debug(f"Failed to parse as Delta3SetReply: {e}")
        except Exception as e:
            _LOGGER.debug(f"Protobuf parse failed for set_reply: {e}")

        return PreparedData(None, None, {"proto": raw_data.hex()})
