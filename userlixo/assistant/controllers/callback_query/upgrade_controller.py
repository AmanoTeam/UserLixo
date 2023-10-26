from kink import inject
from pyrogram import filters, Client

from userlixo.assistant.handlers.callback_query.upgrade_callback_query_handler import UpgradeCallbackQueryHandler
from userlixo.decorators import Controller, on_callback_query


@Controller()
@inject
class UpgradeController:
    def __init__(self, handler: UpgradeCallbackQueryHandler):
        self.handler = handler

    @on_callback_query(filters.regex("^upgrade"))
    async def upgrade(self, client: Client, message):
        await self.handler.handle_callback_query(client, message)
