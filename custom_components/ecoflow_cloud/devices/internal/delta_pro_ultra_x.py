import logging
from typing import Any, ClassVar, override

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import const
from custom_components.ecoflow_cloud.devices.internal.delta_pro_3 import DeltaPro3
from custom_components.ecoflow_cloud.devices.internal.proto import (
    ef_delta_pro_ultra_x_pb2 as dpux,
)
from custom_components.ecoflow_cloud.sensor import (
    AmpSensorEntity,
    BatteryLimitSensorEntity,
    FrequencySensorEntity,
    InRawVoltSolarSensorEntity,
    InWattsSensorEntity,
    LevelSensorEntity,
    MiscSensorEntity,
    OutWattsSensorEntity,
    QuotaStatusSensorEntity,
    RemainSensorEntity,
    StateOfHealthSensorEntity,
    TempSensorEntity,
    VoltSensorEntity,
)

_LOGGER = logging.getLogger(__name__)

# The DPU X supports up to 10 external battery packs.
MAX_PACKS = 10


class _PhaseWattsSensorEntity(InWattsSensorEntity):
    """Reports phase power (W) by multiplying a voltage key with an amperage key."""

    def __init__(
        self,
        client: EcoflowApiClient,
        device: Any,
        volt_key: str,
        amp_key: str,
        title: str,
        enabled: bool = False,
    ) -> None:
        super().__init__(client, device, volt_key, title, enabled)
        self._amp_key = amp_key
        self._attr_unique_id += f"-{amp_key.replace('_', '-')}-watts"

    def _update_value(self, val: Any) -> bool:
        amp_val = self._device.data.params.get(self._amp_key, 0.0)
        return super()._update_value(float(val) * float(amp_val))


class _ChargingStateTextEntity(MiscSensorEntity):
    """Translates cms_chg_dsg_state (int) into a descriptive text label."""

    _LABELS: ClassVar[dict[int, str]] = {0: "Not Charging", 1: "Discharging", 2: "Charging"}

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._attr_unique_id += "-text"

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(self._LABELS.get(int(val), "Unknown"))


class DeltaProUltraX(DeltaPro3):
    """DELTA Pro Ultra X (private / app API).

    Speaks the Delta Pro 3 protobuf dialect (same header, cmdFunc/cmdId routing
    and DisplayPropertyUpload field numbers), so the DP3 decode pipeline is
    inherited unchanged. Overrides only the entity set: the DPU X has no internal
    main battery (energy is in external packs), so bms_* main-battery sensors are
    dropped and cms_batt_soc is the headline. Control entities are suppressed for
    now — read-only until actuation is deliberately in scope.
    """

    @override
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        # Enabled-by-default = the at-a-glance headline set; everything else is
        # registered but disabled by default (`False`).
        return [
            # --- Headline (enabled) ---
            LevelSensorEntity(client, self, "cms_batt_soc", const.COMBINED_BATTERY_LEVEL),
            # Total in/out power with integrated energy (kWh, total_increasing)
            # = charge / discharge energy for the HA Energy dashboard's battery
            # slot. (Native accu_chg/dsg_energy don't populate for the DPU X's
            # external-pack topology, so integrate here.)
            InWattsSensorEntity(client, self, "pow_in_sum_w", const.TOTAL_IN_POWER).with_energy(),
            OutWattsSensorEntity(client, self, "pow_out_sum_w", const.TOTAL_OUT_POWER).with_energy(),
            RemainSensorEntity(client, self, "cms_chg_rem_time", const.CHARGE_REMAINING_TIME),
            RemainSensorEntity(client, self, "cms_dsg_rem_time", const.DISCHARGE_REMAINING_TIME),
            QuotaStatusSensorEntity(client, self),
            # --- Detail (disabled by default) ---
            # Per-pack SoC (field 786), all 10 bays; unpopulated bays stay
            # unavailable.
            *[
                LevelSensorEntity(client, self, f"bp_{n}_soc", const.BATTERY_N_LEVEL % n, False)
                for n in range(1, MAX_PACKS + 1)
            ],
            # AC input: DPU X does not send pow_get_ac_in; expose per-phase V/A instead.
            VoltSensorEntity(client, self, "plug_in_info_l1_vol", "AC Input L1 Voltage", False),
            AmpSensorEntity(client, self, "plug_in_info_l1_amp", "AC Input L1 Current", False),
            _PhaseWattsSensorEntity(client, self, "plug_in_info_l1_vol", "plug_in_info_l1_amp", "AC Input L1 Power", False),
            VoltSensorEntity(client, self, "plug_in_info_l2_vol", "AC Input L2 Voltage", False),
            AmpSensorEntity(client, self, "plug_in_info_l2_amp", "AC Input L2 Current", False),
            _PhaseWattsSensorEntity(client, self, "plug_in_info_l2_vol", "plug_in_info_l2_amp", "AC Input L2 Power", False),
            OutWattsSensorEntity(client, self, "pow_get_ac", const.AC_OUT_POWER, False),
            # HV/LV = the 240V (line-to-line) and 120V (line-to-neutral) rails of the
            # split-phase output — the X has no HV/LV concept; name by voltage.
            OutWattsSensorEntity(client, self, "pow_get_ac_hv_out", "AC 240V Output Power", False),
            OutWattsSensorEntity(client, self, "pow_get_ac_lv_out", "AC 120V Output Power", False),
            # Two symmetric high-voltage PV inputs (80-500 V, 5 kW each) — not HV/LV
            # like the non-X Delta Pro Ultra; name them as circuits 1/2 per the manual.
            InRawVoltSolarSensorEntity(client, self, "pv_vin_ref", const.SOLAR_1_IN_VOLTS, False),
            InRawVoltSolarSensorEntity(client, self, "pv2_vin_ref", const.SOLAR_2_IN_VOLTS, False),
            FrequencySensorEntity(client, self, "ac_out_freq", "AC Output Frequency", False),
            # Per-phase output power, signed to preserve direction.
            OutWattsSensorEntity(client, self, "pow_get_l1", "AC Output Power L1", False),
            OutWattsSensorEntity(client, self, "pow_get_l2", "AC Output Power L2", False),
            # SoC limits — config thresholds, not remaining charge (no BATTERY device class).
            BatteryLimitSensorEntity(client, self, "cms_max_chg_soc", const.MAX_CHARGE_LEVEL, False),
            BatteryLimitSensorEntity(client, self, "cms_min_dsg_soc", const.MIN_DISCHARGE_LEVEL, False),
            *[
                TempSensorEntity(client, self, f"bp_{n}_temp", const.BATTERY_N_TEMP % n, False)
                for n in range(1, MAX_PACKS + 1)
            ],
            # Inverter / LLC / PCS temperatures.
            TempSensorEntity(client, self, "inv_ntc_temp2", "Inverter Temperature 2", False),
            TempSensorEntity(client, self, "inv_ntc_temp3", "Inverter Temperature 3", False),
            TempSensorEntity(client, self, "llc_ntc_temp", "LLC Temperature", False),
            TempSensorEntity(client, self, "temp_pcs_ac", "PCS AC Temperature", False),
            TempSensorEntity(client, self, "temp_pcs_dc", "PCS DC Temperature", False),
            # Power conversion bus metrics.
            VoltSensorEntity(client, self, "llc_bat_vol", "Battery Bus Voltage", False),
            AmpSensorEntity(client, self, "llc_bat_cur", "Battery Bus Current", False),
            VoltSensorEntity(client, self, "cms_batt_vol", "CMS Battery Voltage", False),
            AmpSensorEntity(client, self, "cms_batt_amp", "CMS Battery Current", False),
            StateOfHealthSensorEntity(client, self, "cms_batt_soh", "Battery State of Health", False),
            VoltSensorEntity(client, self, "mppt_bat_vol", "MPPT Battery Voltage", False),
            AmpSensorEntity(client, self, "mppt_bat_amp", "MPPT Battery Current", False),
            VoltSensorEntity(client, self, "inv_bus_vol", "Inverter Bus Voltage", False),
            # Charging state (0=idle, 1=discharging, 2=charging per DP3 proto).
            MiscSensorEntity(client, self, "cms_chg_dsg_state", "Charging State", False),
            _ChargingStateTextEntity(client, self, "cms_chg_dsg_state", "Charging State Text", False),
            # MPPT pause-event counters.
            MiscSensorEntity(client, self, "pv_pause_cnt", "Solar 1 MPPT Pause Count", False),
            MiscSensorEntity(client, self, "pv2_pause_cnt", "Solar 2 MPPT Pause Count", False),
            # Firmware / hardware versions (diagnostic).
            MiscSensorEntity(client, self, "bms_firm_ver", "BMS Firmware Version", False),
            MiscSensorEntity(client, self, "pd_firm_ver", "PD Firmware Version", False),
            MiscSensorEntity(client, self, "llc_firm_ver", "LLC Firmware Version", False),
            MiscSensorEntity(client, self, "iot_firm_ver", "IoT Firmware Version", False),
            MiscSensorEntity(client, self, "mppt_hardware_ver", "MPPT Hardware Version", False),
            # Error codes (diagnostic).
            MiscSensorEntity(client, self, "errcode", "Error Code", False),
            MiscSensorEntity(client, self, "bms_err_code", "BMS Error Code", False),
            MiscSensorEntity(client, self, "mppt_err_code", "MPPT Error Code", False),
            MiscSensorEntity(client, self, "pd_err_code", "PD Error Code", False),
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
    def _decode_message_by_type(self, pdata: bytes, header_info: dict[str, Any]) -> dict[str, Any]:
        # DP3 decode drops the per-pack array (DisplayPropertyUpload field 786,
        # absent from its proto). Recover it with a second pass over the same
        # payload and inject flat bp_<bay>_soc / bp_<bay>_temp keys.
        result = super()._decode_message_by_type(pdata, header_info)
        if header_info.get("cmdFunc") == 254 and header_info.get("cmdId") == 21:
            try:
                extra = dpux.DPUXDisplayPropertyExtra()
                extra.ParseFromString(pdata)
                for pack in extra.bp_info.packs:
                    if not pack.HasField("bay"):
                        continue
                    result[f"bp_{pack.bay}_soc"] = pack.soc
                    result[f"bp_{pack.bay}_temp"] = pack.temp
            except Exception as e:
                _LOGGER.debug("DPU X per-pack (field 786) parse skipped: %s", e)
        return result
