from pyrogram import filters

from userlixo.assistant.controllers.utils import on_callback_query

on_callback_query(
    filters.regex(
        r"^info_plugin (?P<basename>.+) (?P<plugin_type>user|bot) (?P<pg>\d+)"
    ),
    handler=lambda *_: None,
    sudoers_only=True,
)

on_callback_query(
    filters.regex(
        r"^(?P<deactivate>de)?activate_plugin (?P<basename>.+) (?P<plugin_type>user|bot) (?P<pg>\d+)"
    ),
    handler=lambda *_: None,
    sudoers_only=True,
)

on_callback_query(
    filters.regex(
        r"^remove_plugin (?P<basename>.+) (?P<plugin_type>user|bot) (?P<page>\d+)"
    ),
    sudoers_only=True,
)

on_callback_query(filters.regex("^add_plugin"))

on_callback_query(filters.regex("^cancel_plugin"))

on_callback_query(
    filters.regex("^confirm_add_plugin (?P<plugin_type>user|bot) (?P<filename>.+)")
)

on_callback_query(filters.regex("^list_plugins"))

on_callback_query(filters.regex(r"^(?P<type>user|bot)_plugins (?P<page>\d+)"))
