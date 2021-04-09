import asyncio
import logging
from typing import Callable, Optional, Awaitable

from aiohttp import web
from aiohttp.abc import Request

from fbmessenger.api import API
from fbmessenger.models import Message


class Messenger(API):
    access_token: str
    verify_token: str
    callback: Callable[[Message], Awaitable[None]]
    log: logging.Logger = logging.getLogger(__name__)

    def __init__(self, access_token: str, verify_token: str, message_callback: Callable[[Message], Awaitable[None]],
                 attachment_location: Optional[str] = None, public_attachment_url: Optional[str] = None):
        super().__init__(access_token, attachment_location, public_attachment_url)
        self.access_token = access_token
        self.verify_token = verify_token
        self.callback = message_callback

    def start_receiving(self, port=8080):
        app = web.Application()
        app.add_routes([web.post('/{tail:.*}', self._message_handler),
                        web.get('/{tail:.*}', self._verification_handler)])
        web.run_app(app, port=port)

    async def _message_handler(self, request: Request):
        self.log.debug(f'Received request:\n{await request.text()}')
        raw_message = await request.json()
        for event in raw_message['entry']:

            # Handle messaging events
            if 'messaging' in event:
                for m in event['messaging']:
                    message = None

                    if 'message' in m:
                        if 'text' in m['message']:
                            message = Message(m['sender']['id'], m['recipient']['id'], text=m['message']['text'])

                        if 'quick_reply' in m['message']:
                            message.payload = m['message']['quick_reply']['payload']

                    if 'postback' in m:
                        message = Message(m['sender']['id'], m['recipient']['id'],
                                          payload=m['postback']['payload'])

                    if not message:
                        self.log.debug("No content, skip message")
                        continue

                    asyncio.ensure_future(self.callback(message))

            # Handle postback events

        return web.Response(text="")

    async def _verification_handler(self, request: Request):
        self.log.debug(f'Received verification request with query {request.query_string}')

        if request.query.get('hub.verify_token') != self.verify_token:
            raise web.HTTPForbidden(reason="Verify token is invalid")

        challenge = request.query.get('hub.challenge')
        if not challenge:
            raise web.HTTPBadRequest(reason='hub.challenge not set')

        return web.Response(text=challenge)
