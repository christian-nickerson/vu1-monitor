from vu1_monitor.dials.models import DialType


class DialNotFound(Exception):
    pass


class DialNotImplemented(Exception):

    def __init__(self, message: str, dial: DialType):
        super().__init__(message)
        self.dial = dial


class ServerNotFound(Exception):

    def __init__(self, message: str = "VU Server is unreachable. Is it on?"):
        super().__init__(message)
