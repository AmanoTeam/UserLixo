from pyrogram import Client

from . import index


class InlineQueryController:
    @staticmethod
    def register_handlers(client: Client):
        index.register_handlers(client)
