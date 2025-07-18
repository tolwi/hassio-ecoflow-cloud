from typing import Any

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode
from homeassistant.components.climate.const import PRESET_NONE, PRESET_ECO, PRESET_SLEEP
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ECOFLOW_DOMAIN
from .api import EcoflowApiClient
from .devices import BaseDevice
from .entities import EcoFlowAbstractEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    client: EcoflowApiClient = hass.data[ECOFLOW_DOMAIN][entry.entry_id]
    for sn, device in client.devices.items():
        async_add_entities(device.climates(client))


class Wave2ClimateEntity(ClimateEntity, EcoFlowAbstractEntity):
    """
    Proper climate entity that directly manages multiple MQTT keys
    without fighting the single-key EcoFlowDictEntity pattern.
    """
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 1
    _attr_min_temp = 16  # Per vendor spec: 16-30°C
    _attr_max_temp = 30
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL, HVACMode.HEAT, HVACMode.FAN_ONLY]
    _attr_fan_modes = ["Low", "Medium", "High"]
    _attr_preset_modes = [PRESET_NONE, PRESET_ECO, PRESET_SLEEP, "Max"]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(
        self,
        client: EcoflowApiClient,
        device: BaseDevice,
    ):
        super().__init__(client, device, "Air Conditioner", "climate")
        
        # Climate state - managed directly by this entity
        self._current_temperature = None
        self._target_temperature = None
        self._hvac_mode = HVACMode.OFF
        self._fan_mode = "Low"
        self._preset_mode = PRESET_NONE
        self._attr_available = True

    @property
    def current_temperature(self) -> float | None:
        return self._current_temperature

    @property
    def target_temperature(self) -> float | None:
        return self._target_temperature

    @property
    def hvac_mode(self) -> HVACMode:
        return self._hvac_mode

    @property
    def fan_mode(self) -> str | None:
        return self._fan_mode

    @property
    def preset_mode(self) -> str | None:
        return self._preset_mode

    def _handle_coordinator_update(self) -> None:
        """
        Direct access to coordinator data - parse all MQTT keys we care about.
        This is cleaner than trying to force multiple keys through single-key framework.
        """
        if not self.coordinator.data.changed:
            return
            
        data = self.coordinator.data.data_holder.params
        if not data:
            return

        # Always use Celsius as per vendor spec (16-30°C)
        # Let Home Assistant handle any user preference conversions in the UI

        # Update current temperature from ambient sensor
        if "pd.envTemp" in data:
            self._current_temperature = float(data["pd.envTemp"])

        # Update target temperature  
        if "pd.setTemp" in data:
            self._target_temperature = float(data["pd.setTemp"])

        # Update HVAC mode based on power mode, power status, and main mode
        # Vendor docs show both pd.mainMode and pd.pdMainMode
        power_mode = data.get("pd.powerMode")  # Command state: 1=on, 2=off
        power_status = data.get("pd.powerSts")  # Actual power status from device
        run_status = data.get("pd.runSts")  # Device running status bit flags
        main_mode = data.get("pd.mainMode") or data.get("pd.pdMainMode")
        
        # Determine if device is actually running by checking multiple indicators
        # Priority: pd.powerSts (actual status) > pd.runSts (running flags) > pd.powerMode (commands)
        if power_status is not None:
            # pd.powerSts indicates actual device power status (best indicator)
            device_is_on = (power_status == 1)
        elif run_status is not None:
            # pd.runSts has bit flags - if any bits are set, device is running
            device_is_on = (run_status > 0)
        elif power_mode is not None:
            # Fallback to command state if no actual status available
            device_is_on = (power_mode == 1)
        else:
            device_is_on = False
        
        if not device_is_on:
            # Device is off
            self._hvac_mode = HVACMode.OFF
        else:
            # Device is on - determine which mode based on mainMode
            if main_mode == 0:  # Cool
                self._hvac_mode = HVACMode.COOL
            elif main_mode == 1:  # Heat
                self._hvac_mode = HVACMode.HEAT
            elif main_mode == 2:  # Fan
                self._hvac_mode = HVACMode.FAN_ONLY
            else:
                # Device is on but mode unclear - default to OFF
                self._hvac_mode = HVACMode.OFF
        
        # Update fan mode
        fan_value = data.get("pd.fanValue")
        if fan_value == 0:
            self._fan_mode = "Low"
        elif fan_value == 1:
            self._fan_mode = "Medium"
        elif fan_value == 2:
            self._fan_mode = "High"
        
        # Update preset mode - vendor uses pd.pdSubMode, not pd.subMode
        sub_mode = data.get("pd.pdSubMode") or data.get("pd.subMode")  # Try both for compatibility
        if sub_mode == 0:
            self._preset_mode = "Max"
        elif sub_mode == 1:
            self._preset_mode = PRESET_SLEEP
        elif sub_mode == 2:
            self._preset_mode = PRESET_ECO
        elif sub_mode == 3:
            self._preset_mode = PRESET_NONE  # Manual
        else:
            self._preset_mode = PRESET_NONE

        # Entity is available if we have basic device data
        self._attr_available = any(key in data for key in ["pd.setTemp", "pd.powerMode", "pd.envTemp", "pd.runSts", "pd.powerSts"])
        
        self.schedule_update_ha_state()

    def _send_command(self, mqtt_key: str, value: Any, operate_type: str, param_name: str) -> None:
        """
        Send command using established API pattern.
        This follows the same pattern as other entities but handles multiple keys properly.
        """
        command = {
            "moduleType": 1,
            "operateType": operate_type,
            "sn": self._device.device_info.sn,
            "params": {param_name: value}
        }
        
        # Use the device's key format logic
        if self._device.flat_json():
            adopted_key = f"'{mqtt_key}'"
        else:
            adopted_key = mqtt_key
            
        self._client.send_set_message(
            self._device.device_info.sn,
            {adopted_key: value},
            command
        )

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if ATTR_TEMPERATURE in kwargs:
            temperature = int(kwargs[ATTR_TEMPERATURE])
            # Send temperature command in Celsius (16-30°C range)
            self._send_command("pd.setTemp", temperature, "setTemp", "setTemp")

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            # Set to power off - vendor docs: "1: Power on; 2: Power off"
            self._send_command("pd.powerMode", 2, "powerMode", "powerMode")
        else:
            # First ensure device is on (power on mode)
            self._send_command("pd.powerMode", 1, "powerMode", "powerMode")

            # Then set the main mode
            main_mode_value = 0  # Cool
            if hvac_mode == HVACMode.HEAT:
                main_mode_value = 1  # Heat
            elif hvac_mode == HVACMode.FAN_ONLY:
                main_mode_value = 2  # Fan
            elif hvac_mode == HVACMode.COOL:
                main_mode_value = 0  # Cool

            self._send_command("pd.mainMode", main_mode_value, "mainMode", "mainMode")

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        fan_value = 0  # Low
        if fan_mode == "Medium":
            fan_value = 1
        elif fan_mode == "High":
            fan_value = 2

        self._send_command("pd.fanValue", fan_value, "fanValue", "fanValue")

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        sub_mode_value = 3  # Manual/None
        if preset_mode == "Max":
            sub_mode_value = 0
        elif preset_mode == PRESET_SLEEP:
            sub_mode_value = 1
        elif preset_mode == PRESET_ECO:
            sub_mode_value = 2

        self._send_command("pd.subMode", sub_mode_value, "subMode", "subMode")

    async def async_turn_on(self) -> None:
        self._send_command("pd.powerMode", 1, "powerMode", "powerMode")

    async def async_turn_off(self) -> None:
        self._send_command("pd.powerMode", 2, "powerMode", "powerMode")