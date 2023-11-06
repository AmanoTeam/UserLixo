from dataclasses import dataclass

from pyrogram import Client, filters
from pyrogram.types import Message

from userlixo.decorators import controller, on_message

from .web_app_message_handler import WebAppMessageHandler


@controller()
@dataclass
class WebAppMessageController:
    handler: WebAppMessageHandler

    @on_message(filters.regex("^/(start )?webapp"))
    async def webapp(self, client: Client, message: Message):
        await self.handler.handle_message(client, message)
