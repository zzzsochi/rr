import argparse
import logging
import signal
import sys
import time

from colorama import Fore, Style

from rr.process import Process
from rr.watcher import Watcher


logger = logging.getLogger(__name__)


def color_print(string):
    print(('{C}' + string + '{R}').format(C=Fore.YELLOW, R=Style.RESET_ALL))


def main():
    parser = argparse.ArgumentParser(
        description='Runner-Reloader for development',
    )

    parser.add_argument('--interval', '-i', type=int, default=3,
                        help='interval for check')

    parser.add_argument('--loglevel', default='NOTSET',
                        choices=['NOTSET', 'DEBUG', 'INFO',
                                 'WARNING', 'ERROR', 'CRITICAL'],
                        help='loglevel for rr')

    parser.add_argument('cmd', type=str, nargs=1, help='command')
    parser.add_argument('args', type=str, nargs=argparse.REMAINDER,
                        help='arguments')

    args = parser.parse_args()

    setup_loglevel(args.loglevel)

    cmd = ' '.join(args.cmd + args.args)
    start(cmd, interval=args.interval)


def setup_loglevel(loglevel):
    if loglevel != 'NOTSET':
        logging.basicConfig(level=getattr(logging, loglevel))


def start(cmd, *, interval):
    process = Process(cmd)
    color_print("Starting...")
    process.start()

    def restart_callback(old_state, new_state, process=process):
        color_print("Restarting...")
        process.restart()

    watcher = Watcher(restart_callback, interval=interval)
    watcher.start()

    def stop_sig_handler(sig, frame, process=process, watcher=watcher):
        stop(process, watcher)

    signal.signal(signal.SIGINT, stop_sig_handler)
    signal.signal(signal.SIGTERM, stop_sig_handler)

    while True:  # endless loop
        time.sleep(60)


def stop(process, watcher):
    color_print("Stopping watcher...")
    watcher.stop()
    watcher.join()

    color_print("Stopping process...")
    process.stop()

    color_print("Stopped.")
    sys.exit(1)


if __name__ == '__main__':
    main()
