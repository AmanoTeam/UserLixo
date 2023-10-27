from pyrogram import filters, Client

from userlixo.assistant.controllers.utils import on_callback_query


def register_handlers(client: Client):
    on_callback_query(client, filters.regex(r"^list_commands (?P<page>\d+)"))

    on_callback_query(client, filters.regex(r"^info_command (?P<cmd>.+) (?P<pg>\d+)"))
