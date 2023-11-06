from dataclasses import dataclass

from pyrogram import filters

from userlixo.decorators import controller, on_callback_query

from .about_callback_query_handler import (
    AboutCallbackQueryHandler,
)


@controller()
@dataclass
class AboutCallbackQueryController:
    handler: AboutCallbackQueryHandler

    @on_callback_query(filters.regex("^about_(?P<subject>userlixo|plugins|commands)"))
    async def about_userlixo(self, _c, callback_query):
        await self.handler.handle_callback_query(_c, callback_query)
