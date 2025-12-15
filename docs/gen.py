from custom_components.ecoflow_cloud.api.private_api import PrivateAPIMessageProtocol
import asyncio
import json
import logging
import os
from typing import Any, List
from unittest.mock import Mock

from homeassistant.core import HomeAssistant
from homeassistant.helpers.frame import async_setup as frame_setup

from custom_components.ecoflow_cloud.device_data import DeviceData, DeviceOptions
from custom_components.ecoflow_cloud.devices import BaseDevice, EcoflowDeviceInfo

from custom_components.ecoflow_cloud.devices.registry import (
    device_by_product,
    device_support_sub_devices,
    devices,
)
from custom_components.ecoflow_cloud.entities import (
    BaseNumberEntity,
    BaseSelectEntity,
    BaseSensorEntity,
    BaseSwitchEntity,
    EcoFlowBaseCommandEntity,
    EcoFlowDictEntity,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration constants
MARKER_VALUE = 6666
OUTPUT_DIR = "devices"
SUMMARY_FILENAME = "summary.md"

# Device test configuration constants
DEVICE_SN = "SN"
DEVICE_NAME = "_[Device Name]_"
DEVICE_TYPE = "TYPE"
DATA_TOPIC = "DATA_TOPIC"
DEVICE_STATUS = 1
SET_TOPIC = "SET_TOPIC"
SET_REPLY_TOPIC = "SET_REPLY_TOPIC"


def create_test_device_info() -> EcoflowDeviceInfo:
    """Create a test device info object."""
    return EcoflowDeviceInfo(
        public_api=False,
        sn=DEVICE_SN,
        name=DEVICE_NAME,
        device_type=DEVICE_TYPE,
        data_topic=DATA_TOPIC,
        status=DEVICE_STATUS,
        set_topic=SET_TOPIC,
        set_reply_topic=SET_REPLY_TOPIC,
        get_topic=None,
        get_reply_topic=None,
        status_topic=None,
    )


# Multi-device configurations
MULTI_DEVICE_CONFIGURATIONS = {
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

# Initialize configurations
device_options = DeviceOptions(0, 0, False)


class MockSetup:
    """Handles setup of mock objects for documentation generation."""

    @staticmethod
    async def setup_hass() -> HomeAssistant:
        """Set up Home Assistant with all necessary mocks."""
        hass = HomeAssistant("./")
        hass.data["entity_registry"] = Mock()
        hass.data["device_registry"] = Mock()

        await hass.async_start()
        frame_setup(hass)

        logger.info("Home Assistant mock setup completed")
        return hass


class DocumentationGenerator:
    """Handles generation of device documentation."""

    def get_device_data(self, device_type: str) -> List[DeviceData]:
        """Get device data for a given device type."""
        if device_type in device_support_sub_devices:
            if device_type in MULTI_DEVICE_CONFIGURATIONS:
                return [
                    DeviceData(
                        DEVICE_SN,
                        DEVICE_NAME,
                        module_type,
                        device_options,
                        "DISPLAY_NAME",
                        DeviceData(
                            DEVICE_SN,
                            DEVICE_NAME,
                            DEVICE_TYPE,
                            device_options,
                            None,
                            None,
                        ),
                    )
                    for module_type in MULTI_DEVICE_CONFIGURATIONS[device_type]
                ]
            raise NotImplementedError(
                f"Multi-device type '{device_type}' requires configuration but none provided"
            )
        else:
            return [
                DeviceData(
                    DEVICE_SN,
                    DEVICE_NAME,
                    DEVICE_TYPE,
                    device_options,
                    None,
                    None,
                )
            ]

    def get_devices(
        self, hass: HomeAssistant, device_type: str, dev: type[BaseDevice]
    ) -> List[BaseDevice]:
        real_devices = []
        device_info = create_test_device_info()
        for device_data in self.get_device_data(device_type):
            device = dev(device_info, device_data)
            device.configure(hass)
            real_devices.append(device)
        return real_devices

    def device_summary(self, base_devices: List[BaseDevice]) -> str:
        """Generate a summary string for devices."""
        if not base_devices:
            return "No devices available"

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

    def render_brief_summary(self, hass: HomeAssistant):
        """Generate brief summary documentation."""
        content_summary = "## Current state\n"
        content_summary += "### Devices available with private_api\n"

        for dt, dev in devices.items():
            if not dt.upper().startswith("DIAGNOSTIC"):
                content = ""
                real_devices = self.get_devices(hass, dt, dev)
                for device in real_devices:
                    if len(real_devices) > 1:
                        content = content + f"\n### {device.device_data.device_type}\n"
                    content = content + render_device_summary(device, True)
                content_summary += "<details><summary> %s <i>(%s)</i> </summary>" % (
                    dt,
                    self.device_summary(real_devices),
                )
                content_summary += "\n<p>\n"
                content_summary += content
                content_summary += "\n</p></details>\n"
                content_summary += "\n"

        content_summary += "### Devices available with public_api\n"
        for dt, dev in device_by_product.items():
            if not dt.upper().startswith("DIAGNOSTIC"):
                content = ""
                real_devices = self.get_devices(hass, dt, dev)
                for device in real_devices:
                    if len(real_devices) > 1:
                        content = content + f"\n### {device.device_data.device_type}\n"
                    content = content + render_device_summary(device, True)
                content_summary += (
                    "<details><summary> %s (API) <i>(%s)</i> </summary>"
                    % (
                        dt,
                        self.device_summary(real_devices),
                    )
                )

                content_summary += "\n<p>\n"
                content_summary += content
                content_summary += "\n</p></details>\n"
                content_summary += "\n"

        print(content_summary)

        with open(SUMMARY_FILENAME, "w+", encoding="utf-8") as f_summary:
            f_summary.write(content_summary)
            f_summary.write("\n")

    def update_full_summary(self, hass: HomeAssistant):
        """Generate full device documentation."""
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        for dt, dev in devices.items():
            if not dt.upper().startswith("DIAGNOSTIC"):
                content = ""
                real_devices = self.get_devices(hass, dt, dev)
                for device in real_devices:
                    if len(real_devices) > 1:
                        content = content + f"\n### {device.device_data.device_type}\n"
                    content = content + render_device_summary(device)

                filename = f"{OUTPUT_DIR}/{dt}.md"
                with open(filename, "w+", encoding="utf-8") as f:
                    f.write("## %s\n" % dt)
                    f.write(content)
                    f.write("\n\n")

                print("- [%s](devices/%s.md)" % (dt, dt))

        for dt, dev in device_by_product.items():
            if not dt.upper().startswith("DIAGNOSTIC"):
                content = ""
                real_devices = self.get_devices(hass, dt, dev)
                for device in real_devices:
                    if len(real_devices) > 1:
                        content = content + f"\n### {device.device_data.device_type}\n"
                    content = content + render_device_summary(device)

                name = dt.replace(" ", "_")
                filename = f"{OUTPUT_DIR}/{name}-Public.md"
                with open(filename, "w+", encoding="utf-8") as f:
                    f.write("## %s\n" % name)
                    f.write(content)
                    f.write("\n\n")

                print("- [%s](devices/%s-Public.md)" % (name, name))


class MarkdownRenderer:
    """Handles rendering of entities to markdown format."""

    def command_ro(self, e: EcoFlowBaseCommandEntity) -> str:
        """Check if entity is read-only."""
        command_dict = e.command_dict(MARKER_VALUE)
        return " _(read-only)_" if command_dict is None else ""

    def prepare_options(self, options: dict[str, Any]) -> str:
        """Prepare options string for display."""
        return ", ".join(["%s (%s)" % (k, v) for k, v in options.items()])

    def prepare_command(self, e: EcoFlowBaseCommandEntity) -> str:
        """Prepare command string for display."""
        command_dict = e.command_dict(MARKER_VALUE)
        if command_dict is not None:
            if isinstance(command_dict, dict):
                json_dict = command_dict
            elif isinstance(command_dict, PrivateAPIMessageProtocol):
                json_dict = command_dict.to_dict()
            else:
                raise TypeError(
                    "Unsupported command_dict type: %s" % type(command_dict).__name__
                )

            # Check if params exist and update marker values
            if "params" in json_dict:
                for k, v in json_dict["params"].items():
                    if v == MARKER_VALUE:
                        json_dict["params"][k] = "VALUE"

            return json.dumps(json_dict)
        else:
            return "_ command not available _"

    def render_sensor(self, sw: BaseSensorEntity, brief: bool = False) -> str:
        """Render sensor entity to markdown."""
        if not isinstance(sw, EcoFlowDictEntity):
            res = "- %s" % sw.name
        elif brief:
            if sw.enabled_default:
                res = "- %s" % sw.name
            else:
                if sw.auto_enable:
                    res = "- %s  _(auto)_" % sw.name
                else:
                    res = "- %s  _(disabled)_" % sw.name
        else:
            if sw.enabled_default:
                res = "- %s (`%s`)" % (sw.name, sw.mqtt_key)
            else:
                if sw.auto_enable:
                    res = "- %s (`%s`)   _(auto)_" % (sw.name, sw.mqtt_key)
                else:
                    res = "- %s (`%s`)   _(disabled)_" % (sw.name, sw.mqtt_key)

        # Check for energy sensor on all sensor types
        if hasattr(sw, "energy_sensor"):
            sw.entity_id = "sensor.%s" % sw._attr_unique_id
            energy_sensor = sw.energy_sensor()
            if energy_sensor is not None:
                res = res + " (energy:  %s)" % energy_sensor.name

        return res

    def render_switch(self, sw: BaseSwitchEntity, brief: bool = False) -> str:
        """Render switch entity to markdown."""
        if brief:
            return "- %s %s" % (sw.name, self.command_ro(sw))
        else:
            return "- %s (`%s` -> `%s`)" % (
                sw.name,
                sw.mqtt_key,
                self.prepare_command(sw),
            )

    def render_number(self, sw: BaseNumberEntity, brief: bool = False) -> str:
        """Render number entity to markdown."""
        if brief:
            return "- %s %s" % (sw.name, self.command_ro(sw))
        else:
            return "- %s (`%s` -> `%s` [%d - %d])" % (
                sw.name,
                sw.mqtt_key,
                self.prepare_command(sw),
                int(sw.native_min_value),
                int(sw.native_max_value),
            )

    def render_select(self, sw: BaseSelectEntity, brief: bool = False) -> str:
        """Render select entity to markdown."""
        if brief:
            return "- %s %s" % (sw.name, self.command_ro(sw))
        else:
            return "- %s (`%s` -> `%s` [%s])" % (
                sw.name,
                sw.mqtt_key,
                self.prepare_command(sw),
                self.prepare_options(sw.options_dict()),
            )

    def render_device_summary(self, device: BaseDevice, brief: bool = False) -> str:
        """Render complete device summary to markdown."""
        client = Mock()
        client.device = device
        res = ""

        res += "\n*Sensors*\n"
        for sw in device.sensors(client):
            res += self.render_sensor(sw, brief) + "\n"

        res += "\n*Switches*\n"
        for sw in device.switches(client):
            res += self.render_switch(sw, brief) + "\n"

        res += "\n*Sliders (numbers)*\n"
        for sw in device.numbers(client):
            res += self.render_number(sw, brief) + "\n"

        res += "\n*Selects*\n"
        for sw in device.selects(client):
            res += self.render_select(sw, brief) + "\n"

        return res


# Global renderer instance
renderer = MarkdownRenderer()


# Convenience functions for backwards compatibility
def render_device_summary(device: BaseDevice, brief: bool = False) -> str:
    """Backwards compatibility wrapper."""
    return renderer.render_device_summary(device, brief)


if __name__ == "__main__":
    print("Generate docs started !")

    async def main():
        hass = await MockSetup.setup_hass()
        generator = DocumentationGenerator()

        generator.update_full_summary(hass)
        generator.render_brief_summary(hass)

        print("Generate docs finished !")

    asyncio.run(main())
