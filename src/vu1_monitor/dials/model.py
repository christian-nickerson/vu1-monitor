from dataclasses import dataclass
from enum import StrEnum

from config.settings import settings


@dataclass
class Dial:

    dial_name: str
    uid: str
    value: str
    backlight: dict
    image_file: str


class DialType(StrEnum):

    CPU = settings.cpu.name
    GPU = settings.gpu.name
    MEMORY = settings.memory.name
    NETWORK = settings.network.name
