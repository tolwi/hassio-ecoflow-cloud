from enum import IntEnum


class AddressId(IntEnum):
    IOT = 1
    IOT2 = 2
    DEVICE = 20   # alternator (and similar) device-direct address
    APP = 32
    MQTT = 53


class DirectionId(IntEnum):
    DEFAULT = 1
