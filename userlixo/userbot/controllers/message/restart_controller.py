from dataclasses import dataclass

from pyrogram import filters, Client
from pyrogram.types import Message

from userlixo.decorators import Controller, on_message
from userlixo.userbot.handlers.restart_message_handler import RestartMessageHandler


@Controller()
@dataclass
class RestartController:
    handler: RestartMessageHandler

    @on_message(filters.su_cmd("restart"))
    async def restart(self, client: Client, message: Message):
        await self.handler.handle_message(client, message)
