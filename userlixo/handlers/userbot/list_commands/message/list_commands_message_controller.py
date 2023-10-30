from dataclasses import dataclass

from pyrogram import Client, filters
from pyrogram.types import Message

from userlixo.decorators import Controller, on_message
from userlixo.handlers.userbot.list_commands.message.list_commands_message_handler import (
    ListCommandsMessageHandler,
)


@Controller()
@dataclass
class ListCommandsMessageController:
    handler: ListCommandsMessageHandler

    @on_message(filters.su_cmd("(commands|cmds)"))
    async def list_commands(self, client: Client, message: Message):
        await self.handler.handle_message(client, message)
