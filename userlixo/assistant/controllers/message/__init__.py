from pyrogram import Client

from . import add_sudoer, execs, plugin, restart, settings, start, upgrade, web_app


class MessageController:
    @staticmethod
    def register_handlers(client: Client):
        add_sudoer.register_handlers(client)
        execs.register_handlers(client)
        plugin.register_handlers(client)
        restart.register_handlers(client)
        settings.register_handlers(client)
        start.register_handlers(client)
        upgrade.register_handlers(client)
        web_app.register_handlers(client)
