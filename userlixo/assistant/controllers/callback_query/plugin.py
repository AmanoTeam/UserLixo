from pyrogram import filters, Client

from userlixo.assistant.controllers.utils import on_callback_query


def register_handlers(client: Client):
    on_callback_query(
        client,
        filters.regex(
            r"^info_plugin (?P<basename>.+) (?P<plugin_type>user|bot) (?P<pg>\d+)"
        ),
        handler=lambda *_: None,
        sudoers_only=True,
    )

    on_callback_query(
        client,
        filters.regex(
            r"^(?P<deactivate>de)?activate_plugin (?P<basename>.+) (?P<plugin_type>user|bot) (?P<pg>\d+)"
        ),
        handler=lambda *_: None,
        sudoers_only=True,
    )

    on_callback_query(
        client,
        filters.regex(
            r"^remove_plugin (?P<basename>.+) (?P<plugin_type>user|bot) (?P<page>\d+)"
        ),
        sudoers_only=True,
    )

    on_callback_query(client, filters.regex("^add_plugin"))

    on_callback_query(client, filters.regex("^cancel_plugin"))

    on_callback_query(
        client,
        filters.regex("^confirm_add_plugin (?P<plugin_type>user|bot) (?P<filename>.+)"),
    )

    on_callback_query(client, filters.regex("^list_plugins"))

    on_callback_query(
        client, filters.regex(r"^(?P<type>user|bot)_plugins (?P<page>\d+)")
    )
