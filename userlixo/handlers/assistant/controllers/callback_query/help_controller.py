from dataclasses import dataclass

from pyrogram import filters

from userlixo.decorators import Controller, on_callback_query
from userlixo.handlers.assistant.handlers.callback_query.help_callback_query_handler import (
    HelpCallbackQueryHandler,
)


@Controller()
@dataclass
class HelpController:
    handler: HelpCallbackQueryHandler

    @on_callback_query(filters.regex("^help"))
    async def help(self, c, callback_query):
        await self.handler.handle_callback_query(c, callback_query)
