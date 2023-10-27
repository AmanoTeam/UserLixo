from dataclasses import dataclass

from pyrogram import filters, Client

from userlixo.handlers.assistant.handlers.message.add_sudoer_message_handler import (
    AddSudoerMessageHandler,
)
from userlixo.decorators import Controller, on_message


@Controller()
@dataclass
class AddSudoerController:
    handler: AddSudoerMessageHandler

    @on_message(filters.regex("^/(start )?add_sudoer"))
    async def add_sudoer(self, client: Client, message):
        await self.handler.handle_message(client, message)
