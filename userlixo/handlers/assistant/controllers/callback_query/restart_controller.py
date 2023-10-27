from dataclasses import dataclass

from pyrogram import filters

from userlixo.handlers.assistant.handlers.callback_query.restart_callback_query_handler import (
    RestartCallbackQueryHandler,
)
from userlixo.decorators import Controller, on_callback_query


@Controller()
@dataclass
class RestartController:
    handler: RestartCallbackQueryHandler

    @on_callback_query(filters.regex("^restart"))
    async def on_restart(self, c, callback_query):
        await self.handler.handle_callback_query(c, callback_query)
