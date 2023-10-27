from kink import di
from pyrogram import filters, Client

from userlixo.assistant.controllers.utils import on_callback_query
from userlixo.assistant.handlers.common.start import StartHandler


def register_handlers(client: Client):
    handler: StartHandler = di[StartHandler]

    on_callback_query(
        client, filters.regex("^start"), handler=handler.handle_callback_query
    )
