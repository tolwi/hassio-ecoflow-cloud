import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er


from .config.const import CONF_DEVICE_TYPE, CONF_USERNAME, CONF_PASSWORD, OPTS_POWER_STEP, OPTS_REFRESH_PERIOD_SEC, \
    DEFAULT_REFRESH_PERIOD_SEC, CONF_DEVICE_ID
from .mqtt.ecoflow_mqtt import EcoflowMQTTClient, EcoflowAuthentication

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ecoflow_cloud"
CONFIG_VERSION = 3

_PLATFORMS = {
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.BUTTON,

}

ATTR_STATUS_SN = "SN"
ATTR_STATUS_UPDATES = "status_request_count"
ATTR_STATUS_LAST_UPDATE = "status_last_update"
ATTR_STATUS_DATA_LAST_UPDATE = "data_last_update"
ATTR_STATUS_RECONNECTS = "reconnects"
ATTR_STATUS_PHASE = "status_phase"


async def async_migrate_entry(hass, config_entry: ConfigEntry):
    """Migrate old entry."""
    if config_entry.version == 1:
        from .devices.registry import devices as device_registry
        device = device_registry[config_entry.data[CONF_DEVICE_TYPE]]

        new_data = {**config_entry.data}
        new_options = {OPTS_POWER_STEP: device.charging_power_step(),
                       OPTS_REFRESH_PERIOD_SEC: DEFAULT_REFRESH_PERIOD_SEC}

        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new_data, options=new_options)
        _LOGGER.info("Migration to version %s successful", config_entry.version)

    if config_entry.version < CONFIG_VERSION:
        from .devices.registry import devices as device_registry
        from .entities import EcoFlowAbstractEntity
        from .devices import EntityMigration, MigrationAction

        device = device_registry[config_entry.data[CONF_DEVICE_TYPE]]
        device_sn = config_entry.data[CONF_DEVICE_ID]
        entity_registry = er.async_get(hass)

        for v in (config_entry.version, CONFIG_VERSION):
            migrations: list[EntityMigration] = device.migrate(v)
            for m in migrations:
                if m.action == MigrationAction.REMOVE:
                    entity_id = entity_registry.async_get_entity_id(
                                                domain=m.domain,
                                                platform=DOMAIN,
                                                unique_id=EcoFlowAbstractEntity.gen_unique_id(sn=device_sn, key=m.key))

                    if entity_id:
                        _LOGGER.info(".... removing entity_id = %s", entity_id)
                        entity_registry.async_remove(entity_id)

        config_entry.version = CONFIG_VERSION
        hass.config_entries.async_update_entry(config_entry)
        _LOGGER.info("Migration to version %s successful", config_entry.version)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    auth = EcoflowAuthentication(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])
    await hass.async_add_executor_job(auth.authorize)
    client = EcoflowMQTTClient(hass, entry, auth)

    hass.data[DOMAIN][entry.entry_id] = client
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    if not await hass.config_entries.async_unload_platforms(entry, _PLATFORMS):
        return False

    client: EcoflowMQTTClient = hass.data[DOMAIN].pop(entry.entry_id)
    client.stop()
    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
