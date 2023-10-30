from dataclasses import dataclass

from pyrogram import Client, filters

from userlixo.decorators import Controller, on_message
from userlixo.handlers.assistant.handlers.message.restart_message_handler import (
    RestartMessageHandler,
)


@Controller()
@dataclass
class RestartController:
    handler: RestartMessageHandler

    @on_message(filters.regex("^/(start )?restart"))
    async def restart(self, client: Client, message):
        await self.handler.handle_message(client, message)
