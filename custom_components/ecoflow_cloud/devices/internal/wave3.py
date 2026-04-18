import json
import logging
import random
from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.components.climate.const import (
    PRESET_NONE,
    PRESET_BOOST,
    PRESET_ECO,
    PRESET_SLEEP,
)
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from typing import Any, Optional

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.api.message import PrivateAPIMessageProtocol
from custom_components.ecoflow_cloud.devices import BaseInternalDevice, const
from custom_components.ecoflow_cloud.number import LevelEntity
from custom_components.ecoflow_cloud.select import DictSelectEntity
from custom_components.ecoflow_cloud.sensor import (
    LevelSensorEntity,
    MiscSensorEntity,
    RemainSensorEntity,
    TempSensorEntity,
    WattsSensorEntity,
    InWattsSensorEntity,
    OutWattsSensorEntity,
)
from custom_components.ecoflow_cloud.switch import BeeperEntity
from .proto import wave3_pb2

_LOGGER = logging.getLogger(__name__)

_AIRFLOW_TO_FAN_MODE: dict[int, str] = {20: "1", 40: "2", 60: "3", 80: "4", 100: "5"}
_FAN_MODE_TO_AIRFLOW: dict[str, int] = {"1": 20, "2": 40, "3": 60, "4": 80, "5": 100}

_SUBMODE_TO_PRESET: dict[int, str] = {0: PRESET_NONE, 2: PRESET_BOOST, 3: PRESET_SLEEP, 4: PRESET_ECO}
_PRESET_TO_SUBMODE: dict[str, int] = {PRESET_NONE: 0, PRESET_BOOST: 2, PRESET_SLEEP: 3, PRESET_ECO: 4}


class Wave3CommandMessage(PrivateAPIMessageProtocol):
    def __init__(self, payload: bytes):
        self._payload = payload

    def to_mqtt_payload(self) -> bytes:
        return self._payload

    def to_dict(self) -> dict:
        return {"Wave3CommandMessage": self._payload.hex()}


def _create_wave3_command(device_sn: str, **kwargs) -> Optional[Wave3CommandMessage]:
    try:
        cw = wave3_pb2.ConfigWrite()
        for key, value in kwargs.items():
            try:
                setattr(cw, key, value)
            except AttributeError:
                pass

        pdata_bytes = cw.SerializeToString()

        msg = wave3_pb2.setMessage()
        h = msg.header

        h.src = 32
        h.dest = 66
        h.d_src = 1
        h.d_dest = 1
        h.cmd_func = 254
        h.cmd_id = 17
        h.data_len = len(pdata_bytes)
        h.need_ack = 1
        h.device_sn = device_sn
        h.seq = random.randint(10, 999)

        for attr, val in [("enc_type", 1), ("check_type", 3), ("version", 3), ("payload_ver", 1), ("is_rw_cmd", 1),
                          ("from", "Android")]:
            try:
                setattr(h, attr, val)
            except AttributeError:
                pass

        h.pdata = pdata_bytes
        return Wave3CommandMessage(msg.SerializeToString())

    except Exception as exc:
        _LOGGER.error("Wave3 ConfigWrite error: %s", exc)
        return None


class Wave3(BaseInternalDevice):

    def _prepare_data(self, raw_data: bytes) -> dict[str, Any]:
        try:
            msg = wave3_pb2.setMessage()
            msg.ParseFromString(raw_data)

            if not msg.HasField("header"):
                return self._fallback_json(raw_data)

            h = msg.header
            pdata_bytes: bytes = getattr(h, "pdata", b"")
            if not pdata_bytes:
                return {}

            enc_type = getattr(h, "enc_type", 0)
            src = getattr(h, "src", 0)
            seq = getattr(h, "seq", 0)

            if enc_type == 1 and src != 32:
                pdata_bytes = bytes(b ^ (seq & 0xFF) for b in pdata_bytes)

            cmd_func = getattr(h, "cmd_func", 0)
            cmd_id = getattr(h, "cmd_id", 0)
            result: dict[str, Any] = {}

            if cmd_func == 254 and cmd_id in (1, 21):
                msg_obj = wave3_pb2.DisplayPropertyUpload()
                msg_obj.ParseFromString(pdata_bytes)
                for field, value in msg_obj.ListFields():
                    result[field.name] = value
                self._extract_active_mode_params(msg_obj, result)

            elif cmd_func == 254 and cmd_id == 22:
                msg_obj = wave3_pb2.RuntimePropertyUpload()
                msg_obj.ParseFromString(pdata_bytes)
                for field, value in msg_obj.ListFields():
                    result[field.name] = value

            elif cmd_func == 254 and cmd_id == 18:
                msg_obj = wave3_pb2.ConfigWriteAck()
                msg_obj.ParseFromString(pdata_bytes)
                for field, value in msg_obj.ListFields():
                    result[field.name] = value

            else:
                msg_obj = wave3_pb2.DisplayPropertyUpload()
                msg_obj.ParseFromString(pdata_bytes)
                for field, value in msg_obj.ListFields():
                    result[field.name] = value
                self._extract_active_mode_params(msg_obj, result)

            if result:
                if "en_beep" in result:
                    result["en_beep"] = 0 if result["en_beep"] else 1
                return {"params": result}

        except Exception:
            pass

        return self._fallback_json(raw_data)

    def _extract_active_mode_params(self, msg_obj, result) -> None:
        try:
            if not msg_obj.HasField("wave_mode_info"):
                return

            current_mode = msg_obj.wave_operating_mode if msg_obj.HasField(
                "wave_operating_mode") else self.data.params.get("wave_operating_mode", 0)
            mode_list = msg_obj.wave_mode_info.list_info

            if current_mode < 1 or current_mode >= len(mode_list):
                return

            active = mode_list[current_mode]

            if active.HasField("submode"):
                result["current_submode"] = active.submode
            if active.HasField("airflow_speed"):
                speed = active.airflow_speed
                result["current_airflow_speed"] = speed
                closest = min(_AIRFLOW_TO_FAN_MODE, key=lambda k: abs(k - speed))
                result["current_fan_mode"] = _AIRFLOW_TO_FAN_MODE.get(closest, "1")
            if active.HasField("temp_set"):
                result["current_temp_set"] = active.temp_set
            if active.HasField("humi_set"):
                result["current_humi_set"] = active.humi_set
            if active.HasField("temp_thermostatic_upper_limit"):
                result["current_temp_upper"] = active.temp_thermostatic_upper_limit
            if active.HasField("temp_thermostatic_lower_limit"):
                result["current_temp_lower"] = active.temp_thermostatic_lower_limit
        except Exception:
            pass

    @staticmethod
    def _fallback_json(raw_data: bytes) -> dict[str, Any]:
        try:
            return json.loads(raw_data.decode("utf-8"))
        except Exception:
            return {}

    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            # Power Entities
            InWattsSensorEntity(client, self, "pow_in_sum_w", const.TOTAL_IN_POWER),
            OutWattsSensorEntity(client, self, "pow_out_sum_w", const.TOTAL_OUT_POWER),
            WattsSensorEntity(client, self, "pow_get_ac", const.AC_OUT_POWER),
            InWattsSensorEntity(client, self, "pow_get_ac_in", const.AC_IN_POWER),
            WattsSensorEntity(client, self, "pow_get_bms", const.DC_BATTERY_POWER),
            InWattsSensorEntity(client, self, "pow_get_pv", const.SOLAR_IN_POWER),
            WattsSensorEntity(client, self, "pow_get_self_consume", const.SELF_CONSUMPTION_POWER, False),

            # Battery and Water Entities
            LevelSensorEntity(client, self, "bms_batt_soc", const.MAIN_BATTERY_LEVEL),
            LevelSensorEntity(client, self, "condensate_water_level", const.WATER_LEVEL),
            RemainSensorEntity(client, self, "bms_dsg_rem_time", const.DISCHARGE_REMAINING_TIME),
            RemainSensorEntity(client, self, "bms_chg_rem_time", const.CHARGE_REMAINING_TIME),
            RemainSensorEntity(client, self, "power_off_delay_remaining", const.POWER_OFF_DELAY_REMAINING_TIME),

            # Temperature Entities
            TempSensorEntity(client, self, "temp_ambient", const.AMBIENT_TEMPERATURE),
            TempSensorEntity(client, self, "temp_indoor_supply_air", const.INDOOR_SUPPLY_AIR_TEMP, False),
            TempSensorEntity(client, self, "temp_condenser", const.CONDENSER_TEMP, False),
            TempSensorEntity(client, self, "temp_evaporator", const.EVAPORATOR_TEMP, False),

            # Diagnostics
            MiscSensorEntity(client, self, "bms_err_code", "BMS Error Code", False),
        ]

    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        sn = self.device_info.sn
        return [
            LevelEntity(client, self, "lcd_light", const.SCREEN_BRIGHTNESS, 0, 100,
                        lambda v: _create_wave3_command(sn, lcdLight=int(v))),
        ]

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        sn = self.device_info.sn
        return [
            BeeperEntity(client, self, "en_beep", const.BEEPER,
                         lambda v: _create_wave3_command(sn, enBeep=0 if v else 1)),
            BeeperEntity(client, self, "drainage_mode", const.MANUAL_DRAINAGE,
                         lambda v: _create_wave3_command(sn, cfg_drainage_mode=1 if v else 0))
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        sn = self.device_info.sn
        return [
            DictSelectEntity(client, self, "screen_off_time", const.SCREEN_TIMEOUT,
                             {"Nie": 0, "10 s": 10, "30 s": 30, "1 min": 60, "5 min": 300, "10 min": 600},
                             lambda v: _create_wave3_command(sn, screenOffTime=int(v))),
            DictSelectEntity(client, self, "dev_standby_time", const.UNIT_TIMEOUT,
                             {"Nie": 0, "30 min": 30, "1 hr": 60, "2 hr": 120, "4 hr": 240, "6 hr": 360, "12 hr": 720, "24 hr": 1440},
                             lambda v: _create_wave3_command(sn, devStandbyTime=int(v))),
            DictSelectEntity(client, self, "power_off_delay_set", const.AUTO_OFF_TIMEOUT,
                             {"Nie": 0, "30 min": 30, "1 hr": 60, "2 hr": 120, "3 hr": 180, "4 hr": 240, "6 hr": 360, "8 hr": 480, "12 hr": 720, "24 hr": 1440},
                             lambda v: _create_wave3_command(sn, cfg_power_off_delay_set=int(v))),
        ]

    def climates(self, client: EcoflowApiClient) -> list[ClimateEntity]:
        return [Wave3ClimateEntity(client, self)]


class Wave3ClimateEntity(ClimateEntity):
    _attr_has_entity_name = True
    _attr_name = "Climate"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_should_poll = True

    _attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL, HVACMode.HEAT, HVACMode.FAN_ONLY, HVACMode.DRY, HVACMode.HEAT_COOL]
    _attr_fan_modes = ["1", "2", "3", "4", "5"]
    _attr_preset_modes = [PRESET_NONE, PRESET_BOOST, PRESET_ECO, PRESET_SLEEP]

    _attr_min_temp = 16.0
    _attr_max_temp = 30.0
    _attr_target_temperature_step = 1.0
    _attr_min_humidity = 40
    _attr_max_humidity = 80

    _ECOFLOW_MODE_MAP = {
        0: HVACMode.OFF,
        1: HVACMode.COOL,
        2: HVACMode.HEAT,
        3: HVACMode.FAN_ONLY,
        4: HVACMode.DRY,
        5: HVACMode.HEAT_COOL
    }

    def __init__(self, client: EcoflowApiClient, device: Wave3):
        self._client = client
        self._device = device
        self._attr_device_info = {"identifiers": {("ecoflow_cloud", device.device_info.sn)}}
        self._attr_unique_id = f"{device.device_info.sn}_climate"

    def _params(self) -> dict[str, Any]:
        if hasattr(self._device, "data") and hasattr(self._device.data, "params"):
            return self._device.data.params
        return {}

    def _send(self, msg: Optional[Wave3CommandMessage], opt_state: dict[str, Any] = None) -> None:
        if msg:
            try:
                self._client.send_set_message(self._device.device_info.sn, opt_state or {}, msg)
            except Exception as e:
                _LOGGER.error("Wave3 MQTT send error: %s", e)

    @property
    def supported_features(self) -> ClimateEntityFeature:
        features = ClimateEntityFeature(0)

        if hasattr(ClimateEntityFeature, "TURN_ON"):
            features |= ClimateEntityFeature.TURN_ON | ClimateEntityFeature.TURN_OFF

        mode = self.hvac_mode
        if mode in (HVACMode.COOL, HVACMode.HEAT):
            features |= ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE | ClimateEntityFeature.PRESET_MODE
        elif mode == HVACMode.FAN_ONLY:
            features |= ClimateEntityFeature.FAN_MODE
        elif mode == HVACMode.DRY:
            features |= ClimateEntityFeature.TARGET_HUMIDITY | ClimateEntityFeature.FAN_MODE
        elif mode == HVACMode.HEAT_COOL:
            features |= ClimateEntityFeature.TARGET_TEMPERATURE_RANGE

        return features

    @property
    def current_temperature(self) -> Optional[float]:
        return self._params().get("temp_ambient")

    @property
    def target_temperature(self) -> Optional[float]:
        if self.hvac_mode in (HVACMode.DRY, HVACMode.FAN_ONLY, HVACMode.HEAT_COOL):
            return None
        return self._params().get("current_temp_set", 22.0)

    @property
    def target_temperature_high(self) -> Optional[float]:
        return self._params().get("current_temp_upper", 24.0)

    @property
    def target_temperature_low(self) -> Optional[float]:
        return self._params().get("current_temp_lower", 20.0)

    @property
    def current_humidity(self) -> Optional[float]:
        return self._params().get("humi_ambient")

    @property
    def target_humidity(self) -> Optional[float]:
        return self._params().get("current_humi_set", 50.0)

    @property
    def hvac_mode(self) -> HVACMode:
        mode_val = self._params().get("wave_operating_mode", 0)
        return self._ECOFLOW_MODE_MAP.get(mode_val, HVACMode.OFF)

    @property
    def fan_mode(self) -> str:
        speed = self._params().get("current_airflow_speed")
        if speed is not None:
            closest = min(_AIRFLOW_TO_FAN_MODE, key=lambda k: abs(k - int(speed)))
            return _AIRFLOW_TO_FAN_MODE.get(closest, "1")
        return "1"

    @property
    def preset_mode(self) -> Optional[str]:
        return _SUBMODE_TO_PRESET.get(self._params().get("current_submode", 3), PRESET_NONE)

    def set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        sn = self._device.device_info.sn
        if hvac_mode == HVACMode.OFF:
            opt_state = {"wave_operating_mode": 0}
            self._send(_create_wave3_command(sn, cfg_sys_pause=True), opt_state)
        else:
            mode_id = next((k for k, v in self._ECOFLOW_MODE_MAP.items() if v == hvac_mode), 1)
            opt_state = {"wave_operating_mode": mode_id}
            self._send(_create_wave3_command(sn, cfg_main_power=True, cfg_wave_operating_mode=mode_id), opt_state)
        self.schedule_update_ha_state()

    def set_temperature(self, **kwargs: Any) -> None:
        cmd = {}
        opt_state = {}

        if ATTR_TEMPERATURE in kwargs:
            cmd["cfg_temp_set"] = float(kwargs[ATTR_TEMPERATURE])
            opt_state["current_temp_set"] = cmd["cfg_temp_set"]
        if "target_temp_high" in kwargs:
            cmd["cfg_temp_thermostatic_upper_limit"] = float(kwargs["target_temp_high"])
            opt_state["current_temp_upper"] = cmd["cfg_temp_thermostatic_upper_limit"]
        if "target_temp_low" in kwargs:
            cmd["cfg_temp_thermostatic_lower_limit"] = float(kwargs["target_temp_low"])
            opt_state["current_temp_lower"] = cmd["cfg_temp_thermostatic_lower_limit"]

        if cmd:
            self._send(_create_wave3_command(self._device.device_info.sn, **cmd), opt_state)
            self.schedule_update_ha_state()

    def set_fan_mode(self, fan_mode: str) -> None:
        speed = _FAN_MODE_TO_AIRFLOW.get(fan_mode, 20)
        opt_state = {"current_airflow_speed": speed, "current_fan_mode": fan_mode}
        self._send(_create_wave3_command(self._device.device_info.sn, cfg_airflow_speed=speed), opt_state)
        self.schedule_update_ha_state()

    def set_preset_mode(self, preset_mode: str) -> None:
        submode = _PRESET_TO_SUBMODE.get(preset_mode, 3)
        opt_state = {"current_submode": submode}
        self._send(_create_wave3_command(self._device.device_info.sn, cfg_wave_operating_submode=submode), opt_state)
        self.schedule_update_ha_state()

    def set_humidity(self, humidity: int) -> None:
        opt_state = {"current_humi_set": float(humidity)}
        self._send(_create_wave3_command(self._device.device_info.sn, cfg_humi_set=float(humidity)), opt_state)
        self.schedule_update_ha_state()

    def turn_on(self) -> None:
        self._send(_create_wave3_command(self._device.device_info.sn, cfg_main_power=True))
        self.schedule_update_ha_state()

    def turn_off(self) -> None:
        self.set_hvac_mode(HVACMode.OFF)