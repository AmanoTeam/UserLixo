from dataclasses import dataclass

from pyrogram import filters

from userlixo.decorators import Controller, on_message
from userlixo.handlers.assistant.handlers.message.help_message_handler import (
    HelpMessageHandler,
)


@Controller()
@dataclass
class HelpController:
    handler: HelpMessageHandler

    @on_message(filters.command("help"))
    async def on_help(self, client, message):
        await self.handler.handle_message(client, message)
