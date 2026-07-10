"""EcoFlow OCEAN 2 / OCEAN 2 Plus home battery.

This device is NOT the same product as "PowerOcean" (``devices/public/powerocean.py``,
EcoFlow's public-API-only whole-home solar/backup system) - OCEAN 2 is a newer,
separate product line, currently absent from EcoFlow's Developer API entirely.

See ``ocean2_protocol.py`` in this package for the full write-up of what is and
is not confirmed about the wire protocol, and ``docs/devices/OCEAN_2.md`` for
the human-readable version plus how to help confirm the remaining fields.

Status: EXPERIMENTAL. Telemetry decoding works and has been validated against
two real captured MQTT frames, but the exact meaning of most fields (which is
Grid vs Battery vs SoC, etc.) is not yet confirmed - see the diagnostic raw
telemetry sensor's attributes for the full picture in the meantime.
"""

import enum
import logging
from collections.abc import Sequence
from typing import Any, NamedTuple, cast, override

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.util import dt

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.api.message import JSONDict, Message, PrivateAPIMessageProtocol
from custom_components.ecoflow_cloud.devices import BaseInternalDevice
from custom_components.ecoflow_cloud.devices.internal import ocean2_protocol as proto
from custom_components.ecoflow_cloud.entities import EcoFlowAbstractDataEntity
from custom_components.ecoflow_cloud.sensor import QuotaStatusSensorEntity, StatusSensorEntity, WattsSensorEntity

_LOGGER = logging.getLogger(__name__)


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

    # Same (func=20, id=1) convention used by PowerStream/SmartMeter in this
    # project for "please send your current state". NOT CONFIRMED to do
    # anything for OCEAN 2 - worst case it is silently ignored, same as any
    # other cmd_func/cmd_id the firmware doesn't recognise (observed in the
    # portal's own message handler, which just no-ops on unknown commands).
    HEARTBEAT = CommandFuncAndId(func=20, id=1)

    DISPLAY_PROPERTY_UPLOAD = CommandFuncAndId(
        func=proto.DISPLAY_PROPERTY_UPLOAD_CMD_FUNC,
        id=proto.DISPLAY_PROPERTY_UPLOAD_CMD_ID,
    )


# Sub-field slots observed so far within the two "experimental power group"
# top-level fields (see ocean2_protocol.py). Declared as fixed sensors since
# Home Assistant entities must be defined up front; the full, unrestricted
# decode is always available via the diagnostic raw-telemetry sensor's
# attributes regardless of what shows up here.
_EXPERIMENTAL_GROUP_SLOTS: dict[int, tuple[int, ...]] = {
    7: (1, 3, 4, 6),
    87: (1, 3, 6),
}


class Ocean2CommandMessage(PrivateAPIMessageProtocol):
    """Outgoing command wrapper, hand-encoded (see ocean2_protocol.py) since
    no compiled protobuf schema exists for this product yet."""

    def __init__(self, device_sn: str, command: Command):
        self._device_sn = device_sn
        self._command = command
        self._seq = Message.gen_seq()

    @override
    def to_mqtt_payload(self):
        header = proto.encode_header_message(
            device_sn=self._device_sn,
            cmd_func=self._command.func,
            cmd_id=self._command.id,
            seq=self._seq,
            src=32,
            dest=32,
            from_="HomeAssistant",
        )
        return proto.encode_send_header_msg(header)

    @override
    def to_dict(self) -> dict:
        return {
            "Ocean2SendHeaderMsg": {
                "cmd_func": self._command.func,
                "cmd_id": self._command.id,
                "seq": self._seq,
                "device_sn": self._device_sn,
            }
        }


class Ocean2RawTelemetrySensorEntity(SensorEntity, EcoFlowAbstractDataEntity):
    """Diagnostic sensor exposing the fully generic decode of the latest
    (cmd_func=254, cmd_id=39) "displayPropertyUpload" message as attributes.

    The field-number -> meaning mapping is not fully reverse engineered yet
    (see ocean2_protocol.py), so rather than guessing wrong and shipping
    misleading named sensors, everything that could be decoded is exposed
    here so it can be correlated against the EcoFlow app/portal over time.
    """

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:code-json"

    def __init__(self, client: EcoflowApiClient, device: "Ocean2"):
        super().__init__(client, device, "OCEAN 2 Raw Telemetry (Diagnostic)", "254_39.seq")
        self._attr_native_value = None

    def _handle_coordinator_update(self) -> None:
        params = self._device.data.params
        seq = params.get("254_39.seq")
        if seq is not None and seq != self._attr_native_value:
            self._attr_native_value = seq
            self.schedule_update_ha_state()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        params = self._device.data.params
        return {
            "cmd_func": params.get("254_39.cmd_func"),
            "cmd_id": params.get("254_39.cmd_id"),
            "enc_type": params.get("254_39.enc_type"),
            "raw_decoded": params.get("254_39.raw_decoded"),
        }


class Ocean2(BaseInternalDevice):
    @override
    def sensors(self, client: EcoflowApiClient) -> Sequence[SensorEntity]:
        result: list[SensorEntity] = [Ocean2RawTelemetrySensorEntity(client, self)]
        for group, slots in _EXPERIMENTAL_GROUP_SLOTS.items():
            for slot in slots:
                result.append(
                    WattsSensorEntity(
                        client,
                        self,
                        f"254_39.group_{group}.f{slot}",
                        f"Experimental Power (field {group}.{slot}, unconfirmed)",
                        enabled=False,
                        diagnostic=True,
                    )
                )
        result.append(self._status_sensor(client))
        return result

    @override
    def numbers(self, client: EcoflowApiClient) -> Sequence[NumberEntity]:
        return []

    @override
    def switches(self, client: EcoflowApiClient) -> Sequence[SwitchEntity]:
        return []

    @override
    def selects(self, client: EcoflowApiClient) -> Sequence[SelectEntity]:
        return []

    @override
    def _prepare_data(self, raw_data: bytes) -> dict[str, Any]:
        res: dict[str, Any] = {"params": {}}
        params = cast(JSONDict, res["params"])

        try:
            headers = proto.parse_send_header_msg(raw_data)
        except proto.ProtoParseError as error:
            _LOGGER.warning("Failed to parse OCEAN 2 envelope: %s. Raw: %s", error, raw_data.hex())
            return res

        for header in headers:
            if header.device_sn is not None and header.device_sn != self.device_data.sn:
                _LOGGER.info(
                    "Ignoring EcoPacket for SN %s on topic for SN %s",
                    header.device_sn,
                    self.device_data.sn,
                )
                continue

            _LOGGER.debug(
                "OCEAN 2 message cmd_func=%s cmd_id=%s seq=%s enc_type=%s pdata=%s",
                header.cmd_func,
                header.cmd_id,
                header.seq,
                header.enc_type,
                header.pdata.hex() if header.pdata else None,
            )

            if (
                header.cmd_func == Command.DISPLAY_PROPERTY_UPLOAD.func
                and header.cmd_id == Command.DISPLAY_PROPERTY_UPLOAD.id
                and header.pdata is not None
            ):
                try:
                    pdata = proto.maybe_decrypt_pdata(header.pdata, header.seq, header.enc_type)
                    decoded = proto.decode_display_property_upload(pdata)
                except proto.ProtoParseError as error:
                    _LOGGER.warning("Failed to parse OCEAN 2 payload: %s. Raw: %s", error, header.pdata.hex())
                    continue

                prefix = f"{Command.DISPLAY_PROPERTY_UPLOAD.func}_{Command.DISPLAY_PROPERTY_UPLOAD.id}"
                params[f"{prefix}.seq"] = header.seq
                params[f"{prefix}.cmd_func"] = header.cmd_func
                params[f"{prefix}.cmd_id"] = header.cmd_id
                params[f"{prefix}.enc_type"] = header.enc_type
                params[f"{prefix}.raw_decoded"] = decoded["raw"]
                for group, values in decoded["experimental_power_groups"].items():
                    for slot, value in values.items():
                        params[f"{prefix}.{group}.{slot}"] = value

                res["cmdFunc"] = header.cmd_func
                res["cmdId"] = header.cmd_id
                res["timestamp"] = dt.utcnow()

        return res

    @override
    def get_quota_message(self) -> Message:
        # NOT CONFIRMED to trigger anything for OCEAN 2 - see Command.HEARTBEAT.
        # Harmless if ignored; telemetry otherwise arrives passively via the
        # data topic subscription regardless of this message.
        return Ocean2CommandMessage(device_sn=self.device_info.sn, command=Command.HEARTBEAT)

    def _status_sensor(self, client: EcoflowApiClient) -> StatusSensorEntity:
        return QuotaStatusSensorEntity(client, self)
