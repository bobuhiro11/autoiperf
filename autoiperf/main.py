import argparse
import autoiperf.plot as p
from autoiperf import tcp, udp


def main():
    parser = argparse.ArgumentParser(
                    prog='autoiperf',
                    description='',
                    epilog='')
    parser.add_argument('client_ip', help='Client IP address')
    parser.add_argument('n', type=int, help='Number of parallel connections')
    parser.add_argument('link_speed', type=int, help='Link speed in Gbps')
    parser.add_argument('-f', type=str, help='Output file name')
    parser.add_argument('-u', action='store_true', help='Use UDP')

    args = parser.parse_args()

    pkt_sizes = [1518, 1280, 1024, 512, 256, 128]

    # For Jumbo frames.
    # pkt_sizes = [8192, 4096, 2048, 1518, 1280, 1024, 512, 256, 128]

    Mppss = []
    for pkt_size in pkt_sizes:
        mpps = []

        if args.u:
            mpps = udp.run(args.client_ip, args.n, pkt_size)
        else:
            mpps = tcp.run(args.client_ip, args.n, pkt_size)

        l1gbps = p.L1Gbps(pkt_size, mpps)
        print('pkt_size', pkt_size,
              'mpps', mpps,
              'L1Gbps', l1gbps)
        Mppss.append(mpps)

    # Plot
    p.plot_L1Gbps(pkt_sizes, Mppss, args.link_speed*1e9, args.f)
    p.plot_L2Gbps(pkt_sizes, Mppss, args.link_speed*1e9, args.f)
    p.plot_Mpps(pkt_sizes, Mppss, args.link_speed*1e9, args.f)


if __name__ == '__main__':
    main()
