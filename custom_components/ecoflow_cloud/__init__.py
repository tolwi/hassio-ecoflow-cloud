import logging
from typing import Final, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from custom_components.ecoflow_cloud.DeviceData import (
    DeviceData,
    ChildDeviceData,
    DeviceDataImportFactory,
)
from custom_components.ecoflow_cloud.DeviceOptions import DeviceOptions

from .api import EcoflowApiClient
from .api.private_api import EcoflowPrivateApiClient
from .api.public_api import EcoflowPublicApiClient

_LOGGER = logging.getLogger(__name__)

ECOFLOW_DOMAIN = "ecoflow_cloud"
CONFIG_VERSION = 8

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

CONF_API_HOST: Final = "api_host"
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


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    updated: bool = False
    if config_entry.version in (5, 6):
        new_data = dict(config_entry.data)
        new_options = dict(config_entry.options)
        new_devices = dict[str, DeviceData]()
        for sn, device_info in config_entry.data[CONF_DEVICE_LIST].items():
            new_devices[sn] = DeviceData(
                sn,
                device_info[CONF_DEVICE_NAME],
                device_info[CONF_DEVICE_TYPE],
                DeviceOptions(
                    config_entry.options[CONF_DEVICE_LIST][sn][OPTS_REFRESH_PERIOD_SEC],
                    config_entry.options[CONF_DEVICE_LIST][sn][OPTS_POWER_STEP],
                    config_entry.options[CONF_DEVICE_LIST][sn][OPTS_DIAGNOSTIC_MODE],
                ),
                None,
            )
        # remove options for the devices, because they are now part of the devices
        new_options.pop(CONF_DEVICE_LIST)
        # update the data with the class structured data
        new_data[CONF_DEVICE_LIST] = new_devices
        # update the entry in home assistant
        updated = hass.config_entries.async_update_entry(
            config_entry,
            version=7,
            data=new_data,
            options=new_options,
        )
        _LOGGER.info("Config entries updated to version %d", config_entry.version)

    if config_entry.version == 7:
        new_data = dict(config_entry.data)
        is_api = CONF_ACCESS_KEY in config_entry.data
        if is_api:
            new_data[CONF_API_HOST] = "api-e.ecoflow.com"
        else:
            new_data[CONF_API_HOST] = "api.ecoflow.com"
        
        updated = hass.config_entries.async_update_entry(
            config_entry,
            version=8,
            data=new_data
        )
        _LOGGER.info("Config entries updated to version %d", config_entry.version)

    return updated


def extract_devices(entry: ConfigEntry) -> dict[str, DeviceData]:
    result = entry.data[CONF_DEVICE_LIST]
    if isinstance(next(iter(result.values())), (dict, list)):
        return {sn: DeviceDataImportFactory.create(data) for sn, data in result.items()}
    return entry.data[CONF_DEVICE_LIST]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    if entry.version != CONFIG_VERSION:
        return False

    _LOGGER.info("Setup entry %s (data = %s)", str(entry), str(entry.data))
    if ECOFLOW_DOMAIN not in hass.data:
        hass.data[ECOFLOW_DOMAIN] = {}

    if CONF_USERNAME in entry.data and CONF_PASSWORD in entry.data:
        api_client = EcoflowPrivateApiClient(
            entry.data[CONF_API_HOST],
            entry.data[CONF_USERNAME], 
            entry.data[CONF_PASSWORD], 
            entry.data[CONF_GROUP]
        )

    elif CONF_ACCESS_KEY in entry.data and CONF_SECRET_KEY in entry.data:
        api_client = EcoflowPublicApiClient(
            entry.data[CONF_API_HOST],
            entry.data[CONF_ACCESS_KEY],
            entry.data[CONF_SECRET_KEY],
            entry.data[CONF_GROUP],
        )
    else:
        return False

    await api_client.login()

    devices_list: dict[str, DeviceData] = {}

    if CONF_LOAD_ALL_DEVICES not in entry.data or not entry.data[CONF_LOAD_ALL_DEVICES]:
        devices_list.update(extract_devices(entry))
    else:
        try:
            from .devices.registry import device_by_product

            device_list = list(device_by_product.keys())
            devices = await api_client.fetch_all_available_devices()
            for device in devices:
                if device.device_type in device_list:
                    devices_list[device.sn] = DeviceData(
                        device.sn,
                        device.name,
                        device.device_type,
                        DeviceOptions(DEFAULT_REFRESH_PERIOD_SEC, -1, False),
                        None,
                    )
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception in fetch device action")

    for sn, device_data in devices_list.items():
        device = api_client.configure_device(device_data)
        device.configure(
            hass,
            device_data.options.refresh_period,
            device_data.options.diagnostic_mode,
        )

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
