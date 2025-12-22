from __future__ import annotations

import inspect
from typing import Any, Callable, Mapping, Optional, OrderedDict, cast

import jsonpath_ng.ext as jp
from homeassistant.components.button import ButtonEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import EntityCategory, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .. import ECOFLOW_DOMAIN
from ..api import EcoflowApiClient, Message
from ..devices import (
    BaseDevice,
    EcoflowDeviceUpdateCoordinator,
)
import logging

_LOGGER = logging.getLogger(__name__)


class EcoFlowAbstractEntity(CoordinatorEntity[EcoflowDeviceUpdateCoordinator]):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self, client: EcoflowApiClient, device: BaseDevice, title: str, key: str
    ):
        super().__init__(device.coordinator)
        self._client: EcoflowApiClient = client
        self._device: BaseDevice = device
        self._attr_name = title
        self._attr_unique_id = self._gen_unique_id(self._device.device_data.sn, key)

    @property
    def device_info(self) -> DeviceInfo | None:
        name = self._device.device_data.name
        if self._device.device_data.display_name:
            name = self._device.device_data.display_name
        return DeviceInfo(
            identifiers={
                (ECOFLOW_DOMAIN, f"{self._type_prefix()}{self._device.device_data.sn}")
            },
            manufacturer="EcoFlow",
            name=name,
            model=self._device.device_data.device_type,
            serial_number=self._device.device_data.sn,
        )

    def _type_prefix(self):
        return "api-" if self._device.device_info.public_api else ""

    def _gen_unique_id(self, sn: str, key: str):
        return (
            "ecoflow-"
            + self._type_prefix()
            + sn
            + "-"
            + key.replace(".", "-")
            .replace("_", "-")
            .replace("[", "-")
            .replace("]", "-")
        )

    def title(self) -> str:
        return self._attr_name

    def with_category(self, category: EntityCategory) -> EcoFlowAbstractEntity:
        self._attr_entity_category = category
        return self

    def with_device_class(self, device_class: str) -> EcoFlowAbstractEntity:
        self._attr_device_class = device_class
        return self

    def with_icon(self, icon: str) -> EcoFlowAbstractEntity:
        self._attr_icon = icon
        return self

    def with_state_class(self, state_class: str) -> EcoFlowAbstractEntity:
        self._attr_state_class = state_class
        return self

    def with_unit_of_measurement(self, unit: str) -> EcoFlowAbstractEntity:
        self._attr_native_unit_of_measurement = unit
        return self


class EcoFlowDictEntity(EcoFlowAbstractEntity):
    def __init__(
        self,
        client: EcoflowApiClient,
        device: BaseDevice,
        mqtt_key: str,
        title: str,
        enabled: bool = True,
        auto_enable: bool = False,
        diagnostic: Optional[bool] = None,
    ):
        super().__init__(client, device, title, mqtt_key)

        self.__mqtt_key = mqtt_key
        self._mqtt_key_adopted = self._adopt_json_key(mqtt_key)
        self._mqtt_key_expr = jp.parse(self._mqtt_key_adopted)
        self._multiple_value_sum = False

        self._auto_enable = auto_enable
        self._attr_entity_registry_enabled_default = enabled
        self._attr_entity_registry_visible_default = enabled
        self._attr_available = enabled
        self.__attributes_mapping: dict[str, str] = {}
        self.__attrs = OrderedDict[str, Any]()
        if diagnostic is not None:
            self._attr_entity_category = (
                EntityCategory.DIAGNOSTIC if diagnostic else None
            )

    def attr(self, mqtt_key: str, title: str, default: Any) -> EcoFlowDictEntity:
        self.__attributes_mapping[mqtt_key] = title
        self.__attrs[title] = default
        return self

    def _adopt_json_key(self, key: str):
        if self._device.flat_json():
            return "'" + key + "'"
        else:
            return key

    @property
    def mqtt_key(self):
        return self.__mqtt_key

    @property
    def auto_enable(self):
        return self._auto_enable

    @property
    def enabled_default(self):
        return self._attr_entity_registry_enabled_default

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        # d = self._device.data.params_observable().subscribe(self._updated)
        # self.async_on_remove(d.dispose)

    def _handle_coordinator_update(self) -> None:
        try:
            changed = getattr(self.coordinator.data, "changed", None)
        except Exception as exc:
            _LOGGER.exception(
                "Failed to read 'changed' attribute from coordinator data for entity %s",
                self._attr_unique_id,
            )
            changed = None
        _LOGGER.debug(
            "Entity %s _handle_coordinator_update called (coordinator.changed=%s)",
            self._attr_unique_id,
            changed,
        )
        if changed is False:
            return

        self._updated(self.coordinator.data.data_holder.params)

    def _updated(self, data: dict[str, Any]):
        # update attributes
        attr_changed = False
        for key, title in self.__attributes_mapping.items():
            key_expr = jp.parse(self._adopt_json_key(key))
            attr_values = key_expr.find(data)
            if len(attr_values) == 1:
                if self.__attrs.get(title) != attr_values[0].value:
                    self.__attrs[title] = attr_values[0].value
                    attr_changed = True
            elif len(attr_values) > 1 and self._multiple_value_sum:
                total = attr_values[0].value
                for v in attr_values[1:]:
                    total += v.value
                if self.__attrs.get(title) != total:
                    self.__attrs[title] = total
                    attr_changed = True

        # update value
        values = self._mqtt_key_expr.find(data)
        if len(values) == 1 or (len(values) > 1 and self._multiple_value_sum):
            self._attr_available = True
            if self._auto_enable:
                self._attr_entity_registry_enabled_default = True
                self._attr_entity_registry_visible_default = True

            total = values[0].value
            if len(values) > 1 and self._multiple_value_sum:
                for v in values[1:]:
                    total += v.value
            value_changed = False
            if self._update_value(total):
                value_changed = True
                _LOGGER.debug(
                    "Entity %s value changed to %s (mqtt_key=%s)",
                    self._attr_unique_id,
                    total,
                    self.__mqtt_key,
                )

            if value_changed or attr_changed:
                self.schedule_update_ha_state()

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return self.__attrs

    def _update_value(self, val: Any) -> bool:
        return False

    # This allows summing the multiple values found by a jsonpath expression that returns multiple matches
    # Specifically useful for multiple circuits being combined into a single entity in the Smart Home Panels
    def with_multiple_value_sum(self) -> EcoFlowDictEntity:
        self._multiple_value_sum = True
        return self

    def multiple_value_sum_enabled(self) -> bool:
        return self._multiple_value_sum

class EcoFlowBaseCommandEntity[_CommandArg](EcoFlowDictEntity):
    def __init__(
        self,
        client: EcoflowApiClient,
        device: BaseDevice,
        mqtt_key: str,
        title: str,
        command: Callable[[_CommandArg], dict[str, Any] | Message]
        | Callable[[_CommandArg, dict[str, Any]], dict[str, Any] | Message]
        | None,
        enabled: bool = True,
        auto_enable: bool = False,
    ):
        super().__init__(client, device, mqtt_key, title, enabled, auto_enable)
        self._command = command

    def command_dict(self, value: _CommandArg) -> dict[str, Any] | Message | None:
        if self._command:
            p_count = len(inspect.signature(self._command).parameters)
            if p_count == 1:
                command = cast(
                    Callable[[_CommandArg], dict[str, Any] | Message], self._command
                )
                return command(value)
            elif p_count == 2:
                command = cast(
                    Callable[[_CommandArg, dict[str, Any]], dict[str, Any] | Message],
                    self._command,
                )
                return command(value, self._device.data.params)
            return None
        else:
            return None

    def send_set_message(self, target_value: Any, command: dict | Message):
        self._client.send_set_message(
            self._device.device_info.sn, {self._mqtt_key_adopted: target_value}, command
        )


class BaseNumberEntity(NumberEntity, EcoFlowBaseCommandEntity[int]):
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        client: EcoflowApiClient,
        device: BaseDevice,
        mqtt_key: str,
        title: str,
        min_value: int,
        max_value: int,
        command: Callable[[int], dict[str, Any] | Message]
        | Callable[[int, dict[str, Any]], dict[str, Any] | Message]
        | None,
        enabled: bool = True,
        auto_enable: bool = False,
    ):
        super().__init__(client, device, mqtt_key, title, command, enabled, auto_enable)
        self._attr_native_max_value = max_value
        self._attr_native_min_value = min_value

    def _update_value(self, val: Any) -> bool:
        if self._attr_native_value != val:
            self._attr_native_value = val
            return True
        else:
            return False


class BaseSensorEntity(SensorEntity, EcoFlowDictEntity):
    def _update_value(self, val: Any) -> bool:
        if self._attr_native_value != val:
            self._attr_native_value = val
            return True
        else:
            return False


class BaseSwitchEntity[_CommandArg](
    SwitchEntity, EcoFlowBaseCommandEntity[_CommandArg]
):
    pass


class BaseSelectEntity[_CommandArg](
    SelectEntity, EcoFlowBaseCommandEntity[_CommandArg]
):
    pass


class BaseButtonEntity[_CommandArg](
    ButtonEntity, EcoFlowBaseCommandEntity[_CommandArg]
):
    pass
