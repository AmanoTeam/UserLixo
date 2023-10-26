from kink import inject
from pyrogram import filters

from userlixo.assistant.handlers.callback_query.restart_callback_query_handler import RestartCallbackQueryHandler
from userlixo.decorators import Controller, on_callback_query


@Controller()
@inject
class RestartController:
    def __init__(self, handler: RestartCallbackQueryHandler):
        self.handler = handler

    @on_callback_query(filters.regex("^restart"))
    async def on_restart(self, c, callback_query):
        await self.handler.handle_callback_query(c, callback_query)
