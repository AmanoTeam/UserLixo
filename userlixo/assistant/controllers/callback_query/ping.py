from pyrogram import filters

from userlixo.assistant.controllers.utils import on_callback_query

on_callback_query(
    filters.regex("ping"),
    handler=lambda *_: None,
    sudoers_only=True,
)
