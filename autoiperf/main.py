import argparse
import subprocess
import autoiperf.plot as p


def run_iperf(client_ip, n, mss):
    output = ''
    for _ in range(3):
        result = subprocess.run([
            'iperf', '-c', client_ip, '-i', '1', '-t', '10',
            '--format', 'bits', '-M', str(mss),
            '-P', str(n)], stdout=subprocess.PIPE)
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


def main():
    parser = argparse.ArgumentParser(
                    prog='autoiperf',
                    description='',
                    epilog='')
    parser.add_argument('client_ip', help='Client IP address')
    parser.add_argument('n', type=int, help='Number of parallel connections')
    parser.add_argument('link_speed', type=int, help='Link speed in Gbps')

    args = parser.parse_args()

    pkt_sizes = [1518, 1280, 1024, 512, 256, 128]

    # For Jumbo frames.
    # pkt_sizes = [8192, 4096, 2048, 1518, 1280, 1024, 512, 256, 128]

    Mppss = []
    for pkt_size in pkt_sizes:
        mss = pkt_size - 40
        output = run_iperf(args.client_ip, args.n, mss)
        mpps = get_mpps(output, mss)
        print('pkt_size', pkt_size, 'mpps', mpps)
        Mppss.append(mpps)

    # Plot
    p.plot_L1Gbps(pkt_sizes, Mppss, args.link_speed*1e9)
    p.plot_L2Gbps(pkt_sizes, Mppss, args.link_speed*1e9)
    p.plot_Mpps(pkt_sizes, Mppss, args.link_speed*1e9)


if __name__ == '__main__':
    main()
