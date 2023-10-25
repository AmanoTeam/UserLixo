from pyrogram import filters

from userlixo.decorators import Controller, on_inline_query


@Controller()
class IndexController:
    @staticmethod
    @on_inline_query(filters.regex(r"^(?P<index>\d+)"))
    async def index(_c, inline_query):
        pass
