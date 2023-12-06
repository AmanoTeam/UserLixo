from dataclasses import dataclass

from hydrogram import filters

from userlixo.decorators import controller, on_message

from .start_message_handler import StartMessageHandler


@controller
@dataclass
class StartMessageController:
    handler: StartMessageHandler

    @on_message(filters.regex("^/start$"))
    async def handle_message(self, *args):
        await self.handler.handle_message(*args)
