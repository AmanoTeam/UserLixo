from pyrogram import filters, Client

from userlixo.assistant.controllers.utils import on_callback_query


def register_handlers(client: Client):
    on_callback_query(
        client,
        filters.regex("^setting_language"),
        handler=lambda *_: None,
        sudoers_only=True,
    )

    on_callback_query(
        client,
        filters.regex(r"^set_language (?P<code>\w+)"),
        handler=lambda *_: None,
        sudoers_only=True,
    )
