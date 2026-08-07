import logging
from typing import Any, override

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
    BatteryLimitSensorEntity,
    FrequencySensorEntity,
    InRawWattsSolarSensorEntity,
    InWattsSensorEntity,
    LevelSensorEntity,
    OutWattsSensorEntity,
    QuotaStatusSensorEntity,
    RemainSensorEntity,
    TempSensorEntity,
)

_LOGGER = logging.getLogger(__name__)

# The DPU X supports up to 10 external battery packs.
MAX_PACKS = 10


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
            InWattsSensorEntity(client, self, "pow_get_ac_in", const.AC_IN_POWER, False),
            OutWattsSensorEntity(client, self, "pow_get_ac", const.AC_OUT_POWER, False),
            # HV/LV = the 240V (line-to-line) and 120V (line-to-neutral) rails of the
            # split-phase output — the X has no HV/LV concept; name by voltage.
            OutWattsSensorEntity(client, self, "pow_get_ac_hv_out", "AC 240V Output Power", False),
            OutWattsSensorEntity(client, self, "pow_get_ac_lv_out", "AC 120V Output Power", False),
            # Two symmetric high-voltage PV inputs (80-500 V, 5 kW each) — not HV/LV
            # like the non-X Delta Pro Ultra; name them as circuits 1/2 per the manual.
            InRawWattsSolarSensorEntity(client, self, "pow_get_pv_h", const.SOLAR_1_IN_POWER, False),
            InRawWattsSolarSensorEntity(client, self, "pow_get_pv_l", const.SOLAR_2_IN_POWER, False),
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
