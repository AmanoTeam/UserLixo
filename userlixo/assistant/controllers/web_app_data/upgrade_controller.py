from pyrogram import filters, Client

from userlixo.assistant.handlers.web_app_data.upgrade_web_app_data_handler import (
    UpgradeWebAppDataHandler,
)
from userlixo.decorators import Controller, on_message


@Controller()
class UpgradeController:
    handler: UpgradeWebAppDataHandler

    @on_message(filters.web_data_cmd("upgrade"))
    async def upgrade(self, client: Client, message):
        await self.handler.handle_web_app_data(client, message)
