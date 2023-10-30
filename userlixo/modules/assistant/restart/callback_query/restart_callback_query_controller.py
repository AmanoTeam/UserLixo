from dataclasses import dataclass

from pyrogram import filters

from userlixo.decorators import Controller, on_callback_query

from .restart_callback_query_handler import RestartCallbackQueryHandler


@Controller()
@dataclass
class RestartCallbackQueryController:
    handler: RestartCallbackQueryHandler

    @on_callback_query(filters.regex("^restart"))
    async def on_restart(self, c, callback_query):
        await self.handler.handle_callback_query(c, callback_query)
