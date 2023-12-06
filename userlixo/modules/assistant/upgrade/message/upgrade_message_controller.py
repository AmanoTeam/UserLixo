from dataclasses import dataclass

from hydrogram import Client, filters

from userlixo.decorators import controller, on_message

from .upgrade_message_handler import UpgradeMessageHandler


@controller
@dataclass
class UpgradeMessageController:
    handler: UpgradeMessageHandler

    @on_message(filters.regex("^/(start )?upgrade"))
    async def upgrade(self, client: Client, message):
        await self.handler.handle_message(client, message)
