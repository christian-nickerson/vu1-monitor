import httpx
from dials.model import Dial, DialType
from exceptions.dials import DialNotFound


class VU1Client:

    def __init__(self, server_addr: str, key: str) -> None:
        self.__addr = server_addr
        self.__auth = {"key": key}
        self.__dials = self._load_dials()

    def get_dials(self) -> list[dict]:
        """get list of all available dials"""
        with httpx.Client(base_url=self.__addr, params=self.__auth) as client:
            response = client.get("/api/v0/dial/list")
        if response.status_code != 200:
            response.raise_for_status()
        return response.json()["data"]

    def _load_dials(self) -> dict:
        resp = self.get_dials()
        types = [item.value for item in DialType]

        if len(resp) <= 0:
            raise DialNotFound("no dials returned from VU1 server")

        dials = {d["dial_name"]: Dial(**d) for d in resp if d["dial_name"] in types}

        if len(dials) <= 0:
            raise DialNotFound("no known dials found")

        return dials

    def set_dial(self, dial: DialType, value: int) -> None:
        path = f"/api/v0/dial/{self.__dials[dial].uid}/set"
        with httpx.Client(base_url=self.__addr, params=self.__auth) as client:
            response = client.get(path, params={"value": value})
        if response.status_code != 200:
            response.raise_for_status()
