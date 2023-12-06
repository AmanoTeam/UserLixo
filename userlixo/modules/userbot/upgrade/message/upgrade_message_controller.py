from dataclasses import dataclass

from hydrogram import Client, filters
from hydrogram.types import Message

from userlixo.decorators import controller, on_message
from userlixo.modules.userbot.upgrade.message.upgrade_message_handler import (
    UpgradeMessageHandler,
)


@controller
@dataclass
class UpgradeMessageController:
    handler: UpgradeMessageHandler

    @on_message(filters.su_cmd("upgrade"))
    async def upgrade(self, client: Client, message: Message):
        await self.handler.handle_message(client, message)
