from dataclasses import dataclass

from pyrogram import Client, filters

from userlixo.decorators import Controller, on_message
from userlixo.handlers.assistant.handlers.message.settings_message_handler import (
    SettingsMessageHandler,
)


@Controller()
@dataclass
class SettingsController:
    handler: SettingsMessageHandler

    @on_message(filters.regex("^/(start )?settings"))
    async def settings(self, client: Client, message):
        await self.handler.handle_message(client, message)
