import asyncio
import logging
import os
from types import MappingProxyType

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.ecoflow_cloud.devices.powerkit import PowerKit
from custom_components.ecoflow_cloud.entities import BaseSensorEntity
from custom_components.ecoflow_cloud import EcoflowAuthentication, EcoflowMQTTClient

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

async def main():

    data = MappingProxyType(
        {
            "type": "powerkit",
            "device_id": os.environ['ecoflowSn']
        }
    )

    config = ConfigEntry(
        version='1.0.0',
        minor_version='1',
        domain='homeassistant.local',
        title='debugEcoflow',
        data=data,
        source='',
        options= MappingProxyType(
        {
            "refresh_period_sec": 1
        })
    )
    auth = EcoflowAuthentication(os.environ['ecoflowUserName'], os.environ['ecoflowPassword'])
    auth.authorize()
    home = HomeAssistant('./')
    client = EcoflowMQTTClient(home, config, auth)
    powerkit = PowerKit()
    sensors = powerkit.sensors(client)
    client.data.params_observable().subscribe(lambda v: updateSensors(v))
    def updateSensors(data: dict[str, any]):
        for v in sensors:
            v.hass = home
            v._updated(data)
            _LOGGER.info(v.name)
            _LOGGER.info(v._attr_native_value)

    while True:
            await asyncio.sleep(1)
asyncio.run(main())
