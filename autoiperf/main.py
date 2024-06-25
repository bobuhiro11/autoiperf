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
    parser.add_argument('-s', type=str, help='The list of packet size',
                        default='128,256,512,1024,1280,1518')

    args = parser.parse_args()

    pkt_sizes = list(map(int, args.s.split(',')))
    pkt_sizes.reverse()

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
