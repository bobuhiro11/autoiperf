import re
import subprocess
import signal
import time


PING_RESULT_FILE = '/tmp/ping_result.txt'


def start_ping_background(client_ip):
    return subprocess.Popen(
        ['ping', client_ip, '-i', '0.2'],
        stdout=open(PING_RESULT_FILE, 'w'),
        stderr=subprocess.STDOUT)


def stop_ping_background(process):
    process.send_signal(signal.SIGINT)
    time.sleep(0.01)
    process.send_signal(signal.SIGTERM)

    last_line = ''

    with open(PING_RESULT_FILE, 'r') as f:
        lines = f.readlines()
        last_line = lines[-1].strip()

    return last_line


def run_iperf(client_ip, n, pkt_size, mpps):
    process = start_ping_background(client_ip)

    # 20: IP header, 8: UDP header
    size = pkt_size - 28

    args = [
        'iperf',
        '-c', client_ip,
        '-t', '3',
        '-u',
        '-e',
        '-P', str(n),
        '-l', str(size),
        '-b', str(mpps / float(n) * 1e6) + 'pps',
        ]

    ok = False

    for _ in range(2):
        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

        output = result.stdout.decode("utf-8")
        time.sleep(1)

        if is_expected_tx_rate(output, mpps) and is_low_drop_rate(output):
            ok = True
            break

    latency = stop_ping_background(process)

    print('    {} pkt_size={} n={} mpps={:.3f} latency="{}" cmd="{}"'.format(
        'OK' if ok else 'NG', pkt_size, n, mpps, latency, ' '.join(args)))

    return ok


def is_expected_tx_rate(output, mpps):
    for line in output.split('\n'):
        regex = r'(\d+) pps'

        res = re.search(regex, line)
        if not res:
            continue

        pps = float(res.group(1))

        if (pps / (mpps * 1e6)) > 0.99:
            return True

    return False


def is_low_drop_rate(output):
    max_drop_rate = -1.0

    for line in output.split('\n'):
        regex = r'\((.*?)%\)'
        match = re.search(regex, line)
        if not match:
            continue

        drop_rate = float(match.group(1))
        max_drop_rate = max(max_drop_rate, drop_rate)

    if max_drop_rate > 0.99:
        return False

    if max_drop_rate < 0:
        return False

    return True


def run(client_ip, n, pkt_size):
    left_mpps = 0.0
    right_mpps = 10.0

    while right_mpps - left_mpps > 0.01:
        mpps = (left_mpps + right_mpps) / 2
        ok = run_iperf(client_ip, n, pkt_size, mpps)

        if ok:
            left_mpps = mpps
        else:
            right_mpps = mpps

    return left_mpps
