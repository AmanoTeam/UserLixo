from pyrogram import filters

from userlixo.decorators import Controller, on_inline_query


@Controller()
class IndexController:
    @on_inline_query(filters.regex(r"^(?P<index>\d+)"))
    async def index(self, _c, inline_query):
        pass
