from dataclasses import dataclass

from pyrogram import Client, filters

from userlixo.decorators import Controller, on_callback_query
from userlixo.handlers.assistant.handlers.callback_query.settings_callback_query_handler import (
    SettingsCallbackQueryHandler,
)


@Controller()
@dataclass
class SettingsController:
    handler: SettingsCallbackQueryHandler

    @on_callback_query(filters.regex("^settings"))
    async def settings(self, client: Client, query):
        await self.handler.handle_callback_query(client, query)
