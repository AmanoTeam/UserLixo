from pyrogram import filters, Client

from userlixo.assistant.controllers.utils import on_inline_query


def register_handlers(client: Client):
    on_inline_query(
        client,
        filters.regex(r"^(?P<index>\d+)"),
    )
