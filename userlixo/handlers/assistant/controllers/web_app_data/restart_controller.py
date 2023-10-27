from pyrogram import Client, filters

from userlixo.decorators import Controller, on_message
from userlixo.handlers.assistant.handlers.web_app_data.restart_web_app_data_handler import (
    RestartWebAppDataHandler,
)


@Controller()
class RestartController:
    handler: RestartWebAppDataHandler

    @on_message(filters.web_data_cmd("restart"))
    async def restart(self, client: Client, message):
        await self.handler.handle_web_app_data(client, message)
