from kink import inject
from pyrogram import filters

from userlixo.assistant.handlers.message.help_message_handler import HelpMessageHandler
from userlixo.decorators import Controller, on_message


@Controller()
@inject
class HelpController:
    def __init__(self, handler: HelpMessageHandler):
        self.handler = handler

    @on_message(filters.command('help'))
    async def on_help(self, client, message):
        await self.handler.handle_message(client, message)
