from pathlib import Path

import click

from vu1_monitor.config import settings
from vu1_monitor.handlers import reset_dials, set_backlight, set_image, start_monitoring
from vu1_monitor.logger import create_logger
from vu1_monitor.models import Bright, Colours, DialType, Element

logger = create_logger(settings.name, settings.server.logging_level)

COLOURS = [item.name for item in Colours]
BRIGHT = [item.name for item in Bright]


@click.group
def main() -> None:
    """main command group"""
    pass


@main.command(help="set the backlight colour and brightness of a dial")
@click.option("--colour", "-c", default=Colours.WHITE.name, type=click.Choice(COLOURS))
@click.option("--brightness", "-b", default=Bright.LOW.name, type=click.Choice(BRIGHT))
@click.option("--dial", "-d", default=None, type=DialType)
def backlight(colour: str, brightness: str, dial: DialType | None) -> None:
    """set backlight of a dial"""
    set_backlight(colour, brightness, dial)


@main.command(help="set the image of a dial")
@click.argument("filename", type=click.Path(exists=True))
@click.option("--dial", "-d", required=True, type=DialType)
def image(filename: str, dial: DialType) -> None:
    """Set the image for a dial"""
    set_image(filename, dial)


@main.command(help="start VU1-Monitoring")
@click.option("--interval", "-i", default=2, help="update interval (seconds)")
@click.option("--cpu/--no-cpu", default=True, help=f"update {DialType.CPU.value} dial")
@click.option("--gpu/--no-gpu", default=False, help=f"update {DialType.GPU.value} dial")
@click.option("--mem/--no-mem", default=False, help=f"update {DialType.MEMORY.value} dial")
@click.option("--net/--no-net", default=False, help=f"update {DialType.NETWORK.value} dial")
def run(interval: int, cpu: bool, gpu: bool, mem: bool, net: bool) -> None:
    """Start VU1-Monitoring"""
    start_monitoring(interval, cpu, gpu, mem, net)


@main.command(help="reset all dials to default")
@click.argument("element", type=Element, required=True)
def reset(element: Element) -> None:
    """reset all dials"""
    reset_dials(element)


if __name__ == "__main__":
    main()
