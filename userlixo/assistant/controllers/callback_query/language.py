from pyrogram import filters

from userlixo.assistant.controllers.utils import on_callback_query

on_callback_query(
    filters.regex("^setting_language"),
    handler=lambda *_: None,
    sudoers_only=True,
)

on_callback_query(
    filters.regex(r"^set_language (?P<code>\w+)"),
    handler=lambda *_: None,
    sudoers_only=True,
)
