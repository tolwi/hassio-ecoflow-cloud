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

ECOFLOW_DOMAIN = "ecoflow_cloud"
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
ATTR_MQTT_CONNECTED = "mqtt_connected"
ATTR_STATUS_RECONNECTS = "reconnects"
ATTR_STATUS_PHASE = "status_phase"
ATTR_QUOTA_REQUESTS = "quota_requests"

CONF_AUTH_TYPE: Final = "auth_type"

CONF_USERNAME: Final = "username"
CONF_PASSWORD: Final = "password"
CONF_ACCESS_KEY: Final = "access_key"
CONF_SECRET_KEY: Final = "secret_key"
CONF_LOAD_ALL_DEVICES: Final = "load_all_devices"
CONF_GROUP: Final = "group"
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


@dataclasses.dataclass
class DeviceData:
    sn: str
    name: str
    device_type: str


@dataclasses.dataclass
class DeviceOptions:
    refresh_period: int
    power_step: int
    diagnostic_mode: bool


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Migrate old entry."""
    if config_entry.version <= 2:
        from .devices.registry import devices as device_registry
        device = device_registry[config_entry.data[CONF_DEVICE_TYPE]]

        new_data = {**config_entry.data}
        new_options = {OPTS_POWER_STEP: device.default_charging_power_step(),
                       OPTS_REFRESH_PERIOD_SEC: DEFAULT_REFRESH_PERIOD_SEC}

        config_entry.version = 3
        hass.config_entries.async_update_entry(config_entry, data=new_data, options=new_options)
        _LOGGER.info("Migration to version %s successful", config_entry.version)
        return True

    elif config_entry.version in (3, 4):
        is_internal = CONF_USERNAME in config_entry.data
        current_entry_id = config_entry.entry_id
        entries_to_merge: list[ConfigEntry] = [
            entry for entry in hass.config_entries.async_entries(ECOFLOW_DOMAIN)
            if (is_internal and CONF_USERNAME in entry.data) or (not is_internal and CONF_ACCESS_KEY in entry.data)
        ]

        new_data = {CONF_LOAD_ALL_DEVICES: False, CONF_DEVICE_LIST: {}}
        new_options = {CONF_DEVICE_LIST: {}}
        for old_entry in entries_to_merge:
            old_data = old_entry.data
            if CONF_DEVICE_ID in old_data:
                sn = old_data[CONF_DEVICE_ID]
                if old_entry.version == 3:
                    device_info = {
                        CONF_DEVICE_TYPE: old_data["type"],
                        CONF_DEVICE_NAME: old_data["name"],
                        CONF_DEVICE_ID: old_data[CONF_DEVICE_ID]
                    }

                elif old_entry.version == 4:
                    device_info = {
                        CONF_DEVICE_TYPE: old_data[CONF_DEVICE_TYPE],
                        CONF_DEVICE_NAME: old_data[CONF_DEVICE_NAME],
                        CONF_DEVICE_ID: old_data[CONF_DEVICE_ID]
                    }

                new_data[CONF_DEVICE_LIST][sn] = device_info
                new_options[CONF_DEVICE_LIST][sn] = {
                    OPTS_REFRESH_PERIOD_SEC: old_entry.options[OPTS_REFRESH_PERIOD_SEC],
                    OPTS_POWER_STEP: old_entry.options[OPTS_POWER_STEP],
                    OPTS_DIAGNOSTIC_MODE: False
                }



        if is_internal:
            title = "Home_internal"
            new_data[CONF_USERNAME] = config_entry.data[CONF_USERNAME]
            new_data[CONF_PASSWORD] = config_entry.data[CONF_PASSWORD]
        else:
            title = "Home_api"
            new_data[CONF_ACCESS_KEY] = config_entry.data[CONF_ACCESS_KEY]
            new_data[CONF_SECRET_KEY] = config_entry.data[CONF_SECRET_KEY]
            new_data[CONF_LOAD_ALL_DEVICES] = False
        new_data[CONF_GROUP] = title

        hass.config_entries.async_update_entry(config_entry,
                                               version=CONFIG_VERSION,
                                               title=title,
                                               unique_id="group-" + new_data[CONF_GROUP],
                                               data=new_data,
                                               options=new_options)
        _LOGGER.info("Config entries merged into new one with version %s", CONFIG_VERSION)

        for old_entry in entries_to_merge:
            if old_entry.entry_id != current_entry_id:
                await hass.config_entries.async_unload(old_entry.entry_id)
                await hass.config_entries.async_remove(old_entry.entry_id)
                _LOGGER.info(".. removed entry %s", old_entry.entry_id)

        return True

    return False



def extract_devices(entry: ConfigEntry) -> dict[str, DeviceData]:
    devices: dict[str, DeviceData] = {}
    for sn, device_data in entry.data[CONF_DEVICE_LIST].items():
        devices[sn] = DeviceData(
            sn, device_data[CONF_DEVICE_NAME], device_data[CONF_DEVICE_TYPE]
        )
    return devices


def extract_options(entry: ConfigEntry) -> dict[str, DeviceOptions]:
    options: dict[str, DeviceOptions] = {}
    for sn, device_option in entry.options[CONF_DEVICE_LIST].items():
        options[sn] = DeviceOptions(
            device_option[OPTS_REFRESH_PERIOD_SEC], device_option[OPTS_POWER_STEP], device_option[OPTS_DIAGNOSTIC_MODE]
        )
    return options


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    if entry.version != CONFIG_VERSION:
        return False

    _LOGGER.info("Setup entry %s (data = %s)", str(entry), str(entry.data))
    if ECOFLOW_DOMAIN not in hass.data:
        hass.data[ECOFLOW_DOMAIN] = {}

    if CONF_USERNAME in entry.data and CONF_PASSWORD in entry.data:
        api_client = EcoflowPrivateApiClient(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD],
                                             entry.data[CONF_GROUP])

    elif CONF_ACCESS_KEY in entry.data and CONF_SECRET_KEY in entry.data:
        api_client = EcoflowPublicApiClient(entry.data[CONF_ACCESS_KEY], entry.data[CONF_SECRET_KEY],
                                            entry.data[CONF_GROUP])
    else:
        return False

    await api_client.login()

    devices_list: dict[str, DeviceData] = {}
    devices_options: dict[str, DeviceOptions] = {}

    if CONF_LOAD_ALL_DEVICES not in entry.data or not entry.data[CONF_LOAD_ALL_DEVICES]:
        devices_list.update(extract_devices(entry))
        devices_options.update(extract_options(entry))
    else:
        try:
            from .devices.registry import device_by_product
            device_list = list(device_by_product.keys())
            devices = await api_client.fetch_all_available_devices()
            for device in devices:
                if device.device_type in device_list:
                    devices_list[device.sn] = DeviceData(device.sn, device.name, device.device_type)
                    devices_options[device.sn] = DeviceOptions(DEFAULT_REFRESH_PERIOD_SEC, -1, False)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception in fetch device action")

    for sn, device_data in devices_list.items():
        device_option = devices_options[sn]
        device = api_client.configure_device(device_data.sn, device_data.name, device_data.device_type,
                                             device_option.power_step)
        device.configure(hass, device_option.refresh_period, device_option.diagnostic_mode)

    await hass.async_add_executor_job(api_client.start)
    hass.data[ECOFLOW_DOMAIN][entry.entry_id] = api_client
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)
    await api_client.quota_all(None)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    if not await hass.config_entries.async_unload_platforms(entry, _PLATFORMS):
        return False

    client: EcoflowApiClient = hass.data[ECOFLOW_DOMAIN].pop(entry.entry_id)
    client.stop()
    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
