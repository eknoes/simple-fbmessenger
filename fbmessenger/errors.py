from dataclasses import dataclass


@dataclass
class MessengerError(BaseException):
    message: str
    type: str
    code: int
    subcode: int
    fbtrace_id: str
