from dataclasses import dataclass

from hydrogram import Client, filters
from hydrogram.types import Message

from userlixo.decorators import controller, on_message
from userlixo.modules.userbot.settings.message.settings_message_handler import (
    SettingsMessageHandler,
)


@controller
@dataclass
class SettingsMessageController:
    handler: SettingsMessageHandler

    @on_message(filters.su_cmd("settings"))
    async def settings(self, client: Client, message: Message):
        await self.handler.handle_message(client, message)
