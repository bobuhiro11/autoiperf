import unittest
from autoiperf import udp
from mock import patch


# iperf -c localhost -t 10 -u -b 70000pps  -l 36 -P 1 -e
output_success_singleflow = '''
------------------------------------------------------------
Client connecting to localhost, UDP port 5001 with pid 2809419
Sending 36 byte datagrams, IPG target: 14.29 us (kalman adjust)
UDP buffer size:  260 KByte (default)
------------------------------------------------------------
[  3] local 127.0.0.1 port 54068 connected with 127.0.0.1 port 5001
[ ID] Interval        Transfer     Bandwidth      Write/Err  PPS
[  3] 0.00-10.00 sec  24.0 MBytes  20.2 Mbits/sec  700001/0    69999 pps
[  3] Sent 700001 datagrams
[  3] Server Report:
[  3]  0.0-10.0 sec  24.0 MBytes  20.2 Mbits/sec   0.000 ms    0/700001 (0%)
'''  # noqa: E501

# iperf -c localhost -t 10 -u -b 1000pps  -l 1490 -P 4 -e
output_success_multiflow = '''
------------------------------------------------------------
Client connecting to localhost, UDP port 5001 with pid 2806131
Sending 1490 byte datagrams, IPG target: 1000.00 us (kalman adjust)
UDP buffer size:  260 KByte (default)
------------------------------------------------------------
[  3] local 127.0.0.1 port 49259 connected with 127.0.0.1 port 5001
[  4] local 127.0.0.1 port 36989 connected with 127.0.0.1 port 5001
[  7] local 127.0.0.1 port 57557 connected with 127.0.0.1 port 5001
[  9] local 127.0.0.1 port 36170 connected with 127.0.0.1 port 5001
[ ID] Interval        Transfer     Bandwidth      Write/Err  PPS
[  3] 0.00-10.00 sec  14.2 MBytes  11.9 Mbits/sec  10001/0      999 pps
[  3] Sent 10001 datagrams
[  4] 0.00-10.00 sec  14.2 MBytes  11.9 Mbits/sec  10001/0      999 pps
[  4] Sent 10001 datagrams
[  7] 0.00-10.00 sec  14.2 MBytes  11.9 Mbits/sec  10001/0      999 pps
[  7] Sent 10001 datagrams
[  9] 0.00-10.00 sec  14.2 MBytes  11.9 Mbits/sec  10001/0      999 pps
[  9] Sent 10001 datagrams
[SUM] 0.00-10.00 sec  56.8 MBytes  47.7 Mbits/sec  40004/0     3996 pps
[SUM] Sent 40004 datagrams
[  9] Server Report:
[  9]  0.0-10.0 sec  14.0 MBytes  11.8 Mbits/sec   0.001 ms    0/10001 (0%)
[  9] 0.00-9.95 sec  3 datagrams received out-of-order
[  3] Server Report:
[  3]  0.0-10.0 sec  14.0 MBytes  11.8 Mbits/sec   0.001 ms    0/10001 (0%)
[  3] 0.00-9.95 sec  1 datagrams received out-of-order
[  7] Server Report:
[  7]  0.0-10.0 sec  14.0 MBytes  11.8 Mbits/sec   0.000 ms    1/10001 (0.01%)
[  4] Server Report:
[  4]  0.0-10.0 sec  14.0 MBytes  11.8 Mbits/sec   0.001 ms    3/10001 (0.03%)
'''  # noqa: E501

# iperf -c localhost -t 10 -u -b 1000000pps  -l 36 -P 1 -e
output_fail_singleflow_low_tx_rate = '''
------------------------------------------------------------
Client connecting to localhost, UDP port 5001 with pid 2808738
Sending 36 byte datagrams, IPG target: 1.00 us (kalman adjust)
UDP buffer size:  260 KByte (default)
------------------------------------------------------------
[  3] local 127.0.0.1 port 60229 connected with 127.0.0.1 port 5001
[ ID] Interval        Transfer     Bandwidth      Write/Err  PPS
[  3] 0.00-10.00 sec   115 MBytes  96.1 Mbits/sec  3336533/0   333652 pps
[  3] Sent 3336533 datagrams
[  3] Server Report:
[  3]  0.0-10.0 sec   114 MBytes  96.2 Mbits/sec   0.000 ms 1713/3336533 (0.051%)
'''  # noqa: E501

# iperf -c localhost -t 10 -u -b 4000000pps  -l 1490 -P 4 -e
output_fail_multiflow_low_tx_rate = '''
------------------------------------------------------------
Client connecting to localhost, UDP port 5001 with pid 2806722
Sending 1490 byte datagrams, IPG target: 0.25 us (kalman adjust)
UDP buffer size:  260 KByte (default)
------------------------------------------------------------
[  5] local 127.0.0.1 port 53407 connected with 127.0.0.1 port 5001
[  3] local 127.0.0.1 port 40885 connected with 127.0.0.1 port 5001
[  9] local 127.0.0.1 port 58916 connected with 127.0.0.1 port 5001
[  4] local 127.0.0.1 port 33374 connected with 127.0.0.1 port 5001
[ ID] Interval        Transfer     Bandwidth      Write/Err  PPS
[  5] 0.00-10.00 sec  3.71 GBytes  3.18 Gbits/sec  2671867/0   267185 pps
[  5] Sent 2671867 datagrams
[  3] 0.00-10.00 sec  3.68 GBytes  3.16 Gbits/sec  2652782/18   265277 pps
[  3] Sent 2652782 datagrams
[  9] 0.00-10.00 sec  3.79 GBytes  3.26 Gbits/sec  2733408/23   273339 pps
[  9] Sent 2733408 datagrams
[  4] 0.00-10.00 sec  3.64 GBytes  3.13 Gbits/sec  2626499/13   262648 pps
[  4] Sent 2626499 datagrams
[SUM] 0.00-10.00 sec  14.8 GBytes  12.7 Gbits/sec  10684556/54  1068449 pps
[SUM] Sent 10684556 datagrams
[  3] Server Report:
[  3]  0.0- 9.9 sec  3.59 GBytes  3.11 Gbits/sec   0.000 ms 27767/2652782 (1%)
[  3] 0.00-9.93 sec  1 datagrams received out-of-order
[  5] Server Report:
[  5]  0.0- 9.9 sec  3.62 GBytes  3.13 Gbits/sec   0.000 ms 27382/2671867 (1%)
[  5] 0.00-9.93 sec  22 datagrams received out-of-order
[  4] Server Report:
[  4]  0.0- 9.9 sec  3.56 GBytes  3.08 Gbits/sec   0.000 ms 27505/2626499 (1%)
[  4] 0.00-9.93 sec  2 datagrams received out-of-order
[  9] Server Report:
[  9]  0.0- 9.9 sec  3.70 GBytes  3.20 Gbits/sec   0.000 ms 27490/2733408 (1%)
'''  # noqa: E501

# iperf -c localhost -t 10 -u -b 400000pps  -l 36 -P 1 -e
output_fail_singleflow_high_drop = '''
------------------------------------------------------------
Client connecting to localhost, UDP port 5001 with pid 2810490
Sending 36 byte datagrams, IPG target: 2.50 us (kalman adjust)
UDP buffer size:  260 KByte (default)
------------------------------------------------------------
[  3] local 127.0.0.1 port 40739 connected with 127.0.0.1 port 5001
[ ID] Interval        Transfer     Bandwidth      Write/Err  PPS
[  3] 0.00-10.00 sec   113 MBytes  94.6 Mbits/sec  3283409/0   328340 pps
[  3] Sent 3283409 datagrams
[  3] Server Report:
[  3]  0.0-11.7 sec   109 MBytes  78.2 Mbits/sec   0.000 ms 101037/3283409 (3.1%)
'''  # noqa: E501

# iperf -c localhost -t 10 -u -b 1000000pps  -l 36 -P 16 -e
output_fail_multiflow_high_drop = '''
------------------------------------------------------------
Client connecting to localhost, UDP port 5001 with pid 2807954
Sending 36 byte datagrams, IPG target: 1.00 us (kalman adjust)
UDP buffer size:  260 KByte (default)
------------------------------------------------------------
[ 27] local 127.0.0.1 port 60261 connected with 127.0.0.1 port 5001
[ 14] local 127.0.0.1 port 59403 connected with 127.0.0.1 port 5001
[ 13] local 127.0.0.1 port 47279 connected with 127.0.0.1 port 5001
[ 10] local 127.0.0.1 port 44913 connected with 127.0.0.1 port 5001
[  9] local 127.0.0.1 port 52367 connected with 127.0.0.1 port 5001
[ 17] local 127.0.0.1 port 53113 connected with 127.0.0.1 port 5001
[ 21] local 127.0.0.1 port 60004 connected with 127.0.0.1 port 5001
[ 18] local 127.0.0.1 port 39660 connected with 127.0.0.1 port 5001
[ 23] local 127.0.0.1 port 51870 connected with 127.0.0.1 port 5001
[ 31] local 127.0.0.1 port 47346 connected with 127.0.0.1 port 5001
[ 33] local 127.0.0.1 port 38076 connected with 127.0.0.1 port 5001
[ 24] local 127.0.0.1 port 50862 connected with 127.0.0.1 port 5001
[  5] local 127.0.0.1 port 56066 connected with 127.0.0.1 port 5001
[ 29] local 127.0.0.1 port 45323 connected with 127.0.0.1 port 5001
[  3] local 127.0.0.1 port 41211 connected with 127.0.0.1 port 5001
[  4] local 127.0.0.1 port 35982 connected with 127.0.0.1 port 5001
[ ID] Interval        Transfer     Bandwidth      Write/Err  PPS
[ 10] 0.00-10.00 sec  73.0 MBytes  61.2 Mbits/sec  2125054/86   212504 pps
[ 10] Sent 2125054 datagrams
[ 23] 0.00-10.00 sec  71.6 MBytes  60.1 Mbits/sec  2085928/22   208590 pps
[ 23] Sent 2085928 datagrams
[ 31] 0.00-10.00 sec  73.2 MBytes  61.4 Mbits/sec  2133340/14   213331 pps
[ 31] Sent 2133340 datagrams
[ 33] 0.00-10.00 sec  77.7 MBytes  65.2 Mbits/sec  2263515/9   226348 pps
[ 33] Sent 2263515 datagrams
[  5] 0.00-10.00 sec  70.7 MBytes  59.3 Mbits/sec  2059490/58   205946 pps
[  5] Sent 2059490 datagrams
[ 29] 0.00-10.00 sec  71.5 MBytes  60.0 Mbits/sec  2082211/42   208218 pps
[ 29] Sent 2082211 datagrams
[  3] 0.00-10.00 sec  72.2 MBytes  60.6 Mbits/sec  2102683/26   210265 pps
[  3] Sent 2102683 datagrams
[ 31] Server Report:
[ 31]  0.0-10.0 sec  70.1 MBytes  59.1 Mbits/sec   0.000 ms 91076/2133340 (4.3%)
[ 31] 0.00-9.95 sec  21 datagrams received out-of-order
[ 29] Server Report:
[ 29]  0.0-10.0 sec  71.3 MBytes  60.1 Mbits/sec   0.000 ms 6446/2082211 (0.31%)
[ 29] 0.00-9.95 sec  51 datagrams received out-of-order
[ 23] Server Report:
[ 23]  0.0-10.0 sec  67.5 MBytes  56.9 Mbits/sec   0.000 ms 119280/2085928 (5.7%)
[ 23] 0.00-9.95 sec  17 datagrams received out-of-order
[  3] Server Report:
[  3]  0.0-10.0 sec  68.4 MBytes  57.6 Mbits/sec   0.000 ms 110762/2102683 (5.3%)
[  3] 0.00-9.95 sec  24 datagrams received out-of-order
[ 33] Server Report:
[ 33]  0.0-10.0 sec  72.7 MBytes  61.2 Mbits/sec   0.000 ms 147174/2263515 (6.5%)
[ 33] 0.00-9.95 sec  33 datagrams received out-of-order
[  5] Server Report:
[  5]  0.0-10.0 sec  67.5 MBytes  56.9 Mbits/sec   0.000 ms 92001/2059490 (4.5%)
[  5] 0.00-9.95 sec  16 datagrams received out-of-order
[ 10] Server Report:
[ 10]  0.0-10.0 sec  70.2 MBytes  59.1 Mbits/sec   0.000 ms 81544/2125054 (3.8%)
[ 10] 0.00-9.95 sec  1 datagrams received out-of-order
[ 27] 0.00-10.00 sec  74.2 MBytes  62.3 Mbits/sec  2161974/110   216196 pps
[ 27] Sent 2161974 datagrams
[ 14] 0.00-10.00 sec  69.2 MBytes  58.0 Mbits/sec  2014482/0   201447 pps
[ 14] Sent 2014482 datagrams
[ 13] 0.00-10.00 sec  70.9 MBytes  59.5 Mbits/sec  2065103/12   206509 pps
[ 13] Sent 2065103 datagrams
[  9] 0.00-10.00 sec  69.3 MBytes  58.2 Mbits/sec  2019732/78   201971 pps
[  9] Sent 2019732 datagrams
[ 17] 0.00-10.00 sec  70.9 MBytes  59.5 Mbits/sec  2065717/70   206570 pps
[ 17] Sent 2065717 datagrams
[ 21] 0.00-10.00 sec  69.8 MBytes  58.6 Mbits/sec  2033026/45   203301 pps
[ 21] Sent 2033026 datagrams
[ 18] 0.00-10.00 sec  71.0 MBytes  59.6 Mbits/sec  2067740/41   206772 pps
[ 18] Sent 2067740 datagrams
[ 24] 0.00-10.00 sec  66.8 MBytes  56.1 Mbits/sec  1947082/22   194705 pps
[ 24] Sent 1947082 datagrams
[  4] 0.00-10.00 sec  71.7 MBytes  60.1 Mbits/sec  2088363/8   208833 pps
[  4] Sent 2088363 datagrams
[SUM] 0.00-10.00 sec  1.12 GBytes   959 Mbits/sec  33315440/643  3331506 pps
[SUM] Sent 33315440 datagrams
[ 27] Server Report:
[ 27]  0.0-10.0 sec  70.4 MBytes  59.4 Mbits/sec   0.000 ms 110908/2161974 (5.1%)
[ 13] Server Report:
[ 13]  0.0-10.0 sec  68.7 MBytes  57.9 Mbits/sec   0.000 ms 65039/2065103 (3.1%)
[ 13] 0.00-9.95 sec  21 datagrams received out-of-order
[ 24] Server Report:
[ 24]  0.0-10.0 sec  64.8 MBytes  54.7 Mbits/sec   0.000 ms 58304/1947082 (3%)
[ 24] 0.00-9.95 sec  39 datagrams received out-of-order
[  4] Server Report:
[  4]  0.0-10.0 sec  69.6 MBytes  58.7 Mbits/sec   0.000 ms 59831/2088363 (2.9%)
[  4] 0.00-9.95 sec  41 datagrams received out-of-order
[ 18] Server Report:
[ 18]  0.0-10.0 sec  68.5 MBytes  57.8 Mbits/sec   0.000 ms 71538/2067740 (3.5%)
[ 18] 0.00-9.95 sec  11 datagrams received out-of-order
[  9] Server Report:
[  9]  0.0-10.0 sec  67.2 MBytes  56.6 Mbits/sec   0.000 ms 63496/2019732 (3.1%)
[  9] 0.00-9.95 sec  8 datagrams received out-of-order
[ 21] Server Report:
[ 21]  0.0-10.0 sec  67.6 MBytes  57.0 Mbits/sec   0.000 ms 64942/2033026 (3.2%)
[ 21] 0.00-9.95 sec  26 datagrams received out-of-order
[ 17] Server Report:
[ 17]  0.0-10.0 sec  68.7 MBytes  57.9 Mbits/sec   0.000 ms 63410/2065717 (3.1%)
[ 17] 0.00-9.95 sec  40 datagrams received out-of-order
[ 14] Server Report:
[ 14]  0.0-10.0 sec  66.5 MBytes  56.0 Mbits/sec   0.000 ms 78845/2014482 (3.9%)
[ 14] 0.00-9.95 sec  79 datagrams received out-of-order
'''  # noqa: E501

# iperf -c localhost -t 4 -u -b 312500.0pps -l 1490 -e -P 8
output_fail_no_drop_rate_report = '''
------------------------------------------------------------
Client connecting to localhost, UDP port 5001 with pid 2866409
Sending 1490 byte datagrams, IPG target: 3.20 us (kalman adjust)
UDP buffer size: 1.00 GByte (default)
------------------------------------------------------------
[  9] local 127.0.0.1 port 37297 connected with 127.0.0.1 port 5001
[  4] local 127.0.0.1 port 50092 connected with 127.0.0.1 port 5001
[  3] local 127.0.0.1 port 37310 connected with 127.0.0.1 port 5001
[ 13] local 127.0.0.1 port 60288 connected with 127.0.0.1 port 5001
[ 17] local 127.0.0.1 port 35263 connected with 127.0.0.1 port 5001
[ 15] local 127.0.0.1 port 45057 connected with 127.0.0.1 port 5001
[ 10] local 127.0.0.1 port 46708 connected with 127.0.0.1 port 5001
[  5] local 127.0.0.1 port 57588 connected with 127.0.0.1 port 5001
[ 13] WARNING: did not receive ack of last datagram after 10 tries.
[ 10] WARNING: did not receive ack of last datagram after 10 tries.
[  5] WARNING: did not receive ack of last datagram after 10 tries.
[ 15] WARNING: did not receive ack of last datagram after 10 tries.
[  4] WARNING: did not receive ack of last datagram after 10 tries.
[ 17] WARNING: did not receive ack of last datagram after 10 tries.
[  3] WARNING: did not receive ack of last datagram after 10 tries.
[  9] WARNING: did not receive ack of last datagram after 10 tries.
[ ID] Interval        Transfer     Bandwidth      Write/Err  PPS
[  9] 0.00-4.00 sec  1.53 GBytes  3.30 Gbits/sec  1105861/0   276463 pps
[  9] Sent 1105861 datagrams
[  4] 0.00-4.00 sec  1.61 GBytes  3.46 Gbits/sec  1162608/21   290649 pps
[  4] Sent 1162608 datagrams
[  3] 0.00-4.00 sec  1.54 GBytes  3.31 Gbits/sec  1111851/14   277960 pps
[  3] Sent 1111851 datagrams
[ 13] 0.00-4.00 sec  1.66 GBytes  3.57 Gbits/sec  1198744/11   299683 pps
[ 13] Sent 1198744 datagrams
[ 17] 0.00-4.00 sec  1.60 GBytes  3.43 Gbits/sec  1152069/13   288014 pps
[ 17] Sent 1152069 datagrams
[ 15] 0.00-4.00 sec  1.67 GBytes  3.60 Gbits/sec  1206599/6   301646 pps
[ 15] Sent 1206599 datagrams
[ 10] 0.00-4.00 sec  1.67 GBytes  3.59 Gbits/sec  1206271/6   301563 pps
[ 10] Sent 1206271 datagrams
[  5] 0.00-4.00 sec  1.68 GBytes  3.61 Gbits/sec  1210077/25   302514 pps
[  5] Sent 1210077 datagrams
[SUM] 0.00-4.00 sec  13.0 GBytes  27.9 Gbits/sec  9354080/96  2338492 pps
[SUM] Sent 9354080 datagrams
'''  # noqa: E501


def mock_run_iperf(*args):
    mpps = args[3]
    return mpps <= 3.0


class TestUDP(unittest.TestCase):
    def test_is_expected_tx_rate(self):
        self.assertTrue(udp.is_expected_tx_rate(output_success_singleflow, 1 * 70000 / 1e6))  # noqa: E501
        self.assertTrue(udp.is_expected_tx_rate(output_success_multiflow, 4 * 1000 / 1e6))  # noqa: E501
        self.assertFalse(udp.is_expected_tx_rate(output_fail_singleflow_low_tx_rate, 1 * 1000000 / 1e6))  # noqa: E501
        self.assertFalse(udp.is_expected_tx_rate(output_fail_multiflow_low_tx_rate, 4 * 4000000 / 1e6))  # noqa: E501
        self.assertFalse(udp.is_expected_tx_rate(output_fail_singleflow_high_drop, 1 * 400000 / 1e6))  # noqa: E501
        self.assertFalse(udp.is_expected_tx_rate(output_fail_multiflow_high_drop, 16 * 1000000 / 1e6))  # noqa: E501

    def test_is_low_drop_rate(self):
        self.assertTrue(udp.is_low_drop_rate(output_success_singleflow))  # noqa: E501
        self.assertTrue(udp.is_low_drop_rate(output_success_multiflow))  # noqa: E501
        self.assertTrue(udp.is_low_drop_rate(output_fail_singleflow_low_tx_rate))  # noqa: E501
        self.assertFalse(udp.is_low_drop_rate(output_fail_multiflow_low_tx_rate))  # noqa: E501
        self.assertFalse(udp.is_low_drop_rate(output_fail_singleflow_high_drop))  # noqa: E501
        self.assertFalse(udp.is_low_drop_rate(output_fail_multiflow_high_drop))  # noqa: E501
        self.assertFalse(udp.is_low_drop_rate(output_fail_no_drop_rate_report))  # noqa: E501

    @patch('autoiperf.udp.run_iperf', mock_run_iperf)
    def test_run(self):
        self.assertAlmostEqual(udp.run('localhost', 1, 64), 3.0, places=1)


if __name__ == '__main__':
    unittest.main()
