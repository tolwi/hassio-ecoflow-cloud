import logging
import dataclasses
from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import EcoflowApiClient
from .api.private_api import EcoflowPrivateApiClient
from .api.public_api import EcoflowPublicApiClient

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ecoflow_cloud"
CONFIG_VERSION = 6

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

CONF_AUTH_TYPE: Final = "auth_type"

CONF_USERNAME: Final = "username"
CONF_PASSWORD: Final = "password"
CONF_ACCESS_KEY: Final = "access_key"
CONF_SECRET_KEY: Final = "secret_key"
CONF_LOAD_AUTOMATIQUE: Final = "load_automatique_device"
CONF_INSTALLATION_SITE: Final = "installation_site"
CONF_DEVICE_LIST: Final = "devices_list"
CONF_ENTRY_ID: Final = "entry_id"

CONF_SELECT_DEVICE_KEY: Final = "select_device"

CONF_DEVICE_TYPE: Final = "device_type"
CONF_DEVICE_NAME: Final = "device_name"
CONF_DEVICE_ID: Final = "device_id"
OPTS_DIAGNOSTIC_MODE: Final = "diagnostic_mode"
OPTS_POWER_STEP: Final = "power_step"
OPTS_REFRESH_PERIOD_SEC: Final = "refresh_period_sec"

DEFAULT_REFRESH_PERIOD_SEC: Final = 5



async def async_migrate_entry(hass, config_entry: ConfigEntry):
    """Migrate old entry."""
    entry_version = config_entry.version
    if entry_version <= 1:
        from .devices.registry import devices as device_registry
        device = device_registry[config_entry.data[CONF_DEVICE_TYPE]]

        new_data = {**config_entry.data}
        new_options = {OPTS_POWER_STEP: device.charging_power_step(),
                       OPTS_REFRESH_PERIOD_SEC: DEFAULT_REFRESH_PERIOD_SEC}

    if entry_version <= 2:
        hass.config_entries.async_update_entry(config_entry, data=new_data, options=new_options)
        _LOGGER.info("Migration to version %s successful", config_entry.version)

    if entry_version <= 3:
        new_data = {**config_entry.data}
        new_data[CONF_DEVICE_TYPE] = new_data["type"]
        new_data[CONF_DEVICE_NAME] = new_data["name"]
        del new_data["type"]
        del new_data["name"]

        new_options = {**config_entry.options, OPTS_DIAGNOSTIC_MODE: False}

        config_entry.version = CONFIG_VERSION
        hass.config_entries.async_update_entry(config_entry, data=new_data, options=new_options)
        _LOGGER.info("Migration to version %s successful", config_entry.version)

    if entry_version <= 5:
        new_data = {**config_entry.data}
        new_options = {**config_entry.options}
        try:
            if CONF_INSTALLATION_SITE not in new_data:  # The variable
                new_data[CONF_INSTALLATION_SITE] = "Home"
        except NameError:
            new_data[CONF_INSTALLATION_SITE] = "Home"
        try:
            if CONF_DEVICE_LIST not in new_data:  # The variable
                new_data[CONF_DEVICE_LIST] = [{
                    CONF_DEVICE_TYPE: new_data[CONF_DEVICE_TYPE],
                    CONF_DEVICE_NAME: new_data[CONF_DEVICE_NAME],
                    CONF_DEVICE_ID: new_data[CONF_DEVICE_ID]
                    }]
        except NameError:
            new_data[CONF_DEVICE_LIST] = [{
                CONF_DEVICE_TYPE: new_data[CONF_DEVICE_TYPE],
                CONF_DEVICE_NAME: new_data[CONF_DEVICE_NAME],
                CONF_DEVICE_ID: new_data[CONF_DEVICE_ID]
                }]
        config_entry.version = CONFIG_VERSION
        hass.config_entries.async_update_entry(config_entry, data=new_data, options=new_options)
        _LOGGER.info("Migration to version %s successful", config_entry.version)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    if CONF_USERNAME in entry.data and CONF_PASSWORD in entry.data:
        api_client = EcoflowPrivateApiClient(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD], entry.data[CONF_INSTALLATION_SITE])

    elif CONF_ACCESS_KEY in entry.data and CONF_SECRET_KEY in entry.data:
        api_client = EcoflowPublicApiClient(entry.data[CONF_ACCESS_KEY], entry.data[CONF_SECRET_KEY], entry.data[CONF_INSTALLATION_SITE])

    else:
        return False

    await api_client.login()
    devices_list: dict[str, DeviceConfLoader] = {}

    if (CONF_LOAD_AUTOMATIQUE not in entry.data or entry.data[CONF_LOAD_AUTOMATIQUE] == False) and CONF_DEVICE_LIST in entry.data:
        for device_data in entry.data[CONF_DEVICE_LIST]:
            devices_list[device_data[CONF_DEVICE_ID]] = DeviceConfLoader(device_data[CONF_DEVICE_ID], device_data[CONF_DEVICE_NAME], device_data[CONF_DEVICE_TYPE])

    else:
        # ajout automatique des devices
        try:
            from .devices.registry import device_by_product
            device_list = list(device_by_product.keys())
            devices = await api_client.fetch_all_available_devices()
            for device in devices:
                if device.device_type in device_list:
                    devices_list[device.sn] = DeviceConfLoader(device.sn, device.name, device.device_type)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception in fetch device action")

    new_data = {**entry.data}
    for sn,deviceConf in devices_list.items():

        if CONF_DEVICE_LIST in new_data:
            to_delete = {}
            for device_data in new_data[CONF_DEVICE_LIST]:
                if device_data[CONF_DEVICE_ID] == sn:
                    to_delete = device_data
                    break
            if to_delete:
                new_data[CONF_DEVICE_LIST].remove(to_delete)
        else:
            new_data[CONF_DEVICE_LIST]=[]

        new_data[CONF_DEVICE_LIST].append({
            CONF_DEVICE_ID: deviceConf.sn,
            CONF_DEVICE_NAME: deviceConf.name,
            CONF_DEVICE_TYPE: deviceConf.device_type
        })

        api_client.configure_device(deviceConf.sn, deviceConf.name, deviceConf.device_type)
        api_client.devices[sn].configure(int(entry.options[OPTS_REFRESH_PERIOD_SEC]), bool(entry.options[OPTS_DIAGNOSTIC_MODE]))

    hass.data[DOMAIN][entry.entry_id] = api_client

    hass.config_entries.async_update_entry(entry, data=new_data, options=entry.options)
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    if new_data[CONF_DEVICE_LIST]:
        for device_data in new_data[CONF_DEVICE_LIST]:
            _LOGGER.info("quota_all  : %s", device_data[CONF_DEVICE_ID])
            await api_client.quota_all(device_data[CONF_DEVICE_ID])
    else:
        await api_client.quota_all(new_data[CONF_DEVICE_ID])

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True

@dataclasses.dataclass
class DeviceConfLoader:
    sn: str
    name: str
    device_type: str

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    if not await hass.config_entries.async_unload_platforms(entry, _PLATFORMS):
        return False

    client: EcoflowApiClient = hass.data[DOMAIN].pop(entry.entry_id)
    client.stop()
    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
