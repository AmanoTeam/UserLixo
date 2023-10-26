from dataclasses import dataclass

from kink import inject
from pyrogram import filters, Client

from userlixo.assistant.handlers.callback_query.settings_callback_query_handler import (
    SettingsCallbackQueryHandler,
)
from userlixo.decorators import Controller, on_callback_query


@Controller()
@inject
@dataclass
class SettingsController:
    handler: SettingsCallbackQueryHandler

    @on_callback_query(filters.regex("^settings"))
    async def settings(self, client: Client, query):
        await self.handler.handle_callback_query(client, query)
