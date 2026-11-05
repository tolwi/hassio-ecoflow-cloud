"""Network-free regression tests for the actual MQTT wrapper.

Run: python -m unittest discover -s tests -v
HA, paho and device imports are stubbed; callbacks and lifecycle code are not.
"""

import importlib.util
import logging
import sys
import threading
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


class FakeTimer:
    def __init__(self, interval, function, args):
        self.interval = interval
        self.function = function
        self.args = args
        self.cancelled = False
        self.daemon = False

    def start(self):
        pass

    def cancel(self):
        self.cancelled = True

    def fire(self):
        # Deliberately run cancelled callbacks too, to exercise generation guards.
        self.function(*self.args)


class PowerStream:
    def __init__(self):
        self.data = types.SimpleNamespace(params={})
        self.device_info = types.SimpleNamespace(
            get_topic="test/powerstream/get", topics=lambda: ["test/powerstream/get_reply"]
        )
        self.get_quota_message = Mock(return_value=types.SimpleNamespace(to_mqtt_payload=lambda: b"read-only-quota"))


def load_wrapper():
    """Import the whole production file without importing HA or opening a socket."""
    modules = {}

    def stub(name, **attributes):
        module = types.ModuleType(name)
        module.__path__ = []
        module.__dict__.update(attributes)
        modules[name] = module

    for name in ["homeassistant", "homeassistant.components", "homeassistant.components.mqtt", "paho", "paho.mqtt"]:
        stub(name)
    stub("homeassistant.core", callback=lambda function: function)
    stub("homeassistant.components.mqtt.async_client", AsyncMQTTClient=Mock())
    stub(
        "paho.mqtt.client",
        **dict.fromkeys(["Client", "ConnectFlags", "DisconnectFlags", "MQTTMessage", "PayloadType"], object),
    )
    stub("paho.mqtt.enums", CallbackAPIVersion=types.SimpleNamespace(VERSION2=2))
    stub("paho.mqtt.properties", Properties=object)
    stub("paho.mqtt.reasoncodes", ReasonCode=object)
    for name in [
        "custom_components",
        "custom_components.ecoflow_cloud",
        "custom_components.ecoflow_cloud.devices.internal",
    ]:
        stub(name)
    stub("custom_components.ecoflow_cloud.api", EcoflowMqttInfo=object)
    stub("custom_components.ecoflow_cloud.devices", BaseDevice=object)
    stub("custom_components.ecoflow_cloud.devices.internal.powerstream", PowerStream=PowerStream)
    path = Path(__file__).resolve().parents[1] / "custom_components/ecoflow_cloud/api/ecoflow_mqtt.py"
    name = "custom_components.ecoflow_cloud.api.ecoflow_mqtt"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module, modules


class PowerStreamBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.module, self.modules = load_wrapper()
        self.module.threading = types.SimpleNamespace(RLock=threading.RLock, Timer=FakeTimer)
        self.module._LOGGER = Mock(spec=logging.Logger)
        self.imports = patch.dict(sys.modules, self.modules)
        self.imports.start()
        self.addCleanup(self.imports.stop)
        self.device = PowerStream()
        self.transport = Mock()
        self.transport.subscribe.return_value = (0, 42)
        self.transport.is_connected.return_value = True
        self.modules["homeassistant.components.mqtt.async_client"].AsyncMQTTClient.return_value = self.transport
        info = types.SimpleNamespace(client_id="test", username="test", password="test", url="invalid.test", port=8883)
        self.client = self.module.EcoflowMQTTClient(info, {"test": self.device})
        self.addCleanup(self.client.stop)

    def connect(self):
        self.transport.on_connect(self.transport, None, None, 0, None)

    def ack(self, mid=42, failures=(False,)):
        codes = [types.SimpleNamespace(is_failure=failure) for failure in failures]
        self.transport.on_subscribe(self.transport, None, mid, codes, None)

    def timers(self):
        return self.client._EcoflowMQTTClient__bootstrap_timers

    def test_constructor_wires_callback_without_sending_quota(self):
        self.assertEqual(self.transport.on_subscribe, self.client._on_subscribe)
        self.assertEqual(self.timers(), [])
        self.transport.publish.assert_not_called()

    def test_waits_for_matching_successful_suback(self):
        self.connect()
        self.transport.publish.assert_not_called()
        self.assertEqual(self.timers(), [])
        self.ack(mid=41)
        self.assertEqual(self.timers(), [])
        self.ack()
        self.assertEqual([timer.interval for timer in self.timers()], [2, 10, 30])
        self.assertTrue(all(timer.daemon for timer in self.timers()))

    def test_at_most_three_reads_on_get_topic(self):
        self.connect()
        self.ack()
        for timer in self.timers():
            timer.fire()
        self.assertEqual(self.transport.publish.call_count, 3)
        for call in self.transport.publish.call_args_list:
            self.assertEqual(call.args, ("test/powerstream/get", b"read-only-quota", 1))
        self.assertEqual(self.device.data.params, {})

    def test_valid_zero_already_present_needs_no_retry(self):
        self.device.data.params["20_1.supplyPriority"] = 0
        self.connect()
        self.ack()
        self.assertEqual(self.timers(), [])

    def test_mode_received_before_first_retry_suppresses_all_reads(self):
        self.connect()
        self.ack()
        self.device.data.params["20_1.supplyPriority"] = 0
        for timer in self.timers():
            timer.fire()
        self.transport.publish.assert_not_called()

    def test_late_mode_suppresses_remaining_reads(self):
        self.connect()
        self.ack()
        self.timers()[0].fire()
        self.device.data.params["20_1.supplyPriority"] = 0
        for timer in self.timers()[1:]:
            timer.fire()
        self.assertEqual(self.transport.publish.call_count, 1)

    def test_failed_or_empty_suback_does_not_schedule(self):
        for failures in [(True,), (False, True), ()]:
            with self.subTest(failures=failures):
                self.connect()
                self.ack(failures=failures)
                self.assertEqual(self.timers(), [])

    def test_subscribe_failure_does_not_schedule(self):
        self.transport.subscribe.return_value = (4, 42)
        self.connect()
        self.ack()
        self.assertEqual(self.timers(), [])

    def test_duplicate_suback_does_not_duplicate_timers(self):
        self.connect()
        self.ack()
        self.ack()
        self.assertEqual(len(self.timers()), 3)

    def test_other_devices_are_untouched(self):
        other = PowerStream()
        other.__class__ = type("OtherDevice", (), {})
        self.client._EcoflowMQTTClient__devices = {"other": other}
        self.connect()
        self.ack()
        self.assertEqual(self.timers(), [])
        other.get_quota_message.assert_not_called()

    def test_disconnect_cancels_and_invalidates_callbacks(self):
        self.connect()
        self.ack()
        old = list(self.timers())
        self.transport.on_disconnect(self.transport, None, None, types.SimpleNamespace(is_failure=False), None)
        for timer in old:
            self.assertTrue(timer.cancelled)
            timer.fire()
        self.transport.publish.assert_not_called()

    def test_disconnected_transport_suppresses_retry(self):
        self.connect()
        self.ack()
        self.transport.is_connected.return_value = False
        self.timers()[0].fire()
        self.transport.publish.assert_not_called()

    def test_reconnect_replaces_old_generation(self):
        self.connect()
        self.ack()
        old = list(self.timers())
        self.client.reconnect()
        self.connect()
        self.ack()
        for timer in old:
            self.assertTrue(timer.cancelled)
            timer.fire()
        self.transport.publish.assert_not_called()
        self.timers()[0].fire()
        self.assertEqual(self.transport.publish.call_count, 1)

    def test_stop_cancels_and_rejects_late_connect_and_suback(self):
        self.connect()
        self.ack()
        old = list(self.timers())
        self.client.stop()
        self.transport.subscribe.reset_mock()
        self.connect()
        self.ack()
        for timer in old:
            self.assertTrue(timer.cancelled)
            timer.fire()
        self.assertEqual(self.timers(), [])
        self.transport.subscribe.assert_not_called()
        self.transport.publish.assert_not_called()


if __name__ == "__main__":
    unittest.main()
