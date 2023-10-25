from pyrogram import filters, Client

from userlixo.decorators import Controller, on_message


@Controller()
class SettingsController:
    @staticmethod
    @on_message(filters.regex("^/(start )?settings"))
    def settings(client: Client, message):
        pass
