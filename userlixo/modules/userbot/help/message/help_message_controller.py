from dataclasses import dataclass

from hydrogram import Client, filters
from hydrogram.types import Message

from userlixo.decorators import controller, on_message
from userlixo.modules.userbot.help.message.help_message_handler import (
    HelpMessageHandler,
)


@controller
@dataclass
class HelpMessageController:
    handler: HelpMessageHandler

    @on_message(filters.su_cmd("help"))
    async def help(self, client: Client, message: Message):
        await self.handler.handle_message(client, message)
