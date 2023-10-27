from dataclasses import dataclass

from pyrogram import Client, filters

from userlixo.decorators import Controller, on_message
from userlixo.handlers.assistant.handlers.message.upgrade_message_handler import (
    UpgradeMessageHandler,
)


@Controller()
@dataclass
class UpgradeController:
    handler: UpgradeMessageHandler

    @on_message(filters.regex("^/(start )?upgrade"))
    async def upgrade(self, client: Client, message):
        await self.handler.handle_message(client, message)