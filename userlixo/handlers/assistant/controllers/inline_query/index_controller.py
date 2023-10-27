from dataclasses import dataclass

from pyrogram import filters

from userlixo.handlers.assistant.handlers.inline_query.index_inline_query_handler import (
    IndexInlineQueryHandler,
)
from userlixo.decorators import Controller, on_inline_query


@Controller()
@dataclass
class IndexController:
    handler: IndexInlineQueryHandler

    @on_inline_query(filters.regex(r"^(?P<index>\d+)"))
    async def index(self, _c, inline_query):
        await self.handler.handle_inline_query(_c, inline_query)
