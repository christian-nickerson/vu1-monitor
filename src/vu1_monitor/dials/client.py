import httpx

from vu1_monitor.dials.models import Dial, DialType
from vu1_monitor.exceptions.dials import DialNotFound, DialNotImplemented


class VU1Client:

    def __init__(self, hostname: str, port: int, key: str) -> None:
        self.__addr = f"http://{hostname}:{port}"
        self.__auth = {"key": key}
        self.__dials = self._load_dials()

    def _load_dials(self) -> dict:
        """build a dictionary of available dials

        :raises DialNotFound: Raised when no dials found
        :return: dict of all available dials
        """
        resp = self.get_dials()
        types = [item.value for item in DialType]

        if len(resp) <= 0:
            raise DialNotFound("no dials returned from VU1 server")

        dials = {d["dial_name"]: Dial(**d) for d in resp if d["dial_name"] in types}

        if len(dials) <= 0:
            raise DialNotFound("no known dials found")

        return dials

    def get_dials(self) -> list[dict]:
        """get list of all available dials"""
        with httpx.Client(base_url=self.__addr, params=self.__auth) as client:
            response = client.get("/api/v0/dial/list")

        if response.status_code != 200:
            response.raise_for_status()

        return response.json()["data"]

    def set_dial(self, dial: DialType, value: int) -> None:
        """Set the value of a dial

        :param dial: Dial to update
        :param value: 0-100 value to set dial at
        """
        try:
            path = f"/api/v0/dial/{self.__dials[dial].uid}/set"
        except KeyError as e:
            raise DialNotImplemented(f"{dial.value} dial is not set up", dial) from e

        with httpx.Client(base_url=self.__addr, params=self.__auth) as client:
            response = client.get(path, params={"value": value})

        if response.status_code != 200:
            response.raise_for_status()

    def reset_dials(self) -> None:
        """Reset the values of all dials to 0"""
        with httpx.Client(base_url=self.__addr, params=self.__auth) as client:
            for dial in self.__dials:
                params = {"value": 0}
                path = f"/api/v0/dial/{self.__dials[dial].uid}/set"
                response = client.get(path, params=params)
                if response.status_code != 200:
                    response.raise_for_status()

    def set_background(self, dial: DialType, colour: tuple[int, ...]) -> None:
        """Set background colour of a dial

        :param dial: Dial to update
        :param colour: A tuple of (red, green, blue) RGB percent values (0-100)
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

    def reset_backgrounds(self) -> None:
        """Reset the backgrounds of all dials to off"""
        with httpx.Client(base_url=self.__addr, params=self.__auth) as client:
            for dial in self.__dials:
                params = {"red": 0, "green": 0, "blue": 0}
                path = f"/api/v0/dial/{self.__dials[dial].uid}/backlight"
                response = client.get(path, params=params)
                if response.status_code != 200:
                    response.raise_for_status()
