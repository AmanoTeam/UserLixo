from dataclasses import dataclass

from pyrogram import Client, filters
from pyrogram.types import Message

from userlixo.decorators import Controller, on_message
from userlixo.handlers.userbot.help.message.help_message_handler import (
    HelpMessageHandler,
)


@Controller()
@dataclass
class HelpMessageController:
    handler: HelpMessageHandler

    @on_message(filters.su_cmd("help"))
    async def help(self, client: Client, message: Message):
        await self.handler.handle_message(client, message)
