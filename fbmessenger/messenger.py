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
    attachment_location: Optional[str]
    public_attachment_url: Optional[str]
    log: logging.Logger = logging.getLogger(__name__)

    def __init__(self, access_token: str, verify_token: str, message_callback: Callable[[Message], Awaitable[None]],
                 attachment_location: Optional[str] = None, public_attachment_url: Optional[str] = None):
        super().__init__(access_token)
        self.access_token = access_token
        self.verify_token = verify_token
        self.callback = message_callback
        self.attachment_location = attachment_location
        self.public_attachment_url = public_attachment_url

    def start_receiving(self, port=8080):
        app = web.Application()
        app.add_routes([web.post('/{tail:.*}', self._message_handler), web.get('/{tail:.*}', self._verification_handler)])
        web.run_app(app, port=port)

    async def _message_handler(self, request: Request):
        self.log.debug(f'Received request:\n{await request.text()}')
        raw_message = await request.json()

        message = Message(raw_message['sender']['id'], raw_message['recipient']['id'], raw_message['message']['text'], None)
        asyncio.ensure_future(self.callback(message))

        return web.Response(text="")

    async def _verification_handler(self, request: Request):
        self.log.debug(f'Received verification request with query {request.query_string}')

        if request.query.get('hub.verify_token') != self.verify_token:
            raise web.HTTPForbidden(reason="Verify token is invalid")

        challenge = request.query.get('hub.challenge')
        if not challenge:
            raise web.HTTPBadRequest(reason='hub.challenge not set')

        return web.Response(text=challenge)
