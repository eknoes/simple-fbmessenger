import logging
import os
import shutil
from typing import List, Optional

import aiohttp

from fbmessenger.models import Message, MessagingType


class API:
    API_URL = "https://graph.facebook.com/v10.0/"

    access_token: str
    attachment_location: Optional[str]
    public_attachment_url: Optional[str]

    log: logging.Logger = logging.getLogger(__name__)

    def __init__(self, access_token: str, attachment_location: Optional[str] = None,
                 public_attachment_url: Optional[str] = None):
        self.access_token = access_token
        self.attachment_location = attachment_location
        self.public_attachment_url = public_attachment_url

    async def send_reply(self, message: Message, text: str, images: Optional[List[str]] = None) -> bool:
        base_dict = self._get_messaging_dict(MessagingType.RESPONSE, message.sender_id)
        if images:
            for image in images:
                await self._send_attachment(base_dict.copy(), image)

        base_dict['message'] = {'text': text}
        return await self._send_message_dict(base_dict)

    async def send_message(self, recipient_id: str, text: str, images: Optional[List[str]] = None):
        base_dict = self._get_messaging_dict(MessagingType.MESSAGE_TAG, recipient_id)
        if images:
            for image in images:
                await self._send_attachment(base_dict.copy(), image)

        base_dict['message'] = {'text': text}
        return await self._send_message_dict(base_dict)

    async def send_attachments(self, recipient_id: str, attachments: List[str], file_type: str = "image"):
        for attachment in attachments:
            await self._send_attachment(self._get_messaging_dict(MessagingType.MESSAGE_TAG, recipient_id),
                                        attachment, file_type)

    async def _send_attachment(self, message_dict, attachment: str, file_type: str = "image"):
        filename = os.path.basename(shutil.copy2(attachment, self.attachment_location))
        url = self.public_attachment_url + filename
        message_dict['message']['attachment'] = {'type': file_type, 'payload': {'url': url, 'is_reusable': True}}
        return message_dict

    async def _send_message_dict(self, message_dict) -> bool:
        self.log.debug(f"Send message:\n{message_dict}")
        async with aiohttp.ClientSession() as session:
            url = self._get_endpoint_url("me/messages")
            self.log.debug(f"Send to {url}")
            response = await session.post(url, json=message_dict)
            self.log.debug(f"Response of Facebook API: {response.status} {response.reason}")
            json_response = await response.json()
            if 'message_id' in json_response:
                return True
        return False

    @staticmethod
    def _get_messaging_dict(messaging_type: MessagingType, recipient_id: str):
        return {'messaging_type': messaging_type.value, 'recipient': {'id': recipient_id}}

    def _get_endpoint_url(self, endpoint: str) -> str:
        return f"{self.API_URL}{endpoint}?access_token={self.access_token}"
