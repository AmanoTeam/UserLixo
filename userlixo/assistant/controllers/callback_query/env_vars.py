from pyrogram import filters, Client

from userlixo.assistant.controllers.utils import on_callback_query


def register_handlers(client: Client):
    on_callback_query(
        client,
        filters.regex("^setting_env"),
        handler=lambda *_: None,
        sudoers_only=True,
    )

    on_callback_query(
        client,
        filters.regex("^edit_env (?P<key>.+)"),
        handler=lambda *_: None,
        sudoers_only=True,
    )

    on_callback_query(
        client,
        filters.regex("^view_env (?P<key>.+)"),
        handler=lambda *_: None,
        sudoers_only=True,
    )

    on_callback_query(
        client,
        filters.regex("^restart_now"),
        handler=lambda *_: None,
        sudoers_only=True,
    )
