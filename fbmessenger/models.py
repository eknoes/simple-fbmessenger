from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional


@dataclass
class Message:
    sender_id: str
    receiver_id: str
    text: str
    attachments: Optional[List[Path]]


class MessagingType(Enum):
    RESPONSE = "RESPONSE"
    UPDATE = "UPDATE"
    MESSAGE_TAG = "MESSAGE_TAG"
