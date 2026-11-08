"""Unit tests for official STREAM 5000 quota normalization.

Run with: python -m unittest discover -s tests -p 'test_stream_5000_data.py'
The pure parser is loaded by file path to avoid importing Home Assistant.
"""

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components/ecoflow_cloud/devices/public/stream_5000_data.py"
)
spec = importlib.util.spec_from_file_location("stream_5000_data", MODULE_PATH)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
normalize_quota = module.normalize_quota


class TestStream5000Quota(unittest.TestCase):
    def test_nested_mqtt(self):
        raw = {
            "params": {
                "sysEnergyStreamReport": {"bpSoc": 72, "pvPwr": 490, "gridPwr": -180},
                "bpBackupConfig": {"backupSoc": 20, "backupSocOnOff": True},
            }
        }
        self.assertEqual(
            normalize_quota(raw),
            {
                "sysEnergyStreamReport.bpSoc": 72,
                "sysEnergyStreamReport.pvPwr": 490,
                "sysEnergyStreamReport.gridPwr": -180,
                "bpBackupConfig.backupSoc": 20,
                "bpBackupConfig.backupSocOnOff": True,
            },
        )

    def test_flat_http(self):
        self.assertEqual(
            normalize_quota({
                "sysEnergyStreamReport-bpSoc": 56,
                "sysEnergyStreamReport-pvPwr": 120,
                "powerParameterConfig-feedToGridLimitOnOff": False,
                "devSwitch-acSocketOnoff": True,
            }),
            {
                "sysEnergyStreamReport.bpSoc": 56,
                "sysEnergyStreamReport.pvPwr": 120,
                "powerParameterConfig.feedToGridLimitOnOff": False,
                "devSwitch.acSocketOnoff": True,
            },
        )

    def test_preserves_unknown_fields(self):
        self.assertEqual(
            normalize_quota({"other-group": 1, "workMode": "AI_MODE", "soc": 40}),
            {"other-group": 1, "workMode": "AI_MODE", "soc": 40},
        )

    def test_malformed_params(self):
        self.assertEqual(normalize_quota({"params": None}), {})

    def test_does_not_mutate_input(self):
        raw = {"bpBackupConfig": {"backupSoc": 15}}
        self.assertEqual(normalize_quota(raw), {"bpBackupConfig.backupSoc": 15})
        self.assertEqual(raw, {"bpBackupConfig": {"backupSoc": 15}})


if __name__ == "__main__":
    unittest.main()
