import functools
import time
from pathlib import Path
from typing import Any, Callable

import httpx

from vu1_monitor.dials.models import Dial, DialImage, DialType
from vu1_monitor.exceptions.dials import (
    DialNotFound,
    DialNotImplemented,
    ServerNotFound,
)

TYPES = [item.value for item in DialType]


def server_handler(timeout_retries: int = 3, sleep: int = 2) -> Callable:
    """decorator for handling server errors"""

    def server_decorator(func) -> Callable:
        @functools.wraps(func)
        def handle_errors(*args, **kwargs) -> Any:
            """handle errors"""
            try:
                return func(*args, **kwargs)
            except httpx.ConnectError as e:
                raise ServerNotFound from e
            except httpx.TimeoutException as e:
                # retry on timeout
                for _ in range(timeout_retries):
                    try:
                        return func(*args, **kwargs)
                    except httpx.TimeoutException:
                        time.sleep(sleep)
                raise e

        return handle_errors

    return server_decorator


class VU1Client:

    def __init__(self, hostname: str, port: int, key: str, **kwargs: bool) -> None:
        self.__addr = f"http://{hostname}:{port}"
        self.__auth = {"key": key}
        if not kwargs.get("testing", False):
            self._load_dials()

    @property
    def dials(self) -> dict:
        """available dials"""
        return self.__dials

    def _load_dials(self) -> dict:
        """build a dictionary of available dials

        :raises DialNotFound: Raised when no dials found
        :return: dict of all available dials
        """
        resp = self.get_dials()

        if len(resp) <= 0:
            raise DialNotFound("no dials returned from VU Server")

        dials = {d["dial_name"]: Dial(**d) for d in resp if d["dial_name"] in TYPES}

        if len(dials) <= 0:
            raise DialNotFound("no known dials found")

        self.__dials: dict = dials
        return dials

    @server_handler(5)
    def get_dials(self) -> list[dict]:
        """get list of all available dials"""
        with httpx.Client(base_url=self.__addr, params=self.__auth) as client:
            response = client.get("/api/v0/dial/list")

        if response.status_code != 200:
            response.raise_for_status()

        return response.json()["data"]

    @server_handler(5)
    def set_dial(self, dial: DialType, value: int) -> dict:
        """Set the value of a dial

        :param dial: Dial to update
        :param value: 0-100 value to set dial at
        :raises DialNotImplemented: Raised when dial selected is not found.
        :return: Set dial response body
        """
        try:
            path = f"/api/v0/dial/{self.__dials[dial].uid}/set"
        except KeyError as e:
            raise DialNotImplemented(f"{dial.value} dial is not set up", dial) from e

        with httpx.Client(base_url=self.__addr, params=self.__auth) as client:
            response = client.get(path, params={"value": value})

        if response.status_code != 200:
            response.raise_for_status()

        return response.json()

    def reset_dials(self) -> None:
        """Reset the values of all dials to 0"""
        for dial in self.__dials:
            self.set_dial(dial, 0)

    @server_handler(5)
    def set_backlight(self, dial: DialType, colour: tuple[int, ...]) -> dict:
        """Set backlight colour of a dial

        :param dial: Dial to update
        :param colour: A tuple of (red, green, blue) RGB percent values (0-100)
        :raises DialNotImplemented: Raised when dial selected is not found.
        :return: Set backlight response body
        """
        try:
            path = f"/api/v0/dial/{self.__dials[dial].uid}/backlight"
        except KeyError as e:
            raise DialNotImplemented(f"{dial.value} dial is not set up", dial) from e

        with httpx.Client(base_url=self.__addr, params=self.__auth) as client:
            params = {"red": colour[0], "green": colour[1], "blue": colour[2]}
            response = client.get(path, params=params)

        if response.status_code != 200:
            response.raise_for_status()

        return response.json()

    def reset_backlights(self) -> None:
        """Reset the backlight of all dials to off"""
        for dial in self.__dials:
            self.set_backlight(dial, (0, 0, 0))

    @server_handler(5)
    def set_image(self, dial: DialType, image_path: Path) -> dict:
        """Set an image for a dial

        :param dial: :param dial: Dial to update.
        :param image_path: _description_
        :raises DialNotImplemented: Raised when dial selected is not found.
        :return: Set image response body
        """
        try:
            path = f"/api/v0/dial/{self.__dials[dial].uid}/image/set"
        except KeyError as e:
            raise DialNotImplemented(f"{dial.value} dial is not set up", dial) from e

        with httpx.Client(base_url=self.__addr, params=self.__auth) as client:
            files = {"imgfile": open(image_path, "rb")}
            response = client.post(path, files=files)

        if response.status_code != 200:
            response.raise_for_status()

        return response.json()

    def reset_images(self) -> None:
        """Reset all dials to their default images"""
        for dial in self.__dials.keys():
            self.set_image(dial, DialImage[dial].value)
