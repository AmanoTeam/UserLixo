from pyrogram import filters

from userlixo.assistant.controllers.utils import on_inline_query

on_inline_query(
    filters.regex(r"^(?P<index>\d+)"),
)
