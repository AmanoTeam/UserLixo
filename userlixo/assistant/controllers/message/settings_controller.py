from dataclasses import dataclass

from pyrogram import filters, Client

from userlixo.assistant.handlers.message.settings_message_handler import (
    SettingsMessageHandler,
)
from userlixo.decorators import Controller, on_message


@Controller()
@dataclass
class SettingsController:
    handler: SettingsMessageHandler

    @on_message(filters.regex("^/(start )?settings"))
    async def settings(self, client: Client, message):
        await self.handler.handle_message(client, message)
