from pyrogram import filters

from userlixo.assistant.handlers.message.start_message_handler import (
    StartMessageHandler,
)
from userlixo.decorators import Controller, on_message


@Controller()
class StartController:
    def __init__(self, handler: StartMessageHandler):
        self.handler = handler

    @on_message(filters.command("start"))
    async def handle_message(self, *args):
        await self.handler.handle_message(*args)
