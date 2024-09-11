from vu1_monitor.dials.models import DialType


class DialNotFound(Exception):
    pass


class DialNotImplemented(Exception):

    def __init__(self, message: str, dial: DialType):
        super().__init__(message)
        self.dial = dial
