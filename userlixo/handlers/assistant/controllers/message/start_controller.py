from dataclasses import dataclass

from pyrogram import filters

from userlixo.decorators import Controller, on_message
from userlixo.handlers.assistant.handlers.message.start_message_handler import (
    StartMessageHandler,
)


@Controller()
@dataclass
class StartController:
    handler: StartMessageHandler

    @on_message(filters.regex("^/start$"))
    async def handle_message(self, *args):
        await self.handler.handle_message(*args)
