from dataclasses import dataclass

from pyrogram import filters

from userlixo.decorators import controller, on_callback_query

from .ping_callback_query_handler import PingCallbackQueryHandler


@controller()
@dataclass
class PingCallbackQueryController:
    handler: PingCallbackQueryHandler

    @on_callback_query(filters.regex("^ping"))
    async def ping(self, client, callback_query):
        await self.handler.handle_callback_query(client, callback_query)
