from pyrogram import filters, Client

from userlixo.decorators import Controller, on_message


@Controller()
class UpgradeController:
    @staticmethod
    @on_message(filters.regex("^/(start )?upgrade"))
    def upgrade(client: Client, message):
        pass
