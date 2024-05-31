from dataclasses import dataclass

from hydrogram import Client, filters
from hydrogram.types import Message

from userlixo.decorators import controller, on_message
from userlixo.modules.userbot.about.message.about_message_handler import (
    AboutMessageHandler,
)


@controller
@dataclass
class AboutMessageController:
    handler: AboutMessageHandler

    @on_message(filters.su_cmd("about"))
    async def about(self, client: Client, message: Message):
        await self.handler.handle_message(client, message)
