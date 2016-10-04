import argparse
import signal
import sys
import time

from colorama import Fore, Style

from rr.process import Process
from rr.watcher import Watcher


def color_print(string):
    print(('{C}' + string + '{R}').format(C=Fore.YELLOW, R=Style.RESET_ALL))


def main():
    parser = argparse.ArgumentParser(description='Runner-Reloader for development')
    parser.add_argument('--interval', '-i', type=int, default=3,
                        help='interval for check')
    parser.add_argument('cmd', type=str, nargs=1, help='command')
    parser.add_argument('args', type=str, nargs='*', help='arguments')

    args = parser.parse_args()

    cmd = ' '.join(args.cmd + args.args)
    start(cmd, interval=args.interval)


def start(cmd, *, interval):
    process = Process(cmd)
    color_print("Starting...")
    process.start()

    def restart_callback(old_state, new_state, process=process):
        color_print("Restarting...")
        process.restart()

    watcher = Watcher(restart_callback, interval=interval)
    watcher.start()

    def sigint_handler(sig, frame, process=process, watcher=watcher):
        color_print("Stopping watcher...")
        watcher.stop()
        watcher.join()

        color_print("Stopping process...")
        process.stop()

        color_print("Stopped.")
        sys.exit(1)

    signal.signal(signal.SIGINT, sigint_handler)

    while True:
        time.sleep(60)


if __name__ == '__main__':
    main()
