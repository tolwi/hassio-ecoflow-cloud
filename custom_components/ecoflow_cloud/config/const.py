from enum import Enum, StrEnum
from typing import Final

from homeassistant import const

CONF_AUTH_TYPE: Final = "auth_type"

CONF_USERNAME: Final = const.CONF_USERNAME
CONF_PASSWORD: Final = const.CONF_PASSWORD

CONF_ACCESS_KEY: Final = "access_key"
CONF_SECRET_KEY: Final = "secret_key"

CONF_SELECT_DEVICE_KEY: Final = "select_device"

CONF_DEVICE_TYPE: Final = "device_type"
CONF_DEVICE_NAME: Final = "device_name"
CONF_DEVICE_ID: Final = "device_id"
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
    DELTA_MAX = 8,   # productType = 13
    DELTA_2_MAX = 9, # productType = 81
    DELTA_MINI = 15,   # productType = 15
    RIVER_MINI = 17,
    POWERSTREAM = 51, 
    GLACIER = 46,
    WAVE_2 = 45, # productType = 45
    DIAGNOSTIC = 99

    @classmethod
    def list(cls) -> list[str]:
        return [e.name for e in EcoflowModel]

class EcoflowApiProducts (StrEnum):

    DELTA_2 = "DELTA 2",
    RIVER_2 = "RIVER 2",
    RIVER_2_MAX = "RIVER 2 Max",
    DIAGNOSTIC = "DIAGNOSTIC"

    @classmethod
    def list(cls) -> list[str]:
        return [e for e in EcoflowApiProducts]
