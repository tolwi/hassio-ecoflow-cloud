from homeassistant.core import callback, HomeAssistant

from custom_components.ecoflow_cloud import ATTR_LAST_PING


@callback
def exclude_attributes(hass: HomeAssistant) -> set[str]:
    return {ATTR_LAST_PING}