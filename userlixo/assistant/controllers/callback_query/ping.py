from pyrogram import filters, Client

from userlixo.assistant.controllers.utils import on_callback_query


def register_handlers(client: Client):
    on_callback_query(
        client,
        filters.regex("ping"),
        handler=lambda *_: None,
        sudoers_only=True,
    )
