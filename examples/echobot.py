import logging
import os

from fbmessenger import Messenger
from fbmessenger.models import Message, SenderAction


class EchoBot:

    def __init__(self):
        access_token = os.getenv('FB_TOKEN')
        self.messenger = Messenger(access_token, "verify", self.reply)

    async def reply(self, message: Message):
        await self.messenger.send_reply(message, message.text)

    def run(self):
        logging.basicConfig(level=logging.DEBUG)
        self.messenger.start_receiving()


if __name__ == "__main__":
    EchoBot().run()
