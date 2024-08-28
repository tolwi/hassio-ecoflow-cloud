from __future__ import annotations

import inspect
from typing import Any, Callable, OrderedDict, Mapping

import jsonpath_ng.ext as jp
from homeassistant.components.button import ButtonEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import EntityCategory, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.ecoflow_cloud import ECOFLOW_DOMAIN
from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import BaseDevice, EcoflowDeviceUpdateCoordinator


class EcoFlowAbstractEntity(CoordinatorEntity[EcoflowDeviceUpdateCoordinator]):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, client: EcoflowApiClient, device: BaseDevice, title: str, key: str):
        super().__init__(device.coordinator)
        self._client: EcoflowApiClient = client
        self._device: BaseDevice = device
        self._attr_name = title
        self._attr_unique_id = self.__gen_unique_id(self._device.device_info.sn, key)

    @property
    def device_info(self) -> DeviceInfo | None:
        return DeviceInfo(
            identifiers={(ECOFLOW_DOMAIN, f"{self._type_prefix()}{self._device.device_info.sn}")},
            manufacturer="EcoFlow",
            name=self._device.device_info.name,
            model=self._device.device_info.device_type,
        )

    def _type_prefix(self):
        return "api-" if self._device.device_info.public_api else ""

    def __gen_unique_id(self, sn: str, key: str):
        return ('ecoflow-' + self._type_prefix() + sn + '-' + key.replace('.', '-')
                .replace('_', '-')
                .replace('[', '-')
                .replace(']', '-')
                )


class EcoFlowDictEntity(EcoFlowAbstractEntity):

    def __init__(self, client: EcoflowApiClient, device: BaseDevice, mqtt_key: str, title: str, enabled: bool = True,
                 auto_enable: bool = False):
        super().__init__(client, device, title, mqtt_key)

        self.__mqtt_key = mqtt_key
        self._mqtt_key_adopted = self._adopt_json_key(mqtt_key)
        self._mqtt_key_expr = jp.parse(self._mqtt_key_adopted)

        self._auto_enable = auto_enable
        self._attr_entity_registry_enabled_default = enabled
        self._attr_entity_registry_visible_default = enabled
        self._attr_available  = enabled
        self.__attributes_mapping: dict[str, str] = {}
        self.__attrs = OrderedDict[str, Any]()

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
        if self.coordinator.data.changed:
            self._updated(self.coordinator.data.data_holder.params)

    def _updated(self, data: dict[str, Any]):
        # update attributes
        for key, title in self.__attributes_mapping.items():
            key_expr = jp.parse(self._adopt_json_key(key))
            attr_values = key_expr.find(data)
            if len(attr_values) == 1:
                self.__attrs[title] = attr_values[0].value

        # update value
        values = self._mqtt_key_expr.find(data)
        if len(values) == 1:
            self._attr_available = True
            if self._auto_enable:
                self._attr_entity_registry_enabled_default = True
                self._attr_entity_registry_visible_default = True

            if self._update_value(values[0].value):
                self.schedule_update_ha_state()

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return self.__attrs

    def _update_value(self, val: Any) -> bool:
        return False


class EcoFlowBaseCommandEntity(EcoFlowDictEntity):
    def __init__(self, client: EcoflowApiClient, device: BaseDevice, mqtt_key: str, title: str,
                 command: Callable[[Any], dict[str, Any]] | Callable[[Any, dict[str, Any]], dict[str, Any]] | None,
                 enabled: bool = True, auto_enable: bool = False):
        super().__init__(client, device, mqtt_key, title, enabled, auto_enable)
        self._command = command

    def command_dict(self, value: Any) -> dict[str, Any] | None:
        if self._command:
            p_count = len(inspect.signature(self._command).parameters)
            if p_count == 1:
                return self._command(value)
            elif p_count == 2:
                return self._command(value, self._device.data.params)
        else:
            return None

    def send_set_message(self, target_value: Any, command: dict):
        self._client.mqtt_client.send_set_message(self._device.device_info.sn, {self._mqtt_key_adopted: target_value}, command)


class BaseNumberEntity(NumberEntity, EcoFlowBaseCommandEntity):
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, client: EcoflowApiClient, device: BaseDevice, mqtt_key: str, title: str, min_value: int, max_value: int,
                 command: Callable[[int], dict[str, Any]] | Callable[[int, dict[str, Any]], dict[str, Any]] | None,
                 enabled: bool = True,
                 auto_enable: bool = False):
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


class BaseSwitchEntity(SwitchEntity, EcoFlowBaseCommandEntity):
    pass


class BaseSelectEntity(SelectEntity, EcoFlowBaseCommandEntity):
    pass


class BaseButtonEntity(ButtonEntity, EcoFlowBaseCommandEntity):
    pass
