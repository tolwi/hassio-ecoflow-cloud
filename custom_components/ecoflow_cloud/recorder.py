from homeassistant.core import callback, HomeAssistant

from custom_components.ecoflow_cloud import ATTR_STATUS_UPDATES, ATTR_STATUS_DATA_LAST_UPDATE, \
    ATTR_STATUS_LAST_UPDATE, ATTR_STATUS_PHASE, ATTR_QUOTA_REQUESTS


@callback
def exclude_attributes(hass: HomeAssistant) -> set[str]:
    return {ATTR_STATUS_UPDATES, ATTR_STATUS_DATA_LAST_UPDATE, ATTR_STATUS_LAST_UPDATE, ATTR_STATUS_PHASE, ATTR_QUOTA_REQUESTS}
