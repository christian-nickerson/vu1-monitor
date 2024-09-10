import time

import click
import psutil
from config.settings import settings
from dials.client import VU1Client
from dials.model import DialType


@click.command()
@click.option("--interval", default=2, help="interval seconds")
def main(interval: int) -> None:
    address = f"http://{settings.server.hostname}:{settings.server.port}"
    client = VU1Client(address, settings.key)

    while True:
        cpu = int(psutil.cpu_percent())
        client.set_dial(DialType.CPU, cpu)
        print(cpu)
        time.sleep(interval)


if __name__ == "__main__":
    main()
