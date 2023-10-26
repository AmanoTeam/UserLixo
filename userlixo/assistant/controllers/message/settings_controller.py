from kink import inject
from pyrogram import filters, Client

from userlixo.assistant.handlers.message.settings_message_handler import SettingsMessageHandler
from userlixo.decorators import Controller, on_message


@Controller()
@inject
class SettingsController:
    def __init__(self, handler: SettingsMessageHandler):
        self.handler = handler

    @on_message(filters.regex("^/(start )?settings"))
    async def settings(self, client: Client, message):
        await self.handler.handle_message(client, message)
