from dataclasses import dataclass

from pyrogram import filters, Client
from pyrogram.types import Message

from userlixo.decorators import Controller, on_message
from userlixo.userbot.handlers.upgrade_message_handler import UpgradeMessageHandler


@Controller()
@dataclass
class UpgradeController:
    handler: UpgradeMessageHandler

    @on_message(filters.su_cmd("upgrade"))
    async def upgrade(self, client: Client, message: Message):
        await self.handler.handle_message(client, message)
