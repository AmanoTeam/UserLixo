from pyrogram import filters, Client

from userlixo.decorators import Controller, on_message


@Controller()
class SettingsController:
    @on_message(filters.regex("^/(start )?settings"))
    def settings(self, client: Client, message):
        pass
