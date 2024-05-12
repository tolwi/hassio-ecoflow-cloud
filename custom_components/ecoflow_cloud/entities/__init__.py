from __future__ import annotations
import inspect
from typing import Any, Callable, Optional, OrderedDict, Mapping

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import Entity, EntityCategory

from ..mqtt.ecoflow_mqtt import EcoflowMQTTClient


class EcoFlowAbstractEntity(Entity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, client: EcoflowMQTTClient, title: str, key: str):
        self._client = client
        self._attr_name = title
        self._attr_device_info = client.device_info_main
        self._attr_unique_id = self.gen_unique_id(client.device_sn, key)

    def send_get_message(self, command: dict):
        self._client.send_get_message(command)

    def send_set_message(self, target_dict: dict[str, Any] | None, command: dict):
        self._client.send_set_message(target_dict, command)

    @staticmethod
    def gen_unique_id(sn: str, key: str):
        return 'ecoflow-' + sn + '-' + key.replace('.', '-').replace('_', '-')


class EcoFlowDictEntity(EcoFlowAbstractEntity):

    def __init__(self, client: EcoflowMQTTClient, mqtt_key: str, title: str, enabled: bool = True,
                 auto_enable: bool = False) -> object:
        super().__init__(client, title, mqtt_key)
        self._mqtt_key = mqtt_key
        self._auto_enable = auto_enable
        self._attr_entity_registry_enabled_default = enabled
        self.__attributes_mapping: dict[str, str] = {}
        self.__attrs = OrderedDict[str, Any]()

    def attr(self, mqtt_key: str, title: str, default: Any) -> EcoFlowDictEntity:
        self.__attributes_mapping[mqtt_key] = title
        self.__attrs[title] = default
        return self

    @property
    def mqtt_key(self):
        return self._mqtt_key

    @property
    def auto_enable(self):
        return self._auto_enable

    def send_set_message(self, target_value: Any, command: dict):
        super().send_set_message({self._mqtt_key: target_value}, command)

    @property
    def enabled_default(self):
        return self._attr_entity_registry_enabled_default

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        d = self._client.data.params_observable().subscribe(self._updated)
        self.async_on_remove(d.dispose)

    def _updated(self, data: dict[str, Any]):
        # update attributes
        for key, title in self.__attributes_mapping.items():
            if key in data:
                self.__attrs[title] = data[key]

        # update value
        if self._mqtt_key in data:
            self._attr_available = True
            if self._auto_enable:
                self._attr_entity_registry_enabled_default = True

            if self._update_value(data[self._mqtt_key]):
                self.schedule_update_ha_state()

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return self.__attrs

    def _update_value(self, val: Any) -> bool:
        return False


class EcoFlowBaseCommandEntity(EcoFlowDictEntity):
    def __init__(self, client: EcoflowMQTTClient, mqtt_key: str, title: str,
                 command: Callable[[int, Optional[dict[str, Any]]], dict[str, Any]] | None,
                 enabled: bool = True, auto_enable: bool = False):
        super().__init__(client, mqtt_key, title, enabled, auto_enable)
        self._command = command

    def command_dict(self, value: int) -> dict[str, any] | None:
        if self._command:
            p_count = len(inspect.signature(self._command).parameters)
            if p_count == 1:
                return self._command(value)
            elif p_count == 2:
                return self._command(value, self._client.data.params)
        else:
            return None


class BaseNumberEntity(NumberEntity, EcoFlowBaseCommandEntity):
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, client: EcoflowMQTTClient, mqtt_key: str, title: str, min_value: int, max_value: int,
                 command: Callable[[int], dict[str, any]] | None, enabled: bool = True,
                 auto_enable: bool = False):
        super().__init__(client, mqtt_key, title, command, enabled, auto_enable)
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

