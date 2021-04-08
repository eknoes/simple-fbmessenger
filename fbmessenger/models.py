from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from typing import List, Optional


@dataclass
class Message:
    sender_id: str
    receiver_id: str
    text: str
    attachments: Optional[List[Path]] = None
    payload: Optional[str] = None


@dataclass
class QuickReply:
    title: str
    payload: str
    image_url: Optional[str] = None


class MessagingType(Enum):
    RESPONSE = "RESPONSE"
    UPDATE = "UPDATE"
    MESSAGE_TAG = "MESSAGE_TAG"


class SenderAction(Enum):
    TYPING_ON = "typing_on"
    TYPING_OFF = "typing_off"
    MARK_SEEN = "mark_seen"
