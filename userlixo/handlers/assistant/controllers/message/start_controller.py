from dataclasses import dataclass

from pyrogram import filters

from userlixo.handlers.assistant.handlers.message.start_message_handler import (
    StartMessageHandler,
)
from userlixo.decorators import Controller, on_message


@Controller()
@dataclass
class StartController:
    handler: StartMessageHandler

    @on_message(filters.command("start"))
    async def handle_message(self, *args):
        await self.handler.handle_message(*args)
