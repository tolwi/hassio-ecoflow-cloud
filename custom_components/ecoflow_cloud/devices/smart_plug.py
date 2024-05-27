from . import BaseDevice
from .. import EcoflowMQTTClient
from ..entities import (
    BaseSensorEntity, BaseNumberEntity, BaseSelectEntity, BaseSwitchEntity
)
from ..sensor import (
    AmpSensorEntity, CentivoltSensorEntity, DeciampSensorEntity,
    DecicelsiusSensorEntity, DecihertzSensorEntity, DeciwattsSensorEntity,
    DecivoltSensorEntity, InWattsSolarSensorEntity, LevelSensorEntity,
    MiscSensorEntity, RemainSensorEntity, StatusSensorEntity,
)
# from ..number import MinBatteryLevelEntity, MaxBatteryLevelEntity
# from ..select import DictSelectEntity

class PowerStream(BaseDevice):
    def sensors(self, client: EcoflowMQTTClient) -> list[BaseSensorEntity]:
        return [

            DeciwattsSensorEntity(client, "watts", "Current Load"),
            DecivoltSensorEntity(client, "volt", "Operating Voltage"),
            DeciampSensorEntity(client, "current", "Operating Current"),
            DecicelsiusSensorEntity(client, "temp", "Plug Temperature"),
            
            StatusSensorEntity(client)
        ]