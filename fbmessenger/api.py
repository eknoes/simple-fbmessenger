import json
import logging
from typing import List, Optional

import aiohttp

from fbmessenger.models import Message, MessagingType


class API:
    access_token: str
    API_URL = "https://graph.facebook.com/v10.0/"
    log: logging.Logger = logging.getLogger(__name__)

    def __init__(self, access_token: str):
        self.access_token = access_token

    async def reply(self, message: Message, text: str) -> bool:
        base_dict = self.send_message_dict(MessagingType.RESPONSE, message.sender_id)
        base_dict['message'] = {'text': text}
        return await self._send_message_dict(base_dict)

    async def send_message(self, recipient_id: str, text: str, attachments: Optional[List[str]] = None):
        base_dict = self.send_message_dict(MessagingType.MESSAGE_TAG, recipient_id)
        base_dict['message'] = {'text': text}
        return await self._send_message_dict(base_dict)

    async def _send_message_dict(self, message_dict) -> bool:
        self.log.debug(f"Send message:\n{message_dict}")
        async with aiohttp.ClientSession() as session:
            url = self.get_endpoint_url("me/messages")
            self.log.debug(f"Send to {url}")
            response = await session.post(url, json=message_dict)
            self.log.debug(f"Response of Facebook API: {response.status} {response.reason}")
            json_response = await response.json()
            if 'message_id' in json_response:
                return True
        return False

    @staticmethod
    def send_message_dict(messaging_type: MessagingType, recipient_id: str):
        return {'messaging_type': messaging_type.value, 'recipient': {'id': recipient_id}}

    def get_endpoint_url(self, endpoint: str) -> str:
        return f"{self.API_URL}{endpoint}?access_token={self.access_token}"
