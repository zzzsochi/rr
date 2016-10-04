import enum
import logging
import signal
import subprocess
import sys
from threading import Thread


logger = logging.getLogger(__name__)

STOP_TIMEOUT = 5


class ProcessStatus(enum.Enum):
    stopped = 0
    runing = 1
    stopping = 2


class Process:
    status = ProcessStatus.stopped
    popen = None

    def __init__(self, cmd, *, stop_signal=signal.SIGINT):
        super().__init__()
        self.cmd = cmd
        self.stop_signal = stop_signal
        self.logger = logger.getChild(repr(self))

    def __repr__(self):
        return "{}({!r}, {})".format(
            self.__class__.__name__, self.cmd, hex(id(self)))

    def start(self):
        self.logger.debug("start")
        if self.status == ProcessStatus.stopped:
            self.status == ProcessStatus.runing
            self.popen = subprocess.Popen(
                args=self.cmd,
                stdout=sys.stdout,
                stderr=sys.stderr,
                shell=True,
            )

        else:
            raise RuntimeError("process is already running")

    def stop(self):
        self.logger.debug("stop")
        if self.status == ProcessStatus.runing:
            self.status = ProcessStatus.stopping
            self.send_signal(self.stop_signal)

            try:
                self.popen.wait(STOP_TIMEOUT)
            except subprocess.TimeoutExpired:
                self.logger.warn("kill")
                self.popen.kill()

            self.status = ProcessStatus.stopped

    def restart(self):
        if self.status == ProcessStatus.runing:
            self.stop()
        elif self.status == ProcessStatus.stopping:
            self.popen.wait(STOP_TIMEOUT * 2)

        self.start()

    def send_signal(self, sig):
        self.logger.debug("send_signal")
        if self.status == ProcessStatus.runing:
            self.popen.send_signal(sig)
