from pyrogram import filters, Client

from userlixo.assistant.controllers.utils import on_message


def register_handlers(client: Client):
    on_message(client, filters.command("settings"))
