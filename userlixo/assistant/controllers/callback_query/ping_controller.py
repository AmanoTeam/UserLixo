from pyrogram import filters

from userlixo.decorators import Controller, on_callback_query


@Controller()
class PingController:
    @on_callback_query(filters.regex("^ping"))
    async def ping(self, _c, callback_query):
        await callback_query.answer("pong")
