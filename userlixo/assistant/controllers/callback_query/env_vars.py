from pyrogram import filters

from userlixo.assistant.controllers.utils import on_callback_query

on_callback_query(
    filters.regex("^setting_env"),
    handler=lambda *_: None,
    sudoers_only=True,
)

on_callback_query(
    filters.regex("^edit_env (?P<key>.+)"),
    handler=lambda *_: None,
    sudoers_only=True,
)

on_callback_query(
    filters.regex("^view_env (?P<key>.+)"),
    handler=lambda *_: None,
    sudoers_only=True,
)

on_callback_query(
    filters.regex("^restart_now"),
    handler=lambda *_: None,
    sudoers_only=True,
)
