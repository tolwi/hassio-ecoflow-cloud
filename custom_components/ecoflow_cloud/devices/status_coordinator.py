"""Global coordinator that polls device online statuses via the public API.

A single instance is created per hass instance. API clients register/unregister
as config entries load/unload. On each poll cycle it:
1. Collects all devices from all registered clients.
2. Checks whether any device's StatusTracker is in the ASSUME_OFFLINE state.
3. If so, calls /device/list via a public API client and distributes statuses by SN.
"""

from __future__ import annotations

import datetime
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from ..api import EcoflowApiClient
from .data_coordinator import EcoflowBroadcastDataHolder

_LOGGER = logging.getLogger(__name__)

DEFAULT_STATUS_POLL_INTERVAL_SEC = 300  # fallback when no devices are registered


class DeviceStatusCoordinator(DataUpdateCoordinator[None]):
    """Periodically polls the public API /device/list for online statuses."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Ecoflow device status coordinator",
            update_interval=datetime.timedelta(seconds=DEFAULT_STATUS_POLL_INTERVAL_SEC),
        )
        self._clients: dict[str, EcoflowApiClient] = {}  # entry_id -> client

    def register(self, entry_id: str, client: EcoflowApiClient) -> None:
        self._clients[entry_id] = client
        self._actualize_interval()

    def unregister(self, entry_id: str) -> None:
        self._clients.pop(entry_id, None)
        self._actualize_interval()

    def _actualize_interval(self) -> None:
        interval = min(
            (d.device_data.options.assume_offline_sec for c in self._clients.values() for d in c.devices.values()),
            default=DEFAULT_STATUS_POLL_INTERVAL_SEC,
        )
        self.update_interval = datetime.timedelta(seconds=interval)
        _LOGGER.debug("Status poll interval set to %ds", interval)

    @property
    def empty(self) -> bool:
        return not self._clients

    def _collect_all_devices(self) -> dict[str, list]:
        """Collect all devices grouped by SN. Same SN may appear in multiple clients."""
        all_devices: dict[str, list] = {}
        for client in self._clients.values():
            for sn, device in client.devices.items():
                all_devices.setdefault(sn, []).append(device)
        return all_devices

    def _public_clients(self) -> list[EcoflowApiClient]:
        from ..api.public_api import EcoflowPublicApiClient

        return [c for c in self._clients.values() if isinstance(c, EcoflowPublicApiClient)]

    async def _async_update_data(self) -> None:
        public_clients = self._public_clients()
        if not public_clients:
            return

        all_devices = self._collect_all_devices()
        if not all_devices:
            return

        # Only poll if at least one device needs status clarification
        needs_poll = any(
            device.status_tracker.wants_status_poll for devices in all_devices.values() for device in devices
        )
        if not needs_poll:
            _LOGGER.debug("No devices need status poll — skipping")
            return

        # Fetch from each public API client (each covers its own account)
        for client in public_clients:
            try:
                api_devices = await client.fetch_all_available_devices()
            except Exception as err:
                _LOGGER.warning("Status poll failed: %s", err)
                continue

            for api_device in api_devices:
                for device in all_devices.get(api_device.sn, []):
                    online = api_device.status == 1
                    device.status_tracker.on_explicit_status(online)
                    device.data.mark_status_changed()
                    device.coordinator.async_set_updated_data(EcoflowBroadcastDataHolder(device.data, online))
