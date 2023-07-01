from homeassistant.core import callback, HomeAssistant

from custom_components.ecoflow_cloud import ATTR_STATUS_QUOTA_UPDATES, ATTR_STATUS_DATA_LAST_UPDATE, \
    ATTR_STATUS_QUOTA_LAST_UPDATE


@callback
def exclude_attributes(hass: HomeAssistant) -> set[str]:
    return {ATTR_STATUS_QUOTA_UPDATES, ATTR_STATUS_DATA_LAST_UPDATE, ATTR_STATUS_QUOTA_LAST_UPDATE}
