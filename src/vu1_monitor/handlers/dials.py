import functools
import logging
import sys
import time
from pathlib import Path

import psutil
from PIL import Image

from vu1_monitor.config import settings
from vu1_monitor.dials import VU1Client
from vu1_monitor.exceptions import DialNotImplemented, ServerNotFound
from vu1_monitor.files import extract_tarfile
from vu1_monitor.metrics import get_gpu_utilisation
from vu1_monitor.models import Bright, Colours, DialType, Element

logger = logging.getLogger(settings.name)

FILETYPES = (".png", ".jpg", "jpeg")


def server_not_found(func):
    @functools.wraps(func)
    def handle_not_found_errors(*args, **kwargs):
        """handle server not found errors"""
        try:
            value = func(*args, **kwargs)
            return value
        except ServerNotFound as e:
            logger.critical(e.message)
            sys.exit(1)

    return handle_not_found_errors


@server_not_found
def set_backlight(colour: str, brightness: str, dial: DialType | None) -> None:
    """Set backlight colour and brightness for a dial

    :param colour: Pre-set colour to set dial to, defaults to WHITE.
    :param brightness: Brightness level to set dial to, defaults to LOW.
    :param dial: Dial to set, defaults to None (sets all dials).
    """
    client = VU1Client(settings.server.hostname, settings.server.port, settings.server.key)
    adj_colour = tuple([int(value * Bright[brightness].value) for value in Colours[colour].value])

    if not dial:
        for type in DialType:
            try:
                client.set_backlight(type, adj_colour)
                logger.debug(f"{type.value} backlight set to {colour}")
            except DialNotImplemented:
                logger.warning(f"{type.value} backlight not set: dial not found")
    else:
        try:
            client.set_backlight(DialType(dial), adj_colour)
            logger.debug(f"{dial} backlight set to {colour}")
        except DialNotImplemented:
            logger.error(f"{dial} backlight not set: dial not found")


@server_not_found
def set_image(filename: str, dial: DialType) -> None:
    """Set the image for a dial

    :param dial: :param dial: Dial to set
    """
    client = VU1Client(settings.server.hostname, settings.server.port, settings.server.key)
    assert filename.endswith(FILETYPES), f"file must be of type: {FILETYPES}"

    width, height = Image.open(filename).size
    assert (width * height) == (200 * 144), "image must be exactly 144 x 200 pixels"

    try:
        client.set_image(dial, Path(filename))
        logger.debug(f"{dial} image set to {filename}")
    except DialNotImplemented:
        logger.error(f"{dial} image not set: dial not found")


@server_not_found
def start_monitoring(interval: int, cpu: bool, gpu: bool, mem: bool, net: bool) -> None:
    """Start VU1-Monitoring

    :param interval: Wait interval between each update (seconds), defaults to 2.
    :param cpu: Flag for CPU Dial updates, defaults to True.
    :param gpu: Flag for GPU Dial updates, defaults to False.
    :param mem: Flag for Memory Dial updates, defaults to False.
    :param net: Flag for Network Dial updates, defaults to False.
    """
    client = VU1Client(settings.server.hostname, settings.server.port, settings.server.key)
    logger.info("starting VU1-Monitor..")

    if True not in [cpu, gpu, mem, net]:
        logger.critical("at least one dial must be set to update")
        sys.exit(1)

    bytes_recv = psutil.net_io_counters().bytes_recv

    while True:
        try:
            if cpu:
                cpu_percent = int(psutil.cpu_percent())
                client.set_dial(DialType.CPU, cpu_percent)
            if gpu:
                gpu_percent = int(get_gpu_utilisation(settings.gpu.backend))
                client.set_dial(DialType.GPU, gpu_percent)
            if mem:
                memory_percent = int(psutil.virtual_memory().percent)
                client.set_dial(DialType.MEMORY, memory_percent)
            if net:
                bytes_recv_updated = psutil.net_io_counters().bytes_recv
                mb_rev = (bytes_recv_updated - bytes_recv) / (1024 * 1024)
                client.set_dial(DialType.NETWORK, int(mb_rev))
                bytes_recv = bytes_recv_updated
        except DialNotImplemented as e:
            logger.critical(f"failed to update {e.dial.value}: dial not found")
            sys.exit(1)

        logger.debug("update successful")
        time.sleep(interval)


@server_not_found
def reset_dials(element: Element) -> None:
    """reset all dials

    :element: Dial element to reset
    """
    client = VU1Client(settings.server.hostname, settings.server.port, settings.server.key)
    match element:
        case Element.DIAL:
            client.reset_dials()
        case Element.BACKLIGHT:
            client.reset_backlights()
        case Element.IMAGE:
            extract_tarfile(Path("src/vu1_monitor/static/static.tgz"))
            client.reset_images()
