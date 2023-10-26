from kink import inject
from pyrogram import filters

from userlixo.assistant.handlers.callback_query.help_callback_query_handler import HelpCallbackQueryHandler
from userlixo.decorators import on_callback_query, Controller


@Controller()
@inject
class HelpController:
    def __init__(self, handler: HelpCallbackQueryHandler):
        self.handler = handler

    @on_callback_query(filters.regex("^help"))
    async def help(self, c, callback_query):
        await self.handler.handle_callback_query(c, callback_query)
