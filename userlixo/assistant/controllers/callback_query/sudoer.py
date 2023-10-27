from pyrogram import filters, Client

from userlixo.assistant.controllers.utils import on_callback_query


def register_handlers(client: Client):
    on_callback_query(
        client,
        filters.regex("^setting_sudoers"),
        handler=lambda *_: None,
        sudoers_only=True,
    )

    on_callback_query(
        client,
        filters.regex(r"^remove_sudoer (?P<who>\w+)"),
        handler=lambda *_: None,
        sudoers_only=True,
    )
