from pyrogram import filters

from userlixo.assistant.controllers.utils import on_callback_query

on_callback_query(filters.regex("^list_commands (?P<page>\d+)"))

on_callback_query(filters.regex("^info_command (?P<cmd>.+) (?P<pg>\d+)"))
