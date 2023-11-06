from dataclasses import dataclass

from pyrogram import Client, filters

from userlixo.decorators import controller, on_message

from .restart_message_handler import RestartMessageHandler


@controller
@dataclass
class RestartMessageController:
    handler: RestartMessageHandler

    @on_message(filters.regex("^/(start )?restart"))
    async def restart(self, client: Client, message):
        await self.handler.handle_message(client, message)
