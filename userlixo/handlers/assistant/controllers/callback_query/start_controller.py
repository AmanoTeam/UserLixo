from dataclasses import dataclass

from pyrogram import filters

from userlixo.decorators import Controller, on_callback_query
from userlixo.handlers.assistant.handlers.callback_query.start_callback_query_handler import (
    StartCallbackQueryHandler,
)


@Controller()
@dataclass
class StartController:
    handler: StartCallbackQueryHandler

    @on_callback_query(filters.regex("^start"))
    async def start(self, *args):
        await self.handler.handle_callback_query(*args)
