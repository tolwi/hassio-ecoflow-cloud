from typing import Any, List
import json
from unittest.mock import Mock

from custom_components.ecoflow_cloud.device_data import DeviceData, DeviceOptions
from custom_components.ecoflow_cloud.devices import BaseDevice, EcoflowDeviceInfo
from custom_components.ecoflow_cloud.devices.registry import (
    devices,
    device_by_product,
    device_support_sub_devices,
)
from custom_components.ecoflow_cloud.entities import (
    EcoFlowBaseCommandEntity,
    BaseSwitchEntity,
    BaseSensorEntity,
    BaseNumberEntity,
    BaseSelectEntity,
    EcoFlowDictEntity,
)

MARKER_VALUE = -66666

multi_device_config = {
    "Power Kits": [
        "bbcin",
        "bbcout",
        "iclow",
        "bpxxx",
        "kitscc",
        "lddc",
        "ichigh",
        "ldac",
    ]
}

device_info = EcoflowDeviceInfo(
    public_api=False,
    sn="SN",
    name="NAME",
    device_type="TYPE",
    data_topic="DATA_TOPIC",
    status=1,
    set_topic="SET_TOPIC",
    set_reply_topic="SET_REPLY_TOPIC",
    get_topic=None,
    get_reply_topic=None,
    status_topic=None,
)
device_options = DeviceOptions(0, 0, False)


def get_device_data(deviceType: str) -> List[DeviceData]:
    if deviceType in device_support_sub_devices:
        if deviceType in multi_device_config:
            return [
                DeviceData(
                    "SN",
                    "NAME",
                    moduleType,
                    device_options,
                    "DISPLAY_NAME",
                    DeviceData("SN", "NAME", "TYPE", device_options, None, None),
                )
                for moduleType in multi_device_config[deviceType]
            ]
        raise NotImplementedError(
            "For all multi-device types, a configuration must be provided"
        )
    else:
        return [DeviceData("SN", "NAME", "TYPE", device_options, None, None)]


def get_devices(deviceType: str, dev: type[BaseDevice]) -> List[BaseDevice]:
    real_devices = []
    for device_data in get_device_data(deviceType):
        device = dev(device_info, device_data)
        device.configure(None)
        real_devices.append(device)
    return real_devices


def device_summary(base_devices: List[BaseDevice]) -> str:
    total_sensors = 0
    total_switches = 0
    total_numbers = 0
    total_selects = 0
    for device in base_devices:
        client = Mock()
        client.device = device
        total_sensors += len(device.sensors(client))
        total_switches += len(device.switches(client))
        total_numbers += len(device.numbers(client))
        total_selects += len(device.selects(client))
    return f"sensors: {total_sensors}, switches: {total_switches}, sliders: {total_numbers}, selects: {total_selects}"


def command_ro(e: EcoFlowBaseCommandEntity) -> str:
    command_dict = e.command_dict(MARKER_VALUE)
    if command_dict is None:
        return " _(read-only)_"
    else:
        return ""


def prepare_options(options: dict[str, Any]) -> str:
    return ", ".join(["%s (%s)" % (k, v) for k, v in options.items()])


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
            sw.name,
            sw.mqtt_key,
            prepare_command(sw),
            int(sw.native_min_value),
            int(sw.native_max_value),
        )


def render_select(sw: BaseSelectEntity, brief: bool = False) -> str:
    if brief:
        return "- %s %s" % (sw.name, command_ro(sw))
    else:
        return "- %s (`%s` -> `%s` [%s])" % (
            sw.name,
            sw.mqtt_key,
            prepare_command(sw),
            prepare_options(sw.options_dict()),
        )


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
    content_summary = "## Current state\n"
    content_summary+= "### Devices available with private_api\n"
    for dt, dev in devices.items():
        if not dt.upper().startswith("DIAGNOSTIC"):
            content = ""
            real_devices = get_devices(dt, dev)
            for device in real_devices:
                if len(real_devices) > 1:
                    content = content + f"\n### {device.device_data.device_type}\n"
                content = content + render_device_summary(device, True)
            content_summary+="<details><summary> %s <i>(%s)</i> </summary>" % (dt, device_summary(real_devices))
            content_summary+="\n<p>\n"
            content_summary+=content
            content_summary+="\n</p></details>\n"
            content_summary+= "\n"

    content_summary+= "### Devices available with public_api\n"
    for dt, dev in device_by_product.items():
        if not dt.upper().startswith("DIAGNOSTIC"):
            content = ""
            real_devices = get_devices(dt, dev)
            for device in real_devices:
                if len(real_devices) > 1:
                    content = content + f"\n### {device.device_data.device_type}\n"
                content = content + render_device_summary(device, True)
            content_summary+="<details><summary> %s (API) <i>(%s)</i> </summary>" % (dt, device_summary(real_devices))

            content_summary+="\n<p>\n"
            content_summary +=content
            content_summary+="\n</p></details>\n"
            content_summary+="\n"
    print(content_summary)
    with open("summary.md" , "w+") as f_summary:
        f_summary.write(content_summary)
        f_summary.write("\n")


def update_full_summary():
    for dt, dev in devices.items():
        if not dt.upper().startswith("DIAGNOSTIC"):
            content = ""
            real_devices = get_devices(dt, dev)
            for device in real_devices:
                if len(real_devices) > 1:
                    content = content + f"\n### {device.device_data.device_type}\n"
                content = content + render_device_summary(device)
            with open("devices/%s.md" % dt, "w+") as f:
                f.write("## %s\n" % dt)
                f.write(content)
                f.write("\n\n")

            print("- [%s](devices/%s.md)" % (dt, dt))

    for dt, dev in device_by_product.items():
        if not dt.upper().startswith("DIAGNOSTIC"):
            content = ""
            real_devices = get_devices(dt, dev)
            for device in real_devices:
                if len(real_devices) > 1:
                    content = content + f"\n### {device.device_data.device_type}\n"
                content = content + render_device_summary(device)
            name = dt.replace(" ", "_")
            with open("devices/%s-Public.md" % name, "w+") as f:
                f.write("## %s\n" % name)
                f.write(content)
                f.write("\n\n")

            print("- [%s](devices/%s-Public.md)" % (name, name))


if __name__ == "__main__":
    update_full_summary()
    render_brief_summary()
