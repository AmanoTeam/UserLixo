from dataclasses import dataclass

from kink import inject
from pyrogram import filters, Client

from userlixo.assistant.handlers.message.restart_message_handler import (
    RestartMessageHandler,
)
from userlixo.decorators import Controller, on_message


@Controller()
@inject
@dataclass
class RestartController:
    handler: RestartMessageHandler

    @on_message(filters.regex("^/(start )?restart"))
    async def restart(self, client: Client, message):
        await self.handler.handle_message(client, message)
