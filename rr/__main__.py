import argparse
import datetime
import logging
import os
import signal
import shlex
import sys
import time

from colorama import Fore, Style
import zini

from rr.process import Process
from rr.watcher import Watcher


logger = logging.getLogger(__name__)


def color_print(string):
    print(('{C}' + string + '{R}').format(C=Fore.YELLOW, R=Style.RESET_ALL))


def main():
    settings = read_settings('.rr', 'default')
    settings = parse_arguments(settings)
    settings = prepare_settings(settings)

    setup_loglevel(settings['loglevel'])
    logger.debug('settings: %r', settings)

    start(settings['command'],
          interval=settings['interval'],
          exclude=settings['exclude'])


def read_settings(file, env):
    z = zini.Zini()

    z[env]['interval'] = datetime.timedelta(seconds=3)
    z[env]['exclude'] = [str]
    z[env]['loglevel'] = 'NOTSET'
    z[env]['command'] = str

    if os.path.isfile(file):
        return z.read(file)[env]
    else:
        return z.defaults[env]


def parse_arguments(settings):
    parser = argparse.ArgumentParser(
        description="Runner-Reloader for development",
    )

    parser.add_argument('--interval', '-i', type=int,
                        default=settings.get('interval', 3),
                        help="interval for check")

    parser.add_argument('--exclude', '-e', type=str, action='append',
                        default=settings.get('exclude', []),
                        help="exclude pattern")

    parser.add_argument('--loglevel',
                        default=settings.get('loglevel', 'NOTSET'),
                        choices=['NOTSET', 'DEBUG', 'INFO',
                                 'WARNING', 'ERROR', 'CRITICAL'],
                        help="loglevel for rr")

    parser.add_argument('command', type=str, nargs=argparse.REMAINDER,
                        help='command')

    args = parser.parse_args()

    if not args.command:
        del args.command

    for key, value in args.__dict__.items():
        settings[key] = value

    return settings


def prepare_settings(settings):
    if 'command' in settings:
        if isinstance(settings['command'], str):
            settings['command'] = shlex.split(settings['command'])
        elif isinstance(settings['command'], list):
            pass

    return settings


def setup_loglevel(loglevel):
    if loglevel != 'NOTSET':
        logging.basicConfig(level=getattr(logging, loglevel))


def start(cmd, *, interval, exclude):
    process = Process(cmd)
    color_print("Starting...")
    process.start()

    def restart_callback(old_state, new_state, process=process):
        color_print("Restarting...")
        process.restart()

    watcher = Watcher(restart_callback, interval=interval, exclude=exclude)
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
