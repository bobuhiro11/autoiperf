import unittest
from autoiperf import udp
import json


class TestUDP(unittest.TestCase):
    def test_is_expected_tx_rate(self):
        with open('autoiperf/output.json', 'r') as f:
            output = json.load(f)
        self.assertTrue(udp.is_expected_tx_rate(output))

    def test_is_low_drop_rate(self):
        with open('autoiperf/output.json', 'r') as f:
            output = json.load(f)
        self.assertTrue(udp.is_low_drop_rate(output))


if __name__ == '__main__':
    unittest.main()
