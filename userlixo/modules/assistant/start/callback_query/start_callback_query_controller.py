from dataclasses import dataclass

from hydrogram import filters

from userlixo.decorators import controller, on_callback_query

from .start_callback_query_handler import StartCallbackQueryHandler


@controller
@dataclass
class StartCallbackQueryController:
    handler: StartCallbackQueryHandler

    @on_callback_query(filters.regex("^start"))
    async def start(self, *args):
        await self.handler.handle_callback_query(*args)
