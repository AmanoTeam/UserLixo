from kink import inject
from pyrogram import filters

from userlixo.assistant.handlers.callback_query.start_callback_query_handler import (
    StartCallbackQueryHandler,
)
from userlixo.decorators import Controller, on_callback_query


@Controller()
@inject
class StartController:
    def __init__(self, handler: StartCallbackQueryHandler):
        self.handler = handler

    @on_callback_query(filters.regex("^start"))
    async def start(self, *args):
        await self.handler.handle_callback_query(*args)
