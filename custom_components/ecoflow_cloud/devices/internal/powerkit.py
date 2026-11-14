"""Power Kits (Power Hub) over the app protocol (private_api).

The 2nd-generation 5 kVA Power Hub is listed by the developer platform, but every
data request for it fails with error 1006, so the public_api ``Power Kits`` device
never sees it. The app's MQTT stream carries the same modules as the public device
(bbcin, bbcout, iclow, bpXXXX, kitscc, lddc, ichigh, ldac) plus the hub's own
``wireless`` and ``gps`` modules, only wrapped differently; see ``powerkit_data``
for the shapes.

The entities are the public ones plus what a 2nd-generation hub reports on top:
system totals (``bmsTotal`` / ``mainBP``), battery health and cumulative energy,
the inverter's effective settings (``appCfg``), the distribution box's extra DC
channels. Every module is its own Home Assistant device, discovered by the config
flow from a ``latestQuotas`` reply; the hub device keeps the totals and its own
modules.

Where a switch reads its state from one module but the command goes to another
(the public implementation left those switches without a readable state), the
switch lives on the module that reports the state and addresses the sibling
module in the command.

The commands for the main DC output, the three DC charging ports (ALT IN n / PV
IN n: charging on/off and the auto / alternator / solar mode), the battery SOC
limits, AC charging and the DC circuits were captured from the EcoFlow app
talking to a 2nd-generation hub; they differ from the 1st-generation
documentation in places (module types 15363 and 15368, grid priority set
through iclow). The AC charging and input current limits travel together in
one dischgIcParaSet (2 to 20 A and 2 to 50 A on a 230 V hub, charging never
above input). Only the AC output switch is not captured yet; it is the powerOn
field of the message the AC charging switch uses.
"""

import logging
import re
from collections.abc import Callable
from typing import Any, Self, override

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.text import TextEntity
from homeassistant.const import PERCENTAGE, UnitOfElectricCurrent, UnitOfElectricPotential, UnitOfFrequency, UnitOfPower
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity import EntityCategory

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.api.message import JSONMessage, Message
from custom_components.ecoflow_cloud.device_data import DeviceData
from custom_components.ecoflow_cloud.devices import EcoflowDeviceInfo, const
from custom_components.ecoflow_cloud.devices.data_holder import PreparedData
from custom_components.ecoflow_cloud.devices.internal.powerkit_data import (
    alias_request,
    alias_set_command,
    hub_fields_from_message,
    hub_quota_fields,
    module_quota_fields,
    parse_alias_entries,
    parse_alias_set,
    parse_module_message,
    reply_online,
)
from custom_components.ecoflow_cloud.entities import EcoFlowAbstractEntity, EcoFlowDictEntity
from custom_components.ecoflow_cloud.devices.public.powerkit import BitMaskEnableEntity
from custom_components.ecoflow_cloud.devices.public.powerkit import PowerKit as PublicPowerKit
from custom_components.ecoflow_cloud.number import (
    AcChargingPowerInAmpereEntity,
    MaxBatteryLevelEntity,
    MinBatteryLevelEntity,
)
from custom_components.ecoflow_cloud.select import DictSelectEntity
from custom_components.ecoflow_cloud.sensor import (
    AmpSensorEntity,
    CapacitySensorEntity,
    CumulativeCapacitySensorEntity,
    EnergySensorEntity,
    InWattsSensorEntity,
    LevelSensorEntity,
    MiscSensorEntity,
    OutMilliampSensorEntity,
    OutMilliVoltSensorEntity,
    OutWattsSensorEntity,
    QuotaStatusSensorEntity,
    RemainSensorEntity,
    StateOfHealthSensorEntity,
    TempSensorEntity,
)
from custom_components.ecoflow_cloud.switch import EnabledEntity

_LOGGER = logging.getLogger(__name__)

# moduleType values of the set commands, as the EcoFlow app sends them to a 2nd generation hub
INVERTER_MODULE_TYPE = 15365  # iclow / ichigh
DC_IN_MODULE_TYPE = 15362  # bbcin
DC_OUT_MODULE_TYPE = 15363  # bbcout
MPPT_MODULE_TYPE = 15364  # kitscc
DC_PANEL_MODULE_TYPE = 15368  # lddc
# commands the hub routes to the batteries itself carry no module serial
NO_MODULE_SN = "0000000000000000"

DC_PANEL_CHANNELS = 16  # F1 to F16 on the 2nd generation panel

# DC charging mode of the ALT IN n / PV IN n ports: port 1 is bbcin, ports 2 and 3 the two MPPT inputs
_PORT_MODES = {"Auto": 0, "Alternator": 1, "Solar": 2}
# alternator type on port 1; with a 48 V excited alternator the port cannot discharge in reverse
_ALTERNATOR_TYPES = {"Generic": 0, "48V Excited": 1}

# AC current limits as the app offers them on a 230 V hub; the charging current may not exceed the input current
AC_CHARGE_CURRENT_RANGE = (2, 20)
AC_INPUT_CURRENT_RANGE = (2, 50)

# volTag of the main DC output, captured from the app: 0 is 12 V, 1 is 24 V
_DC_OUTPUT_VOLTAGES = {"12V": 0, "24V": 1}
DC_PANEL_SWITCHES = 12  # channels in the dcChRelay bitmask; dcChRelayV2 carries the remaining four
AC_PANEL_CHANNELS = 6  # breaker positions the AC board reports
# the app accepts 24 letters or digits, or 8 Chinese characters, for a circuit name: 24 bytes of UTF-8
CIRCUIT_NAME_MAX_BYTES = 24
# the public per-circuit sensors: dcChWatt[3], acChCur[0], ...
_CIRCUIT_KEY = re.compile(r"^(?P<board>dc|ac)Ch(?P<kind>Watt|Cur)\[(?P<index>\d+)\]$")

# the app sends every parameter of a group and marks the unchanged ones
_UNCHANGED = 255
_UNCHANGED_WORD = 65535
_DC_OUT_PARAMS = {
    "swSta": _UNCHANGED,
    "beepEn": _UNCHANGED,
    "volTag": _UNCHANGED,
    "hubExitLsp": _UNCHANGED,
    "bbcInExitLsp": _UNCHANGED,
    "icExitLsp": _UNCHANGED,
    "sccExitLsp": _UNCHANGED,
    "noLoadPwr": _UNCHANGED_WORD,
    "standbyTime": _UNCHANGED_WORD,
}
_DC_IN_PARAMS = {
    "chgPause": _UNCHANGED,
    "maxChgCurr": -1,
    "altCableLen": -1,
    "altCableUnit": _UNCHANGED,
    "altVoltLmt": _UNCHANGED_WORD,
    "altVoltLmtEn": _UNCHANGED,
    "shakeCtrlDisable": _UNCHANGED,
    "setPortType": _UNCHANGED,
}
_PV_PARAMS = {
    "mpptt1": _UNCHANGED,
    "mpptt2": _UNCHANGED,
    "alt1CableLen": -1,
    "alt2CableLen": -1,
    "alt1CableUnit": _UNCHANGED,
    "alt2CableUnit": _UNCHANGED,
    "alt1VoltLmt": _UNCHANGED_WORD,
    "alt2VoltLmt": _UNCHANGED_WORD,
    "alt1VoltLmtEn": _UNCHANGED,
    "alt2VoltLmtEn": _UNCHANGED,
    "setPort1Type": _UNCHANGED,
    "setPort2Type": _UNCHANGED,
}
# passByModeEn: 1 runs the loads from the grid when it is present, 2 from the battery
_GRID_PRIORITY_PARAMS = {
    "invNoLoadPwr": _UNCHANGED_WORD,
    "dsgLowPwrEn": _UNCHANGED,
    "setInvTag": _UNCHANGED,
    "pfcDsgModeEn": _UNCHANGED,
    "passByCurrMax": _UNCHANGED,
}

_MODULE_LABELS = {
    "iclow": "BMS",
    "kitscc": "MPPT",
    "bbcout": "Hub DC Out",
    "bbcin": "Hub DC In",
    "lddc": "DC Panel",
    "ichigh": "Hub AC Out",
    "ldac": "AC Panel",
}

# Product names as EcoFlow prints them (Chinese manual name, English name), shown as the
# Home Assistant device model. The hub is the 智控五合一充逆一体机 / Power Hub; iclow, ichigh,
# kitscc, bbcin and bbcout are the five functions inside it, bp* the batteries, lddc / ldac
# the two boards of the AC/DC smart distribution panel.
HUB_MODEL = "智控五合一充逆一体机 (Power Hub)"
_MODULE_MODELS = {
    "iclow": "智控五合一充逆一体机 逆变充电 电池侧 (Power Hub inverter charger, battery side)",
    "ichigh": "智控五合一充逆一体机 逆变充电 交流侧 (Power Hub inverter charger, AC side)",
    "kitscc": "智控五合一充逆一体机 MPPT 太阳能充电控制器 (Power Hub MPPT solar charge controller)",
    "bbcin": "智控五合一充逆一体机 DC-DC 电池充电器 (Power Hub DC-DC battery charger)",
    "bbcout": "智控五合一充逆一体机 DC-DC 降压输出 (Power Hub DC-DC step-down converter)",
    "lddc": "交直流智能配电盘 直流回路 (AC/DC Smart Distribution Panel, DC circuits)",
    "ldac": "交直流智能配电盘 交流回路 (AC/DC Smart Distribution Panel, AC circuits)",
}


def _module_label(module_type: str) -> str:
    if module_type.startswith("bp"):
        return "Battery"
    return _MODULE_LABELS.get(module_type, module_type)


# The two battery packs EcoFlow sells for the Power Kits, by the module type they report
_BATTERY_MODELS = {
    "bp5000": "磷酸铁锂电池5度电 (LFP Battery 5kWh)",  # 51.2 V / 100 Ah
    "bp2000": "磷酸铁锂电池2度电 (LFP Battery 2kWh)",  # 51.2 V / 40 Ah
}


def _module_model(module_type: str) -> str:
    if module_type.startswith("bp"):
        return _BATTERY_MODELS.get(module_type, "磷酸铁锂电池 (LFP Battery)")
    return _MODULE_MODELS.get(module_type, module_type)


class TotalCurrentSensorEntity(AmpSensorEntity):
    """``totalAmp`` is a signed 16-bit value in 0.1 A sent unsigned: 65486 is -5.0 A."""

    def _update_value(self, val: Any) -> bool:
        ival = int(val)
        if ival > 32767:
            ival -= 65536
        return super()._update_value(ival / 10)


class CircuitAliasMixin(EcoFlowAbstractEntity):
    """Names a panel circuit's entity after the alias the owner gave it in the app.

    The default title is what the entity is registered with, so the entity id stays stable;
    the alias replaces the display name once the entity is added and follows later changes.
    """

    _circuit_index: int = -1
    _title_template: str = "{alias}"
    _default_title: str = ""

    def for_circuit(self, index: int, template: str = "{alias}") -> Self:
        """``index`` is zero based; ``template`` formats the alias into the title."""
        self._circuit_index = index
        self._title_template = template
        self._default_title = self._attr_name
        return self

    def _apply_alias(self) -> bool:
        device = self._device
        alias = device.circuit_alias(self._circuit_index) if isinstance(device, PowerKit) else None
        title = self._title_template.format(alias=alias) if alias else self._default_title
        if title == self._attr_name:
            return False
        self._attr_name = title
        return True

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if isinstance(self._device, PowerKit):
            self.async_on_remove(self._device.add_alias_listener(self._alias_changed))
        self._apply_alias()

    def _alias_changed(self) -> None:
        # called on the MQTT thread when the panel reports new names
        if self._apply_alias():
            self.schedule_update_ha_state()


class CircuitWattsSensorEntity(CircuitAliasMixin, OutWattsSensorEntity):
    pass


class CircuitAmpSensorEntity(CircuitAliasMixin, OutMilliampSensorEntity):
    pass


class CircuitSwitchEntity(CircuitAliasMixin, BitMaskEnableEntity):
    pass


class CircuitNameEntity(EcoFlowAbstractEntity, TextEntity):
    """The name of a panel circuit as the app shows it; writing it renames the circuit in the app too.

    The icon the owner picked for the circuit (``logoNum``) is kept as it is.
    """

    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:rename-box"
    _attr_native_max = CIRCUIT_NAME_MAX_BYTES
    _attr_should_poll = False

    def __init__(self, client: EcoflowApiClient, device: PowerKit, index: int, title: str) -> None:
        super().__init__(client, device, title, f"circuitName.{index + 1}")
        self._panel = device
        self._index = index
        self._attr_native_value = device.circuit_alias(index) or ""

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(self._panel.add_alias_listener(self._alias_changed))
        self._attr_native_value = self._panel.circuit_alias(self._index) or ""

    def _alias_changed(self) -> None:
        # called on the MQTT thread when the panel reports new names
        value = self._panel.circuit_alias(self._index) or ""
        if value != self._attr_native_value:
            self._attr_native_value = value
            self.schedule_update_ha_state()

    def command_dict(self, value: str) -> dict[str, Any]:
        command = alias_set_command(
            self._panel.device_data.device_type,
            self._panel.module_sn,
            self._index,
            value,
            self._panel.circuit_logo(self._index),
        )
        if command is None:
            raise ValueError(f"{self._panel.device_data.device_type} has no circuit names")
        return {"id": 123456789, "version": "1.0", **command}

    def set_value(self, value: str) -> None:
        name = value.strip()
        if not name:
            return
        if len(name.encode("utf-8")) > CIRCUIT_NAME_MAX_BYTES:
            raise ServiceValidationError(
                f"A circuit name holds at most {CIRCUIT_NAME_MAX_BYTES} bytes of UTF-8 "
                f"(24 letters or digits, 8 Chinese characters): {name!r} is too long"
            )
        self._client.send_set_message(self._device.device_data.sn, {}, self.command_dict(name))
        # the board does not echo the name back: take it now so that the other entities follow
        self._attr_native_value = name
        self._panel.set_circuit_alias(self._index, name, self._panel.circuit_logo(self._index))


class PowerKit(PublicPowerKit):
    def __init__(self, device_info: EcoflowDeviceInfo, device_data: DeviceData) -> None:
        super().__init__(device_info, device_data)
        # the app's names and icons for a panel board's circuits, in circuit order (see circuit_alias)
        self.circuit_aliases: list[str] = []
        self.circuit_logos: list[int] = []
        self._alias_listeners: list[Callable[[], None]] = []
        # the app addresses the DC panel's relays with module type 15368, not the documented 15362
        self.dcSwitchFunction = lambda sn, value: {
            "id": 123456789,
            "version": "1.0",
            "moduleSn": sn,
            "moduleType": DC_PANEL_MODULE_TYPE,
            "operateType": "chSwitch",
            "params": {"bitsSwSta": value},
        }
        if device_data.parent is not None:
            device_data.display_name = (
                f"{device_data.parent.name} {_module_label(device_data.device_type)} ({self.module_sn})"
            )
            self.model_name = _module_model(device_data.device_type)
        else:
            self.model_name = HUB_MODEL

    @property
    def is_hub(self) -> bool:
        return self.device_data.parent is None

    def get_quota_message(self) -> Message:
        return JSONMessage(
            {
                "version": "1.1",
                "moduleType": 0,
                "operateType": "latestQuotas",
                "params": {},
            }
        )

    # -------------------------------------------------------- circuit names
    def circuit_alias(self, index: int) -> str | None:
        """The app's name of circuit ``index`` (zero based), None when unknown or empty."""
        if 0 <= index < len(self.circuit_aliases) and self.circuit_aliases[index]:
            return self.circuit_aliases[index]
        return None

    def circuit_logo(self, index: int) -> int:
        """The app's icon number of circuit ``index`` (zero based), 0 when unknown."""
        if 0 <= index < len(self.circuit_logos):
            return self.circuit_logos[index]
        return 0

    def add_alias_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        """Call ``listener`` whenever the circuit names change; returns the remover."""
        self._alias_listeners.append(listener)

        def remove() -> None:
            if listener in self._alias_listeners:
                self._alias_listeners.remove(listener)

        return remove

    def set_circuit_alias(self, index: int, alias: str, logo: int) -> None:
        """Take a name and icon for one circuit and tell the listeners when it changed."""
        if index < 0:
            return
        if index >= len(self.circuit_aliases):
            self.circuit_aliases += [""] * (index + 1 - len(self.circuit_aliases))
        if index >= len(self.circuit_logos):
            self.circuit_logos += [0] * (index + 1 - len(self.circuit_logos))
        if (self.circuit_aliases[index], self.circuit_logos[index]) == (alias, logo):
            return
        self.circuit_aliases[index] = alias
        self.circuit_logos[index] = logo
        self._notify_alias_listeners()

    def _notify_alias_listeners(self) -> None:
        for listener in list(self._alias_listeners):
            listener()

    @override
    def startup_set_messages(self) -> list[dict[str, Any]]:
        request = alias_request(self.device_data.device_type, self.module_sn)
        return [request] if request else []

    @override
    def _prepare_data_set_topic(self, raw_data: bytes) -> PreparedData:
        # a rename, by the app or by this integration, passes here before the board confirms it
        data = self._prepare_data(raw_data)
        renamed = parse_alias_set(data, self.device_data.device_type, self.module_sn)
        if renamed is not None:
            self.set_circuit_alias(*renamed)
        return PreparedData(None, None, data)

    @override
    def _prepare_data_set_reply_topic(self, raw_data: bytes) -> PreparedData:
        # the panel answers the alias request here, and again whenever the app asks for the names
        data = self._prepare_data(raw_data)
        entries = parse_alias_entries(data, self.device_data.device_type, self.module_sn)
        if entries is not None:
            aliases = [alias for alias, _ in entries]
            logos = [logo for _, logo in entries]
            if aliases != self.circuit_aliases or logos != self.circuit_logos:
                self.circuit_aliases = aliases
                self.circuit_logos = logos
                self._notify_alias_listeners()
        return PreparedData(None, None, data)

    def _named_circuit_sensors(self, client: EcoflowApiClient, sensors: list[SensorEntity]) -> list[SensorEntity]:
        """The public per-circuit sensors, rebuilt so that they take the app's circuit names."""
        named: list[SensorEntity] = []
        for sensor in sensors:
            match = _CIRCUIT_KEY.match(sensor.mqtt_key) if isinstance(sensor, EcoFlowDictEntity) else None
            if match is None:
                named.append(sensor)
                continue
            index = int(match.group("index"))
            key, title = match.group(0), sensor.title()
            if match.group("kind") == "Watt":
                named.append(CircuitWattsSensorEntity(client, self, key, title).for_circuit(index, "{alias} Power"))
            else:
                named.append(CircuitAmpSensorEntity(client, self, key, title).for_circuit(index, "{alias} Current"))
        return named

    # ------------------------------------------------------------------ data
    @override
    def _prepare_data_data_topic(self, raw_data: bytes) -> PreparedData:
        # raw_data stays None: in diagnostic mode the data holder merges raw_data["params"] into the
        # device params a second time, which would bring the other modules' double-encoded strings along
        data = self._prepare_data(raw_data)
        if not data:
            return PreparedData(None, None, None)

        if self.is_hub:
            fields = hub_fields_from_message(data, self.device_data.sn)
            # any module traffic proves the hub is online, even when nothing is kept
            return PreparedData(None, {"params": fields or {}}, None)

        module_sn, fields = parse_module_message(data)
        if module_sn != self.module_sn:
            return PreparedData(None, None, None)
        return PreparedData(None, {"moduleSn": module_sn, "params": fields}, None)

    @override
    def _prepare_data_get_reply_topic(self, raw_data: bytes) -> PreparedData:
        data = self._prepare_data(raw_data)
        if data.get("operateType") != "latestQuotas" or not isinstance(data.get("data"), dict):
            return PreparedData(None, None, data)

        reply = data["data"]
        online = reply_online(reply)
        if online is False:
            return PreparedData(False, None, data)

        quota_map = reply.get("quotaMap")
        if self.is_hub:
            return PreparedData(online, {"params": hub_quota_fields(quota_map, self.device_data.sn)}, data)

        fields = module_quota_fields(quota_map, self.device_data.device_type, self.module_sn)
        if not fields:
            # the hub is online but does not report this module (disconnected battery, unplugged
            # panel): neither the status nor the stale readings must look fresh
            return PreparedData(None, None, data)
        return PreparedData(online, {"params": fields}, data)

    # -------------------------------------------------------------- commands
    def _sibling_sn(self, client: EcoflowApiClient, module_type: str) -> str:
        """Serial of another module of the same hub, for commands handled by a different module."""
        devices = getattr(client, "devices", None)
        parent = self.device_data.parent
        if not isinstance(devices, dict) or parent is None:
            return self.module_sn
        for device in devices.values():
            sibling = device.device_data
            if sibling.parent is not None and sibling.parent.sn == parent.sn and sibling.device_type == module_type:
                return getattr(device, "module_sn", sibling.sn)
        _LOGGER.warning("No %s module found for %s; sending the command to %s", module_type, parent.sn, self.module_sn)
        return self.module_sn

    def _module_command(self, module_type: int, operate_type: str, params: dict[str, Any]) -> dict[str, Any]:
        """A command for this module itself."""
        return {
            "id": 123456789,
            "version": "1.0",
            "moduleSn": self.module_sn,
            "moduleType": module_type,
            "operateType": operate_type,
            "params": params,
        }

    def _ac_current_command(
        self,
        client: EcoflowApiClient,
        params: dict[str, Any],
        charge: int | None = None,
        bypass: int | None = None,
    ) -> dict[str, Any]:
        """The app sends both AC current limits together; the charging current never exceeds the input one."""
        raw_cfg = params.get("appCfg")
        app_cfg: dict[str, Any] = raw_cfg if isinstance(raw_cfg, dict) else {}
        charge_value = charge if charge is not None else app_cfg.get("acMaxCurrSer", 255)
        bypass_value = bypass if bypass is not None else app_cfg.get("passByMaxCurr", 255)
        if isinstance(charge_value, int) and isinstance(bypass_value, int) and 255 not in (charge_value, bypass_value):
            charge_value = min(charge_value, bypass_value)
        return self._inverter_command(
            client,
            {
                "wakeup": 1,
                "powerOn": 255,
                "acChgDisa": 255,
                "acRlyCtrlDisable": 255,
                "acCurrMaxSet": charge_value,
                "passByMaxCurr": bypass_value,
                "acVolSet": 255,
                "acFrequencySet": 255,
                "standbyTime": 255,
            },
        )

    def _inverter_command(self, client: EcoflowApiClient, params: dict[str, Any]) -> dict[str, Any]:
        # the inverter settings are read on ichigh but set through iclow
        return {
            "id": 123456789,
            "version": "1.0",
            "moduleSn": self._sibling_sn(client, "iclow"),
            "moduleType": INVERTER_MODULE_TYPE,
            "operateType": "dischgIcParaSet",
            "params": params,
        }

    # -------------------------------------------------------------- entities
    @override
    def texts(self, client: EcoflowApiClient) -> list[TextEntity]:
        module_type = self.device_data.device_type
        if module_type == "lddc":
            return [CircuitNameEntity(client, self, i, f"DC Out {i + 1} Name") for i in range(DC_PANEL_CHANNELS)]
        if module_type == "ldac":
            return [CircuitNameEntity(client, self, i, f"AC Out {i + 1} Name") for i in range(AC_PANEL_CHANNELS)]
        return []

    @override
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        if self.is_hub:
            return self.hubSensors(client)

        sensors = list(super().sensors(client))
        module_type = self.device_data.device_type
        if module_type.startswith("bp"):
            sensors += [
                StateOfHealthSensorEntity(client, self, "soh", const.SOH),
                CapacitySensorEntity(client, self, "designCap", "Design Capacity", False),
                EnergySensorEntity(client, self, "accuChgEnergy", const.ACCU_CHARGE_ENERGY),
                EnergySensorEntity(client, self, "accuDsgEnergy", const.ACCU_DISCHARGE_ENERGY),
                CumulativeCapacitySensorEntity(client, self, "accuChgCap", const.ACCU_CHARGE_CAP, False),
                CumulativeCapacitySensorEntity(client, self, "accuDsgCap", const.ACCU_DISCHARGE_CAP, False),
                TempSensorEntity(client, self, "maxCellTemp", "Max Cell Temperature", False),
                TempSensorEntity(client, self, "minCellTemp", "Min Cell Temperature", False),
                MiscSensorEntity(client, self, "chgSetSoc", "Charge Limit", False).with_unit_of_measurement(PERCENTAGE),
                MiscSensorEntity(client, self, "dsgSetSoc", "Discharge Limit", False).with_unit_of_measurement(
                    PERCENTAGE
                ),
                MiscSensorEntity(client, self, "kitNum", "Kit Number", False),
                MiscSensorEntity(client, self, "warnCode", "Warning Code", False),
                MiscSensorEntity(client, self, "bmsFault", "BMS Fault", False),
            ]
        elif module_type == "iclow":
            sensors += [
                MiscSensorEntity(client, self, "acAlwaysOn", "AC Always On", False),
                MiscSensorEntity(
                    client, self, "invNoLoadPwr", "Inverter No Load Power", False
                ).with_unit_of_measurement(UnitOfPower.WATT),
            ]
        elif module_type == "ichigh":
            sensors += [
                MiscSensorEntity(client, self, "outVa", "AC Out Apparent Power").with_unit_of_measurement("VA"),
                InWattsSensorEntity(client, self, "chgWatts", "AC Charge Power"),
                MiscSensorEntity(
                    client, self, "appCfg.acVolSet", "AC Out Voltage Setting", False
                ).with_unit_of_measurement(UnitOfElectricPotential.VOLT),
                MiscSensorEntity(
                    client, self, "appCfg.acFreqSet", "AC Out Frequency Setting", False
                ).with_unit_of_measurement(UnitOfFrequency.HERTZ),
            ]
        elif module_type == "ldac":
            sensors = self._named_circuit_sensors(client, sensors)
            # the 2nd generation panel feeds two AC buses (L1 / L2 for split phase)
            sensors += [
                OutWattsSensorEntity(client, self, "acTotalWatts1", "AC L1 Power"),
                OutWattsSensorEntity(client, self, "acTotalWatts2", "AC L2 Power"),
                OutMilliVoltSensorEntity(client, self, "acInVol2", "AC L2 In Voltage"),
            ]
        elif module_type == "lddc":
            sensors = self._named_circuit_sensors(client, sensors)
            # the 2nd generation panel has 16 DC circuits: dcChWatt carries 12, the high current
            # circuits come in a second set of arrays (F13 to F16 as far as the data shows)
            sensors += [
                CircuitWattsSensorEntity(
                    client, self, f"dcChWattV2[{i}]", f"DC Out {DC_PANEL_SWITCHES + i + 1}"
                ).for_circuit(DC_PANEL_SWITCHES + i, "{alias} Power")
                for i in range(DC_PANEL_CHANNELS - DC_PANEL_SWITCHES)
            ]
            sensors += [
                CircuitAmpSensorEntity(
                    client, self, f"dcChCurV2[{i}]", f"DC Ampere Out {DC_PANEL_SWITCHES + i + 1}"
                ).for_circuit(DC_PANEL_SWITCHES + i, "{alias} Current")
                for i in range(DC_PANEL_CHANNELS - DC_PANEL_SWITCHES)
            ]
            sensors.append(MiscSensorEntity(client, self, "dcChRelayV2", "DC Out 13-16 Ch Relay", False))
        elif module_type == "bbcin":
            sensors += [
                MiscSensorEntity(client, self, "alternatorMode", "Alternator Mode", False),
                MiscSensorEntity(client, self, "thirdWatts", "Third Input Power", False).with_unit_of_measurement(
                    UnitOfPower.WATT
                ),
                MiscSensorEntity(client, self, "setPortType", "Input Port Type", False),
            ]
        elif module_type == "bbcout":
            sensors += [
                MiscSensorEntity(client, self, "dcOutSta", "DC Output Enabled"),
                MiscSensorEntity(client, self, "beepEn", "Beeper", False),
                MiscSensorEntity(client, self, "dcAlwaysOn", "DC Always On", False),
                MiscSensorEntity(client, self, "noLoadPwr", "No Load Power", False).with_unit_of_measurement(
                    UnitOfPower.WATT
                ),
                MiscSensorEntity(client, self, "hubWorkMode", "Hub Work Mode", False),
                MiscSensorEntity(client, self, "dayEnergy", "DC Out Energy Today", False),
            ]
        return sensors

    def hubSensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            LevelSensorEntity(client, self, "totalSoc", const.COMBINED_BATTERY_LEVEL),
            InWattsSensorEntity(client, self, "totalInWatts", const.TOTAL_IN_POWER),
            OutWattsSensorEntity(client, self, "totalOutWatts", const.TOTAL_OUT_POWER),
            TotalCurrentSensorEntity(client, self, "totalAmp", "Total Current"),
            RemainSensorEntity(client, self, "totalRemainTime", const.REMAINING_TIME),
            MiscSensorEntity(client, self, "totalFullCap", "Total Full Capacity", False).with_unit_of_measurement("Ah"),
            MiscSensorEntity(client, self, "totalChgDsgState", "Total Charge Discharge State", False),
            MiscSensorEntity(client, self, "bmsChgUpline", "Charge Upper Limit", False).with_unit_of_measurement(
                PERCENTAGE
            ),
            MiscSensorEntity(client, self, "bmsDsgDownline", "Discharge Lower Limit", False).with_unit_of_measurement(
                PERCENTAGE
            ),
            MiscSensorEntity(client, self, "oilStartDownline", "Generator Start Level", False).with_unit_of_measurement(
                PERCENTAGE
            ),
            MiscSensorEntity(client, self, "oilStopUpline", "Generator Stop Level", False).with_unit_of_measurement(
                PERCENTAGE
            ),
            MiscSensorEntity(client, self, "scenes", "Scene", False),
            MiscSensorEntity(client, self, "gpsOn", "GPS Enabled", False),
            MiscSensorEntity(client, self, "gpsCon", "GPS Connected", False),
            QuotaStatusSensorEntity(client, self),
        ]

    @override
    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        module_type = self.device_data.device_type
        if module_type == "iclow":
            # its switches read a state only ichigh reports; see there
            return []
        if module_type == "ichigh":
            return [
                # the inverter settings are read on ichigh; the app sets them through iclow
                # disabled by default: switching the priority while on shore power dropped the AC output
                # of the hub this was captured on, and the owner had to press the hub's AC button
                EnabledEntity(
                    client,
                    self,
                    "passByModeEn",
                    "Grid Priority",
                    lambda value: {
                        "id": 123456789,
                        "version": "1.0",
                        "moduleSn": self._sibling_sn(client, "iclow"),
                        "moduleType": INVERTER_MODULE_TYPE,
                        "operateType": "dsgIcParaSet",
                        "params": {**_GRID_PRIORITY_PARAMS, "passByModeEn": 1 if value == 1 else 2},
                    },
                    enabled=False,
                    enableValue=1,
                    disableValue=2,
                ),
                # disabled by default: cutting the AC output remotely cuts whatever keeps the hub online
                EnabledEntity(
                    client,
                    self,
                    "invSwSta",
                    "AC Output",
                    lambda value: self._inverter_command(
                        client,
                        {
                            "powerOn": 1 if value == 1 else 0,
                            "acCurrMaxSet": 255,
                            "acChgDisa": 255,
                            "acFrequencySet": 255,
                            "acVolSet": 255,
                        },
                    ),
                    enabled=False,
                    enableValue=1,
                ),
                EnabledEntity(
                    client,
                    self,
                    "appCfg.acChgDisable",
                    "AC Charging",
                    lambda value: self._inverter_command(
                        client,
                        {
                            "acCurrMaxSet": 255,
                            "powerOn": 255,
                            "acChgDisa": 0 if value == 0 else 1,
                            "acFrequencySet": 255,
                            "wakeup": 1,
                            "standbyTime": 255,
                            "acRlyCtrlDisable": 255,
                            "acVolSet": 255,
                            "passByMaxCurr": 255,
                        },
                    ),
                    enableValue=0,
                    disableValue=1,
                ),
            ]
        if module_type == "kitscc":
            return [
                EnabledEntity(
                    client,
                    self,
                    "mppt1SwSta",
                    "Port 2 Charging",
                    lambda value: self._module_command(
                        MPPT_MODULE_TYPE, "pvSwitch", {**_PV_PARAMS, "mpptt1": 1 if value == 1 else 0}
                    ),
                    enableValue=1,
                ),
                EnabledEntity(
                    client,
                    self,
                    "mppt2SwSta",
                    "Port 3 Charging",
                    lambda value: self._module_command(
                        MPPT_MODULE_TYPE, "pvSwitch", {**_PV_PARAMS, "mpptt2": 1 if value == 1 else 0}
                    ),
                    enableValue=1,
                ),
            ]
        if module_type == "bbcin":
            return [
                # chgPause 1 pauses charging from port 1 (ALT IN 1 / PV IN 1)
                EnabledEntity(
                    client,
                    self,
                    "chgPause",
                    "Port 1 Charging",
                    lambda value: self._module_command(
                        DC_IN_MODULE_TYPE, "chgParaSet", {**_DC_IN_PARAMS, "chgPause": 0 if value == 0 else 1}
                    ),
                    enableValue=0,
                    disableValue=1,
                ),
            ]
        if module_type == "bbcout":
            return [
                EnabledEntity(
                    client,
                    self,
                    "dcOutSta",
                    "Main DC Output",
                    lambda value: self._module_command(
                        DC_OUT_MODULE_TYPE, "dischgParaSet", {**_DC_OUT_PARAMS, "swSta": 1 if value == 1 else 0}
                    ),
                    enableValue=1,
                ),
                EnabledEntity(
                    client,
                    self,
                    "beepEn",
                    "Beeper",
                    lambda value: self._module_command(
                        DC_OUT_MODULE_TYPE, "dischgParaSet", {**_DC_OUT_PARAMS, "beepEn": 1 if value == 1 else 0}
                    ),
                    enableValue=1,
                ),
            ]
        if module_type == "lddc":
            switches: list[SwitchEntity] = [
                CircuitSwitchEntity(
                    client,
                    self,
                    f"dcChRelay.{n}",
                    f"DC Switch {n}",
                    self.dcSwitchFunction,
                    bits=DC_PANEL_SWITCHES,
                ).for_circuit(n - 1)
                for n in range(1, DC_PANEL_SWITCHES + 1)
            ]
            switches += [
                CircuitSwitchEntity(
                    client,
                    self,
                    f"dcChRelayV2.{n - DC_PANEL_SWITCHES}",
                    f"DC Switch {n}",
                    self.dcSwitchFunction,
                    bits=DC_PANEL_CHANNELS - DC_PANEL_SWITCHES,
                    command_index=n - 1,
                ).for_circuit(n - 1)
                for n in range(DC_PANEL_SWITCHES + 1, DC_PANEL_CHANNELS + 1)
            ]
            return switches
        return super().switches(client)

    @override
    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        module_type = self.device_data.device_type
        if module_type == "bbcin":
            return [
                DictSelectEntity(
                    client,
                    self,
                    "setPortType",
                    "Port 1 Charging Mode",
                    _PORT_MODES,
                    lambda value: self._module_command(
                        DC_IN_MODULE_TYPE, "chgParaSet", {**_DC_IN_PARAMS, "setPortType": value}
                    ),
                ),
                DictSelectEntity(
                    client,
                    self,
                    "alternatorMode",
                    "Port 1 Alternator Type",
                    _ALTERNATOR_TYPES,
                    lambda value: self._module_command(
                        DC_IN_MODULE_TYPE, "chgDsgAltmodeSet", {"rsvd": ["0"] * 20, "alternatorMode": value}
                    ),
                ),
            ]
        if module_type == "bbcout":
            return [
                # off by default: 24 V on 12 V loads can damage them, the app asks for confirmation
                DictSelectEntity(
                    client,
                    self,
                    "cfgVolTag",
                    "DC Output Voltage",
                    _DC_OUTPUT_VOLTAGES,
                    lambda value: self._module_command(
                        DC_OUT_MODULE_TYPE, "dischgParaSet", {**_DC_OUT_PARAMS, "volTag": value}
                    ),
                    enabled=False,
                ),
            ]
        if module_type == "kitscc":
            return [
                DictSelectEntity(
                    client,
                    self,
                    "setPort1Type",
                    "Port 2 Charging Mode",
                    _PORT_MODES,
                    lambda value: self._module_command(
                        MPPT_MODULE_TYPE, "pvSwitch", {**_PV_PARAMS, "setPort1Type": value}
                    ),
                ),
                DictSelectEntity(
                    client,
                    self,
                    "setPort2Type",
                    "Port 3 Charging Mode",
                    _PORT_MODES,
                    lambda value: self._module_command(
                        MPPT_MODULE_TYPE, "pvSwitch", {**_PV_PARAMS, "setPort2Type": value}
                    ),
                ),
            ]
        return super().selects(client)

    @override
    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        if self.is_hub:
            return [
                MinBatteryLevelEntity(
                    client,
                    self,
                    "bmsDsgDownline",
                    const.MIN_DISCHARGE_LEVEL,
                    0,
                    30,
                    lambda value: {
                        "id": 123456789,
                        "version": "1.0",
                        "moduleSn": NO_MODULE_SN,
                        "moduleType": 0,
                        "operateType": "socLowerLimit",
                        "params": {"minDsgSoc": int(value)},
                    },
                ),
                MaxBatteryLevelEntity(
                    client,
                    self,
                    "bmsChgUpline",
                    const.MAX_CHARGE_LEVEL,
                    50,
                    100,
                    lambda value: {
                        "id": 123456789,
                        "version": "1.0",
                        "moduleSn": NO_MODULE_SN,
                        "moduleType": 0,
                        "operateType": "socUpperLimit",
                        "params": {"maxChgSoc": int(value)},
                    },
                ),
            ]
        module_type = self.device_data.device_type
        if module_type == "iclow":
            return []
        if module_type == "ichigh":
            return [
                AcChargingPowerInAmpereEntity(
                    client,
                    self,
                    "appCfg.acMaxCurrSer",
                    "AC Charging Current",
                    *AC_CHARGE_CURRENT_RANGE,
                    lambda value, params: self._ac_current_command(client, params, charge=int(value)),
                ).with_unit_of_measurement(UnitOfElectricCurrent.AMPERE),
                AcChargingPowerInAmpereEntity(
                    client,
                    self,
                    "appCfg.passByMaxCurr",
                    "AC Input Current",
                    *AC_INPUT_CURRENT_RANGE,
                    lambda value, params: self._ac_current_command(client, params, bypass=int(value)),
                ).with_unit_of_measurement(UnitOfElectricCurrent.AMPERE),
            ]
        return super().numbers(client)
