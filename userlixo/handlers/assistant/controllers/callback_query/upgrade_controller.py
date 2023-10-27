from dataclasses import dataclass

from pyrogram import filters, Client

from userlixo.handlers.assistant.handlers.callback_query.upgrade_callback_query_handler import (
    UpgradeCallbackQueryHandler,
)
from userlixo.decorators import Controller, on_callback_query


@Controller()
@dataclass
class UpgradeController:
    handler: UpgradeCallbackQueryHandler

    @on_callback_query(filters.regex("^upgrade"))
    async def upgrade(self, client: Client, query):
        await self.handler.handle_callback_query(client, query)
