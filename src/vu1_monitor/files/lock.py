import fcntl
import json
import os
from pathlib import Path

FILENAME = "monitoring.lock"


def write_lock(data: dict) -> None:
    """write lock file

    :param data: data to write to lock
    """
    with open(Path(FILENAME), "w") as file:
        fcntl.flock(file.fileno(), fcntl.LOCK_EX)
        json.dump(data, file)
        fcntl.flock(file.fileno(), fcntl.LOCK_UN)


def read_lock() -> dict:
    """read lock file"""
    with open(Path(FILENAME), "r") as file:
        fcntl.flock(file.fileno(), fcntl.LOCK_EX)
        lock = json.load(file)
        fcntl.flock(file.fileno(), fcntl.LOCK_UN)
    return lock


def check_pid(key: str) -> bool:
    """check for PID from lock file

    :param key: name of key for PID in lock file
    """
    try:
        lock = read_lock()
        os.kill(lock[key], 0)  # checks PID is running
    except FileNotFoundError:
        return False
    except KeyError:
        return False
    except TypeError:
        return False
    except OSError:
        return False
    else:
        return True
