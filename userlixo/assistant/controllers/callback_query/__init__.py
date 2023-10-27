from pyrogram import Client

from . import about, command, env_vars, help, language, ping, plugin, start, sudoer


class CallbackQueryController:
    @staticmethod
    def register_handlers(client: Client):
        about.register_handlers(client)
        command.register_handlers(client)
        env_vars.register_handlers(client)
        help.register_handlers(client)
        language.register_handlers(client)
        ping.register_handlers(client)
        plugin.register_handlers(client)
        start.register_handlers(client)
        sudoer.register_handlers(client)
