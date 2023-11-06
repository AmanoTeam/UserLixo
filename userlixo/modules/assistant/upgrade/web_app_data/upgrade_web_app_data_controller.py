from dataclasses import dataclass

from pyrogram import Client, filters

from userlixo.decorators import controller, on_message

from .upgrade_web_app_data_handler import UpgradeWebAppDataHandler


@controller
@dataclass
class UpgradeWebAppDataController:
    handler: UpgradeWebAppDataHandler

    @on_message(filters.web_data_cmd("upgrade"))
    async def upgrade(self, client: Client, message):
        await self.handler.handle_web_app_data(client, message)
