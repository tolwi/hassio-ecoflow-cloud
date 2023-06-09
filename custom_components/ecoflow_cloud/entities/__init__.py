from typing import Any, Callable

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import Entity, EntityCategory

from ..mqtt.ecoflow_mqtt import EcoflowMQTTClient


class EcoFlowBaseEntity(Entity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, client: EcoflowMQTTClient, mqtt_key: str, title: str, enabled: bool = True,
                 auto_enable: bool = False) -> object:
        # self._attr_available = False
        self._client = client
        self._mqtt_key = mqtt_key
        self._auto_enable = auto_enable

        self._attr_name = title
        self._attr_entity_registry_enabled_default = enabled
        self._attr_device_info = client.device_info_main
        self._attr_unique_id = 'ecoflow-' + client.device_sn + '-' + mqtt_key.replace('.', '-').replace('_', '-')

    @property
    def mqtt_key(self):
        return self._mqtt_key

    @property
    def auto_enable(self):
        return self._auto_enable

    @property
    def enabled_default(self):
        return self._attr_entity_registry_enabled_default

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        d = self._client.data.observable().subscribe(self.__updated)
        self.async_on_remove(d.dispose)

    def __updated(self, data: dict[str, Any]):
        if self._mqtt_key in data:
            self._attr_available = True
            if self._auto_enable:
                self._attr_entity_registry_enabled_default = True

            if self._update_value(data[self._mqtt_key]):
                self.async_write_ha_state()

    def _update_value(self, val: Any) -> bool:
        return False

    def send_message(self, target_value: Any, command: dict):
        self._client.send_message({self._mqtt_key: target_value}, command)


class EcoFlowBaseCommandEntity(EcoFlowBaseEntity):
    def __init__(self, client: EcoflowMQTTClient, mqtt_key: str, title: str,
                 command: Callable[[int], dict[str, any]] | None, enabled: bool = True, auto_enable: bool = False):
        super().__init__(client, mqtt_key, title, enabled, auto_enable)
        self._command = command

    def command_dict(self, value: int) -> dict[str, any] | None:
        if self._command:
            return self._command(value)
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


class BaseSensorEntity(SensorEntity, EcoFlowBaseEntity):

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
