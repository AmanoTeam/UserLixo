import re

from pyrogram import filters, Client

from userlixo.assistant.controllers.utils import on_message


def register_handlers(client: Client):
    on_message(
        client, filters.regex(r"^/(?P<command>cmd|sh)\s+(?P<code>.+)", flags=re.S)
    )

    on_message(client, filters.regex(r"^/(?P<cmd>ev(al)?)\s+(?P<code>.+)", flags=re.S))

    on_message(client, filters.regex(r"^/(?P<cmd>ex(ec)?)\s+(?P<code>.+)", flags=re.S))
