"""Public EcoFlow Developer API support for the STREAM 5000 (BKW3 / ES21).

This device exposes a *system-level* energy-flow report, not the BK-series
per-inverter/MPPT telemetry. All values and controls here use the official
JSON MQTT quota/set API, without the App API or protobuf.

The API supplies MQTT quota fields as nested dictionaries and may return
HTTP quota fields flattened with a hyphen separator. Both transports are
normalized to the same dotted sensor keys.
"""

from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import BaseDevice, const
from custom_components.ecoflow_cloud.devices.public.stream_5000_data import normalize_quota
from custom_components.ecoflow_cloud.number import MinMaxLevelEntity
from custom_components.ecoflow_cloud.select import DictSelectEntity
from custom_components.ecoflow_cloud.sensor import LevelSensorEntity, StatusSensorEntity, WattsSensorEntity
from custom_components.ecoflow_cloud.switch import EnabledEntity


class Stream5000(BaseDevice):
    """The STREAM 5000 series using EcoFlow's public API."""

    def _command(self, params: dict[str, Any]) -> dict[str, Any]:
        """Build the documented BKW3 JSON set envelope."""
        return {
            "sn": self.device_info.sn,
            "cmdId": 38,
            "cmdFunc": 254,
            "dirDest": 1,
            "dirSrc": 1,
            "dest": 2,
            "needAck": True,
            "params": params,
        }

    def normalize_quota(self, quota: dict[str, Any]) -> dict[str, Any]:
        """Normalize HTTP quota values before they enter the data holder."""
        return normalize_quota(quota)

    def _prepare_data(self, raw_data: bytes) -> dict[str, Any]:
        """Normalize nested JSON MQTT data into flat dotted keys."""
        raw = super()._prepare_data(raw_data)
        return {"params": normalize_quota(raw), "raw_data": raw}

    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            LevelSensorEntity(client, self, "sysEnergyStreamReport.bpSoc", const.STREAM_BATTERY_LEVEL),
            WattsSensorEntity(client, self, "sysEnergyStreamReport.pvPwr", const.STREAM_POWER_PV_SUM),
            WattsSensorEntity(client, self, "sysEnergyStreamReport.bpPwr", const.STREAM_POWER_BATTERY),
            WattsSensorEntity(client, self, "sysEnergyStreamReport.loadPwr", const.STREAM_GET_SYS_LOAD),
            WattsSensorEntity(client, self, "sysEnergyStreamReport.gridPwr", const.STREAM_POWER_GRID),
            WattsSensorEntity(client, self, "sysEnergyStreamReport.onGridPwr", const.STREAM_POWER_AC_SYS),
            StatusSensorEntity(client, self),
        ]

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return [
            EnabledEntity(
                client, self, "bpBackupConfig.backupSocOnOff", "Backup Reserve",
                lambda value: self._command({"bpBackupConfig": {"backupSocOnOff": bool(value)}}),
                enableValue=True, disableValue=False,
            ),
            EnabledEntity(
                client, self, "powerParameterConfig.feedToGridLimitOnOff", "Feed-in Limit",
                lambda value: self._command({"powerParameterConfig": {"feedToGridLimitOnOff": bool(value)}}),
                enableValue=True, disableValue=False,
            ),
            EnabledEntity(
                client, self, "devSwitch.acSocketOnoff", "AC Socket",
                lambda value: self._command({"devSwitch": {"acSocketOnoff": bool(value)}}),
                enableValue=True, disableValue=False,
            ),
        ]

    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return [
            MinMaxLevelEntity(
                client, self, "bpBackupConfig.backupSoc", const.BACKUP_RESERVE_LEVEL,
                0, 100,
                lambda value: self._command({
                    "bpBackupConfig": {"backupSocOnOff": True, "backupSoc": int(value)}
                }),
            ),
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return [
            DictSelectEntity(
                client, self, "workMode", "Operating Mode",
                {
                    "Self consumption": "SELF_CONSUMPTION",
                    "AI mode": "AI_MODE",
                    "Timer task": "TIMER_TASK",
                    "Time of use": "POU_MODE",
                    "Emergency stop": "EMERGENCY_STOP",
                },
                lambda value: self._command({"workMode": value}),
            ),
        ]
