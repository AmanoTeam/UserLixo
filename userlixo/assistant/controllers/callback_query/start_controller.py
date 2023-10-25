from kink import di
from pyrogram import filters

from userlixo.assistant.handlers.callback_query.start_callback_query_handler import (
    StartCallbackQueryHandler,
)
from userlixo.decorators import Controller, on_callback_query

handler: StartCallbackQueryHandler = di[StartCallbackQueryHandler]


@Controller()
class StartController:
    @staticmethod
    @on_callback_query(filters.regex("^start"))
    async def start(*args):
        await handler.handle_callback_query(*args)
