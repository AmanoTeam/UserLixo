from kink import di
from pyrogram import filters, Client

from userlixo.assistant.controllers.utils import on_callback_query
from userlixo.assistant.handlers.callback_query.start_callback_query_handler import (
    StartCallbackQueryHandler,
)


def register_handlers(client: Client):
    handler: StartCallbackQueryHandler = di[StartCallbackQueryHandler]

    on_callback_query(
        client, filters.regex("^start"), handler=handler.handle_callback_query
    )
