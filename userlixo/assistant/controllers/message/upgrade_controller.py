from dataclasses import dataclass

from kink import inject
from pyrogram import filters, Client

from userlixo.assistant.handlers.message.upgrade_message_handler import (
    UpgradeMessageHandler,
)
from userlixo.decorators import Controller, on_message


@Controller()
@inject
@dataclass
class UpgradeController:
    handler: UpgradeMessageHandler

    @on_message(filters.regex("^/(start )?upgrade"))
    async def upgrade(self, client: Client, message):
        await self.handler.handle_message(client, message)
