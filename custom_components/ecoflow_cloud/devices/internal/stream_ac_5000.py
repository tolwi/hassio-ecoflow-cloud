"""EcoFlow STREAM AC 5000 (SN prefix ``ES22``) -- internal/App API.

Transport: MQTT topic ``/app/device/property/<SN>``, envelope protobuf
``StreamACSendHeaderMsg`` from ``proto/stream_ac_pb2.py`` -- the same envelope
every Stream device uses. Unlike the STREAM Microinverter, ``msg.pdata`` is
**not** XOR-obfuscated; it parses as plain protobuf.

Why this is a separate class rather than another ``STREAM_AC`` registry alias:
the AC 5000's telemetry (``cmd_id`` 39/40) uses a completely different message
shape from ``StreamACChamp_cmd21_3``. That message is flat with field numbers in
the 500-1200 range (``powGetSysGrid`` = 515, ``powGetPvSum`` = 517); the AC 5000
instead sends small nested blocks keyed by serial number. Only the ``cmd_id``
50 pack frame resembles the existing schema. Configuring an AC 5000 as
``STREAM_AC`` therefore yields a handful of SoC values and nothing else, plus
spurious ``cmd_id``/``enc_type``/``need_ack`` params -- artefacts of
``stream_ac.py`` blind-parsing one payload under five different schemas.

This decoder dispatches on ``cmd_id`` instead, so a frame is either understood
or skipped, never mislabelled.

Field derivation
----------------
Decoded from a 2026-08-21/22 capture of one physical unit (~2200 frames),
anchored to app readings taken at noted wall-clock times:

* ``gridPortPower`` -- app showed "grid port input 1.02 kW" at 14:29; the field
  read 1011.9 / 1018.0 W at 14:29:10-20. After a deliberate load spike flipped
  the unit to discharging, the app showed "162 W grid port output" and the field
  read -159 / -157 W at 14:31. Sign convention confirmed in both directions.
* ``soc`` -- 96% -> 99% across 14:29-14:42, matching the reported ramp, on six
  independent fields that agree with each other.
* ``remainTime`` -- counted 15 -> 9 minutes during the app's "17 min to full",
  then jumped to ~3540 (= 2 d 11 h) the moment the load flipped it to
  discharging, matching the app exactly.
* Half-watt fields -- block 54 field 4 is *exactly* 2x block 50 field 4 (zero
  deviation on every overlapping sample), which is what establishes the unit.
* Lifetime counters -- fields 50/51/79/80 of the pack frame were strictly
  monotonic across 181 frames spanning 18 hours.

Blocks 60/61/62 (``cmd_id`` 40) correlate with power (r ~= 0.78-0.81) but at
ratios that resolve to no clean unit, so they are deliberately left undecoded
rather than shipped under a guessed name.
"""

import logging
from typing import Any, Iterator, override

from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message as ProtoMessageRaw
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.util import utcnow

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.api.message import Message, PrivateAPIMessageProtocol
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

# Envelope constants copied verbatim from the app's own writes. cmd_id 38 with
# cmd_func 254 is what the device acknowledges; the two constants that ride
# alongside the "net power out" value are sent unchanged for the same reason.
_SET_CMD_FUNC = 254
_SET_CMD_ID = 38
_OUT_LIMIT_FIELD4 = 4
_OUT_LIMIT_MAX = 800

# Every control is read back from telemetry, so none of them are optimistic:
# AC output and work mode come from runtime fields 19 and 25, X-Boost and UPS
# from block 23. These constants only exist to keep the parameter name in one
# place, since the protobuf field names differ from the entity keys.
_KEY_AC_OUT = "acOutEnabled"
_KEY_XBOOST = "xboostEnabled"
_KEY_WORK_MODE = "workMode"


class CeilingBoundPowerEntity(ChargingPowerEntity):
    """A power slider whose upper bound follows a ceiling the device reports.

    The AC 5000's output limit is a compliance setting, not a fixed rating: it
    ships at the 800 W EU plug-in-inverter ceiling, the owner can raise it to
    2500 W in the EcoFlow app behind a toggle and a signed declaration, and
    anything above that needs an installer (up to 7400 W). Hard-coding 800 here
    would stop Home Assistant from ever using headroom the owner has
    legitimately unlocked, so the bound follows the device instead.

    The constructor value is only the bound before any telemetry arrives; once
    the ceiling key is seen the bound tracks it in both directions, so an
    installer-raised limit widens the slider without a code change. Mirrors how
    BatteryBackupLevel tracks its limits from sibling keys.
    """

    def __init__(
        self,
        client: EcoflowApiClient,
        device: Any,
        mqtt_key: str,
        title: str,
        min_value: int,
        max_value: int,
        ceiling_key: str,
        command: Any,
    ):
        super().__init__(client, device, mqtt_key, title, min_value, max_value, command)
        self._ceiling_key = ceiling_key

    def _updated(self, data: dict[str, Any]) -> None:
        if self._ceiling_key in data:
            try:
                ceiling = int(data[self._ceiling_key])
            except TypeError, ValueError:
                ceiling = 0
            if ceiling > 0:
                self._attr_native_max_value = ceiling
        super()._updated(data)


class StreamAC5000CommandMessage(PrivateAPIMessageProtocol):
    """One property write, wrapped in the envelope the EcoFlow app uses.

    Verified by round-trip: every payload this builds is byte-identical to the
    frame the iOS app sent for the same action (16/16 commands compared against
    a capture in which each setting was changed to a known value and back).
    """

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

    One MQTT message can carry several concatenated EcoPackets. They cannot be
    parsed by handing the whole buffer to ``ParseFromString``: protobuf *merges*
    repeated occurrences of a singular submessage field, silently blending
    frames together. Boundaries are found by reading each packet's own
    length prefix instead.
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
            StoredEnergyFromSocSensorEntity(
                client, self, "cmsBattFullEnergy", "f32ShowSoc", const.STREAM_STORED_ENERGY
            ),
            # cmsMaxChgSoc / cmsMinDsgSoc are NOT sensors here: they are writable,
            # so they live in numbers() instead. Exposing them in both places put
            # a read-only "Max Charge Level" under Sensors next to the identically
            # named slider under Controls, which is just confusing.
            # RemainSensorEntity already clamps the device's 5939 ("unknown",
            # = 99 h 59 m) sentinel to 0, so it is passed through as-is.
            RemainSensorEntity(client, self, "remainTime", const.REMAINING_TIME),
            RemainSensorEntity(client, self, "bmsChgRemTime", const.CHARGE_REMAINING_TIME, False),
            RemainSensorEntity(client, self, "bmsDsgRemTime", const.DISCHARGE_REMAINING_TIME, False),
            # --- power --------------------------------------------------
            WattsSensorEntity(client, self, "gridPortPower", const.STREAM_AC5000_GRID_PORT_POWER),
            # Battery-side power, unsigned MAGNITUDE -- the device has no signed
            # variant. Confirmed across 58 same-second pairs where the grid port
            # was discharging: the field stayed positive throughout, and never
            # exceeded 2^31 (which is how a negative varint would show up).
            # Both directions carry a ~60 W conversion+standby loss, in the
            # direction that always costs the battery: charging 640 W at the port
            # put 583 W into the pack, while discharging 101 W out of the port
            # drew 162 W from it. Direction must come from Grid Port Power's
            # sign; a template sensor multiplying the two gives a signed value.
            WattsSensorEntity(client, self, "bpPower", const.STREAM_AC5000_BATTERY_POWER),
            WattsSensorEntity(client, self, "maxChgPow", const.STREAM_AC5000_CHARGE_POWER_LIMIT, False),
            WattsSensorEntity(client, self, "maxDsgPow", const.STREAM_AC5000_MAX_DISCHARGE_POWER, False),
            # feedGridModePowLimit is writable and lives in numbers() as
            # "Net Power Out Limit"; only the read-only ceiling stays a sensor.
            WattsSensorEntity(client, self, "feedGridModePowMax", const.STREAM_FEED_GRID_MODE_POW_MAX, False),
            # --- paired P1 meter ----------------------------------------
            # The meter (SN prefix "ES41") has no MQTT topic of its own; it
            # reports inside this device's stream, so its sensors live here and
            # it must NOT be added as a separate device.
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
        """Write both SoC limits at once.

        The app never sends one without the other, so neither does this. The
        entities pass the unchanged limit through from current state rather than
        omitting it, which avoids relying on the device to preserve a field that
        was left absent.
        """
        return self._command(
            propertyId=_PROP_SOC_LIMITS,
            socLimits=stream_ac_5000_pb2.StreamAC5000SetSocLimits(
                cmsMaxChgSoc=max_chg,
                cmsMinDsgSoc=min_dsg,
            ),
        )

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
            # Partial writes are accepted for property 10 -- the app changed the
            # input limit by sending that field alone -- so each of these sends
            # only what it owns.
            # 2500 W is the highest the owner can unlock themselves (a signed
            # declaration in the app); above that needs an installer and a
            # review. Starting there rather than at 7400 keeps the slider honest
            # for the common case -- feedGridModePowMax widens it if the device
            # ever reports a higher ceiling.
            CeilingBoundPowerEntity(
                client,
                self,
                "feedGridModePowLimit",
                const.STREAM_AC5000_NET_POWER_OUT,
                0,
                2500,
                "feedGridModePowMax",
                lambda value: self._command(
                    propertyId=_PROP_POWER_LIMITS,
                    powerLimits=stream_ac_5000_pb2.StreamAC5000SetPowerLimits(
                        feedGridModePowLimit=value,
                        outLimitField4=_OUT_LIMIT_FIELD4,
                        outLimitMax=_OUT_LIMIT_MAX,
                    ),
                ),
            ),
            # The app lets this go to 7200 W, but the hardware tops out at
            # 2500 W (3000 W with a second battery), so the slider stops at 3000
            # rather than accepting setpoints the device silently cannot meet --
            # which would quietly mislead a scheduler like EMHASS.
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
            self._copy(message.battery, params, "cmsMaxChgSoc", "soc", "bmsChgRemTime", "bmsDsgRemTime")
            self._copy(message.battery, params, "f32ShowSoc", "cmsMinDsgSoc")

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
                "f32ShowSoc",
                "realSoh",
                "cycleSoh",
                "calendarSoh",
                "accuChgCap",
                "accuDsgCap",
                "accuChgEnergy",
                "accuDsgEnergy",
            )

    def _decode_runtime(self, message: Any, params: dict[str, Any]) -> None:
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
            # feedGridModePowLimit is NOT taken from this block. Field 33.9 read
            # 800 throughout, including while the limit was set to 700 -- but
            # block 33 is sparse enough that "it is a ceiling" and "it was not
            # sampled during the 6-second window" are indistinguishable here.
            # Block 10 is unambiguous (it is the structure the app writes, and it
            # tracked 800 -> 700 -> 800), so it owns the key alone. Letting an
            # ambiguous source share it risks fighting the user's own setting.
            "feedGridModePowMax",
        )
        # Neither SoC nor the max-charge limit is taken from the BMS block.
        # The BMS reports SoC ~1% below the CMS/app value, and its field 2 is a
        # fixed 100 -- it never followed a change to 95, across every frame in
        # two captures, while 33.7 and the cmd_id 2 status both did. Sharing
        # those keys made the battery level jitter and, worse, snapped the Max
        # Charge Level slider back to 100 a few seconds after any change.
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
        self._copy(message.cms, params, "soc", "cmsBattFullEnergy", "remainTime")
        self._copy(message.powerPack.power, params, "gridPortPower")
        self._copy(message.deviceCfg, params, "upsEnabled", ("xboostEnabled", _KEY_XBOOST))
        self._copy(message.powerLimits, params, "feedGridModePowLimit", "chgPowLimit")
        self._copy(message.acOut, params, ("enabled", _KEY_AC_OUT))
        self._copy(message, params, ("workMode", _KEY_WORK_MODE))

        # Battery-side power arrives only in half-watts; normalise to watts so
        # the sensor carries the unit Home Assistant expects. The CMS copy is
        # preferred because it is emitted more often than the BMS one.
        for source, field in ((message.cms, "cmsPowerHalfW"), (message.bmsPack.bms, "bmsPowerHalfW")):
            if source.HasField(field):
                params["bpPower"] = getattr(source, field) / 2
                break

    @staticmethod
    def _copy(source: Any, params: dict[str, Any], *fields: str | tuple[str, str]) -> None:
        """Copy set protobuf fields onto canonical parameter names.

        A field may be given as ``"name"`` (copied as-is) or ``("name", "alias")``
        to land under a different parameter name -- needed where two blocks carry
        the same quantity under one proto field name but must not overwrite each
        other.

        ``HasField`` is what keeps a block that arrived without a given field
        from overwriting a good value with a proto3 default -- the incremental
        uploads send only what changed, so most blocks are mostly empty.
        """
        for field in fields:
            name, alias = field if isinstance(field, tuple) else (field, field)
            if source.HasField(name):
                params[alias] = getattr(source, name)
