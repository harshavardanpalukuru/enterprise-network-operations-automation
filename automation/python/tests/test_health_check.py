import unittest

from noc_automation.health_check import (
    parse_interfaces,
    summarize_interfaces,
)


class TestNetworkHealth(unittest.TestCase):

    def setUp(self):
        self.sample_output = """
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         unassigned      YES NVRAM  up                    up
GigabitEthernet0/1         unassigned      YES NVRAM  down                  down
GigabitEthernet0/2         unassigned      YES NVRAM  administratively down down
GigabitEthernet0/3         unassigned      YES NVRAM  up                    down
"""

    def test_interface_parsing(self):
        interfaces = parse_interfaces(self.sample_output)
        self.assertEqual(len(interfaces), 4)

    def test_interface_classification(self):
        interfaces = parse_interfaces(self.sample_output)
        summary = summarize_interfaces(interfaces)

        self.assertEqual(summary["up_up"], 1)
        self.assertEqual(summary["down_down"], 1)
        self.assertEqual(summary["administratively_down"], 1)
        self.assertEqual(summary["status_mismatch"], 1)

    def test_empty_output(self):
        interfaces = parse_interfaces("")
        self.assertEqual(interfaces, [])

    def test_all_operational_interfaces(self):
        interfaces = parse_interfaces(
            "GigabitEthernet0/0 unassigned YES NVRAM up up"
        )
        summary = summarize_interfaces(interfaces)

        self.assertEqual(summary["up_up"], 1)
        self.assertEqual(summary["status_mismatch"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
