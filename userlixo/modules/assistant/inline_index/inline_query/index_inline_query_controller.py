from dataclasses import dataclass

from hydrogram import filters

from userlixo.decorators import controller, on_inline_query

from .index_inline_query_handler import IndexInlineQueryHandler


@controller
@dataclass
class IndexInlineQueryController:
    handler: IndexInlineQueryHandler

    @on_inline_query(filters.regex(r"^(?P<index>\d+)"))
    async def index(self, _c, inline_query):
        await self.handler.handle_inline_query(_c, inline_query)
