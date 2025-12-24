from custom_components.ecoflow_cloud.devices.public.data_bridge import to_plain
import base64
import logging
from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import UnitOfEnergy

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import BaseDevice
from custom_components.ecoflow_cloud.sensor import (
    AmpSensorEntity,
    CyclesSensorEntity,
    EnergySensorEntity,
    LevelSensorEntity,
    MilliVoltSensorEntity,
    MiscSensorEntity,
    SolarAmpSensorEntity,
    SolarPowerSensorEntity,
    StatusSensorEntity,
    TempSensorEntity,
    VoltSensorEntity,
    WattsSensorEntity,
)


class ScaledEnergySensorEntity(EnergySensorEntity):
    def __init__(self, client, device, mqtt_key, title, scale: float, enabled: bool = True, auto_enable: bool = False):
        super().__init__(client, device, mqtt_key, title, enabled, auto_enable)
        self._scale = scale
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    def _update_value(self, val: Any) -> bool:
        try:
            scaled = int(val) * self._scale
        except (TypeError, ValueError):
            return False
        if scaled < 0:
            return False
        return super()._update_value(scaled)


_LOGGER = logging.getLogger(__name__)

# PowerOcean supports up to 9 battery modules
MAX_BATTERY_MODULES = 9
# PowerOcean supports up to 2 MPPT strings
MAX_MPPT_STRINGS = 2
MPPT_HEARTBEAT_INDEX = 0
ENERGY_SCALE = 0.001


class PowerOcean(BaseDevice):
    def __init__(self, device_info, device_data):
        super().__init__(device_info, device_data)
        self._last_battery_heartbeat: list[dict[str, Any]] | None = None
        self._mppt_prefix: str = "96_1"
        self._mppt_string_count: int = 2

    def flat_json(self):
        return True

    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        sensors: list[SensorEntity] = [
            LevelSensorEntity(client, self, "96_8.bpSoc", "bpSoc"),
            VoltSensorEntity(client, self, "96_1.pcsAPhase.vol", "pcsAPhase.vol"),
            AmpSensorEntity(client, self, "96_1.pcsAPhase.amp", "pcsAPhase.amp"),
            WattsSensorEntity(client, self, "96_1.pcsAPhase.actPwr", "pcsAPhase.actPwr"),
            WattsSensorEntity(client, self, "96_1.pcsAPhase.reactPwr", "pcsAPhase.reactPwr"),
            WattsSensorEntity(client, self, "96_1.pcsAPhase.apparentPwr", "pcsAPhase.apparentPwr"),
            VoltSensorEntity(client, self, "96_1.pcsBPhase.vol", "pcsBPhase.vol"),
            AmpSensorEntity(client, self, "96_1.pcsBPhase.amp", "pcsBPhase.amp"),
            WattsSensorEntity(client, self, "96_1.pcsBPhase.actPwr", "pcsBPhase.actPwr"),
            WattsSensorEntity(client, self, "96_1.pcsBPhase.reactPwr", "pcsBPhase.reactPwr"),
            WattsSensorEntity(client, self, "96_1.pcsBPhase.apparentPwr", "pcsBPhase.apparentPwr"),
            VoltSensorEntity(client, self, "96_1.pcsCPhase.vol", "pcsCPhase.vol"),
            AmpSensorEntity(client, self, "96_1.pcsCPhase.amp", "pcsCPhase.amp"),
            WattsSensorEntity(client, self, "96_1.pcsCPhase.actPwr", "pcsCPhase.actPwr"),
            WattsSensorEntity(client, self, "96_1.pcsCPhase.reactPwr", "pcsCPhase.reactPwr"),
            WattsSensorEntity(client, self, "96_1.pcsCPhase.apparentPwr", "pcsCPhase.apparentPwr"),
        ]

        mppt_prefix, string_count = self._determine_mppt_metadata()
        _LOGGER.debug("Configuring %s MPPT strings for prefix %s", string_count, mppt_prefix)
        for index in range(string_count):
            sensors.extend(self._create_mppt_string_sensors(client, mppt_prefix, index))

        battery_count = self._determine_battery_count()
        _LOGGER.debug("Detected %s battery modules", battery_count)
        for index in range(1, battery_count + 1):
            sensors.extend(self._create_battery_sensors(client, index))

        sensors.append(StatusSensorEntity(client, self))
        return sensors

    def _determine_mppt_metadata(self) -> tuple[str, int]:
        data_holder = getattr(self, "data", None)
        prefix = self._mppt_prefix
        count = self._mppt_string_count

        if data_holder:
            holder_params = getattr(data_holder, "params", {})
            for key in holder_params:
                if ".mpptHeartBeat[" in key and ".mpptPv[" in key:
                    base, _ = key.split(".mpptHeartBeat", 1)
                    prefix = base
                    pv_part = key.split(".mpptPv[", 1)[1]
                    pv_index_str = pv_part.split("]", 1)[0]
                    if pv_index_str.isdigit():
                        count = max(count, int(pv_index_str) + 1)
                        break

        count = max(1, min(count, MAX_MPPT_STRINGS))

        return prefix, count

    def _determine_battery_count(self) -> int:
        data_holder = getattr(self, "data", None)
        if data_holder:
            holder_params = getattr(data_holder, "params", {})
            battery_indices = self._extract_battery_indices(holder_params)
            if battery_indices:
                return min(max(battery_indices), MAX_BATTERY_MODULES)
            alive_candidates = self._extract_alive_counts(holder_params)
            if alive_candidates:
                return min(max(alive_candidates), MAX_BATTERY_MODULES)
        heartbeat = self._last_battery_heartbeat
        if heartbeat:
            max_index = 0
            for entry in heartbeat:
                if not isinstance(entry, dict):
                    continue
                dsrc = entry.get("bpDsrc")
                if isinstance(dsrc, int):
                    idx = dsrc
                elif isinstance(dsrc, str) and dsrc.isdigit():
                    idx = int(dsrc)
                else:
                    continue
                max_index = max(max_index, idx)
            if max_index:
                return min(max_index, MAX_BATTERY_MODULES)
        return 0

    def _create_mppt_string_sensors(self, client: EcoflowApiClient, prefix: str, index: int) -> list[SensorEntity]:
        name_prefix = f"mpptPv{index + 1}"
        base_path = f"{prefix}.mpptHeartBeat[{MPPT_HEARTBEAT_INDEX}].mpptPv[{index}]"
        return [
            SolarPowerSensorEntity(client, self, f"{base_path}.pwr", f"{name_prefix}.pwr"),
            SolarAmpSensorEntity(client, self, f"{base_path}.amp", f"{name_prefix}.amp"),
            VoltSensorEntity(client, self, f"{base_path}.vol", f"{name_prefix}.vol"),
        ]

    def _create_battery_sensors(self, client: EcoflowApiClient, index: int) -> list[SensorEntity]:
        prefix = f"bp{index}"

        return [
            LevelSensorEntity(client, self, f"{prefix}.bpSoc", f"{prefix}Soc"),
            LevelSensorEntity(client, self, f"{prefix}.bpSoh", f"{prefix}Soh"),
            WattsSensorEntity(client, self, f"{prefix}.bpPwr", f"{prefix}Pwr"),
            AmpSensorEntity(client, self, f"{prefix}.bpAmp", f"{prefix}Amp"),
            VoltSensorEntity(client, self, f"{prefix}.bpVol", f"{prefix}Vol"),
            MilliVoltSensorEntity(client, self, f"{prefix}.bpCellMaxVol", f"{prefix}CellMaxVol"),
            MilliVoltSensorEntity(client, self, f"{prefix}.bpCellMinVol", f"{prefix}CellMinVol"),
            VoltSensorEntity(client, self, f"{prefix}.bpBusVol", f"{prefix}BusVol"),
            TempSensorEntity(client, self, f"{prefix}.bpHvMosTemp", f"{prefix}HvMosTemp"),
            TempSensorEntity(client, self, f"{prefix}.bpLvMosTemp", f"{prefix}LvMosTemp"),
            TempSensorEntity(client, self, f"{prefix}.bpEnvTemp", f"{prefix}EnvTemp"),
            TempSensorEntity(client, self, f"{prefix}.bpHtsTemp", f"{prefix}HtsTemp"),
            TempSensorEntity(client, self, f"{prefix}.bpBusPosTemp", f"{prefix}BusPosTemp"),
            TempSensorEntity(client, self, f"{prefix}.bpBusNegTemp", f"{prefix}BusNegTemp"),
            TempSensorEntity(client, self, f"{prefix}.bpPtcTemp", f"{prefix}PtcTemp"),
            TempSensorEntity(client, self, f"{prefix}.bpPtcTemp2", f"{prefix}PtcTemp2"),
            TempSensorEntity(client, self, f"{prefix}.bpMaxCellTemp", f"{prefix}MaxCellTemp"),
            TempSensorEntity(client, self, f"{prefix}.bpMinCellTemp", f"{prefix}MinCellTemp"),
            TempSensorEntity(client, self, f"{prefix}.bpMaxMosTemp", f"{prefix}MaxMosTemp"),
            TempSensorEntity(client, self, f"{prefix}.bpMinMosTemp", f"{prefix}MinMosTemp"),
            CyclesSensorEntity(client, self, f"{prefix}.bpCycles", f"{prefix}Cycles"),
            EnergySensorEntity(client, self, f"{prefix}.bpRemainWatth", f"{prefix}RemainWatth"),
            ScaledEnergySensorEntity(
                client,
                self,
                f"{prefix}.bpAccuChgEnergy",
                f"{prefix}AccuChgEnergy",
                ENERGY_SCALE,
            ),
            ScaledEnergySensorEntity(
                client,
                self,
                f"{prefix}.bpAccuDsgEnergy",
                f"{prefix}AccuDsgEnergy",
                ENERGY_SCALE,
            ),
            MiscSensorEntity(client, self, f"{prefix}.bpSnDecoded", f"{prefix}Sn"),
            MiscSensorEntity(client, self, f"{prefix}.bmsChgDsgSta", f"{prefix}bmsChgDsgSta"),
            MiscSensorEntity(client, self, f"{prefix}.dabModSta", f"{prefix}dabModSta"),
            MiscSensorEntity(client, self, f"{prefix}.bpSysState", f"{prefix}SysState"),
            MiscSensorEntity(client, self, f"{prefix}.bpRunSta", f"{prefix}RunSta"),
        ]

    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return []

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return []

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return []

    def _prepare_data(self, raw_data) -> dict[str, Any]:
        self._update_mppt_metadata(raw_data)
        res = super()._prepare_data(raw_data)
        _LOGGER.debug("Processing payload: %s", raw_data)
        res = to_plain(res)
        params = res.get("params")
        if isinstance(params, dict):
            self._inject_battery_params(params, res.get("raw_data"))
            flattened: dict[str, Any] = {}
            for key, value in list(params.items()):
                self._flatten_param_branch(key, value, flattened)
            params.update(flattened)
        return res

    def _status_sensor(self, client: EcoflowApiClient) -> StatusSensorEntity:
        return StatusSensorEntity(client, self)

    def _flatten_param_branch(self, prefix: str, value: Any, target: dict[str, Any]) -> None:
        if isinstance(value, dict):
            for child_key, child_value in value.items():
                next_key = f"{prefix}.{child_key}"
                target[next_key] = child_value
                self._flatten_param_branch(next_key, child_value, target)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                next_key = f"{prefix}[{index}]"
                target[next_key] = item
                self._flatten_param_branch(next_key, item, target)

    def _inject_battery_params(self, params: dict[str, Any], raw_data: Any) -> None:
        if not isinstance(raw_data, dict):
            return

        # Battery heartbeat messages carry packs; create per-pack aliases based on bpDsrc.
        heartbeat = None
        if isinstance(raw_data.get("param"), dict):
            heartbeat = raw_data.get("param", {}).get("bpHeartBeat")
        if heartbeat is None and isinstance(raw_data.get("params"), dict):
            heartbeat = raw_data.get("params", {}).get("bpHeartBeat")

        self._last_battery_heartbeat = heartbeat if isinstance(heartbeat, list) else None
        if not isinstance(heartbeat, list):
            return

        for entry in heartbeat:
            if not isinstance(entry, dict):
                continue
            dsrc_value = entry.get("bpDsrc")
            if isinstance(dsrc_value, int):
                dsrc = dsrc_value
            elif isinstance(dsrc_value, str) and dsrc_value.isdigit():
                dsrc = int(dsrc_value)
            else:
                continue
            if dsrc < 1:
                continue
            prefix = f"bp{dsrc}"
            for field, value in entry.items():
                params[f"{prefix}.{field}"] = value

            bp_sn = entry.get("bpSn")
            if isinstance(bp_sn, str):
                try:
                    decoded_sn = base64.b64decode(bp_sn).decode("utf-8")
                except Exception as e:  # noqa: BLE001
                    _LOGGER.debug("Failed to decode battery serial number: %s", e)
                    decoded_sn = None
                if decoded_sn:
                    params[f"{prefix}.bpSnDecoded"] = decoded_sn

    def _extract_battery_indices(self, params: dict[str, Any]) -> set[int]:
        indices: set[int] = set()
        for key in params:
            if not key.startswith("bp"):
                continue
            prefix = key.split(".", 1)[0]
            suffix = prefix[2:]
            if suffix.isdigit():
                indices.add(int(suffix))
        return indices

    @staticmethod
    def _extract_alive_counts(params: dict[str, Any]) -> list[int]:
        values: list[int] = []
        for key, value in params.items():
            if key.endswith("emsBpAliveNum"):
                try:
                    parsed = int(value)
                except (TypeError, ValueError):
                    parsed = 0
                if parsed > 0:
                    values.append(parsed)
        return values

    def _update_mppt_metadata(self, raw_data: Any) -> None:
        if not isinstance(raw_data, dict):
            return

        mppt_list = None
        for container in (raw_data.get("params"), raw_data.get("param")):
            if isinstance(container, dict):
                candidate = container.get("mpptHeartBeat")
                if isinstance(candidate, list):
                    mppt_list = candidate
                    break

        if mppt_list is None:
            return

        cmd_func = raw_data.get("cmdFunc")
        cmd_id = raw_data.get("cmdId")
        if isinstance(cmd_func, int) and isinstance(cmd_id, int):
            self._mppt_prefix = f"{cmd_func}_{cmd_id}"

        max_strings = 0
        for entry in mppt_list:
            if not isinstance(entry, dict):
                continue
            pv_list = entry.get("mpptPv")
            if isinstance(pv_list, list):
                max_strings = max(max_strings, len(pv_list))

        if max_strings:
            self._mppt_string_count = min(max(self._mppt_string_count, max_strings), MAX_MPPT_STRINGS)
