from kink import di
from pyrogram import filters

from userlixo.assistant.handlers.message.start_message_handler import (
    StartMessageHandler,
)
from userlixo.decorators import Controller, on_message

handler: StartMessageHandler = di[StartMessageHandler]


@Controller()
class StartController:
    @staticmethod
    @on_message(filters.command("start"))
    async def handle_message(*args):
        await handler.handle_message(*args)
