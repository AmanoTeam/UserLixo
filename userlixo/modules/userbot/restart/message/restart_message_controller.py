from dataclasses import dataclass

from hydrogram import Client, filters
from hydrogram.types import Message

from userlixo.decorators import controller, on_message
from userlixo.modules.userbot.restart.message.restart_message_handler import (
    RestartMessageHandler,
)


@controller
@dataclass
class RestartMessageController:
    handler: RestartMessageHandler

    @on_message(filters.su_cmd("restart"))
    async def restart(self, client: Client, message: Message):
        await self.handler.handle_message(client, message)
