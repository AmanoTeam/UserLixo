from kink import di
from pyrogram import filters, Client

from userlixo.assistant.controllers.utils import on_message
from userlixo.assistant.handlers.common.start import StartHandler

handler: StartHandler = di[StartHandler]


def register_handlers(client: Client):
    on_message(client, filters.command("start"), handler=handler.handle_message)
