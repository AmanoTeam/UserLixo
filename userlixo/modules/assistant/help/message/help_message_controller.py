from dataclasses import dataclass

from pyrogram import filters

from userlixo.decorators import controller, on_message

from .help_message_handler import HelpMessageHandler


@controller
@dataclass
class HelpMessageController:
    handler: HelpMessageHandler

    @on_message(filters.command("help"))
    async def on_help(self, client, message):
        await self.handler.handle_message(client, message)
