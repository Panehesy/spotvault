import unittest
from core.adb_sync import parse_adb_devices_output, parse_df_available_bytes


class TestAdbSyncHelpers(unittest.TestCase):
    def test_parse_adb_devices_output(self):
        sample_output = """List of devices attached
RF8M123456X\tdevice
emulator-5554\toffline
192.168.1.50:5555\tunauthorized
"""
        devices = parse_adb_devices_output(sample_output)
        self.assertEqual(len(devices), 3)
        self.assertEqual(devices[0]["serial"], "RF8M123456X")
        self.assertEqual(devices[0]["state"], "device")
        self.assertEqual(devices[1]["state"], "offline")
        self.assertEqual(devices[2]["state"], "unauthorized")

    def test_parse_adb_devices_empty(self):
        sample = "List of devices attached\n"
        devices = parse_adb_devices_output(sample)
        self.assertEqual(len(devices), 0)

    def test_parse_df_available_bytes_standard(self):
        sample = """Filesystem     1K-blocks      Used Available Use% Mounted on
/dev/block/dm-0 120000000  40000000  80000000  34% /sdcard
"""
        avail = parse_df_available_bytes(sample)
        self.assertIsNotNone(avail)
        self.assertEqual(avail, 80000000 * 1024)

    def test_parse_df_available_bytes_invalid(self):
        sample = "command failed"
        avail = parse_df_available_bytes(sample)
        self.assertIsNone(avail)


if __name__ == "__main__":
    unittest.main()
