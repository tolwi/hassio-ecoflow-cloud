"""EcoFlow STREAM Microinverter (BK-series, SN prefix ``BK01``) — internal/App API.

Transport: MQTT topic ``/app/device/property/<SN>``, envelope protobuf
``StreamACSendHeaderMsg`` from the already-existing
``devices/internal/proto/stream_ac_pb2.py`` (same envelope schema used by
``devices/internal/stream_ac.py`` — verified by field-by-field ``ListFields()``
inspection against real device pushes: ``pdata(1), src(2), dest(3), d_src(4),
d_dest(5), enc_type(6), check_type(7), cmd_func(8), cmd_id(9), data_len(10),
need_ack(11), seq(14), product_id(15), version(16), payload_ver(17)``).
Observed push values: ``src=2, dest=32, cmd_func=254, cmd_id=21,
product_id=17409``.

Encryption: ``msg.pdata`` is XOR-obfuscated with a single byte derived from
the envelope's own ``seq`` field::

    key = msg.seq & 0xFF
    plain = bytes(b ^ key for b in msg.pdata)

This step is mandatory — parsing ``plain`` as protobuf fails on essentially
every message without it. Verified against 54 real push messages (0 parse
errors, all fields plausible, e.g. ``grid_connection_power`` ~207 W,
``pow_get_pv`` ~104 W, ``grid_connection_vol`` ~232 V).

For ``cmd_func == 254 and cmd_id == 21``, ``plain`` is a
``BkSeriesDisplayPropertyUpload`` message (see ``proto/ef_bk_series.proto``, a slim
subset extracted from rabits/ha-ef-ble, Apache-2.0, and verified by
round-tripping against the original generated module).
"""

import logging
from typing import Any, override

from google.protobuf.json_format import MessageToDict
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.util import utcnow

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.api.message import Message, PrivateAPIMessageProtocol
from custom_components.ecoflow_cloud.devices import BaseInternalDevice, const
from custom_components.ecoflow_cloud.devices.internal.proto import AddressId
from custom_components.ecoflow_cloud.devices.internal.proto import ef_bk_series_pb2
from custom_components.ecoflow_cloud.devices.internal.proto import stream_ac_pb2
from custom_components.ecoflow_cloud.sensor import (
    FrequencySensorEntity,
    InAmpSensorEntity,
    MiscSensorEntity,
    QuotaScheduledStatusSensorEntity,
    StatusSensorEntity,
    VoltSensorEntity,
    WattsSensorEntity,
)

_LOGGER = logging.getLogger(__name__)

# cmd_func/cmd_id pair identifying the BkSeriesDisplayPropertyUpload telemetry push.
_CMD_FUNC_DISPLAY_PROPERTY = 254
_CMD_ID_DISPLAY_PROPERTY = 21


class _BkSeriesPvWattsSensorEntity(WattsSensorEntity):
    """Computed PV watts (``amp x vol``) for internal BK-series protobuf keys.

    ``StreamPvWattsSensorEntity`` (devices/public/stream_pv_helpers.py)
    assumes camelCase Public-API/JSON keys ending in ``"Amp"`` and derives
    the matching ``"Vol"`` key by suffix replacement. The internal (App) API
    BK-series protobuf schema instead uses the field names straight from the
    wire protobuf, e.g. ``plug_in_info_pv_amp`` / ``plug_in_info_pv_vol``
    (snake_case, no ``"Amp"``/``"Vol"`` suffix convention to hook into).
    Rather than teaching the public helper a second naming scheme, this is a
    small standalone counterpart that takes both keys explicitly and follows
    the same amp x vol computation and synthetic-key pattern.
    """

    _SYNTHETIC_KEY_PREFIX = "pvWatts"

    def __init__(
        self,
        client,
        device,
        amp_key: str,
        vol_key: str,
        title,
        enabled: bool = True,
        auto_enable: bool = False,
    ) -> None:
        self._amp_key = amp_key
        self._vol_key = vol_key
        synthetic_key = f"{self._SYNTHETIC_KEY_PREFIX}_{amp_key}"
        super().__init__(client, device, synthetic_key, title, enabled, auto_enable)

    def _updated(self, data: dict[str, Any]) -> None:  # type: ignore[override]
        amp = data.get(self._amp_key)
        vol = data.get(self._vol_key)
        if amp is None or vol is None:
            # Let the upstream pipeline handle offline / default-value reset.
            super()._updated(data)
            return
        try:
            watts = float(amp) * float(vol)
        except (TypeError, ValueError):
            return
        super()._updated({**data, self.mqtt_key: watts})


class StreamMicroinverterCommandMessage(PrivateAPIMessageProtocol):
    """Envelope requesting a re-publish of ``BkSeriesDisplayPropertyUpload``.

    Modeled on ``PowerStreamCommandMessage`` / ``Command.INVERTER_HEARTBEAT``
    in devices/internal/powerstream.py: same ``cmd_func``/``cmd_id`` as the
    device's own telemetry push, empty ``pdata``, ``src``/``dest`` both set
    to ``AddressId.APP``. For PowerStream that pattern reliably makes the
    device re-publish its current state on demand (see issue #830).

    Best effort only, NOT yet verified live against a STREAM Microinverter.
    It exists so ``quota_all()`` (called by ``QuotaScheduledStatusSensorEntity``
    below and at integration startup) has something to send; if it turns out
    to be a no-op for this device, sensors simply keep showing the last value
    received from the device's own unsolicited pushes.
    """

    def __init__(self, device_sn: str):
        self._packet = stream_ac_pb2.StreamACSendHeaderMsg()
        message = self._packet.msg
        message.seq = Message.gen_seq()
        message.device_sn = device_sn
        # stream_ac.proto declares this field as `from` (not `from_`), which
        # collides with the Python keyword, so it can only be reached via
        # get/setattr, not attribute syntax.
        setattr(message, "from", "HomeAssistant")
        message.src = AddressId.APP
        message.dest = AddressId.APP
        message.data_len = 0
        message.cmd_func = _CMD_FUNC_DISPLAY_PROPERTY
        message.cmd_id = _CMD_ID_DISPLAY_PROPERTY

    @override
    def to_mqtt_payload(self) -> bytes:
        return self._packet.SerializeToString()

    @override
    def to_dict(self) -> dict:
        result = MessageToDict(self._packet, preserving_proto_field_name=True)
        result["msg"].pop("seq", None)
        return {type(self._packet).__name__: result}


class StreamMicroinverter(BaseInternalDevice):
    """EcoFlow STREAM Microinverter (BK-series)."""

    @override
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            WattsSensorEntity(client, self, "grid_connection_power", const.STREAM_POWER_AC),
            VoltSensorEntity(client, self, "grid_connection_vol", const.STREAM_POWER_VOL, False),
            InAmpSensorEntity(client, self, "grid_connection_amp", const.STREAM_POWER_AMP, False),
            FrequencySensorEntity(client, self, "grid_connection_freq", "Grid Frequency"),
            MiscSensorEntity(client, self, "grid_connection_sta", const.STREAM_GRID_CONNECTION_STATUS),
            # Per-PV mapping mirrors devices/public/stream_microinverter.py:
            # both the direct pow_get_pv* field and the computed amp x vol
            # path are registered with auto_enable=True so the integration
            # stays firmware-agnostic — HA enables whichever variant first
            # sees a non-zero value. See issues #582/#584.
            WattsSensorEntity(client, self, "pow_get_pv", const.STREAM_POWER_PV_1, False, True),
            WattsSensorEntity(client, self, "pow_get_pv2", const.STREAM_POWER_PV_2, False, True),
            _BkSeriesPvWattsSensorEntity(
                client, self, "plug_in_info_pv_amp", "plug_in_info_pv_vol", const.STREAM_POWER_PV_1, False, True
            ),
            _BkSeriesPvWattsSensorEntity(
                client, self, "plug_in_info_pv2_amp", "plug_in_info_pv2_vol", const.STREAM_POWER_PV_2, False, True
            ),
            VoltSensorEntity(client, self, "plug_in_info_pv_vol", const.STREAM_IN_VOL_PV_1, False, True),
            VoltSensorEntity(client, self, "plug_in_info_pv2_vol", const.STREAM_IN_VOL_PV_2, False, True),
            InAmpSensorEntity(client, self, "plug_in_info_pv_amp", const.STREAM_IN_AMPS_PV_1, False, True),
            InAmpSensorEntity(client, self, "plug_in_info_pv2_amp", const.STREAM_IN_AMPS_PV_2, False, True),
            MiscSensorEntity(client, self, "module_wifi_rssi", const.STREAM_WIFI_RSSI),
            WattsSensorEntity(
                client, self, "feed_grid_mode_pow_limit", const.STREAM_FEED_GRID_MODE_POW_LIMIT, diagnostic=True
            ),
            WattsSensorEntity(
                client, self, "feed_grid_mode_pow_max", const.STREAM_FEED_GRID_MODE_POW_MAX, diagnostic=True
            ),
            self._status_sensor(client),
        ]

    @override
    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return []

    @override
    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return []

    @override
    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return []

    @override
    def _prepare_data(self, raw_data: bytes) -> dict[str, Any]:
        raw: dict[str, Any] = {"params": {}}

        try:
            payload = raw_data

            # Mirrors devices/internal/stream_ac.py's _prepare_data loop
            # structure: a single MQTT payload can carry several concatenated
            # envelope frames.
            while True:
                packet = stream_ac_pb2.StreamACSendHeaderMsg()
                packet.ParseFromString(payload)

                _LOGGER.debug(
                    'cmd_func "%u" cmd_id "%u" seq "%u" pdata "%s"',
                    packet.msg.cmd_func,
                    packet.msg.cmd_id,
                    packet.msg.seq,
                    packet.msg.pdata.hex() if packet.msg.HasField("pdata") else "",
                )

                if (
                    packet.msg.cmd_func == _CMD_FUNC_DISPLAY_PROPERTY
                    and packet.msg.cmd_id == _CMD_ID_DISPLAY_PROPERTY
                    and packet.msg.HasField("pdata")
                    and len(packet.msg.pdata) > 0
                ):
                    self._parse_display_property(packet, raw)
                else:
                    _LOGGER.debug(
                        "Ignoring EcoPacket cmd_func %u cmd_id %u (not BkSeriesDisplayPropertyUpload)",
                        packet.msg.cmd_func,
                        packet.msg.cmd_id,
                    )

                if packet.ByteSize() >= len(payload):
                    break

                _LOGGER.info("Found another frame in payload")

                packet_length = len(payload) - packet.ByteSize()
                payload = payload[:packet_length]

        except Exception as error:
            _LOGGER.error(error)
            _LOGGER.debug('raw_data.hex(): "%s"', raw_data.hex())

        return raw

    def _parse_display_property(self, packet, raw: dict[str, Any]) -> None:
        try:
            # See module docstring: pdata is XOR-obfuscated with a single
            # byte derived from the envelope's own seq field. Mandatory
            # before protobuf parsing can succeed.
            key = packet.msg.seq & 0xFF
            plain = bytes(b ^ key for b in packet.msg.pdata)

            content = ef_bk_series_pb2.BkSeriesDisplayPropertyUpload()
            content.ParseFromString(plain)

            self._store_fields(content, raw)
            raw["timestamp"] = utcnow()
        except Exception as error:
            _LOGGER.debug("Failed to parse BkSeriesDisplayPropertyUpload: %s", error)
            _LOGGER.debug('pdata.hex(): "%s"', packet.msg.pdata.hex())

    @staticmethod
    def _store_fields(content, raw: dict[str, Any]) -> None:
        for descriptor in content.DESCRIPTOR.fields:
            if not content.HasField(descriptor.name):
                continue

            value = getattr(content, descriptor.name)
            if descriptor.type == descriptor.TYPE_ENUM:
                # e.g. grid_connection_sta -> "PANEL_GRID_IN" instead of the
                # raw enum int, so MiscSensorEntity can display it directly.
                value = descriptor.enum_type.values_by_number[value].name

            raw["params"][descriptor.name] = value

    def _status_sensor(self, client: EcoflowApiClient) -> StatusSensorEntity:
        # The Stream family pushes over MQTT irregularly while idle (see
        # devices/public/stream_microinverter.py / issues #696, #651, #830).
        # QuotaScheduledStatusSensorEntity polls quota_all() every 60s as a
        # keep-alive independent of whether StreamMicroinverterCommandMessage
        # actually nudges the device into re-publishing.
        return QuotaScheduledStatusSensorEntity(client, self, reload_delay=60)

    @override
    def get_quota_message(self) -> StreamMicroinverterCommandMessage:
        return StreamMicroinverterCommandMessage(device_sn=self.device_info.sn)
