import logging

from fbmessenger import Messenger
from fbmessenger.models import Message, SenderAction


class EchoBot:

    def __init__(self):
        self.messenger = Messenger("access", "verify", self.reply)

    async def reply(self, message: Message):
        await self.messenger.send_action(message.sender_id, SenderAction.MARK_SEEN)
        await self.messenger.send_action(message.sender_id, SenderAction.TYPING_ON)
        await self.messenger.send_reply(message, message.text)
        await self.messenger.send_action(message.sender_id, SenderAction.TYPING_OFF)

    def run(self):
        logging.basicConfig(level=logging.DEBUG)
        self.messenger.start_receiving()


if __name__ == "__main__":
    EchoBot().run()
