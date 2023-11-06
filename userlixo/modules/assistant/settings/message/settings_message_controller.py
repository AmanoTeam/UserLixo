from dataclasses import dataclass

from pyrogram import Client, filters

from userlixo.decorators import controller, on_message

from .settings_message_handler import SettingsMessageHandler


@controller()
@dataclass
class SettingsMessageController:
    handler: SettingsMessageHandler

    @on_message(filters.regex("^/(start )?settings"))
    async def settings(self, client: Client, message):
        await self.handler.handle_message(client, message)
