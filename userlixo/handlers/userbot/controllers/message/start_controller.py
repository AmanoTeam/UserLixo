from dataclasses import dataclass

from pyrogram import filters, Client
from pyrogram.types import Message

from userlixo.decorators import Controller, on_message
from userlixo.handlers.userbot.handlers.message.start_message_handler import (
    StartMessageHandler,
)


@Controller()
@dataclass
class StartController:
    handler: StartMessageHandler

    @on_message(filters.su_cmd("start"))
    async def start(self, client: Client, message: Message):
        await self.handler.handle_message(client, message)
