from homeassistant.core import callback, HomeAssistant

from custom_components.ecoflow_cloud import ATTR_STATUS_UPDATES


@callback
def exclude_attributes(hass: HomeAssistant) -> set[str]:
    return {ATTR_STATUS_UPDATES}
