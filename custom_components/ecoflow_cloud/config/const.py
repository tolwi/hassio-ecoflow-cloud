from enum import Enum
from typing import Final

from homeassistant import const

CONF_USERNAME: Final = const.CONF_USERNAME
CONF_PASSWORD: Final = const.CONF_PASSWORD
CONF_DEVICE_TYPE: Final = const.CONF_TYPE
CONF_DEVICE_NAME: Final = const.CONF_NAME
CONF_DEVICE_ID: Final = const.CONF_DEVICE_ID
OPTS_POWER_STEP: Final = "power_step"
OPTS_REFRESH_PERIOD_SEC: Final = "refresh_period_sec"

DEFAULT_REFRESH_PERIOD_SEC: Final = 5


class EcoflowModel(Enum):
    DELTA_2 = 1,
    RIVER_2 = 2,
    RIVER_2_MAX = 3,
    RIVER_2_PRO = 4,
    DELTA_PRO = 5,
    RIVER_MAX = 6,
    RIVER_PRO = 7,
    DELTA_MAX = 8,
    DELTA_2_MAX = 9,
    POWERSTREAM = 51,
    DIAGNOSTIC = 99

    @classmethod
    def list(cls) -> list[str]:
        return [e.name for e in EcoflowModel]
