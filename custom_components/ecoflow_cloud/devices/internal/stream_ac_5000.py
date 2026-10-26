"""EcoFlow STREAM AC 5000 (SN prefix ``ES22``) -- internal/App API.

Transport: MQTT topic ``/app/device/property/<SN>``, envelope protobuf
``StreamACSendHeaderMsg`` from ``proto/stream_ac_pb2.py`` -- the same envelope
every Stream device uses. Unlike the STREAM Microinverter, ``msg.pdata`` is
**not** XOR-obfuscated; it parses as plain protobuf.

Not a ``STREAM_AC`` alias: the AC 5000's telemetry (``cmd_id`` 39/40) sends
small nested blocks keyed by serial number, where ``StreamACChamp_cmd21_3`` is
flat with field numbers in the 500-1200 range. Only the ``cmd_id`` 50 pack frame
resembles the existing schema, so configuring one as ``STREAM_AC`` yields a
handful of SoC values and little else. This decoder dispatches on ``cmd_id``
rather than blind-parsing every schema, so a frame is either understood or
skipped, never mislabelled.

Field meanings were decoded from MQTT captures anchored to app readings; the
commit history carries the evidence for each. Blocks 60/61/62 (``cmd_id`` 40)
are deliberately left undecoded.
"""

import logging
from typing import Any, Iterator, override

from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message as ProtoMessageRaw
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.util import utcnow

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.api.message import Message, PrivateAPIMessageProtocol
from custom_components.ecoflow_cloud.binary_sensor import MiscBinarySensorEntity
from custom_components.ecoflow_cloud.devices import BaseInternalDevice, const
from custom_components.ecoflow_cloud.devices.internal.proto import stream_ac_5000_pb2, stream_ac_pb2
from custom_components.ecoflow_cloud.number import ChargingPowerEntity, MaxBatteryLevelEntity, MinBatteryLevelEntity
from custom_components.ecoflow_cloud.select import PowerDictSelectEntity
from custom_components.ecoflow_cloud.switch import EnabledEntity
from custom_components.ecoflow_cloud.sensor import (
    CumulativeCapacitySensorEntity,
    EnergySensorEntity,
    FrequencySensorEntity,
    LevelSensorEntity,
    MilliVoltSensorEntity,
    RemainSensorEntity,
    StateOfHealthSensorEntity,
    StatusSensorEntity,
    StoredEnergyFromSocSensorEntity,
    VoltSensorEntity,
    WattsSensorEntity,
)

_LOGGER = logging.getLogger(__name__)

# cmd_id -> payload message. cmd_id 40 (blocks 60/61/62) is intentionally absent.
_CMD_ID_STATUS = 2
_CMD_ID_RUNTIME = 39
_CMD_ID_PACK = 50

# Wire tag for field 1, wire type 2 -- every EcoPacket starts with it.
_ECOPACKET_TAG = 0x0A

# Property ids, as sent in pdata field 1 of a set command.
_PROP_POWER_LIMITS = 10
_PROP_AC_OUT = 19
_PROP_DEVICE_CFG = 23
_PROP_WORK_MODE = 25
_PROP_SOC_LIMITS = 29

# Envelope constants, copied verbatim from the app's own writes.
_SET_CMD_FUNC = 254
_SET_CMD_ID = 38
_OUT_LIMIT_FIELD4 = 4
_OUT_LIMIT_MAX = 800

# Entity keys for controls whose protobuf field name differs.
_KEY_AC_OUT = "acOutEnabled"
_KEY_XBOOST = "xboostEnabled"
_KEY_WORK_MODE = "workMode"

# Raw pack SoC. Reads above the app-facing system scale near empty, so it is kept
# on its own key rather than fighting it.
_KEY_PACK_SOC = "packSoc"

# On a P1 outage the device still sends meter block 16, but empty -- which would
# otherwise leave every meter sensor holding a stale reading.
_KEY_METER_LINK = "meterLinkUp"


class StreamAC5000CommandMessage(PrivateAPIMessageProtocol):
    """One property write, in the envelope the EcoFlow app uses."""

    def __init__(self, device_sn: str, payload: ProtoMessageRaw):
        self._payload = payload
        self._packet = stream_ac_5000_pb2.StreamAC5000SendCommandMsg()
        message = self._packet.msg

        pdata = payload.SerializeToString()
        message.pdata = pdata
        message.data_len = len(pdata)

        message.src = 32
        message.dest = 2
        message.d_src = 1
        message.d_dest = 1
        message.check_type = 3
        message.need_ack = 1
        message.version = 4
        message.seq = Message.gen_seq()
        message.cmd_func = _SET_CMD_FUNC
        message.cmd_id = _SET_CMD_ID
        message.from_ = "HomeAssistant"
        # The app repeats the serial in all three of these.
        message.device_sn = device_sn
        message.device_sn_2 = device_sn
        message.device_sn_3 = device_sn

    @override
    def to_mqtt_payload(self) -> Any:
        return self._packet.SerializeToString()

    @override
    def to_dict(self) -> dict:
        result = MessageToDict(self._packet, preserving_proto_field_name=True)
        result["msg"]["pdata"] = {
            type(self._payload).__name__: MessageToDict(self._payload, preserving_proto_field_name=True)
        }
        result["msg"].pop("seq", None)
        return {type(self._packet).__name__: result}


def _read_varint(buf: bytes, pos: int) -> tuple[int, int]:
    shift = 0
    result = 0
    while True:
        if pos >= len(buf):
            raise ValueError("truncated varint")
        byte = buf[pos]
        pos += 1
        result |= (byte & 0x7F) << shift
        shift += 7
        if not byte & 0x80:
            return result, pos
        if shift > 63:
            raise ValueError("varint too long")


def _iter_packets(payload: bytes) -> Iterator[Any]:
    """Split a payload into EcoPackets and yield each parsed header.

    One MQTT message can carry several concatenated packets, and handing the
    whole buffer to ``ParseFromString`` would merge them into one instead.
    """
    offset = 0
    while offset < len(payload):
        try:
            tag, pos = _read_varint(payload, offset)
            if tag != _ECOPACKET_TAG:
                return
            length, pos = _read_varint(payload, pos)
            end = pos + length
            if end > len(payload):
                return
            packet = stream_ac_pb2.StreamACSendHeaderMsg()
            packet.ParseFromString(payload[offset:end])
        except Exception as error:
            _LOGGER.debug("Stopped splitting payload at offset %d: %s", offset, error)
            return
        yield packet.msg
        offset = end


class StreamAC5000(BaseInternalDevice):
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            # --- battery ------------------------------------------------
            LevelSensorEntity(client, self, "soc", const.STREAM_BATTERY_LEVEL),
            LevelSensorEntity(client, self, "f32ShowSoc", const.STREAM_POWER_BATTERY_SOC, False),
            LevelSensorEntity(client, self, "bmsBattSoc", const.STREAM_AC5000_BMS_BATTERY_LEVEL, False),
            LevelSensorEntity(client, self, _KEY_PACK_SOC, const.STREAM_AC5000_PACK_BATTERY_LEVEL, False),
            StoredEnergyFromSocSensorEntity(
                client, self, "cmsBattFullEnergy", "f32ShowSoc", const.STREAM_STORED_ENERGY
            ),
            # cmsMaxChgSoc / cmsMinDsgSoc are writable, so they live in numbers().
            # RemainSensorEntity clamps the device's 5939 "unknown" sentinel to 0.
            RemainSensorEntity(client, self, "remainTime", const.REMAINING_TIME),
            RemainSensorEntity(client, self, "bmsChgRemTime", const.CHARGE_REMAINING_TIME, False),
            RemainSensorEntity(client, self, "bmsDsgRemTime", const.DISCHARGE_REMAINING_TIME, False),
            # --- power --------------------------------------------------
            WattsSensorEntity(client, self, "gridPortPower", const.STREAM_AC5000_GRID_PORT_POWER),
            # Unsigned magnitude; the device has no signed variant. Direction has
            # to come from Grid Port Power's sign.
            WattsSensorEntity(client, self, "bpPower", const.STREAM_AC5000_BATTERY_POWER),
            WattsSensorEntity(client, self, "maxChgPow", const.STREAM_AC5000_CHARGE_POWER_LIMIT, False),
            WattsSensorEntity(client, self, "maxDsgPow", const.STREAM_AC5000_MAX_DISCHARGE_POWER, False),
            # feedGridModePowLimit is writable and lives in numbers().
            WattsSensorEntity(client, self, "feedGridModePowMax", const.STREAM_FEED_GRID_MODE_POW_MAX, False),
            # --- paired P1 meter ----------------------------------------
            # The meter has no MQTT topic of its own; it reports inside this
            # device's stream and must not be added as a separate device.
            WattsSensorEntity(client, self, "meterTotalPower", const.SMART_METER_POWER_GLOBAL),
            WattsSensorEntity(client, self, "meterPhaseAPower", const.SMART_METER_POWER_L1),
            WattsSensorEntity(client, self, "meterPhaseBPower", const.SMART_METER_POWER_L2),
            WattsSensorEntity(client, self, "meterPhaseCPower", const.SMART_METER_POWER_L3),
            VoltSensorEntity(client, self, "meterPhaseAVol", const.SMART_METER_VOLT_L1, False),
            VoltSensorEntity(client, self, "meterPhaseBVol", const.SMART_METER_VOLT_L2, False),
            VoltSensorEntity(client, self, "meterPhaseCVol", const.SMART_METER_VOLT_L3, False),
            FrequencySensorEntity(client, self, "meterFreq", const.POWER_GRID_FREQUENCY, False),
            # --- pack health --------------------------------------------
            MilliVoltSensorEntity(client, self, "minCellVol", const.MIN_CELL_VOLT, False),
            MilliVoltSensorEntity(client, self, "maxCellVol", const.MAX_CELL_VOLT, False),
            StateOfHealthSensorEntity(client, self, "realSoh", const.REAL_SOH, False),
            StateOfHealthSensorEntity(client, self, "cycleSoh", const.SOH, False),
            # --- lifetime counters (Energy dashboard) -------------------
            CumulativeCapacitySensorEntity(client, self, "accuChgCap", const.ACCU_CHARGE_CAP, False),
            CumulativeCapacitySensorEntity(client, self, "accuDsgCap", const.ACCU_DISCHARGE_CAP, False),
            EnergySensorEntity(client, self, "accuChgEnergy", const.ACCU_CHARGE_ENERGY),
            EnergySensorEntity(client, self, "accuDsgEnergy", const.ACCU_DISCHARGE_ENERGY),
            StatusSensorEntity(client, self),
        ]

    def _command(self, **fields: Any) -> StreamAC5000CommandMessage:
        return StreamAC5000CommandMessage(
            device_sn=self.device_info.sn,
            payload=stream_ac_5000_pb2.StreamAC5000SetCommand(**fields),
        )

    def _soc_limits_command(self, max_chg: int, min_dsg: int) -> StreamAC5000CommandMessage:
        """Write both SoC limits at once, as the app does."""
        return self._command(
            propertyId=_PROP_SOC_LIMITS,
            socLimits=stream_ac_5000_pb2.StreamAC5000SetSocLimits(
                cmsMaxChgSoc=max_chg,
                cmsMinDsgSoc=min_dsg,
            ),
        )

    def binary_sensors(self, client: EcoflowApiClient) -> list[BinarySensorEntity]:
        return [
            MiscBinarySensorEntity(client, self, _KEY_METER_LINK, const.STREAM_AC5000_METER_LINK),
        ]

    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return [
            MaxBatteryLevelEntity(
                client,
                self,
                "cmsMaxChgSoc",
                const.MAX_CHARGE_LEVEL,
                50,
                100,
                lambda value, params: self._soc_limits_command(value, int(params.get("cmsMinDsgSoc", 5))),
            ),
            MinBatteryLevelEntity(
                client,
                self,
                "cmsMinDsgSoc",
                const.MIN_DISCHARGE_LEVEL,
                0,
                30,
                lambda value, params: self._soc_limits_command(int(params.get("cmsMaxChgSoc", 100)), value),
            ),
            # Property 10 accepts partial writes, so each slider sends only its
            # own field. 2500 W is the most an owner can unlock without an
            # installer; nothing in the telemetry reports the approved ceiling,
            # so the bound is static and compliance stays the owner's business.
            ChargingPowerEntity(
                client,
                self,
                "feedGridModePowLimit",
                const.STREAM_AC5000_NET_POWER_OUT,
                0,
                2500,
                lambda value: self._command(
                    propertyId=_PROP_POWER_LIMITS,
                    powerLimits=stream_ac_5000_pb2.StreamAC5000SetPowerLimits(
                        feedGridModePowLimit=value,
                        outLimitField4=_OUT_LIMIT_FIELD4,
                        outLimitMax=_OUT_LIMIT_MAX,
                    ),
                ),
            ),
            # The app allows 7200 W but the hardware does 2500 W, or 3000 W with a
            # second battery, so the slider stops where the device can deliver.
            ChargingPowerEntity(
                client,
                self,
                "chgPowLimit",
                const.STREAM_AC5000_NET_POWER_IN,
                0,
                3000,
                lambda value: self._command(
                    propertyId=_PROP_POWER_LIMITS,
                    powerLimits=stream_ac_5000_pb2.StreamAC5000SetPowerLimits(chgPowLimit=value),
                ),
            ),
        ]

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return [
            EnabledEntity(
                client,
                self,
                _KEY_AC_OUT,
                const.STREAM_AC5000_AC_OUTPUT,
                lambda value: self._command(
                    propertyId=_PROP_AC_OUT,
                    acOut=stream_ac_5000_pb2.StreamAC5000SetAcOut(enabled=value),
                ),
            ),
            EnabledEntity(
                client,
                self,
                _KEY_XBOOST,
                const.STREAM_AC5000_XBOOST,
                lambda value: self._command(
                    propertyId=_PROP_DEVICE_CFG,
                    deviceCfg=stream_ac_5000_pb2.StreamAC5000SetDeviceCfg(xboostEnabled=value),
                ),
            ),
            EnabledEntity(
                client,
                self,
                "upsEnabled",
                const.STREAM_AC5000_UPS,
                lambda value: self._command(
                    propertyId=_PROP_DEVICE_CFG,
                    deviceCfg=stream_ac_5000_pb2.StreamAC5000SetDeviceCfg(upsEnabled=value),
                ),
            ),
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return [
            PowerDictSelectEntity(
                client,
                self,
                _KEY_WORK_MODE,
                const.STREAM_AC5000_WORK_MODE,
                const.STREAM_AC5000_WORK_MODE_OPTIONS,
                lambda value: self._command(propertyId=_PROP_WORK_MODE, workMode=value),
            ),
        ]

    @override
    def _prepare_data(self, raw_data: bytes) -> dict[str, Any]:
        params: dict[str, Any] = {}

        for header in _iter_packets(raw_data):
            pdata = getattr(header, "pdata", b"")
            if not pdata:
                continue
            try:
                self._decode_pdata(header.cmd_id, pdata, params)
            except Exception as error:
                _LOGGER.debug(
                    "Failed to decode cmd_id %s pdata %s: %s",
                    header.cmd_id,
                    pdata.hex(),
                    error,
                )

        raw: dict[str, Any] = {"params": params}
        if params:
            raw["timestamp"] = utcnow()
        return raw

    def _decode_pdata(self, cmd_id: int, pdata: bytes, params: dict[str, Any]) -> None:
        if cmd_id == _CMD_ID_STATUS:
            message = stream_ac_5000_pb2.StreamAC5000StatusPack()
            message.ParseFromString(pdata)
            # This frame's SoC is the pack scale, not the app-facing one.
            self._copy(message.battery, params, "cmsMaxChgSoc", "bmsChgRemTime", "bmsDsgRemTime")
            self._copy(message.battery, params, ("f32ShowSoc", _KEY_PACK_SOC), "cmsMinDsgSoc")

        elif cmd_id == _CMD_ID_RUNTIME:
            message = stream_ac_5000_pb2.StreamAC5000Runtime()
            message.ParseFromString(pdata)
            self._decode_runtime(message, params)

        elif cmd_id == _CMD_ID_PACK:
            message = stream_ac_5000_pb2.StreamAC5000Pack()
            message.ParseFromString(pdata)
            self._copy(
                message,
                params,
                ("f32ShowSoc", _KEY_PACK_SOC),
                "realSoh",
                "cycleSoh",
                "calendarSoh",
                "accuChgCap",
                "accuDsgCap",
                "accuChgEnergy",
                "accuDsgEnergy",
            )

    def _decode_runtime(self, message: Any, params: dict[str, Any]) -> None:
        if message.HasField("meter"):
            # An empty block means the meter is configured but not responding.
            params[_KEY_METER_LINK] = 1 if message.meter.ByteSize() > 0 else 0
        self._copy(
            message.meter,
            params,
            "meterPhaseAPower",
            "meterPhaseBPower",
            "meterPhaseCPower",
            "meterPhaseAVol",
            "meterPhaseBVol",
            "meterPhaseCVol",
            "meterFreq",
            "meterTotalPower",
        )
        self._copy(
            message.sysConfig,
            params,
            "maxChgPow",
            "maxDsgPow",
            "cmsBattFullEnergy",
            "f32ShowSoc",
            "cmsMaxChgSoc",
            "cmsMinDsgSoc",
            # feedGridModePowLimit deliberately absent: block 10 owns that key,
            # being the structure the app writes and the only unambiguous source.
            "feedGridModePowMax",
        )
        # The BMS SoC runs ~1% low and its max-charge field is a fixed ceiling,
        # so neither may share the app-facing key.
        self._copy(
            message.bmsPack.bms,
            params,
            ("soc", "bmsBattSoc"),
            ("cmsMaxChgSoc", "bmsMaxChgSoc"),
            "cmsBattFullEnergy",
            "bmsDsgRemTime",
            "bmsChgRemTime",
            "minCellVol",
            "maxCellVol",
        )
        self._copy(message.cms, params, "cmsBattFullEnergy", "remainTime")
        # Block 54 owns soc: same scale as block 44 but sent far more often.
        self._copy(message.statPack.stat, params, "soc")
        self._copy(message.powerPack.power, params, "gridPortPower")
        self._copy(message.deviceCfg, params, "upsEnabled", ("xboostEnabled", _KEY_XBOOST))
        self._copy(message.powerLimits, params, "feedGridModePowLimit", "chgPowLimit")
        self._copy(message.acOut, params, ("enabled", _KEY_AC_OUT))
        self._copy(message, params, ("workMode", _KEY_WORK_MODE))

        # Half-watts on the wire; the CMS copy is emitted more often than the BMS.
        for source, field in ((message.cms, "cmsPowerHalfW"), (message.bmsPack.bms, "bmsPowerHalfW")):
            if source.HasField(field):
                params["bpPower"] = getattr(source, field) / 2
                break

    @staticmethod
    def _copy(source: Any, params: dict[str, Any], *fields: str | tuple[str, str]) -> None:
        """Copy set protobuf fields onto parameter names.

        Fields are ``"name"`` or ``("name", "alias")``. The ``HasField`` guard
        matters: incremental uploads carry only what changed, so an absent field
        must not overwrite a good value with a proto3 default.
        """
        for field in fields:
            name, alias = field if isinstance(field, tuple) else (field, field)
            if source.HasField(name):
                params[alias] = getattr(source, name)
