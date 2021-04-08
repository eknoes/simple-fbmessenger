import logging
import os
import shutil
from typing import List, Optional, Dict

import aiohttp

from fbmessenger.errors import MessengerError
from fbmessenger.models import Message, MessagingType, SenderAction, QuickReply, PostbackButton


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

    async def send_action(self, recipient_id: str, action: SenderAction):
        await self._send_message_dict({'recipient': {'id': recipient_id}, 'sender_action': action.value})

    async def send_reply(self, message: Message, text: str, images: Optional[List[str]] = None,
                         quick_replies: List[QuickReply] = None, buttons: List[PostbackButton] = None) -> bool:
        return await self.send_message(message.sender_id, text, reply=True, images=images, quick_replies=quick_replies,
                                       buttons=buttons)

    async def send_message(self, recipient_id: str, text: str, reply: bool = False, images: Optional[List[str]] = None,
                           quick_replies: List[QuickReply] = None, buttons: List[PostbackButton] = None):
        if buttons and quick_replies:
            raise ValueError("Combining buttons and QuickReplies in one message is not possible")

        if buttons and len(buttons) > 3:
            raise ValueError("Using more than 3 buttons is not supported")

        messaging_type = MessagingType.MESSAGE_TAG
        if reply:
            messaging_type = MessagingType.RESPONSE

        # Send all images first
        if images:
            for image in images:
                await self._send_attachment(self._get_messaging_dict(messaging_type, recipient_id), image)

        # Construct message dict
        base_dict = self._get_messaging_dict(messaging_type, recipient_id)

        if not buttons:
            base_dict['message']['text'] = text

        if quick_replies:
            replies = []
            for reply in quick_replies:
                reply_dict = {'content_type': 'text', 'title': reply.title, 'payload': reply.payload}
                if reply.image_url:
                    reply_dict['image_url'] = reply.image_url
                replies.append(reply_dict)
            base_dict['message']['quick_replies'] = replies

        if buttons:
            buttons = list(map(lambda x: {'type': x.type, 'payload': x.payload, 'title': x.title}, buttons))
            payload = {'template_type': 'button', 'text': text, 'buttons': buttons}
            base_dict['message']['attachment'] = {'type': 'template', 'payload': payload}

        return await self._send_message_dict(base_dict)

    async def send_attachments(self, recipient_id: str, attachments: List[str], file_type: str = "image"):
        for attachment in attachments:
            await self._send_attachment(self._get_messaging_dict(MessagingType.MESSAGE_TAG, recipient_id),
                                        attachment, file_type)

    async def _send_attachment(self, message_dict, attachment: str, file_type: str = "image") -> bool:
        filename = os.path.basename(shutil.copy2(attachment, self.attachment_location))
        url = self.public_attachment_url + filename
        message_dict['message']['attachment'] = {'type': file_type, 'payload': {'url': url, 'is_reusable': True}}
        return await self._send_message_dict(message_dict)

    async def _send_message_dict(self, message_dict) -> bool:
        self.log.debug(f"Send message:\n{message_dict}")
        async with aiohttp.ClientSession() as session:
            url = self._get_endpoint_url("me/messages")
            self.log.debug(f"Send to {url}")
            response = await session.post(url, json=message_dict)
            self.log.debug(f"Response of Facebook API: {response.status} {response.reason}")
            json_response = await response.json()

            if 200 <= response.status < 300:
                if 'message_id' in json_response:
                    return True
                return False

            self.log.warning(f"An error occurred:\n{json_response}")
            if 'error' not in json_response:
                raise ValueError("Messenger API did not return an HTTP Status Code 2XX, but also no error response")

            error = json_response['error']

            subcode = None
            if 'subcode' in error:
                subcode = error['subcode']

            raise MessengerError(error['message'], error['type'], error['code'], subcode, error['fbtrace_id'])
        return False

    @staticmethod
    def _get_messaging_dict(messaging_type: MessagingType, recipient_id: str) -> Dict:
        return {'messaging_type': messaging_type.value, 'recipient': {'id': recipient_id}, 'message': {}}

    def _get_endpoint_url(self, endpoint: str) -> str:
        return f"{self.API_URL}{endpoint}?access_token={self.access_token}"
