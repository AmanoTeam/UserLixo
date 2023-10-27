from dataclasses import dataclass

from pyrogram import filters, Client
from pyrogram.types import Message

from userlixo.decorators import Controller, on_message
from userlixo.userbot.handlers.message.settings_message_handler import (
    SettingsMessageHandler,
)


@Controller()
@dataclass
class SettingsController:
    handler: SettingsMessageHandler

    @on_message(filters.su_cmd("settings"))
    async def settings(self, client: Client, message: Message):
        await self.handler.handle_message(client, message)
