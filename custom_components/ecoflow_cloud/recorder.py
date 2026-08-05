from homeassistant.core import HomeAssistant, callback

from . import (
    ATTR_QUOTA_REQUESTS,
    ATTR_STATUS_DATA_LAST_UPDATE,
    ATTR_STATUS_LAST_UPDATE,
    ATTR_STATUS_PHASE,
    ATTR_STATUS_UPDATES,
)


@callback
def exclude_attributes(hass: HomeAssistant) -> set[str]:
    return {
        ATTR_STATUS_UPDATES,
        ATTR_STATUS_DATA_LAST_UPDATE,
        ATTR_STATUS_LAST_UPDATE,
        ATTR_STATUS_PHASE,
        ATTR_QUOTA_REQUESTS,
    }
