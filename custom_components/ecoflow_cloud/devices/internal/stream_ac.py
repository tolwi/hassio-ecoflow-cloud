from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import const, BaseDevice
from custom_components.ecoflow_cloud.entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, \
    BaseSelectEntity
from custom_components.ecoflow_cloud.sensor import WattsSensorEntity,LevelSensorEntity,CapacitySensorEntity, \
    InWattsSensorEntity,OutWattsSensorEntity, RemainSensorEntity, MilliVoltSensorEntity, TempSensorEntity, \
    CyclesSensorEntity

class StreamAC(BaseDevice):
    def sensors(self, client: EcoflowApiClient) -> list[BaseSensorEntity]:
        return [

            WattsSensorEntity(client, self, "sysGridConnectionPower", const.STREAM_POWER_AC_SYS),
            WattsSensorEntity(client, self, "powGetSysLoad", const.STREAM_GET_SYS_LOAD),
            WattsSensorEntity(client, self, "powGetSysLoadFromGrid", const.STREAM_GET_SYS_LOAD_FROM_GRID),
            WattsSensorEntity(client, self, "powGetSchuko1", const.STREAM_GET_SCHUKO1, False),
            WattsSensorEntity(client, self, "gridConnectionPower", const.STREAM_POWER_AC),
            WattsSensorEntity(client, self, "powGetSysGrid", const.STREAM_POWER_GRID),
            WattsSensorEntity(client, self, "powGetPvSum", const.STREAM_POWER_PV),
            WattsSensorEntity(client, self, "powGetBpCms", const.STREAM_POWER_BATTERY),
            LevelSensorEntity(client, self, "f32ShowSoc", const.STREAM_POWER_BATTERY_SOC),
            LevelSensorEntity(client, self, "soc", const.STREAM_POWER_BATTERY)
            .attr("designCap", const.ATTR_DESIGN_CAPACITY, 0)
            .attr("fullCap", const.ATTR_FULL_CAPACITY, 0)
            .attr("remainCap", const.ATTR_REMAIN_CAPACITY, 0),
            CapacitySensorEntity(client, self, "designCap", const.STREAM_DESIGN_CAPACITY,False),
            CapacitySensorEntity(client, self, "fullCap", const.STREAM_FULL_CAPACITY, False),
            CapacitySensorEntity(client, self, "remainCap", const.STREAM_REMAIN_CAPACITY,False),

            MilliVoltSensorEntity(client, self, "vol", const.BATTERY_VOLT, False)
            .attr("minCellVol", const.ATTR_MIN_CELL_VOLT, 0)
            .attr("maxCellVol", const.ATTR_MAX_CELL_VOLT, 0),
            MilliVoltSensorEntity(client, self, "minCellVol", const.MIN_CELL_VOLT, False),
            MilliVoltSensorEntity(client, self, "maxCellVol", const.MAX_CELL_VOLT, False),
            LevelSensorEntity(client, self, "soh", const.SOH),

            TempSensorEntity(client, self, "temp", const.BATTERY_TEMP)
            .attr("minCellTemp", const.ATTR_MIN_CELL_TEMP, 0)
            .attr("maxCellTemp", const.ATTR_MAX_CELL_TEMP, 0),
            TempSensorEntity(client, self, "minCellTemp", const.MIN_CELL_TEMP, False),
            TempSensorEntity(client, self, "maxCellTemp", const.MAX_CELL_TEMP, False),

            CyclesSensorEntity(client, self, "cycles", const.CYCLES),

            InWattsSensorEntity(client, self, "inputWatts", const.STREAM_IN_POWER),
            OutWattsSensorEntity(client, self, "outputWatts", const.STREAM_OUT_POWER),

            RemainSensorEntity(client, self, "remainTime", const.REMAINING_TIME),
        ]
    # moduleWifiRssi
    def numbers(self, client: EcoflowApiClient) -> list[BaseNumberEntity]:
        return []

    def switches(self, client: EcoflowApiClient) -> list[BaseSwitchEntity]:
        return []

    def selects(self, client: EcoflowApiClient) -> list[BaseSelectEntity]:
        return []