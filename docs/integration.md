In order to add a new entity for a device type, following info is needed:
- *sensor*: name, data_key
- *switch*: name, data_key, action_command
- *select*: name, data_key, action_command, options
- *slider*: name, data_key, action_command, min, max

Current integrations details:
- [DELTA_2](devices/DELTA_2.md)
- [RIVER_2](devices/RIVER_2.md)
- [RIVER_2_MAX](devices/RIVER_2_MAX.md)
- [RIVER_2_PRO](devices/RIVER_2_PRO.md)
- [DELTA_PRO](devices/DELTA_PRO.md)
- [RIVER_MAX](devices/RIVER_MAX.md)
- [RIVER_PRO](devices/RIVER_PRO.md)
- [DELTA_MAX](devices/DELTA_MAX.md)
- [DELTA_2_MAX](devices/DELTA_2_MAX.md)


Use [diagnostic](https://www.home-assistant.io/integrations/diagnostics/) dump to find `data_key` and `action_command`:
  - `data_key` 
    
    Compare values from mobile app with values in `data` section and try to define the particular key for the entity you want to add.

  - `action_command`

    Change value in mobile app and then find appropriate command in `commands` section by comparing params with the value you set in the app.


_Note: if your device type is not supported - use **DIAGNOSTIC** type._