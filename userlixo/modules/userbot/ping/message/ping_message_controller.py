from dataclasses import dataclass

from hydrogram import Client, filters
from hydrogram.types import Message

from userlixo.decorators import controller, on_message
from userlixo.modules.userbot.ping.message.ping_message_handler import (
    PingMessageHandler,
)


@controller
@dataclass
class PingMessageController:
    handler: PingMessageHandler

    @on_message(filters.su_cmd("ping"))
    async def ping(self, client: Client, message: Message):
        await self.handler.handle_message(client, message)
