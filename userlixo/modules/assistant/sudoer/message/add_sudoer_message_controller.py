from dataclasses import dataclass

from pyrogram import Client, filters

from userlixo.decorators import Controller, on_message

from .add_sudoer_message_handler import AddSudoerMessageHandler


@Controller()
@dataclass
class AddSudoerMessageController:
    handler: AddSudoerMessageHandler

    @on_message(filters.regex("^/(start )?add_sudoer"))
    async def add_sudoer(self, client: Client, message):
        await self.handler.handle_message(client, message)
