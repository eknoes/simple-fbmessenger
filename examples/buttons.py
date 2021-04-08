import logging
import logging
import os

from fbmessenger import Messenger
from fbmessenger.models import Message, QuickReply, PostbackButton


class ButtonBot:

    def __init__(self):
        access_token = os.getenv('FB_TOKEN')
        self.messenger = Messenger(access_token, "verify", self.reply)

    async def reply(self, message: Message):
        if not message.payload:
            await self.messenger.send_reply(message, "Do you like this library?",
                                            buttons=[PostbackButton(title="Of course!", payload="yes"),
                                                     PostbackButton(title="I found this bug...", payload="bug")])
        elif message.payload == "yes":
            await self.messenger.send_reply(message, "Thanks!")
        else:
            await self.messenger.send_reply(message, "Oh no... You can help here: "
                                                     "https://github.com/eknoes/simple-fbmessenger/issues")

    def run(self):
        logging.basicConfig(level=logging.DEBUG)
        self.messenger.start_receiving()


if __name__ == "__main__":
    ButtonBot().run()
