from dataclasses import dataclass

from pyrogram import Client, filters
from pyrogram.types import Message

from userlixo.decorators import controller, on_message
from userlixo.modules.userbot.info.message.info_message_handler import (
    InfoMessageHandler,
)


@controller()
@dataclass
class InfoMessageController:
    handler: InfoMessageHandler

    @on_message(filters.su_cmd("info"))
    async def info(self, client: Client, message: Message):
        await self.handler.handle_message(client, message)
