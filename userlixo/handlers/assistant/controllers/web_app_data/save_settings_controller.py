from dataclasses import dataclass

from pyrogram import filters, Client

from userlixo.handlers.assistant.handlers.web_app_data.save_settings_web_app_data_handler import (
    SaveSettingsWebAppDataHandler,
)
from userlixo.decorators import Controller, on_message


@Controller()
@dataclass
class SaveSettingsController:
    handler: SaveSettingsWebAppDataHandler

    @on_message(filters.web_data_cmd("save_settings"))
    async def save_settings(self, client: Client, message):
        await self.handler.handle_web_app_data(client, message)
