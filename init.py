import coriolis
import argparse
import sys
import daemon


def main():
    epilog = (
        "example: \r\n%s python2 init.py [args] " % sys.argv[0])

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="Asynchronous IRC Bot.",
        add_help=True,
        epilog=epilog)
    parser.add_argument('--daemonize', action='store_true')
    parser.add_argument('-d', action='store_true')

    args = parser.parse_args()
    if args.d is True or args.daemonize is True:
        print "daemonizing.."
        with daemon.DaemonContext():
            coriolis.start()
    else:
        coriolis.start()

if __name__ == '__main__':
    main()
