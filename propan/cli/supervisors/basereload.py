import os
import threading
from typing import Any, Callable, Optional, Tuple

from propan.cli.supervisors.utils import get_subprocess, set_exit
from propan.log import logger


class BaseReload:
    def __init__(
        self,
        target: Callable[..., Any],
        args: Tuple[Any, ...],
        reload_delay: Optional[float] = 0.5,
    ) -> None:
        self.target = target
        self.should_exit = threading.Event()
        self.pid = os.getpid()
        self.reloader_name: Optional[str] = None
        self.reload_delay = reload_delay
        self._args = args

    def run(self) -> None:
        self.startup()
        while not self.should_exit.wait(self.reload_delay):
            if self.should_restart():
                self.restart()
        self.shutdown()

    def startup(self) -> None:
        logger.info(f"Started reloader process [{self.pid}] using {self.reloader_name}")
        set_exit(lambda *_: self.should_exit.set())
        self._start_process()

    def restart(self) -> None:
        self._stop_process()
        logger.info("Process successfully reloaded")
        self._start_process()

    def shutdown(self) -> None:
        self._stop_process()
        logger.info(f"Stopping reloader process [{self.pid}]")

    def _stop_process(self) -> None:
        self.process.terminate()
        self.process.join()

    def _start_process(self) -> None:
        self.process = get_subprocess(target=self.target, args=self._args)
        self.process.start()

    def should_restart(self) -> bool:
        raise NotImplementedError("Reload strategies should override should_restart()")
