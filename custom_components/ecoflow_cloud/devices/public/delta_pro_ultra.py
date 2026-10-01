# import logging
# _LOGGER = logging.getLogger(__name__)

import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import UnitOfElectricCurrent, UnitOfElectricPotential

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.device_data import DeviceData
from custom_components.ecoflow_cloud.devices import BaseDevice, EcoflowDeviceInfo, const
from custom_components.ecoflow_cloud.devices.data_holder import PreparedData
from custom_components.ecoflow_cloud.devices.public import data_bridge
from custom_components.ecoflow_cloud.entities import BaseSensorEntity
from custom_components.ecoflow_cloud.number import ChargingPowerEntity, MaxBatteryLevelEntity, MinBatteryLevelEntity
from custom_components.ecoflow_cloud.sensor import (
    AmpSensorEntity,
    CapacitySensorEntity,
    CyclesSensorEntity,
    FrequencySensorEntity,
    InWattsSensorEntity,
    LevelSensorEntity,
    MilliampSensorEntity,
    MilliVoltSensorEntity,
    MiscSensorEntity,
    OutWattsSensorEntity,
    QuotaScheduledStatusSensorEntity,
    RemainSensorEntity,
    StateOfHealthSensorEntity,
    TempSensorEntity,
    VoltSensorEntity,
)
from custom_components.ecoflow_cloud.switch import EnabledEntity

# One DELTA Pro Ultra inverter takes up to 5 batteries.
MAX_BATTERIES = 5
_BMS = "hs_yj751_bms_slave_addr"
_BATTERY_COUNT = "hs_yj751_pd_appshow_addr.bpNum"
_POSITION = "position"

# Besides the BMS records returned by quota/all every 5 minutes (hs_yj751_bms_slave_addr.<slot>.*),
# two MQTT messages carry per-battery data:
# - each battery's BMS heartbeat, one battery at a time, every ~3 minutes per battery. It arrives as
#   hs_yj751_bms_slave_addr_<n>.*, where <n> is not the slot; the record names its battery by packSn and
#   has no timestamp, current, pack temperature, probe lists or cycle count.
# - the inverter's per-slot summary, every ~60 seconds: level, signed power and temperature for each
#   slot (bpNo), as hs_yj751_pd_bp_addr.bpInfo.<i>.*
# The quota/all records are the cloud's copy of the latest heartbeats, so they are already up to
# ~3 minutes old when polled. For each value the most recently reported one is used.
_LIVE_BMS_KEY = re.compile(rf"^{_BMS}_(\d+)\.(.+)$")
_BP_INFO = "hs_yj751_pd_bp_addr.bpInfo"
_BP_INFO_KEY = re.compile(rf"^{re.escape(_BP_INFO)}\.(\d+)\.(.+)$")

# BMS field -> (per-slot summary field, conversion to the BMS field's meaning)
_SLOT_SUMMARY_FIELDS: dict[str, tuple[str, Callable[[float], Any]]] = {
    "soc": ("bpSoc", lambda v: v),
    "temp": ("bpTemp", lambda v: v),
    # bpPwr is signed (positive while the battery charges, negative while it discharges) and arrives
    # as a float (-165.0); the BMS reports whole watts, so round to match.
    "inputWatts": ("bpPwr", lambda v: max(round(v), 0)),
    "outputWatts": ("bpPwr", lambda v: max(-round(v), 0)),
}

# Temperature probe lists in the BMS record, with the count to assume if a record lacks the list.
_TEMP_PROBES: tuple[tuple[str, str, int], ...] = (
    ("cellTemp", "Cell Temperature", 7),
    ("mosTemp", "MOSFET Temperature", 4),
    ("ptcTemp", "Heater Temperature", 4),
)


def _battery_slot(params: dict[str, Any], serial: str) -> int | None:
    """Return the BMS slot (1-based position in the stack) currently reporting this battery serial.

    Only slots up to the installed battery count are considered: the cloud can keep returning a
    stale BMS record for a slot that no longer holds a battery, sometimes repeating a serial that
    has since moved. If a serial still appears twice, the most recent record wins.
    """
    count = params.get(_BATTERY_COUNT)
    last = count if isinstance(count, int) and count > 0 else MAX_BATTERIES
    slot: int | None = None
    newest = -1
    for n in range(1, last + 1):
        if params.get(f"{_BMS}.{n}.packSn") != serial:
            continue
        reported = params.get(f"{_BMS}.{n}.unixTime")
        reported = reported if isinstance(reported, int | float) else 0
        if reported > newest:
            slot, newest = n, reported
    return slot


@dataclass
class _Reading:
    value: Any
    time: float  # seconds since the epoch


class _LiveBatteryReadings:
    """Per-battery values from the inverter's MQTT messages, with the time each one arrived."""

    def __init__(self) -> None:
        self.by_serial: dict[str, dict[str, _Reading]] = {}
        self.by_slot: dict[int, dict[str, _Reading]] = {}

    def observe(self, message: dict[str, Any], params: dict[str, Any], now: float) -> None:
        """Record the per-battery values in one flattened MQTT message."""
        heartbeats: dict[str, dict[str, Any]] = {}
        for key, value in message.items():
            if match := _LIVE_BMS_KEY.match(key):
                heartbeats.setdefault(match.group(1), {})[match.group(2)] = value
            elif match := _BP_INFO_KEY.match(key):
                index = int(match.group(1))
                slot = message.get(f"{_BP_INFO}.{index}.bpNo", params.get(f"{_BP_INFO}.{index}.bpNo"))
                if not isinstance(slot, int):
                    slot = index + 1  # bpInfo is ordered by slot
                self.by_slot.setdefault(slot, {})[match.group(2)] = _Reading(value, now)
        for fields in heartbeats.values():
            serial = fields.get("packSn")
            # A heartbeat that doesn't name its battery can't be attributed to one.
            if isinstance(serial, str) and serial:
                readings = self.by_serial.setdefault(serial, {})
                for field, value in fields.items():
                    readings[field] = _Reading(value, now)


class _BatterySensorEntity(BaseSensorEntity):
    """Per-battery sensor identified by the battery's serial number rather than its slot.

    Each update looks up the slot that currently holds the serial, so history follows the
    battery when batteries are swapped between positions in the stack.
    """

    # Keep the last reading when the device goes offline instead of writing a default value.
    _attr_default_value: Any = None

    def __init__(
        self,
        client: EcoflowApiClient,
        device: "DeltaProUltra",
        serial: str,
        field: str,
        title: str,
        enabled: bool = True,
        diagnostic: bool | None = None,
        index: int | None = None,
    ):
        key = field if index is None else f"{field}.{index}"
        super().__init__(
            client, device, f"{_BMS}.{serial}.{key}", f"Battery {serial} {title}", enabled, False, diagnostic
        )
        self._dpu = device
        self._serial = serial
        self._field = field
        self._index = index

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self._updated(self._device.data.params)

    def _updated(self, data: dict[str, Any]):
        slot = _battery_slot(data, self._serial)
        if slot is None:
            # battery no longer reported by this inverter
            if self._attr_available:
                self._attr_available = False
                self.schedule_update_ha_state()
            return
        if self._field == _POSITION:
            value: Any = slot
        else:
            value = self._dpu.battery_value(data, self._serial, slot, self._field, self._index)
        if value is None:
            return
        became_available = not self._attr_available
        self._attr_available = True
        if self._update_value(value) or became_available:
            self.schedule_update_ha_state()


class _BatteryPositionSensorEntity(_BatterySensorEntity, MiscSensorEntity):
    _attr_icon = "mdi:numeric"


class _BatteryLevelSensorEntity(_BatterySensorEntity, LevelSensorEntity):
    pass


class _BatteryChargePowerSensorEntity(_BatterySensorEntity, InWattsSensorEntity):
    # Power flowing into this battery. It can come from the grid or solar, or from the other
    # batteries in the stack when the inverter evens out their levels, so use a battery icon
    # rather than the grid icon InWattsSensorEntity carries.
    _attr_icon = "mdi:battery-arrow-up"


class _BatteryDischargePowerSensorEntity(_BatterySensorEntity, OutWattsSensorEntity):
    # Power flowing out of this battery, measured on the battery (DC) side of the inverter.
    _attr_icon = "mdi:battery-arrow-down"


class _BatteryCurrentSensorEntity(_BatterySensorEntity, MilliampSensorEntity):
    # Reported in mA (negative while discharging); battery voltage is ~105 V, so amps with
    # two decimals reads more naturally.
    _attr_suggested_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_suggested_display_precision = 2


class _BatteryTempSensorEntity(_BatterySensorEntity, TempSensorEntity):
    pass


class _BatteryStateOfHealthSensorEntity(_BatterySensorEntity, StateOfHealthSensorEntity):
    # actSoh is reported with ~5 decimals (e.g. 98.71886)
    _attr_suggested_display_precision = 1


class _BatteryCyclesSensorEntity(_BatterySensorEntity, CyclesSensorEntity):
    pass


class _BatteryMilliVoltSensorEntity(_BatterySensorEntity, MilliVoltSensorEntity):
    pass


class _BatteryCellVoltageDifferenceSensorEntity(_BatterySensorEntity, MilliVoltSensorEntity):
    # Spread between the highest and lowest cell is a few mV, so keep it in mV
    # rather than the V that MilliVoltSensorEntity suggests.
    _attr_suggested_unit_of_measurement = UnitOfElectricPotential.MILLIVOLT


class _BatteryCapacitySensorEntity(_BatterySensorEntity, CapacitySensorEntity):
    pass


class DeltaProUltra(BaseDevice):
    def __init__(self, device_info: EcoflowDeviceInfo, device_data: DeviceData) -> None:
        super().__init__(device_info, device_data)
        self._live_batteries = _LiveBatteryReadings()

    def _prepare_data_data_topic(self, raw_data: bytes) -> PreparedData:
        prepared = super()._prepare_data_data_topic(raw_data)
        message = prepared.params.get("params") if prepared.params is not None else None
        if isinstance(message, dict):
            self._live_batteries.observe(message, self.data.params, time.time())
        return prepared

    def battery_value(
        self, params: dict[str, Any], serial: str, slot: int, field: str, index: int | None = None
    ) -> Any:
        """Return the most recently reported value of a BMS field for this battery.

        Sources: the quota/all BMS record for the battery's slot (timestamped by the battery), the
        battery's last MQTT heartbeat, and, for level, power and temperature, the inverter's
        per-slot summary (both timestamped on arrival).
        """
        candidates: list[tuple[float, Any]] = []
        polled = params.get(f"{_BMS}.{slot}.{field}")
        if polled is not None:
            reported = params.get(f"{_BMS}.{slot}.unixTime")
            candidates.append((reported if isinstance(reported, int | float) else 0, polled))
        heartbeat = self._live_batteries.by_serial.get(serial, {}).get(field)
        if heartbeat is not None:
            candidates.append((heartbeat.time, heartbeat.value))
        if field in _SLOT_SUMMARY_FIELDS:
            summary_field, convert = _SLOT_SUMMARY_FIELDS[field]
            summary = self._live_batteries.by_slot.get(slot, {}).get(summary_field)
            if summary is not None and isinstance(summary.value, int | float):
                candidates.append((summary.time, convert(summary.value)))
        if not candidates:
            return None
        value = max(candidates, key=lambda candidate: candidate[0])[1]
        if index is None:
            return value
        return value[index] if isinstance(value, list) and index < len(value) else None

    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            *self._base_sensors(client),
            *self._battery_sensors(client),
        ]

    def _installed_battery_serials(self) -> list[str]:
        params = self.data.params
        count = params.get(_BATTERY_COUNT)
        last = count if isinstance(count, int) and count > 0 else MAX_BATTERIES
        serials: list[str] = []
        for n in range(1, last + 1):
            serial = params.get(f"{_BMS}.{n}.packSn")
            if isinstance(serial, str) and serial and serial not in serials:
                serials.append(serial)
        return serials

    def _probe_count(self, serial: str, field: str, default: int) -> int:
        slot = _battery_slot(self.data.params, serial)
        probes = self.data.params.get(f"{_BMS}.{slot}.{field}") if slot is not None else None
        return len(probes) if isinstance(probes, list) and probes else default

    def _battery_sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        # One set of sensors per installed battery, keyed by serial number. A battery added
        # later gets its sensors when the integration is reloaded.
        sensors: list[SensorEntity] = []
        for sn in self._installed_battery_serials():
            sensors += [
                _BatteryPositionSensorEntity(client, self, sn, _POSITION, "Position"),
                _BatteryLevelSensorEntity(client, self, sn, "soc", "Level"),
                _BatteryChargePowerSensorEntity(client, self, sn, "inputWatts", "Charge Power"),
                _BatteryDischargePowerSensorEntity(client, self, sn, "outputWatts", "Discharge Power"),
                # mA, negative while discharging
                _BatteryCurrentSensorEntity(client, self, sn, "amp", "Current"),
                _BatteryTempSensorEntity(client, self, sn, "temp", "Temperature", diagnostic=False),
                _BatteryStateOfHealthSensorEntity(client, self, sn, "actSoh", "State of Health"),
                _BatteryCyclesSensorEntity(client, self, sn, "cycles", "Cycles"),
                _BatteryCellVoltageDifferenceSensorEntity(
                    client, self, sn, "maxVolDiff", "Cell Voltage Difference", diagnostic=True
                ),
                _BatteryMilliVoltSensorEntity(client, self, sn, "minCellVol", "Min Cell Volts", False),
                _BatteryMilliVoltSensorEntity(client, self, sn, "maxCellVol", "Max Cell Volts", False),
                _BatteryCapacitySensorEntity(client, self, sn, "fullCap", "Full Capacity", False),
                _BatteryCapacitySensorEntity(client, self, sn, "remainCap", "Remaining Capacity", False),
                # Every temperature probe the BMS reports, as diagnostics
                _BatteryTempSensorEntity(client, self, sn, "maxCellTemp", "Max Cell Temperature", diagnostic=True),
                _BatteryTempSensorEntity(client, self, sn, "minCellTemp", "Min Cell Temperature", diagnostic=True),
                _BatteryTempSensorEntity(client, self, sn, "hwBoardTemp", "Board Temperature", diagnostic=True),
                _BatteryTempSensorEntity(client, self, sn, "curResTemp", "Shunt Temperature", diagnostic=True),
            ]
            for field, title, default_count in _TEMP_PROBES:
                sensors += [
                    _BatteryTempSensorEntity(client, self, sn, field, f"{title} {i + 1}", diagnostic=True, index=i)
                    for i in range(self._probe_count(sn, field, default_count))
                ]
        return sensors

    def _base_sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            QuotaScheduledStatusSensorEntity(client, self, 300),  # required to call quota/all every 5 minutes
            RemainSensorEntity(client, self, "hs_yj751_pd_appshow_addr.remainTime", const.REMAINING_TIME),
            LevelSensorEntity(client, self, "hs_yj751_pd_appshow_addr.soc", const.BATTERY_LEVEL_SOC),
            MiscSensorEntity(client, self, "hs_yj751_pd_appshow_addr.bpNum", const.BATTERY_COUNT),
            MiscSensorEntity(client, self, "hs_yj751_pd_appshow_addr.fullCombo", const.WIRELESS_4G_DATA_MAX, False),
            MiscSensorEntity(
                client, self, "hs_yj751_pd_appshow_addr.remainCombo", const.WIRELESS_4G_DATA_REMAINING, False
            ),
            MiscSensorEntity(
                client, self, "hs_yj751_pd_appshow_addr.wireless4gCon", const.WIRELESS_4G_REGISTERED, False
            ),
            MiscSensorEntity(
                client, self, "hs_yj751_pd_appshow_addr.wirlesss4gErrCode", const.WIRELESS_4G_ERROR_CODE, False
            ),
            MiscSensorEntity(client, self, "hs_yj751_pd_appshow_addr.simIccid", const.WIRELESS_4G_SIM_ID, False),
            MiscSensorEntity(
                client, self, "hs_yj751_pd_appshow_addr.wireless4GSta", const.INTERNET_CONNECTION_TYPE, False
            ),
            MiscSensorEntity(client, self, "hs_yj751_pd_appshow_addr.sysErrCode", const.ERROR_CODE),
            InWattsSensorEntity(
                client, self, "hs_yj751_pd_appshow_addr.wattsInSum", const.TOTAL_IN_POWER
            ).with_energy(),
            OutWattsSensorEntity(
                client, self, "hs_yj751_pd_appshow_addr.wattsOutSum", const.TOTAL_OUT_POWER
            ).with_energy(),
            InWattsSensorEntity(
                client, self, "hs_yj751_pd_appshow_addr.inAc5p8Pwr", const.PIO_PORT_IN_POWER
            ).with_energy(),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.inAc5p8Amp", const.PIO_PORT_IN_CURRENT, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.inAc5p8Vol", const.PIO_PORT_IN_VOLTAGE, False),
            OutWattsSensorEntity(
                client, self, "hs_yj751_pd_appshow_addr.outAc5p8Pwr", const.PIO_PORT_OUT_POWER
            ).with_energy(),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAc5p8Amp", const.PIO_PORT_OUT_CURRENT, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAc5p8Vol", const.PIO_PORT_OUT_VOLTAGE, False),
            MiscSensorEntity(client, self, "hs_yj751_pd_appshow_addr.access5p8InType", const.PIO_PORT_INPUT_TYPE),
            InWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.inAcC20Pwr", const.AC_IN_POWER).with_energy(
                False
            ),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.inAcC20Amp", const.AC_IN_CURRENT, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.inAcC20Vol", const.AC_IN_VOLT, False),
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outUsb1Pwr", const.USB_1_OUT_POWER)
            .with_energy(False)
            .with_icon("mdi:usb-port"),
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outUsb2Pwr", const.USB_2_OUT_POWER)
            .with_energy(False)
            .with_icon("mdi:usb-port"),
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outTypec1Pwr", const.TYPEC_1_OUT_POWER)
            .with_energy(False)
            .with_icon("mdi:usb-c-port"),
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outTypec2Pwr", const.TYPEC_2_OUT_POWER)
            .with_energy(False)
            .with_icon("mdi:usb-c-port"),
            InWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.inHvMpptPwr", const.SOLAR_1_IN_POWER)
            .with_energy()
            .with_icon("mdi:solar-power"),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.inHvMpptAmp", const.SOLAR_1_IN_AMPS, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.inHvMpptVol", const.SOLAR_1_IN_VOLTS, False),
            InWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.inLvMpptPwr", const.SOLAR_2_IN_POWER)
            .with_energy()
            .with_icon("mdi:solar-power"),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.inLvMpptAmp", const.SOLAR_2_IN_AMPS, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.inLvMpptVol", const.SOLAR_2_IN_VOLTS, False),
            # 20A 120V Backup UPS
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outAcL11Pwr", const.AC_N_OUT_POWER % 1)
            .with_energy(False)
            .with_icon("mdi:power-socket-us"),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL11Amp", const.AC_N_OUT_CURRENT % 1, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL11Vol", const.AC_N_OUT_VOLTAGE % 1, False),
            FrequencySensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL11Pf", const.AC_N_OUT_FREQ % 1, False),
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outAcL12Pwr", const.AC_N_OUT_POWER % 2)
            .with_energy(False)
            .with_icon("mdi:power-socket-us"),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL12Amp", const.AC_N_OUT_CURRENT % 2, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL12Vol", const.AC_N_OUT_VOLTAGE % 2, False),
            FrequencySensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL12Pf", const.AC_N_OUT_FREQ % 2, False),
            # 20A 120V Online UPS
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outAcL21Pwr", const.AC_N_OUT_POWER % 3)
            .with_energy(False)
            .with_icon("mdi:power-socket-us"),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL21Amp", const.AC_N_OUT_CURRENT % 3, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL21Vol", const.AC_N_OUT_VOLTAGE % 3, False),
            FrequencySensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL21Pf", const.AC_N_OUT_FREQ % 3, False),
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outAcL22Pwr", const.AC_N_OUT_POWER % 4)
            .with_energy(False)
            .with_icon("mdi:power-socket-us"),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL22Amp", const.AC_N_OUT_CURRENT % 4, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL22Vol", const.AC_N_OUT_VOLTAGE % 4, False),
            FrequencySensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL22Pf", const.AC_N_OUT_FREQ % 4, False),
            # 30A 120V
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outAcL14Pwr", const.AC_N_OUT_POWER % 5)
            .with_energy(False)
            .with_icon("mdi:power-socket-au"),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL14Amp", const.AC_N_OUT_CURRENT % 5, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL14Vol", const.AC_N_OUT_VOLTAGE % 5, False),
            FrequencySensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcL14Pf", const.AC_N_OUT_FREQ % 5, False),
            # 30A 120/240V
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outAcTtPwr", const.AC_N_OUT_POWER % 6)
            .with_energy(False)
            .with_icon("mdi:power-socket-de"),
            AmpSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcTtAmp", const.AC_N_OUT_CURRENT % 6, False),
            VoltSensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcTtVol", const.AC_N_OUT_VOLTAGE % 6, False),
            FrequencySensorEntity(client, self, "hs_yj751_pd_backend_addr.outAcTtPf", const.AC_N_OUT_FREQ % 6, False),
            OutWattsSensorEntity(client, self, "hs_yj751_pd_appshow_addr.outAdsPwr", const.DC_ANDERSON_OUT_POWER)
            .with_energy(False)
            .with_icon("mdi:connection"),
        ]

    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return [
            MinBatteryLevelEntity(
                client,
                self,
                "hs_yj751_pd_app_set_info_addr.dsgMinSoc",
                const.MIN_DISCHARGE_LEVEL,
                0,
                30,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "YJ751_PD_DSG_SOC_MIN_SET",
                    "params": {"minDsgSoc": value},
                },
            ),
            MaxBatteryLevelEntity(
                client,
                self,
                "hs_yj751_pd_app_set_info_addr.chgMaxSoc",
                const.MAX_CHARGE_LEVEL,
                50,
                100,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "YJ751_PD_CHG_SOC_MAX_SET",
                    "params": {"maxChgSoc": value},
                },
            ),
            ChargingPowerEntity(
                client,
                self,
                "hs_yj751_pd_app_set_info_addr.chgC20SetWatts",
                const.AC_CHARGING_POWER,
                600,
                1800,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "YJ751_PD_AC_CHG_SET",
                    "params": {"chgC20Watts": value},
                },
            ).with_icon("mdi:power-plug"),
            ChargingPowerEntity(
                client,
                self,
                "hs_yj751_pd_app_set_info_addr.chg5p8SetWatts",
                const.PIO_PORT_CHARGING_POWER,
                600,
                7200,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "YJ751_PD_AC_CHG_SET",
                    "params": {"chg5p8Watts": value},
                },
            ),
        ]

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return [
            EnabledEntity(
                client,
                self,
                "hs_yj751_pd_appshow_addr.wireless4gOn",
                const.WIRELESS_4G_ENABLED,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "YJ751_PD_4G_SWITCH_SET",
                    "params": {"en4GOpen": value},
                },
            ).with_icon("mdi:signal-4g"),
            EnabledEntity(
                client,
                self,
                "hs_yj751_pd_app_set_info_addr.bmsModeSet",
                const.BATTERY_AUTO_HEATING_ENABLED,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "YJ751_PD_BP_HEAT_SET",
                    "params": {"enBpHeat": value},
                },
            ).with_icon("mdi:thermometer-check"),
            EnabledEntity(
                client,
                self,
                "hs_yj751_pd_appshow_addr.showFlag.6",
                const.DC_MODE,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "YJ751_PD_DC_SWITCH_SET",
                    "params": {"enable": value},
                },
            ).with_icon("mdi:current-dc"),
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return []

    def _prepare_data(self, raw_data) -> dict[str, Any]:
        res = super()._prepare_data(raw_data)
        res = self.to_plain_nested_addr_prefix(res)

        # split showFlag into separate keys for each bit using documentation's bit ordering
        if "hs_yj751_pd_appshow_addr.showFlag" in res["params"] and isinstance(
            res["params"]["hs_yj751_pd_appshow_addr.showFlag"], int
        ):
            documentation_bit_order = ((res["params"]["hs_yj751_pd_appshow_addr.showFlag"] >> 4) & 3855) | (
                res["params"]["hs_yj751_pd_appshow_addr.showFlag"] << 4
            )
            for x in range(16):
                res["params"][f"hs_yj751_pd_appshow_addr.showFlag.{x + 1}"] = (documentation_bit_order >> x) & 1
        return res

    def to_plain_nested_addr_prefix(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        if "typeCode" in raw_data:
            prefix = data_bridge.status_to_plain.get(raw_data["typeCode"], "unknown_" + raw_data["typeCode"])
        elif "addr" in raw_data:
            prefix = raw_data["addr"]
        elif "cmdFunc" in raw_data and "cmdId" in raw_data:
            prefix = f"{raw_data['cmdFunc']}_{raw_data['cmdId']}"
        else:
            # Used for quota/all responses
            return raw_data

        new_params: dict[str, Any] = {}
        if "params" in raw_data:
            self.nested_to_top_level(new_params, prefix, raw_data["params"])
        if "param" in raw_data:
            self.nested_to_top_level(new_params, prefix, raw_data["param"])

        result: dict[str, Any] = {"params": new_params}
        for k, v in raw_data.items():
            if k != "param" and k != "params":
                result[k] = v
        return result

    def nested_to_top_level(self, dest: dict[str, Any], k: str, v: Any):
        """Converts each nested dict/list value to a top-level key of
        the prefix followed by dot notation path to the value.
        ex.
            {"a": [123, {"b": 456}]} -> {"a.0": 123, "a.1.b": 456}
        """
        if isinstance(v, dict):
            for kk, vv in v.items():
                self.nested_to_top_level(dest, f"{k}.{kk}", vv)
        elif isinstance(v, list):
            for ii, vv in enumerate(v):
                self.nested_to_top_level(dest, f"{k}.{ii}", vv)
        else:
            dest[k] = v
