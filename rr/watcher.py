import datetime
import enum
from fnmatch import fnmatch
import logging
from time import sleep, time
from threading import Thread, Lock
from os import listdir
from os.path import abspath, expanduser, join
from os.path import isfile, isdir, getmtime

logger = logging.getLogger(__name__)


class WatcherStatus(enum.Enum):
    stopped = 0
    running = 1
    stopping = 2


class Watcher(Thread):
    status = WatcherStatus.stopped
    state = None

    def __init__(self, callback, *, interval, exclude=(), include=('.',)):
        super().__init__()
        self.callback = callback
        self.exclude = [abspath(expanduser(d)) for d in exclude]
        self.include = [abspath(expanduser(d)) for d in include]

        if isinstance(interval, datetime.timedelta):
            self.interval = int(interval.total_seconds())
        elif isinstance(interval, int):
            self.interval = interval
        else:
            raise TypeError("Wrong type for interval: {!r}".format(interval))

        self._lock = Lock()

    def start(self):
        with self._lock:
            if self.status == WatcherStatus.stopped:
                super().start()
            else:
                raise RuntimeError("watcher is already running")

    def stop(self):
        with self._lock:
            if self.status == WatcherStatus.running:
                self.status = WatcherStatus.stopping
            else:
                raise RuntimeError("watcher not started")

    def run(self):
        self.status = WatcherStatus.running
        try:
            while self.status == WatcherStatus.running:
                logger.debug("scaning...")
                ts = time()

                new_state = self._get_state()

                if self.state is None:
                    self.state = new_state
                elif self.state != new_state and self.status == WatcherStatus.running:
                    self.callback(self.state, new_state)
                    self.state = None

                logger.debug("scaning time: %s", time() - ts)

                logger.debug("sleep for %s seconds", self.interval)
                for _ in range(0, self.interval * 10, 2):
                    if self.status == WatcherStatus.running:
                        sleep(0.2)
                    else:
                        break

        finally:
            with self._lock:
                self.status = WatcherStatus.stopped

    def _get_state(self):
        state = set()

        for d in self.include:
            if self.status == WatcherStatus.running:
                state.update(_read_state(d, self.exclude))
            else:
                break

        return state


def _read_state(d, exclude):
    for item in (join(d, i) for i in listdir(d)):
        skip = False
        for pat in exclude:
            if fnmatch(item, pat):
                skip = True
                break

        if skip:
            continue

        if isfile(item):
            yield (item, getmtime(item))
        elif isdir(item):
            yield item
            yield from _read_state(item, exclude)
        else:
            yield item
