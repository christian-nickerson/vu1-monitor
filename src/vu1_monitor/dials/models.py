from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from vu1_monitor.config.settings import settings


@dataclass
class Dial:

    dial_name: str
    uid: str
    value: str
    backlight: dict
    image_file: str


class DialType(str, Enum):

    CPU: str = settings.cpu.name
    GPU: str = settings.gpu.name
    MEMORY: str = settings.memory.name
    NETWORK: str = settings.network.name


class DialImage(Path, Enum):

    CPU: Path = Path("src/vu1_monitor/static/cpu-load.png")
    GPU: Path = Path("src/vu1_monitor/static/gpu-load.png")
    MEMORY: Path = Path("src/vu1_monitor/static/mem-load.png")
    NETWORK: Path = Path("src/vu1_monitor/static/net-down.png")


class Colours(tuple[int, ...], Enum):

    WHITE: tuple[int, ...] = (100, 100, 100)
    RED: tuple[int, ...] = (100, 0, 0)
    GREEN: tuple[int, ...] = (0, 100, 0)
    BLUE: tuple[int, ...] = (0, 0, 100)


class Bright(float, Enum):

    MAX: float = 1.0
    MID: float = 0.5
    LOW: float = 0.2
    OFF: float = 0.0


class Element(str, Enum):

    DIAL: str = "dial"
    BACKGROUND: str = "background"
    IMAGE: str = "image"
