from dataclasses import dataclass

from pyrogram import Client, filters
from pyrogram.types import Message

from userlixo.decorators import Controller, on_message
from userlixo.handlers.userbot.settings.message.settings_message_handler import (
    SettingsMessageHandler,
)


@Controller()
@dataclass
class SettingsMessageController:
    handler: SettingsMessageHandler

    @on_message(filters.su_cmd("settings"))
    async def settings(self, client: Client, message: Message):
        await self.handler.handle_message(client, message)
