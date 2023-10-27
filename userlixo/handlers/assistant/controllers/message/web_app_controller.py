from dataclasses import dataclass

from pyrogram import filters, Client
from pyrogram.types import Message

from userlixo.decorators import Controller, on_message
from userlixo.handlers.assistant.handlers.message.web_app_message_handler import (
    WebAppMessageHandler,
)


@Controller()
@dataclass
class WebAppController:
    handler: WebAppMessageHandler

    @on_message(filters.regex("^/(start )?webapp"))
    async def webapp(self, client: Client, message: Message):
        await self.handler.handle_message(client, message)
