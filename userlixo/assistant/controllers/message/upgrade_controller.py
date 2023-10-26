from kink import inject
from pyrogram import filters, Client

from userlixo.decorators import Controller, on_message


@Controller()
@inject
class UpgradeController:
    @on_message(filters.regex("^/(start )?upgrade"))
    def upgrade(self, client: Client, message):
        pass
