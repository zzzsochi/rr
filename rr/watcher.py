import enum
from time import sleep
from threading import Thread
from os import listdir
from os.path import abspath, expanduser, join
from os.path import isfile, isdir, getmtime


class WatcherStatus(enum.Enum):
    stopped = 0
    running = 1
    stopping = 2


class Watcher(Thread):
    status = WatcherStatus.stopped
    state = None

    def __init__(self, callback, *, include=['.'], exclude=[], interval=3):
        super().__init__()
        self.callback = callback
        self.include = [abspath(expanduser(d)) for d in include]
        self.exclude = [abspath(expanduser(d)) for d in exclude]
        self.interval = interval

    def start(self):
        if self.status == WatcherStatus.stopped:
            super().start()
        else:
            raise RuntimeError("watcher is already running")

    def stop(self):
        if self.status == WatcherStatus.running:
            self.status = WatcherStatus.stopping
        else:
            raise RuntimeError("watcher not started")

    def run(self):
        self.status = WatcherStatus.running
        try:
            while self.status == WatcherStatus.running:
                new_state = self._get_state()

                if self.state is None:
                    self.state = new_state
                elif self.state != new_state and self.status == WatcherStatus.running:
                    self.callback(self.state, new_state)
                    self.state = new_state

                for _ in range(0, self.interval * 10, 2):
                    if self.status == WatcherStatus.running:
                        sleep(0.2)
                    else:
                        break

        finally:
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
        if item in exclude:
            continue

        if isfile(item):
            yield (item, getmtime(item))
        elif isdir(item):
            yield item
            yield from _read_state(item, exclude)
        else:
            yield item
