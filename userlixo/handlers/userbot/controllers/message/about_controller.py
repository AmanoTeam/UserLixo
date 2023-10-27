from dataclasses import dataclass

from pyrogram import Client, filters
from pyrogram.types import Message

from userlixo.decorators import Controller, on_message
from userlixo.handlers.userbot.handlers.message.about_message_handler import (
    AboutMessageHandler,
)


@Controller()
@dataclass
class AboutController:
    handler: AboutMessageHandler

    @on_message(filters.su_cmd("about"))
    async def about(self, client: Client, message: Message):
        await self.handler.handle_message(client, message)
