import json
from unittest.mock import Mock

from custom_components.ecoflow_cloud.devices import BaseDevice, EcoflowDeviceInfo
from custom_components.ecoflow_cloud.devices.registry import devices, device_by_product
from custom_components.ecoflow_cloud.entities import EcoFlowBaseCommandEntity, BaseSwitchEntity, BaseSensorEntity, \
    BaseNumberEntity, BaseSelectEntity, EcoFlowDictEntity

MARKER_VALUE = -66666

device_info = EcoflowDeviceInfo(public_api = False,
    sn = "SN",
    name = "NAME",
    device_type = "TYPE",
    data_topic = "DATA_TOPIC",
    status=1,
    set_topic = "SET_TOPIC",
    set_reply_topic = "SET_REPLY_TOPIC",
    get_topic = None,
    get_reply_topic = None,
    status_topic = None)


def device_summary(device: BaseDevice) -> str:
    client = Mock()
    client.device = device
    return "sensors: %d, switches: %d, sliders: %d, selects: %d" % (
        len(device.sensors(client)),
        len(device.switches(client)),
        len(device.numbers(client)),
        len(device.selects(client))
    )


def command_ro(e: EcoFlowBaseCommandEntity) -> str:
    command_dict = e.command_dict(MARKER_VALUE)
    if command_dict is None:
        return " _(read-only)_"
    else:
        return ""


def prepare_options(options: dict[str, int]) -> str:
    return ", ".join(["%s (%d)" % (k, v) for k, v in options.items()])


def prepare_command(e: EcoFlowBaseCommandEntity) -> str | None:
    command_dict = e.command_dict(MARKER_VALUE)
    if command_dict is not None:
        for k, v in command_dict["params"].items():
            if v == MARKER_VALUE:
                command_dict["params"][k] = "VALUE"

        return json.dumps(command_dict)
    else:
        return "_ command not available _"


def render_sensor(sw: BaseSensorEntity, brief: bool = False) -> str:
    if not isinstance(sw, EcoFlowDictEntity):
        return "- %s" % sw.name
    elif brief:
        if sw.enabled_default:
            return "- %s" % sw.name
        else:
            if sw.auto_enable:
                return "- %s  _(auto)_" % sw.name
            else:
                return "- %s  _(disabled)_" % sw.name
    else:
        if sw.enabled_default:
            return "- %s (`%s`)" % (sw.name, sw.mqtt_key)
        else:
            if sw.auto_enable:
                return "- %s (`%s`)   _(auto)_" % (sw.name, sw.mqtt_key)
            else:
                return "- %s (`%s`)   _(disabled)_" % (sw.name, sw.mqtt_key)


def render_switch(sw: BaseSwitchEntity, brief: bool = False) -> str:
    if brief:
        return "- %s %s" % (sw.name, command_ro(sw))
    else:
        return "- %s (`%s` -> `%s`)" % (sw.name, sw.mqtt_key, prepare_command(sw))


def render_number(sw: BaseNumberEntity, brief: bool = False) -> str:
    if brief:
        return "- %s %s" % (sw.name, command_ro(sw))
    else:
        return "- %s (`%s` -> `%s` [%d - %d])" % (
            sw.name, sw.mqtt_key, prepare_command(sw), int(sw.native_min_value), int(sw.native_max_value))


def render_select(sw: BaseSelectEntity, brief: bool = False) -> str:
    if brief:
        return "- %s %s" % (sw.name, command_ro(sw))
    else:
        return "- %s (`%s` -> `%s` [%s])" % (
            sw.name, sw.mqtt_key, prepare_command(sw), prepare_options(sw.options_dict()),)


def render_device_summary(device: BaseDevice, brief: bool = False) -> str:
    client = Mock()
    client.device = device
    res = ""
    res += "\n*Sensors*\n"
    for sw in device.sensors(client):
        res += render_sensor(sw, brief) + "\n"

    res += "\n*Switches*\n"
    for sw in device.switches(client):
        res += render_switch(sw, brief) + "\n"

    res += "\n*Sliders (numbers)*\n"
    for sw in device.numbers(client):
        res += render_number(sw, brief) + "\n"

    res += "\n*Selects*\n"
    for sw in device.selects(client):
        res += render_select(sw, brief) + "\n"

    return res


def render_brief_summary():
    for dt, dev in devices.items():
        if dt != "DIAGNOSTIC":
            device = dev(device_info)
            device.configure(None, 10, False)
            print("<details><summary> %s <i>(%s)</i> </summary>" % (dt, device_summary(device)))
            print("<p>")
            print(render_device_summary(device, True))
            print("</p></details>")
            print()

    for dt, dev in device_by_product.items():
        if dt != "DIAGNOSTIC":
            device = dev(device_info)
            device.configure(None, 10, False)
            print("<details><summary> %s (API) <i>(%s)</i> </summary>" % (dt, device_summary(device)))
            print("<p>")
            print(render_device_summary(device, True))
            print("</p></details>")
            print()


def update_full_summary():
    for dt, dev in devices.items():
        if dt != "DIAGNOSTIC":
            device = dev(device_info)
            device.configure(None, 10, False)
            with open("devices/%s.md" % dt, "w+") as f:
                f.write("## %s\n" % dt)
                f.write(render_device_summary(device))
                f.write("\n\n")

            print("- [%s](devices/%s.md)" % (dt, dt))

    for dt, dev in device_by_product.items():
        if dt != "DIAGNOSTIC":
            device = dev(device_info)
            device.configure(None, 10, False)
            name = dt.replace(" ", "_")
            with open("devices/%s-Public.md" % name, "w+") as f:
                f.write("## %s\n" % name)
                f.write(render_device_summary(device))
                f.write("\n\n")

            print("- [%s](devices/%s-Public.md)" % (name, name))


if __name__ == "__main__":
    update_full_summary()
    render_brief_summary()
