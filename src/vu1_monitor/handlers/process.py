import logging
import os
import signal
import subprocess

from vu1_monitor.config import settings
from vu1_monitor.files import check_pid, read_lock, write_lock

logger = logging.getLogger(settings.name)


def run_as_child(commands: list[str]) -> None:
    """Run a command as subprocess and write pid to lock

    :param commands: commands to run
    """
    if not check_pid("pid"):
        proc = subprocess.Popen(
            commands,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        write_lock({"pid": proc.pid})
        logger.info(f"started monitoring (on pid: {proc.pid})")
    else:
        logger.warning("start aborted: monitoring is already running")


def stop_pid() -> None:
    """Stop process in pid lock file"""
    if check_pid("pid"):
        lock = read_lock()
        os.kill(lock["pid"], signal.SIGTERM)
        write_lock({"pid": None})
        logger.info(f"stopped monitoring (on pid: {lock['pid']})")
    else:
        logger.warning("stop aborted: no monitoring running")
