"""Tests for DELTA Pro 3 MQTT message decoding."""

import base64
import json
import unittest

from custom_components.ecoflow_cloud.devices.internal.delta_pro_3 import DeltaPro3
from custom_components.ecoflow_cloud.devices.internal.proto import ef_dp3_iobroker_pb2 as dp3


class DeltaPro3MessageTests(unittest.TestCase):
    def setUp(self) -> None:
        # Message decoding does not need a live device or an API client.
        self.device = object.__new__(DeltaPro3)

    def test_json_messages_do_not_log_protobuf_errors(self):
        messages = [
            {"params": {"status": 1}},
            {"id": 123, "version": "1.0", "params": {"cmsMaxChgSoc": 80}},
            {"id": 123, "code": "0", "message": "success"},
        ]
        for message in messages:
            for prefix in (b"", b" \t\r\n"):
                with self.subTest(message=message, prefix=prefix):
                    with self.assertNoLogs("custom_components.ecoflow_cloud", level="WARNING"):
                        result = self.device._prepare_data(prefix + json.dumps(message).encode())
                    self.assertEqual(result, message)

    def test_json_status_message_preserves_online_state(self):
        for status in (0, 1):
            with self.subTest(status=status):
                message = {"params": {"status": status}}
                with self.assertNoLogs("custom_components.ecoflow_cloud", level="WARNING"):
                    result = self.device._prepare_data_status_topic(json.dumps(message).encode())
                self.assertEqual(result.online, bool(status))
                self.assertIsNone(result.params)
                self.assertEqual(result.raw_data, message)

    def test_protobuf_telemetry_is_still_decoded(self):
        payload = dp3.DP3DisplayPropertyUpload(bms_batt_soc=65.0).SerializeToString()
        envelope = dp3.DP3HeaderMessage()
        header = envelope.header.add()
        header.cmd_func = 254
        header.cmd_id = 21
        header.pdata = payload
        header.data_len = len(payload)
        raw_data = envelope.SerializeToString()
        for message in (raw_data, base64.b64encode(raw_data)):
            with self.subTest(message=message):
                with self.assertNoLogs("custom_components.ecoflow_cloud", level="WARNING"):
                    result = self.device._prepare_data(message)
                self.assertEqual(result["params"]["bms_batt_soc"], 65.0)

    def test_invalid_json_is_still_logged_and_ignored(self):
        with self.assertLogs("custom_components.ecoflow_cloud", level="ERROR"):
            result = self.device._prepare_data(b'{"params":')
        self.assertEqual(result, {})

    def test_invalid_binary_data_is_still_logged_and_ignored(self):
        with self.assertLogs("custom_components.ecoflow_cloud", level="ERROR"):
            result = self.device._prepare_data(b"\xff\xff")
        self.assertEqual(result, {})
