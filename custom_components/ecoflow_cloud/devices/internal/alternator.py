import enum
import logging
from collections.abc import Sequence
from typing import Any, NamedTuple, cast, override

from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message as ProtoMessageRaw
from homeassistant.components.number import NumberMode, NumberEntity  # NumberMode used by _StartVoltageEntity
from homeassistant.components.number.const import NumberDeviceClass
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import UnitOfElectricCurrent, UnitOfElectricPotential
from homeassistant.util import dt

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.api.message import JSONDict, Message, PrivateAPIMessageProtocol
from custom_components.ecoflow_cloud.devices import BaseInternalDevice, const
from custom_components.ecoflow_cloud.devices.internal.proto import AddressId
from custom_components.ecoflow_cloud.devices.internal.proto import ef_alternator_pb2 as alternator_pb2
from custom_components.ecoflow_cloud.devices.data_holder import PreparedData
from custom_components.ecoflow_cloud.entities import BaseNumberEntity
from custom_components.ecoflow_cloud.number import ValueUpdateEntity
from custom_components.ecoflow_cloud.select import PowerDictSelectEntity
from custom_components.ecoflow_cloud.sensor import (
    AmpSensorEntity,
    CelsiusSensorEntity,
    LevelSensorEntity,
    MiscSensorEntity,
    QuotaStatusSensorEntity,
    RemainSensorEntity,
    StatusSensorEntity,
    VoltSensorEntity,
    WattsSensorEntity,
)
from custom_components.ecoflow_cloud.switch import EnabledEntity

_LOGGER = logging.getLogger(__name__)

# cmd_func/cmd_id pair that identifies each alternator packet type
_CMD_FUNC = 254
_CMD_ID_HEARTBEAT = 21     # alternatorHeartbeat — device → app (sensor data)
_CMD_ID_CONFIG_WRITE = 17  # alternatorSet        — app → device (commands)
_CMD_ID_PUSH = 37          # periodic device push / command-applied confirmation

# Prefix used for all sensor keys derived from the heartbeat message
_HB_KEY = f"{_CMD_FUNC}_{_CMD_ID_HEARTBEAT}"


class CommandFuncAndId(NamedTuple):
    func: int
    id: int


class Command(enum.Enum):
    @enum.property
    def func(self) -> int:
        return self.value.func

    @enum.property
    def id(self) -> int:
        return self.value.id

    HEARTBEAT = CommandFuncAndId(func=_CMD_FUNC, id=_CMD_ID_HEARTBEAT)
    CONFIG_WRITE = CommandFuncAndId(func=_CMD_FUNC, id=_CMD_ID_CONFIG_WRITE)
    CONFIG_PUSH = CommandFuncAndId(func=_CMD_FUNC, id=_CMD_ID_PUSH)


class AlternatorCommandMessage(PrivateAPIMessageProtocol):
    """Protobuf command wrapper for the EcoFlow Alternator 800W."""

    def __init__(self, device_sn: str, command: Command, payload: ProtoMessageRaw | None):
        self._packet = alternator_pb2.AlternatorMessage()
        self._payload = payload
        header = self._packet.msg.add()
        header.seq = Message.gen_seq()
        header.device_sn = device_sn
        header.from_ = "HomeAssistant"

        if command == Command.HEARTBEAT:
            # Heartbeat request: src/dest both APP, no payload
            header.src = AddressId.APP
            header.dest = AddressId.APP
            header.data_len = 0
        else:
            header.src = AddressId.APP
            header.dest = AddressId.DEVICE  # device address (20), confirmed by ioBroker reference
            header.d_src = 1
            header.d_dest = 1
            header.check_type = 3
            header.need_ack = 1
            header.version = 19
            header.payload_ver = 1
            if payload is not None:
                pdata = payload.SerializeToString()
                header.pdata = pdata
                header.data_len = len(pdata)

        header.cmd_func = command.func
        header.cmd_id = command.id

    @override
    def to_mqtt_payload(self) -> bytes:
        return self._packet.SerializeToString()

    @override
    def to_dict(self) -> dict:
        if self._payload is None:
            payload_dict: dict = {}
        else:
            payload_dict = MessageToDict(self._payload, preserving_proto_field_name=True)

        result = MessageToDict(self._packet, preserving_proto_field_name=True)
        result["msg"][0]["pdata"] = {type(self._payload).__name__: payload_dict}
        result["msg"][0].pop("seq", None)
        return {type(self._packet).__name__: result}


# ---------------------------------------------------------------------------
# Custom number entities for alternator-specific scaling
# ---------------------------------------------------------------------------

class _StartVoltageEntity(BaseNumberEntity):
    """Number entity for car battery start voltage.

    The heartbeat reports the value as an integer in decivolts (e.g. 120 = 12.0 V).
    The set command expects the same integer encoding.
    """

    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_device_class = NumberDeviceClass.VOLTAGE
    _attr_native_step = 0.5
    _attr_mode = NumberMode.BOX

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10.0)

    async def async_set_native_value(self, value: float) -> None:
        if self._command:
            raw = int(round(value * 10))
            self.send_set_message(raw, self.command_dict(raw))


class _CurrentLimitEntity(BaseNumberEntity):
    """Number entity for alternator charge / reverse-charge current limits (Amps).

    The heartbeat reports the value directly as a float in Amps (e.g. 40.0 = 40 A).
    The set command expects the same float encoding.
    """

    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_device_class = NumberDeviceClass.CURRENT
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    async def async_set_native_value(self, value: float) -> None:
        if self._command:
            self.send_set_message(float(value), self.command_dict(float(value))) # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Device class
# ---------------------------------------------------------------------------

class Alternator(BaseInternalDevice):
    """EcoFlow Alternator 800W smart alternator charger."""

    @override
    def sensors(self, client: EcoflowApiClient) -> Sequence[SensorEntity]:
        return [
            # Power flow
            WattsSensorEntity(client, self, f"{_HB_KEY}.alternatorPower", const.ALTERNATOR_IN_POWER),
            WattsSensorEntity(client, self, f"{_HB_KEY}.stationPower", const.ALTERNATOR_STATION_POWER),
            WattsSensorEntity(client, self, f"{_HB_KEY}.ratedPower", const.ALTERNATOR_RATED_POWER, enabled=False),
            WattsSensorEntity(client, self, f"{_HB_KEY}.permanentWatts", const.ALTERNATOR_POWER_LIMIT, enabled=False),
            # Battery / charging state
            LevelSensorEntity(client, self, f"{_HB_KEY}.batSoc", const.ALTERNATOR_BAT_SOC),
            RemainSensorEntity(client, self, f"{_HB_KEY}.chargeToFull268", const.ALTERNATOR_DISCHARGE_REMAINING),
            RemainSensorEntity(client, self, f"{_HB_KEY}.unknown269", const.ALTERNATOR_CHARGE_REMAINING),
            # Car battery
            VoltSensorEntity(client, self, f"{_HB_KEY}.carBatVolt", const.ALTERNATOR_CAR_BAT_VOLT),
            # Diagnostics
            CelsiusSensorEntity(client, self, f"{_HB_KEY}.temp", const.ALTERNATOR_TEMP),
            MiscSensorEntity(client, self, f"{_HB_KEY}.wifiRssi", const.ALTERNATOR_WIFI_RSSI, enabled=False),
            MiscSensorEntity(client, self, f"{_HB_KEY}.status1", "Alternator Status Code", enabled=False),
            MiscSensorEntity(client, self, f"{_HB_KEY}.operationMode", const.ALTERNATOR_OPERATION_MODE, enabled=False),
            # Per-mode current limits (read-only view — controlled via number entities)
            # car_batt_chg = charging the car battery = Reverse Charge mode (station→car)
            # dev_batt_chg = charging the device/station battery = Charge mode (alternator→station)
            AmpSensorEntity(client, self, f"{_HB_KEY}.spChargerDevBattChgAmpLimit", const.ALTERNATOR_CHARGE_CURRENT_LIMIT, enabled=False),
            AmpSensorEntity(client, self, f"{_HB_KEY}.spChargerCarBattChgAmpLimit", const.ALTERNATOR_REVERSE_CHARGE_CURRENT_LIMIT, enabled=False),
            # Rated max current (device capability, read-only)
            AmpSensorEntity(client, self, f"{_HB_KEY}.spChargerDevBattChgAmpMax", const.ALTERNATOR_CHARGE_CURRENT_MAX, enabled=False),
            AmpSensorEntity(client, self, f"{_HB_KEY}.spChargerCarBattChgAmpMax", const.ALTERNATOR_REVERSE_CHARGE_CURRENT_MAX, enabled=False),
            self._status_sensor(client),
        ]

    @override
    def numbers(self, client: EcoflowApiClient) -> Sequence[NumberEntity]:
        return [
            # dev_batt_chg = charging the device/station battery = Charge mode (alternator→station)
            _CurrentLimitEntity(
                client,
                self,
                f"{_HB_KEY}.spChargerDevBattChgAmpLimit",
                const.ALTERNATOR_CHARGE_CURRENT_LIMIT,
                1,
                70,
                lambda value: AlternatorCommandMessage(
                    device_sn=self.device_info.sn,
                    command=Command.CONFIG_WRITE,
                    payload=alternator_pb2.AlternatorSet(cfg_sp_charger_dev_batt_chg_amp_limit=float(value)),
                ),
            ),
            # car_batt_chg = charging the car battery = Reverse Charge mode (station→car)
            _CurrentLimitEntity(
                client,
                self,
                f"{_HB_KEY}.spChargerCarBattChgAmpLimit",
                const.ALTERNATOR_REVERSE_CHARGE_CURRENT_LIMIT,
                1,
                70,
                lambda value: AlternatorCommandMessage(
                    device_sn=self.device_info.sn,
                    command=Command.CONFIG_WRITE,
                    payload=alternator_pb2.AlternatorSet(cfg_sp_charger_car_batt_chg_amp_limit=float(value)),
                ),
            ),
            _StartVoltageEntity(
                client,
                self,
                f"{_HB_KEY}.startVoltage",
                const.ALTERNATOR_START_VOLTAGE,
                11,
                30,
                lambda raw_value: AlternatorCommandMessage(
                    device_sn=self.device_info.sn,
                    command=Command.CONFIG_WRITE,
                    payload=alternator_pb2.AlternatorSet(start_voltage=raw_value),
                ),
            ),
            ValueUpdateEntity(
                client,
                self,
                f"{_HB_KEY}.cableLength608",
                const.ALTERNATOR_CABLE_LENGTH,
                0,
                10,
                lambda value: AlternatorCommandMessage(
                    device_sn=self.device_info.sn,
                    command=Command.CONFIG_WRITE,
                    payload=alternator_pb2.AlternatorSet(cable_length=float(value)),
                ),
                enabled=False,
            ),
        ]

    @override
    def switches(self, client: EcoflowApiClient) -> Sequence[SwitchEntity]:
        return [
            EnabledEntity(
                client,
                self,
                f"{_HB_KEY}.startStop",
                const.ALTERNATOR_ENABLED,
                lambda value: AlternatorCommandMessage(
                    device_sn=self.device_info.sn,
                    command=Command.CONFIG_WRITE,
                    payload=alternator_pb2.AlternatorSet(start_stop=value),
                ),
                enabled=True,
                enableValue=1,
            ),
        ]

    @override
    def selects(self, client: EcoflowApiClient) -> Sequence[SelectEntity]:
        return [
            PowerDictSelectEntity(
                client,
                self,
                f"{_HB_KEY}.operationMode",
                const.ALTERNATOR_OPERATION_MODE,
                const.ALTERNATOR_OPERATION_MODE_OPTIONS,
                lambda value: AlternatorCommandMessage(
                    device_sn=self.device_info.sn,
                    command=Command.CONFIG_WRITE,
                    payload=alternator_pb2.AlternatorSet(operation_mode=value),
                ),
            ),
        ]

    @override
    def _prepare_data(self, raw_data: bytes) -> dict[str, Any]:
        res: dict[str, Any] = {"params": {}}

        try:
            packet = alternator_pb2.AlternatorMessage()
            _ = packet.ParseFromString(raw_data)

            for header in packet.msg:
                cmd_func = header.cmd_func
                cmd_id = header.cmd_id
                _LOGGER.debug(
                    'alternator cmd_func=%u cmd_id=%u pdata="%s"',
                    cmd_func,
                    cmd_id,
                    header.pdata.hex() if header.HasField("pdata") else "<none>",
                )

                if header.HasField("device_sn") and header.device_sn != self.device_data.sn:
                    _LOGGER.info(
                        "Ignoring alternator packet for SN %s on topic for SN %s",
                        header.device_sn,
                        self.device_data.sn,
                    )

                command_desc = CommandFuncAndId(func=cmd_func, id=cmd_id)
                try:
                    command = Command(command_desc)
                except ValueError:
                    _LOGGER.info(
                        "Unsupported alternator packet cmd_func=%u cmd_id=%u", cmd_func, cmd_id
                    )
                    continue

                params = cast(JSONDict, res.setdefault("params", {}))

                if command in (Command.HEARTBEAT, Command.CONFIG_PUSH):
                    pdata = header.pdata
                    # The alternator uses XOR encryption (enc_type=1): pdata[i] ^ (seq & 0xFF)
                    if header.HasField("enc_type") and header.enc_type == 1:
                        pdata = bytes([b ^ (header.seq % 256) for b in pdata])

                    heartbeat = alternator_pb2.AlternatorHeartbeat()
                    _ = heartbeat.ParseFromString(pdata)
                    hb_dict = cast(JSONDict, MessageToDict(heartbeat, preserving_proto_field_name=False))
                    if hb_dict:
                        params.update((f"{_HB_KEY}.{key}", value) for key, value in hb_dict.items())
                    else:
                        _LOGGER.debug("cmd_id=%d: no fields decoded, raw pdata=%s", cmd_id, pdata.hex())

                res["cmdFunc"] = cmd_func
                res["cmdId"] = cmd_id
                res["timestamp"] = dt.utcnow()

        except Exception as error:
            _LOGGER.error("Failed to parse alternator packet: %s", error)
            _LOGGER.debug("Raw data hex: %s", raw_data.hex())

        return res

    def _parsed_reply(self, raw_data: bytes) -> PreparedData:
        """Parse a reply packet; return PreparedData with params if state data is present."""
        data = self._prepare_data(raw_data)
        if "cmdFunc" in data and "cmdId" in data:
            command_desc = CommandFuncAndId(func=data["cmdFunc"], id=data["cmdId"])
            try:
                command = Command(command_desc)
                if command in (Command.HEARTBEAT, Command.CONFIG_PUSH):
                    return PreparedData(None, data, {"proto": raw_data.hex()})
            except ValueError:
                pass
        return PreparedData(None, None, {"proto": raw_data.hex()})

    @override
    def _prepare_data_get_reply_topic(self, raw_data: bytes) -> PreparedData:
        return self._parsed_reply(raw_data)

    @override
    def _prepare_data_set_reply_topic(self, raw_data: bytes) -> PreparedData:
        return self._parsed_reply(raw_data)

    @override
    def get_quota_message(self) -> AlternatorCommandMessage:
        return AlternatorCommandMessage(
            device_sn=self.device_info.sn,
            command=Command.HEARTBEAT,
            payload=None,
        )

    def _status_sensor(self, client: EcoflowApiClient) -> StatusSensorEntity:
        return QuotaStatusSensorEntity(client, self)
