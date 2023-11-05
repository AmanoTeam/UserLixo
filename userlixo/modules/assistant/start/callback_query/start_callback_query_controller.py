from dataclasses import dataclass

from pyrogram import filters

from userlixo.decorators import Controller, on_callback_query

from .start_callback_query_handler import StartCallbackQueryHandler


@Controller()
@dataclass
class StartCallbackQueryController:
    handler: StartCallbackQueryHandler

    @on_callback_query(filters.regex("^start"))
    async def start(self, *args):
        await self.handler.handle_callback_query(*args)