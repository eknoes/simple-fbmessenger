from dataclasses import dataclass
from typing import Optional


@dataclass
class MessengerError(BaseException):
    message: str
    type: str
    code: int
    subcode: Optional[int] = None
    fbtrace_id: Optional[str] = None
