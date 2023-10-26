from pyrogram import filters, Client

from userlixo.decorators import Controller, on_message


@Controller()
class PluginController:
    @on_message(filters.document & filters.private & ~filters.me)
    def handle_plugin(self, client: Client, message):
        pass

    @on_message(filters.regex("^/(start )?plugin[_ ]add"))
    def add_plugin(self, client: Client, message):
        pass

    @on_message(filters.regex("^/plugins"))
    def plugins(self, client: Client, message):
        pass
