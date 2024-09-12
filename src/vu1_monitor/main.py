import sys
import time
from pathlib import Path

import click
import GPUtil
import psutil

from vu1_monitor.compression.files import extract_tarfile
from vu1_monitor.config.settings import settings
from vu1_monitor.dials.client import VU1Client
from vu1_monitor.dials.models import Bright, Colours, DialType, Element
from vu1_monitor.exceptions.dials import DialNotImplemented
from vu1_monitor.logger.logger import create_logger

COLOURS = [item.name for item in Colours]
BRIGHT = [item.name for item in Bright]

logger = create_logger("VU1-Monitor", settings.server.logging_level)
client = VU1Client(settings.server.hostname, settings.server.port, settings.key)


@click.group
def main() -> None:
    """main command group"""
    pass


@main.command(help="set the background colour of a dial")
@click.option("--colour", "-c", default=Colours.WHITE.name, type=click.Choice(COLOURS))
@click.option("--brightness", "-b", default=Bright.LOW.name, type=click.Choice(BRIGHT))
@click.option("--dial", "-d", default=None, type=DialType)
def background(colour: str, brightness: str, dial: DialType | None) -> None:
    """Set background colour for a dial

    :param colour: Pre-set colour to set dial to, defaults to WHITE.
    :param brightness: Brightness level to set dial to, defaults to LOW.
    :param dial: Dial to set, defaults to None (sets all dials).
    """
    adj_colour = tuple([int(value * Bright[brightness].value) for value in Colours[colour].value])

    if not dial:
        for type in DialType:
            try:
                client.set_background(type, adj_colour)
                logger.debug(f"{type.value} set to {colour}")
            except DialNotImplemented:
                logger.warning(f"{type.value} not set: dial not found")
    else:
        try:
            client.set_background(DialType(dial), adj_colour)
            logger.debug(f"{dial} set to {colour}")
        except DialNotImplemented:
            logger.error(f"{dial} not set: dial not found")


@main.command(help="reset all dials to default")
@click.argument("element", type=Element, nargs=1, required=True)
def reset(element: Element) -> None:
    """reset all dials"""
    match element:
        case Element.DIAL:
            client.reset_dials()
        case Element.BACKGROUND:
            client.reset_backgrounds()
        case Element.IMAGE:
            extract_tarfile(Path("src/vu1_monitor/static/static.tgz"))
            client.reset_images()


@main.command(help="start VU1-Monitoring")
@click.option("--interval", "-i", default=2, help="update interval (seconds)")
@click.option("--cpu/--no-cpu", default=True, help=f"update {DialType.CPU.value} dial")
@click.option("--gpu/--no-gpu", default=False, help=f"update {DialType.GPU.value} dial")
@click.option("--mem/--no-mem", default=False, help=f"update {DialType.MEMORY.value} dial")
@click.option("--net/--no-net", default=False, help=f"update {DialType.NETWORK.value} dial")
def run(interval: int, cpu: bool, gpu: bool, mem: bool, net: bool) -> None:
    """Start VU1-Monitoring

    :param interval: Wait interval between each update (seconds), defaults to 2.
    :param cpu: Flag for CPU Dial updates, defaults to True.
    :param gpu: Flag for GPU Dial updates, defaults to False.
    :param mem: Flag for Memory Dial updates, defaults to False.
    :param net: Flag for Network Dial updates, defaults to False.
    """
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
                gpu_percent = int(GPUtil.getGPUs()[0].load)
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


if __name__ == "__main__":
    main()
