from dataclasses import dataclass

from pyrogram import filters

from userlixo.assistant.handlers.callback_query.ping_callback_query_handler import (
    PingCallbackQueryHandler,
)
from userlixo.decorators import Controller, on_callback_query


@Controller()
@dataclass
class PingController:
    handler: PingCallbackQueryHandler

    @on_callback_query(filters.regex("^ping"))
    async def ping(self, client, callback_query):
        await self.handler.handle_callback_query(client, callback_query)
