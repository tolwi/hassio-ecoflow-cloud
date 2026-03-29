import logging
from typing import Any
from typing import Final

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers import device_registry as dr

from custom_components.ecoflow_cloud.api import EcoflowApiClient

from . import _preload_proto  # noqa: F401 # pyright: ignore[reportUnusedImport]
from .device_data import DeviceData, DeviceOptions

_LOGGER = logging.getLogger(__name__)

ECOFLOW_DOMAIN = "ecoflow_cloud"
CONFIG_VERSION = 11

_PLATFORMS = {
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
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
CONF_GROUP: Final = "group"
CONF_DEVICE_LIST: Final = "devices_list"
CONF_ENTRY_ID: Final = "entry_id"

CONF_SELECT_DEVICE_KEY: Final = "select_device"

CONF_DEVICE_TYPE: Final = "device_type"
CONF_DEVICE_NAME: Final = "device_name"
CONF_DEVICE_ID: Final = "device_id"
CONF_PARENT_SN: Final = "parent_sn"
OPTS_DIAGNOSTIC_MODE: Final = "diagnostic_mode"
OPTS_POWER_STEP: Final = "power_step"
OPTS_REFRESH_PERIOD_SEC: Final = "refresh_period_sec"
OPTS_ASSUME_OFFLINE_SEC: Final = "assume_offline_sec"
OPTS_VERBOSE_STATUS_MODE: Final = "verbose_status_mode"
OPTS_BLE_WIFI_RECOVERY_ENABLED: Final = "ble_wifi_recovery_enabled"
OPTS_BLE_WIFI_SSID: Final = "ble_wifi_ssid"
OPTS_BLE_WIFI_PASSWORD: Final = "ble_wifi_password"
OPTS_BLE_WIFI_BSSID: Final = "ble_wifi_bssid"
OPTS_BLE_RECOVERY_TIMEOUT_SEC: Final = "ble_recovery_timeout_sec"
OPTS_BLE_RECOVERY_COOLDOWN_SEC: Final = "ble_recovery_cooldown_sec"
SERVICE_RECOVER_WIFI_VIA_BLE: Final = "recover_wifi_via_ble"
SERVICE_ATTR_SERIAL_NUMBER: Final = "serial_number"
SERVICE_ATTR_SSID: Final = "ssid"
SERVICE_ATTR_PASSWORD: Final = "password"
SERVICE_ATTR_BSSID: Final = "bssid"

DEFAULT_REFRESH_PERIOD_SEC: Final = 5
DEFAULT_ASSUME_OFFLINE_SEC: Final = 300  # 5 minutes
DEFAULT_BLE_RECOVERY_TIMEOUT_SEC: Final = 120
DEFAULT_BLE_RECOVERY_COOLDOWN_SEC: Final = 300
DEFAULT_BLE_WIFI_RECOVERY_DEVICE_TYPES: Final = {
    "RIVER_2",
    "RIVER_2_MAX",
    "RIVER_2_PRO",
    "RIVER 2",
    "RIVER 2 Max",
    "RIVER 2 Pro",
}


def default_ble_wifi_recovery_enabled(device_type: str) -> bool:
    return device_type in DEFAULT_BLE_WIFI_RECOVERY_DEVICE_TYPES


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    updated: bool = False
    if config_entry.version in (5, 6):
        new_data = dict(config_entry.data)
        new_options = dict(config_entry.options)
        new_devices = dict[str, Any]()
        for sn, device_info in config_entry.data[CONF_DEVICE_LIST].items():
            new_devices[sn] = {
                CONF_DEVICE_NAME: device_info[CONF_DEVICE_NAME],
                CONF_DEVICE_TYPE: device_info[CONF_DEVICE_TYPE],
                "options": {
                    OPTS_REFRESH_PERIOD_SEC: config_entry.options[CONF_DEVICE_LIST][sn][OPTS_REFRESH_PERIOD_SEC],
                    OPTS_POWER_STEP: config_entry.options[CONF_DEVICE_LIST][sn][OPTS_POWER_STEP],
                    OPTS_DIAGNOSTIC_MODE: config_entry.options[CONF_DEVICE_LIST][sn][OPTS_DIAGNOSTIC_MODE],
                },
            }

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

        updated = hass.config_entries.async_update_entry(config_entry, version=8, data=new_data)
        _LOGGER.info("Config entries updated to version %d", config_entry.version)

    if config_entry.version == 8:
        # fix fields and revert options
        new_data = dict(config_entry.data)
        new_options = {CONF_DEVICE_LIST: {}}
        new_data.pop("load_all_devices", None)

        for sn, device_info in new_data[CONF_DEVICE_LIST].items():
            if "name" in device_info:
                new_data[CONF_DEVICE_LIST][sn][CONF_DEVICE_NAME] = new_data[CONF_DEVICE_LIST][sn].pop("name")
                new_data[CONF_DEVICE_LIST][sn].pop("sn", None)

            new_options[CONF_DEVICE_LIST][sn] = new_data[CONF_DEVICE_LIST][sn].pop("options")

            if "refresh_period" in new_options[CONF_DEVICE_LIST][sn]:
                new_options[CONF_DEVICE_LIST][sn][OPTS_REFRESH_PERIOD_SEC] = new_options[CONF_DEVICE_LIST][sn].pop(
                    "refresh_period"
                )

        updated = hass.config_entries.async_update_entry(config_entry, version=9, data=new_data, options=new_options)
        _LOGGER.info("Config entries updated to version %d", config_entry.version)

    if config_entry.version == 9:
        new_options = dict(config_entry.options)
        for sn, device_options in new_options[CONF_DEVICE_LIST].items():
            device_options[OPTS_VERBOSE_STATUS_MODE] = False
            device_options[OPTS_ASSUME_OFFLINE_SEC] = DEFAULT_ASSUME_OFFLINE_SEC

        updated = hass.config_entries.async_update_entry(config_entry, version=10, options=new_options)
        _LOGGER.info("Config entries updated to version %d", config_entry.version)

    if config_entry.version == 10:
        new_options = dict(config_entry.options)
        for sn, device_options in new_options[CONF_DEVICE_LIST].items():
            device_type = config_entry.data[CONF_DEVICE_LIST][sn].get(CONF_DEVICE_TYPE, "")
            device_options[OPTS_BLE_WIFI_RECOVERY_ENABLED] = default_ble_wifi_recovery_enabled(device_type)
            device_options[OPTS_BLE_WIFI_SSID] = ""
            device_options[OPTS_BLE_WIFI_PASSWORD] = ""
            device_options[OPTS_BLE_WIFI_BSSID] = ""
            device_options[OPTS_BLE_RECOVERY_TIMEOUT_SEC] = DEFAULT_BLE_RECOVERY_TIMEOUT_SEC
            device_options[OPTS_BLE_RECOVERY_COOLDOWN_SEC] = DEFAULT_BLE_RECOVERY_COOLDOWN_SEC

        updated = hass.config_entries.async_update_entry(config_entry, version=11, options=new_options)
        _LOGGER.info("Config entries updated to version %d", config_entry.version)

    return updated


def _resolve_sn_from_device_id(hass: HomeAssistant, device_id: str) -> str | None:
    device_registry = dr.async_get(hass)
    device = device_registry.async_get(device_id)
    if device is None:
        return None

    for domain, identifier in device.identifiers:
        if domain != ECOFLOW_DOMAIN:
            continue
        if identifier.startswith("api-"):
            return identifier[4:]
        return identifier

    return None


def _find_client_for_serial(hass: HomeAssistant, serial_number: str) -> EcoflowApiClient | None:
    clients = hass.data.get(ECOFLOW_DOMAIN, {})
    for client in clients.values():
        if serial_number in client.devices:
            return client
    return None


async def _async_handle_recover_wifi_via_ble(hass: HomeAssistant, call: ServiceCall) -> None:
    serial_number = call.data.get(SERVICE_ATTR_SERIAL_NUMBER)
    if serial_number is None and call.data.get(CONF_DEVICE_ID):
        serial_number = _resolve_sn_from_device_id(hass, call.data[CONF_DEVICE_ID])

    if not serial_number:
        raise HomeAssistantError("Provide serial_number or device_id for EcoFlow BLE Wi-Fi recovery")

    client = _find_client_for_serial(hass, serial_number)
    if client is None or serial_number not in client.devices:
        raise HomeAssistantError(f"EcoFlow device not found for serial number: {serial_number}")

    if client.ble_recovery_manager is None:
        raise HomeAssistantError("BLE Wi-Fi recovery manager is not initialized")

    device = client.devices[serial_number]
    if not client.ble_recovery_manager.supports_device(device.device_data):
        raise HomeAssistantError(f"BLE Wi-Fi recovery is not supported for {serial_number}")

    recovered = await client.ble_recovery_manager.async_recover(
        serial_number,
        reason="service",
        manual=True,
        ssid=call.data.get(SERVICE_ATTR_SSID),
        password=call.data.get(SERVICE_ATTR_PASSWORD),
        bssid=call.data.get(SERVICE_ATTR_BSSID),
    )
    if not recovered:
        raise HomeAssistantError(f"BLE Wi-Fi recovery did not succeed for {serial_number}")


def _async_register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(ECOFLOW_DOMAIN, SERVICE_RECOVER_WIFI_VIA_BLE):
        return

    service_schema = vol.Schema(
        {
            vol.Optional(SERVICE_ATTR_SERIAL_NUMBER): str,
            vol.Optional(CONF_DEVICE_ID): str,
            vol.Optional(SERVICE_ATTR_SSID): str,
            vol.Optional(SERVICE_ATTR_PASSWORD): str,
            vol.Optional(SERVICE_ATTR_BSSID): str,
        }
    )

    async def _handle(call: ServiceCall) -> None:
        await _async_handle_recover_wifi_via_ble(hass, call)

    hass.services.async_register(
        ECOFLOW_DOMAIN,
        SERVICE_RECOVER_WIFI_VIA_BLE,
        _handle,
        schema=service_schema,
    )


def extract_devices(entry: ConfigEntry) -> dict[str, DeviceData]:
    result = dict[str, DeviceData]()
    for sn, data in entry.data[CONF_DEVICE_LIST].items():
        result[sn] = DeviceData(
            sn,
            data[CONF_DEVICE_NAME],
            data[CONF_DEVICE_TYPE],
            DeviceOptions(
                refresh_period=entry.options[CONF_DEVICE_LIST][sn][OPTS_REFRESH_PERIOD_SEC],
                power_step=entry.options[CONF_DEVICE_LIST][sn][OPTS_POWER_STEP],
                diagnostic_mode=entry.options[CONF_DEVICE_LIST][sn][OPTS_DIAGNOSTIC_MODE],
                verbose_status_mode=entry.options[CONF_DEVICE_LIST][sn].get(OPTS_VERBOSE_STATUS_MODE, False),
                assume_offline_sec=entry.options[CONF_DEVICE_LIST][sn].get(
                    OPTS_ASSUME_OFFLINE_SEC, DEFAULT_ASSUME_OFFLINE_SEC
                ),
                ble_wifi_recovery_enabled=entry.options[CONF_DEVICE_LIST][sn].get(
                    OPTS_BLE_WIFI_RECOVERY_ENABLED,
                    default_ble_wifi_recovery_enabled(data[CONF_DEVICE_TYPE]),
                ),
                ble_wifi_ssid=entry.options[CONF_DEVICE_LIST][sn].get(OPTS_BLE_WIFI_SSID, ""),
                ble_wifi_password=entry.options[CONF_DEVICE_LIST][sn].get(OPTS_BLE_WIFI_PASSWORD, ""),
                ble_wifi_bssid=entry.options[CONF_DEVICE_LIST][sn].get(OPTS_BLE_WIFI_BSSID, ""),
                ble_recovery_timeout_sec=entry.options[CONF_DEVICE_LIST][sn].get(
                    OPTS_BLE_RECOVERY_TIMEOUT_SEC, DEFAULT_BLE_RECOVERY_TIMEOUT_SEC
                ),
                ble_recovery_cooldown_sec=entry.options[CONF_DEVICE_LIST][sn].get(
                    OPTS_BLE_RECOVERY_COOLDOWN_SEC, DEFAULT_BLE_RECOVERY_COOLDOWN_SEC
                ),
            ),
            None,
            None,
        )

    for sn, data in entry.data[CONF_DEVICE_LIST].items():
        if CONF_PARENT_SN in data:
            result[sn].parent = result[data[CONF_PARENT_SN]]

    return result


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    if entry.version != CONFIG_VERSION:
        return False

    _LOGGER.info("Setup entry %s (data = %s)", str(entry), str(entry.data))
    api_client: EcoflowApiClient
    if ECOFLOW_DOMAIN not in hass.data:
        hass.data[ECOFLOW_DOMAIN] = {}
    if CONF_USERNAME in entry.data and CONF_PASSWORD in entry.data:
        from .api.private_api import EcoflowPrivateApiClient

        api_client = EcoflowPrivateApiClient(
            entry.data[CONF_API_HOST],
            entry.data[CONF_USERNAME],
            entry.data[CONF_PASSWORD],
            entry.data[CONF_GROUP],
        )

    elif CONF_ACCESS_KEY in entry.data and CONF_SECRET_KEY in entry.data:
        from .api.public_api import EcoflowPublicApiClient

        api_client = EcoflowPublicApiClient(
            entry.data[CONF_API_HOST],
            entry.data[CONF_ACCESS_KEY],
            entry.data[CONF_SECRET_KEY],
            entry.data[CONF_GROUP],
        )
    else:
        return False

    devices_list: dict[str, DeviceData] = extract_devices(entry)
    # Try to connect and authenticate
    try:
        await api_client.login()
    except (ConnectionError, TimeoutError) as ex:
        # Transient network issues - retry later
        _LOGGER.warning("Failed to connect to EcoFlow API: %s", ex)
        raise ConfigEntryNotReady(f"Connection failed: {ex}") from ex

    for sn, device_data in devices_list.items():
        device = api_client.configure_device(device_data)
        device.configure(hass)

    from .ble import EcoflowBleRecoveryManager

    api_client.ble_recovery_manager = EcoflowBleRecoveryManager(hass, api_client, entry.entry_id)

    await hass.async_add_executor_job(api_client.start)
    hass.data[ECOFLOW_DOMAIN][entry.entry_id] = api_client
    _async_register_services(hass)

    # Must load all device data before configuring devices because the data
    # is used for entity setup.
    await api_client.quota_all(None)

    # Forward entry setup to the platforms to set up the entities
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    if not await hass.config_entries.async_unload_platforms(entry, _PLATFORMS):
        return False

    client = hass.data[ECOFLOW_DOMAIN].pop(entry.entry_id)
    if client.ble_recovery_manager is not None:
        await client.ble_recovery_manager.async_shutdown()
    if not hass.data[ECOFLOW_DOMAIN] and hass.services.has_service(ECOFLOW_DOMAIN, SERVICE_RECOVER_WIFI_VIA_BLE):
        hass.services.async_remove(ECOFLOW_DOMAIN, SERVICE_RECOVER_WIFI_VIA_BLE)
    client.stop()
    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
