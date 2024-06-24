import subprocess


def run_iperf(client_ip, n, mss):
    output = ''
    for _ in range(3):
        result = subprocess.run([
            'iperf', '-c', client_ip, '-i', '1', '-t', '10',
            '--format', 'bits', '-M', str(mss),
            '-P', str(n)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output += result.stdout.decode("utf-8")
    return output


def get_mpps(output, mss):
    max_bps = -1
    # Parse the output and get the maximum bandwidth.
    lines = output.split('\n')
    for line in lines:
        if 'bits/sec' not in line:
            continue
        bps = float(line.split(' ')[-2])
        max_bps = max(max_bps, bps)

    mpps = max_bps / (mss * 8) / 1e6
    return mpps


def run(client_ip, n, packet_size):
    mss = packet_size - 40

    output = run_iperf(client_ip, n, mss)
    mpps = get_mpps(output, mss)
    return mpps
