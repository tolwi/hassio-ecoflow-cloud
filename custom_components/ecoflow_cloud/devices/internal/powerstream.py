import logging
from collections.abc import Sequence
from typing import Any, cast, override

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.util import dt

from custom_components.ecoflow_cloud.devices.internal.proto.support import (
    to_lower_camel_case,
)

from ...api import EcoflowApiClient
from ...api.message import JSONDict
from ...sensor import (
    QuotaStatusSensorEntity,
    ResettingInEnergySensorEntity,
    ResettingInEnergySolarSensorEntity,
    ResettingOutEnergySensorEntity,
    StatusSensorEntity,
)
from ...switch import EnabledEntity
from ..internal.proto import platform_pb2 as platform
from ..internal.proto import powerstream_pb2 as powerstream
from ..public.powerstream import PowerStream as PublicPowerStream
from ..public.powerstream import build_command
from .proto import PrivateAPIProtoDeviceMixin
from .proto.support.const import Command, WatthType, get_expected_payload_type

_LOGGER = logging.getLogger(__name__)


class PowerStream(PrivateAPIProtoDeviceMixin, PublicPowerStream):
    @override
    def sensors(self, client: EcoflowApiClient) -> Sequence[SensorEntity]:
        sensors = list(super().sensors(client))
        sensors.extend(
            [
                ResettingInEnergySolarSensorEntity(
                    client,
                    self,
                    "254_32.watthPv1",
                    "PV1 Today Energy Total",
                    enabled=True,
                ),
                ResettingInEnergySolarSensorEntity(
                    client,
                    self,
                    "254_32.watthPv2",
                    "PV2 Today Energy Total",
                    enabled=True,
                ),
                ResettingInEnergySensorEntity(
                    client,
                    self,
                    "254_32.watthFromBattery",
                    "From Battery Today Energy Total",
                    enabled=True,
                ),
                ResettingOutEnergySensorEntity(
                    client,
                    self,
                    "254_32.watthToBattery",
                    "To Battery Today Energy Total",
                    enabled=True,
                ),
                ResettingOutEnergySensorEntity(
                    client,
                    self,
                    "254_32.watthToSmartPlugs",
                    "To Smart Plugs Today Energy Total",
                    enabled=True,
                ),
            ]
        )
        return sensors

    @override
    def switches(self, client: EcoflowApiClient) -> Sequence[SwitchEntity]:
        switches = list(super().switches(client))
        switches.extend(
            [
                EnabledEntity(
                    client,
                    self,
                    "20_1.feedProtect",
                    "Feed-in Control",
                    lambda value: build_command(
                        device_sn=self.device_info.sn,
                        command=Command.PRIVATE_API_POWERSTREAM_SET_FEED_PROTECT,
                        payload=powerstream.PrivateAPIGenericSetValue(value=value),
                    ),
                    enabled=True,
                    enableValue=1,
                )
            ]
        )
        return switches

    def _prepare_data(self, raw_data: bytes) -> dict[str, Any]:
        res: dict[str, Any] = {"params": {}}
        from google.protobuf.json_format import MessageToDict

        from .proto import ecopacket_pb2 as ecopacket
        from .proto.support.const import Command, CommandFuncAndId

        try:
            packet = ecopacket.SendHeaderMsg()
            _ = packet.ParseFromString(raw_data)
            for message in packet.msg:
                _LOGGER.debug(
                    'cmd_func %u, cmd_id %u, payload "%s"',
                    message.cmd_func,
                    message.cmd_id,
                    message.pdata.hex(),
                )

                if (
                    message.HasField("device_sn")
                    and message.device_sn != self.device_data.sn
                ):
                    _LOGGER.info(
                        "Ignoring EcoPacket for SN %s on topic for SN %s",
                        message.device_sn,
                        self.device_data.sn,
                    )

                command_desc = CommandFuncAndId(
                    func=message.cmd_func, id=message.cmd_id
                )

                try:
                    command = Command(command_desc)
                except ValueError:
                    _LOGGER.info(
                        "Unsupported EcoPacket cmd_func %u, cmd_id %u",
                        command_desc.func,
                        command_desc.id,
                    )
                    continue

                params = cast(JSONDict, res.setdefault("params", {}))
                if command in {Command.PRIVATE_API_POWERSTREAM_HEARTBEAT}:
                    payload = get_expected_payload_type(command)()
                    _ = payload.ParseFromString(message.pdata)
                    params.update(
                        (f"{command.func}_{command.id}.{key}", value)
                        for key, value in cast(
                            JSONDict,
                            MessageToDict(payload, preserving_proto_field_name=False),
                        ).items()
                    )
                elif command in {Command.PRIVATE_API_PLATFORM_WATTH}:
                    payload = platform.BatchEnergyTotalReport()
                    _ = payload.ParseFromString(message.pdata)
                    for watth_item in payload.watth_item:
                        try:
                            watth_type_name = to_lower_camel_case(
                                WatthType(watth_item.watth_type).name
                            )
                        except ValueError:
                            continue

                        field_name = (
                            f"watth{watth_type_name[0].upper()}{watth_type_name[1:]}"
                        )
                        params.update(
                            {
                                f"{command.func}_{command.id}.{field_name}": sum(
                                    watth_item.watth
                                ),
                                f"{command.func}_{command.id}.{field_name}Timestamp": watth_item.timestamp,
                            }
                        )

                # Add cmd information to allow extraction in private_api_extract_quota_message
                res["cmdFunc"] = command_desc.func
                res["cmdId"] = command_desc.id
                res["timestamp"] = dt.utcnow()
                continue
        except Exception as error:
            _LOGGER.error(error)
            _LOGGER.info(raw_data.hex())
        return res

    def _status_sensor(self, client: EcoflowApiClient) -> StatusSensorEntity:
        return QuotaStatusSensorEntity(client, self)
