from kink import di
from pyrogram import filters, Client

from userlixo.assistant.controllers.utils import on_message
from userlixo.assistant.handlers.message.start import StartMessageHandler


def register_handlers(client: Client):
    handler: StartMessageHandler = di[StartMessageHandler]

    on_message(client, filters.command("start"), handler=handler.handle_message)
