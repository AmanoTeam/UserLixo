from dataclasses import dataclass

from pyrogram import filters, Client
from pyrogram.types import Message

from userlixo.decorators import Controller, on_message
from userlixo.userbot.handlers.message.ping_message_handler import PingMessageHandler


@Controller()
@dataclass
class PingController:
    handler: PingMessageHandler

    @on_message(filters.su_cmd("ping"))
    async def ping(self, client: Client, message: Message):
        await self.handler.handle_message(client, message)
