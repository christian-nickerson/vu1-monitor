from dataclasses import dataclass
from enum import Enum, StrEnum

from vu1_monitor.config.settings import settings


@dataclass
class Dial:

    dial_name: str
    uid: str
    value: str
    backlight: dict
    image_file: str


class DialType(StrEnum):

    CPU: str = settings.cpu.name
    GPU: str = settings.gpu.name
    MEMORY: str = settings.memory.name
    NETWORK: str = settings.network.name


class Colours(Enum):

    WHITE: tuple[int, ...] = (100, 100, 100)
    RED: tuple[int, ...] = (100, 0, 0)
    GREEN: tuple[int, ...] = (0, 100, 0)
    BLUE: tuple[int, ...] = (0, 0, 100)


class Bright(Enum):

    MAX: float = 1.0
    MID: float = 0.5
    LOW: float = 0.2
    OFF: float = 0.0
