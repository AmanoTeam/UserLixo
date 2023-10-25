from pyrogram import filters, Client

from userlixo.decorators import Controller, on_message


@Controller()
class UpgradeController:
    @staticmethod
    @on_message(filters.web_data_cmd("upgrade"))
    def upgrade(client: Client, message):
        pass
