from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import BaseDevice, const
from custom_components.ecoflow_cloud.entities import BaseSensorEntity
from custom_components.ecoflow_cloud.number import (
    LevelEntity,
    MaxBatteryLevelEntity,
    MinBatteryLevelEntity,
)
from custom_components.ecoflow_cloud.sensor import (
    InWattsSensorEntity,
    LevelSensorEntity,
    OutWattsSensorEntity,
    QuotaStatusSensorEntity,
    RemainSensorEntity,
)
from custom_components.ecoflow_cloud.switch import EnabledEntity


def _delta3_set(sn: str, params: dict[str, Any]) -> dict[str, Any]:
    """Build a Delta 3 Max Plus SET command.

    Envelope matches the EcoFlow developer-API SET examples
    (cmdId=17, cmdFunc=254, dest=2) and the proven public/delta_pro_3.py
    pattern that tolwi already ships for the sibling Delta Pro 3.
    """
    return {
        "sn": sn,
        "cmdId": 17,
        "dirDest": 1,
        "dirSrc": 1,
        "cmdFunc": 254,
        "dest": 2,
        "params": params,
    }


class Delta3RemainSensorEntity(RemainSensorEntity):
    """RemainSensorEntity without tolwi's 5000-min hard cap.

    The Delta 3 Max Plus' 2 kWh battery at low idle draw legitimately
    reports estimates over 12,000 min, which the base class truncates to 0.
    """

    def _update_value(self, val: Any) -> Any:
        try:
            ival = int(val)
        except (TypeError, ValueError):
            return False
        if ival < 0 or ival > 100000:
            ival = 0
        return super(RemainSensorEntity, self)._update_value(ival)


class Delta3ChargingStateSensorEntity(BaseSensorEntity):
    """Charge/discharge state mapped to text.

    Per the docs, cms_chg_dsg_state is 0=idle, 1=discharging, 2=charging --
    the inverse of tolwi's generic ChargingStateSensorEntity, so a
    device-specific mapping is required.
    """

    _attr_icon = "mdi:battery-charging"

    def _update_value(self, val: Any) -> bool:
        try:
            text = {0: "idle", 1: "discharging", 2: "charging"}.get(int(val))
        except (TypeError, ValueError):
            return False
        if text is None:
            return False
        return super()._update_value(text)


class FlowControlSwitch(EnabledEntity):
    """Output switch whose state reads a flow_info_* field.

    The docs define flow_info_* as 'on when value is not 4', so the base
    EnabledEntity truthiness check (4 is truthy -> would read ON when the
    output is actually off) can't be used. State is derived from != 4;
    the SET command is built by the caller's command lambda.
    """

    def _update_value(self, val: Any) -> bool:
        try:
            new_state = int(val) != 4
        except (TypeError, ValueError):
            return False
        if self._attr_is_on != new_state:
            self._attr_is_on = new_state
            return True
        return False


# Field set verified against the official EcoFlow developer docs at
# https://developer.ecoflow.com/us/document/delta3maxplus (heartbeat-response
# Example JSON + SET command examples). Wire format is camelCase. Switches and
# numbers double as the state read-out for their respective fields, so those
# fields are not also exposed as standalone sensors.
class Delta3MaxPlus(BaseDevice):
    @staticmethod
    def default_charging_power_step() -> int:
        return 50

    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            # ── Battery / SoC ──────────────────────────────────────────────
            LevelSensorEntity(client, self, "cmsBattSoc", const.MAIN_BATTERY_LEVEL),
            Delta3ChargingStateSensorEntity(client, self, "cmsChgDsgState", const.BATTERY_CHARGING_STATE),

            # ── Power totals ───────────────────────────────────────────────
            InWattsSensorEntity(client, self, "powInSumW", const.TOTAL_IN_POWER).with_energy(),
            OutWattsSensorEntity(client, self, "powOutSumW", const.TOTAL_OUT_POWER).with_energy(),

            # ── AC / Solar inputs ──────────────────────────────────────────
            InWattsSensorEntity(client, self, "powGetAcIn", const.AC_IN_POWER),
            InWattsSensorEntity(client, self, "powGetPv", const.SOLAR_IN_POWER),
            InWattsSensorEntity(client, self, "powGetPv2", "Solar 2 In Power"),

            # ── DC / USB outputs ───────────────────────────────────────────
            OutWattsSensorEntity(client, self, "powGet12v", const.DC_OUT_POWER),
            OutWattsSensorEntity(client, self, "powGetTypec1", const.TYPEC_1_OUT_POWER),
            OutWattsSensorEntity(client, self, "powGetTypec2", const.TYPEC_2_OUT_POWER),
            OutWattsSensorEntity(client, self, "powGetTypec3", "Type-C (3) Out Power"),
            OutWattsSensorEntity(client, self, "powGetQcusb1", const.USB_QC_1_OUT_POWER),
            OutWattsSensorEntity(client, self, "powGetQcusb2", const.USB_QC_2_OUT_POWER),

            # ── Remaining time ─────────────────────────────────────────────
            Delta3RemainSensorEntity(client, self, "cmsChgRemTime", const.CHARGE_REMAINING_TIME),
            Delta3RemainSensorEntity(client, self, "cmsDsgRemTime", const.DISCHARGE_REMAINING_TIME),

            QuotaStatusSensorEntity(client, self),
        ]

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        sn = self.device_info.sn
        return [
            # Output toggles -- state read from flow_info_* (on when != 4).
            FlowControlSwitch(
                client, self, "flowInfoAcOut", "AC Output",
                lambda value, params=None: _delta3_set(sn, {"cfgAcOutOpen": bool(value)}),
            ),
            FlowControlSwitch(
                client, self, "flowInfoAc2Out", "AC2 Output",
                lambda value, params=None: _delta3_set(sn, {"cfgAc2OutOpen": bool(value)}),
            ),
            FlowControlSwitch(
                client, self, "flowInfo12v", "DC Output",
                lambda value, params=None: _delta3_set(sn, {"cfgDc12vOutOpen": bool(value)}),
            ),
            # Boolean config toggles -- state read directly from the flag.
            EnabledEntity(
                client, self, "xboostEn", const.XBOOST_ENABLED,
                lambda value, params=None: _delta3_set(sn, {"cfgXboostEn": bool(value)}),
            ),
            EnabledEntity(
                client, self, "enBeep", const.BEEPER,
                lambda value, params=None: _delta3_set(sn, {"cfgBeepEn": bool(value)}),
            ),
            EnabledEntity(
                client, self, "energyBackupEn", const.BP_ENABLED,
                lambda value, params=None: _delta3_set(
                    sn, {"cfgEnergyBackup": {"energyBackupEn": bool(value)}}
                ),
            ),
            EnabledEntity(
                client, self, "bypassOutDisable", "Bypass Output Disabled",
                lambda value, params=None: _delta3_set(sn, {"cfgBypassOutDisable": bool(value)}),
            ),
        ]

    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        sn = self.device_info.sn
        return [
            MaxBatteryLevelEntity(
                client, self, "cmsMaxChgSoc", const.MAX_CHARGE_LEVEL, 50, 100,
                lambda value: _delta3_set(sn, {"cfgMaxChgSoc": value}),
            ),
            MinBatteryLevelEntity(
                client, self, "cmsMinDsgSoc", const.MIN_DISCHARGE_LEVEL, 0, 30,
                lambda value: _delta3_set(sn, {"cfgMinDsgSoc": value}),
            ),
            LevelEntity(
                client, self, "backupReverseSoc", "Backup Reserve Level", 0, 50,
                lambda value: _delta3_set(sn, {"cfgBackupReverseSoc": value}),
            ),
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return []