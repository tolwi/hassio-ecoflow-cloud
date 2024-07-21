In order to add a new entity for a device type, following info is needed:

- _sensor_: name, data_key
- _switch_: name, data_key, action_command
- _select_: name, data_key, action_command, options
- _slider_: name, data_key, action_command, min, max

Current integrations details:

- [DELTA_2](devices/DELTA_2.md)
- [RIVER_2](devices/RIVER_2.md)
- [RIVER_2_MAX](devices/RIVER_2_MAX.md)
- [RIVER_2_PRO](devices/RIVER_2_PRO.md)
- [DELTA_PRO](devices/DELTA_PRO.md)
- [RIVER_MAX](devices/RIVER_MAX.md)
- [RIVER_PRO](devices/RIVER_PRO.md)
- [DELTA_MINI](devices/DELTA_MINI.md)
- [DELTA_MAX](devices/DELTA_MAX.md)
- [DELTA_2_MAX](devices/DELTA_2_MAX.md)
- [POWERSTREAM](devices/POWERSTREAM.md)
- [GLACIER](devices/GLACIER.md)

Use [diagnostic](https://www.home-assistant.io/integrations/diagnostics/) dump to find `data_key` and `action_command`:

- `data_key`

  Compare values from mobile app with values in `data` section and try to define the particular key for the entity you want to add.

- `action_command`

  Change value in mobile app and then find appropriate command in `commands` section by comparing params with the value you set in the app.

_Note: if your device type is not supported - use **DIAGNOSTIC** type._

## Quick start

Clone this repository and open it as a dev container in VsCode.
This will take some time. After that you can start the debugging task "Home Assistant".
After some while you can access `http://localhost:8123/`.
Create a development user account. After that you can add this addon under the normal hass integrations config.

> Important note: Right now you can only debug the code under: `core/config/custom_components/ecoflow_cloud`.
