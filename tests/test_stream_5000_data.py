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

    def test_real_es22_diagnostic_conflicting_quotas(self):
        """Real-life diagnostic shape: three field variants can disagree.

        Anonymized sample based on a STREAM AC 5000 (ES22) diagnostic.
        """
        raw = {
            "params": {
                "bpBackupConfig": {"backupSocOnOff": False, "backupSoc": 40},
                "bpBackupConfig-backupSoc": 40,
                "bpBackupConfig.backupSoc": 40,
                "devSwitch": {"acSocketOnoff": True},
                "devSwitch-acSocketOnoff": True,
                "powerParameterConfig": {"feedToGridLimitOnOff": True},
                "sysEnergyStreamReport": {
                    "bpSoc": 15,
                    "onGridPwr": -107,
                    "pvPwr": 0,
                    "bpPwr": 107,
                    "gridPwr": -52,
                    "loadPwr": 0,
                },
                "sysEnergyStreamReport-bpSoc": 32,
                "sysEnergyStreamReport-bpPwr": 1,
                "sysEnergyStreamReport.bpSoc": 15,
                "sysEnergyStreamReport.bpPwr": 107,
                "workMode": "SELF_CONSUMPTION",
            }
        }
        result = normalize_quota(raw)
        self.assertEqual(result["sysEnergyStreamReport.bpSoc"], 15)
        self.assertEqual(result["sysEnergyStreamReport.bpPwr"], 107)
        self.assertEqual(result["sysEnergyStreamReport.gridPwr"], -52)
        self.assertEqual(result["sysEnergyStreamReport.onGridPwr"], -107)
        self.assertEqual(result["bpBackupConfig.backupSoc"], 40)
        self.assertIs(result["bpBackupConfig.backupSocOnOff"], False)
        self.assertIs(result["devSwitch.acSocketOnoff"], True)
        self.assertEqual(result["workMode"], "SELF_CONSUMPTION")
        self.assertNotIn("sysEnergyStreamReport-bpSoc", result)

    def test_precedence_is_independent_of_input_order(self):
        variants = [
            ("sysEnergyStreamReport.bpSoc", 15),
            ("sysEnergyStreamReport-bpSoc", 32),
            ("sysEnergyStreamReport", {"bpSoc": 14}),
        ]
        for items in (variants, list(reversed(variants))):
            with self.subTest(order=items):
                self.assertEqual(normalize_quota(dict(items))["sysEnergyStreamReport.bpSoc"], 14)

    def test_malformed_params(self):
        self.assertEqual(normalize_quota({"params": None}), {})

    def test_does_not_mutate_input(self):
        raw = {"bpBackupConfig": {"backupSoc": 15}}
        self.assertEqual(normalize_quota(raw), {"bpBackupConfig.backupSoc": 15})
        self.assertEqual(raw, {"bpBackupConfig": {"backupSoc": 15}})


if __name__ == "__main__":
    unittest.main()
