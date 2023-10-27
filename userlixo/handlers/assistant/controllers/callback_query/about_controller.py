from dataclasses import dataclass

from pyrogram import filters

from userlixo.handlers.assistant.handlers.callback_query.about_callback_query_handler import (
    AboutCallbackQueryHandler,
)
from userlixo.decorators import Controller, on_callback_query


@Controller()
@dataclass
class AboutController:
    handler: AboutCallbackQueryHandler

    @on_callback_query(filters.regex("^about_(?P<subject>userlixo|plugins|commands)"))
    async def about_userlixo(self, _c, callback_query):
        await self.handler.handle_callback_query(_c, callback_query)
