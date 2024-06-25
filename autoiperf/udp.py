import re
import subprocess
import signal
import time
import json
import os
import autoiperf.plot as p


PING_RESULT_FILE = '/tmp/ping_result.txt'


def start_ping_background(client_ip):
    return subprocess.Popen(
        ['ping', client_ip, '-i', '0.2'],
        stdout=open(PING_RESULT_FILE, 'w'),
        stderr=subprocess.STDOUT)


def stop_ping_background(process):
    process.send_signal(signal.SIGQUIT)
    process.send_signal(signal.SIGINT)
    time.sleep(0.1)
    process.send_signal(signal.SIGTERM)

    lines = []
    rtt = ''

    with open(PING_RESULT_FILE, 'r') as f:
        lines = f.readlines()

    for line in lines:
        if re.match(r'^rtt', line):
            rtt = line.strip()
            break

    return rtt


def run_iperf(client_ip, n, pkt_size, mpps):
    process = start_ping_background(client_ip)

    # 20: IP header, 8: UDP header
    size = pkt_size - 28
    bps = mpps * 1e6 * size * 8

    args = [
        'iperf3',
        '-c', client_ip,
        '-t', '3',
        '-u',
        '-P', str(n),
        '-l', str(size),
        '-b', str(bps),
        '-i', '0',
        '--get-server-output',
        '--json',
        '--logfile', '/tmp/iperf.json',
        ]

    ok = False
    output = {}

    for _ in range(3):
        subprocess.run(['rm', '-f', '/tmp/iperf.json'])

        _ = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

        if not os.path.isfile('/tmp/iperf.json'):
            continue

        try:
            with open('/tmp/iperf.json', 'r') as f:
                output = json.load(f)
        except:  # noqa: E722
            continue

        if is_expected_tx_rate(output) and is_low_drop_rate(output):
            ok = True
            break

    latency = stop_ping_background(process)

    print('    {} pkt_size={} n={} mpps={:.3f} L1Gbps={:.3f} cpu_host={:.1f} cpu_remote={:.1f} latency="{}" cmd="{}"'.format(  # noqa: E501
        'OK' if ok else 'NG', pkt_size, n, mpps, p.L1Gbps(pkt_size, mpps), get_cpu_total_host(output), get_cpu_total_remote(output), latency, ' '.join(args)))  # noqa: E501

    return ok


def get_cpu_total_host(output):
    return output.get('end', {}).get('cpu_utilization_percent', {}).get('host_total', -1)  # noqa: E501


def get_cpu_total_remote(output):
    return output.get('end', {}).get('cpu_utilization_percent', {}).get('remote_total', -1)  # noqa: E501


def is_expected_tx_rate(output):
    expected = output.get('start', {}).get('target_bitrate', -1)
    actual = output.get('end', {}).get('sum', {}).get('bits_per_second', -1)

    if expected < 0 or actual < 0:
        return False

    return actual / expected > 0.99


def is_low_drop_rate(output):
    total_lost_packets = \
            output.get('end', {}).get('sum', {}).get('lost_packets', 0) + \
            output.get('end', {}).get('sum_sent', {}).get('lost_packets', 0) + \
            output.get('end', {}).get('sum_received', {}).get('lost_packets', 0)  # noqa: E501

    total_packets = \
        output.get('end', {}).get('sum', {}).get('packets', 0) + \
        output.get('end', {}).get('sum_sent', {}).get('packets', 0) + \
        output.get('end', {}).get('sum_received', {}).get('packets', 0)

    if total_packets == 0:
        return False

    return float(total_lost_packets) / float(total_packets) < 0.01


def run(client_ip, n, pkt_size):
    left_mpps = 0.0
    right_mpps = 3.0

    while right_mpps - left_mpps > 0.01:
        mpps = (left_mpps + right_mpps) / 2
        ok = run_iperf(client_ip, n, pkt_size, mpps)

        if ok:
            left_mpps = mpps
        else:
            right_mpps = mpps

    return left_mpps
