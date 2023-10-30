from dataclasses import dataclass

from pyrogram import Client, filters
from pyrogram.types import Message

from userlixo.decorators import Controller, on_message
from userlixo.modules.userbot.upgrade.message.upgrade_message_handler import (
    UpgradeMessageHandler,
)


@Controller()
@dataclass
class UpgradeMessageController:
    handler: UpgradeMessageHandler

    @on_message(filters.su_cmd("upgrade"))
    async def upgrade(self, client: Client, message: Message):
        await self.handler.handle_message(client, message)
