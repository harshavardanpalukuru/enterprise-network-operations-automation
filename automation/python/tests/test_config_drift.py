import unittest

from noc_automation.config_drift import compare_configurations


BASELINE = """!
hostname R1-HQ
!
interface GigabitEthernet0/0.10
 description HR
 ip address 10.10.10.1 255.255.255.0
 ip access-group ACL-HR-INBOUND in
!
"""


class TestConfigurationDrift(unittest.TestCase):

    def test_identical_configuration_returns_clean(self):
        result = compare_configurations(
            BASELINE,
            BASELINE,
            "R1-HQ",
        )

        self.assertEqual(result["status"], "CLEAN")
        self.assertEqual(result["diff"], "")

    def test_modified_configuration_detects_drift(self):
        modified = BASELINE.replace(
            "ip access-group ACL-HR-INBOUND in",
            "ip access-group ACL-UNEXPECTED in",
        )

        result = compare_configurations(
            BASELINE,
            modified,
            "R1-HQ",
        )

        self.assertEqual(result["status"], "DRIFT_DETECTED")
        self.assertIn("- ip access-group ACL-HR-INBOUND in", result["diff"])
        self.assertIn("+ ip access-group ACL-UNEXPECTED in", result["diff"])

    def test_line_ending_difference_does_not_detect_drift(self):
        windows_config = BASELINE.replace("\n", "\r\n")

        result = compare_configurations(
            BASELINE,
            windows_config,
            "R1-HQ",
        )

        self.assertEqual(result["status"], "CLEAN")
        self.assertEqual(result["diff"], "")

    def test_header_present_in_baseline_but_absent_live_is_clean(self):
        # R1-HQ case: the live config had no "Last configuration change" header.
        with_header = (
            "Current configuration : 5670 bytes\n!\n"
            "! Last configuration change at 01:10:49 UTC Sat Nov 7 2026\n!\n"
            "version 15.9\nhostname R1-HQ\n"
        )
        without_header = (
            "Current configuration : 5609 bytes\n!\n"
            "version 15.9\nhostname R1-HQ\n"
        )

        result = compare_configurations(with_header, without_header, "R1-HQ")

        self.assertEqual(result["status"], "CLEAN")

    def test_changed_timestamp_and_byte_count_is_clean(self):
        # SW1-HQ case: only the last-change timestamp and byte count differ.
        before = (
            "Current configuration : 4969 bytes\n!\n"
            "! Last configuration change at 13:34:59 UTC Sat Nov 7 2026\n!\n"
            "version 15.2\nhostname SW1-HQ\n"
        )
        after = (
            "Current configuration : 4970 bytes\n!\n"
            "! Last configuration change at 03:03:19 UTC Tue Nov 10 2026\n!\n"
            "version 15.2\nhostname SW1-HQ\n"
        )

        result = compare_configurations(before, after, "SW1-HQ")

        self.assertEqual(result["status"], "CLEAN")

    def test_real_change_is_still_detected_next_to_header_changes(self):
        before = (
            "Current configuration : 100 bytes\n!\n"
            "! Last configuration change at 01:00:00 UTC Sat Nov 7 2026\n!\n"
            "hostname R1-HQ\nip route 10.20.30.0 255.255.255.0 172.16.12.2\n"
        )
        after = (
            "Current configuration : 120 bytes\n!\n"
            "! Last configuration change at 02:00:00 UTC Tue Nov 10 2026\n!\n"
            "hostname R1-HQ\nip route 10.20.30.0 255.255.255.0 172.16.12.9\n"
        )

        result = compare_configurations(before, after, "R1-HQ")

        self.assertEqual(result["status"], "DRIFT_DETECTED")
        self.assertIn("172.16.12.9", result["diff"])
        self.assertNotIn("Last configuration change", result["diff"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
