from pyrogram import filters, Client

from userlixo.decorators import Controller, on_message


@Controller()
class PluginController:
    @staticmethod
    @on_message(filters.document & filters.private & ~filters.me)
    def handle_plugin(client: Client, message):
        pass

    @staticmethod
    @on_message(filters.regex("^/(start )?plugin[_ ]add"))
    def add_plugin(client: Client, message):
        pass

    @staticmethod
    @on_message(filters.regex("^/plugins"))
    def plugins(client: Client, message):
        pass
