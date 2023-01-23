from typing import Any

from homeassistant import const
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

from .mqtt.ecoflow_mqtt import EcoflowMQTTClient, EcoflowAuthentication

DOMAIN = "ecoflow-cloud"

_PLATFORMS = {
    # Platform.BINARY_SENSOR,
    # Platform.LIGHT,
    Platform.NUMBER,
    # Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
}


class EcoFlowBaseEntity(Entity):
    _attr_has_entity_name = True
    _attr_should_poll = False
    _connected = False

    def __init__(self, client: EcoflowMQTTClient, module_type: str, mqtt_key: str, title: str, enabled: bool = True):
        self._attr_available = False
        self._client = client
        self._module_type = module_type
        self._mqtt_key = mqtt_key

        self._attr_name = title
        self._attr_entity_registry_enabled_default = enabled
        self._attr_device_info = client.device_info_main
        self._attr_unique_id = 'ecoflow-' + client.device_sn + '-' + mqtt_key.replace('.', '-').replace('_', '-')

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        d = self._client.data.topic(self._module_type).subscribe(self.__updated)
        self.async_on_remove(d.dispose)

    def __updated(self, data: dict[str, Any]):
        if self._mqtt_key in data:
            self._attr_available = True
            self._attr_native_value = self._prepare_value(data[self._mqtt_key])
            self.async_write_ha_state()

    def _prepare_value(self, val: Any) -> Any:
        return val


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    auth = EcoflowAuthentication(entry.data[const.CONF_USERNAME], entry.data[const.CONF_PASSWORD])
    await hass.async_add_executor_job(auth.authorize)
    client = EcoflowMQTTClient(hass, entry, auth)

    hass.data[DOMAIN][entry.entry_id] = client
    hass.config_entries.async_setup_platforms(entry, _PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    if not await hass.config_entries.async_unload_platforms(entry, _PLATFORMS):
        return False

    client: EcoflowMQTTClient = hass.data[DOMAIN].pop(entry.entry_id)
    client.stop()
    return True
