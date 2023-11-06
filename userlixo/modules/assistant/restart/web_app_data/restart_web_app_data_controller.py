from dataclasses import dataclass

from pyrogram import Client, filters

from userlixo.decorators import controller, on_message

from .restart_web_app_data_handler import RestartWebAppDataHandler


@controller()
@dataclass
class RestartWebAppDataController:
    handler: RestartWebAppDataHandler

    @on_message(filters.web_data_cmd("restart"))
    async def restart(self, client: Client, message):
        await self.handler.handle_web_app_data(client, message)
