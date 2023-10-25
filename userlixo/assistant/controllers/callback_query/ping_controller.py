from pyrogram import filters

from userlixo.decorators import Controller, on_callback_query


@Controller()
class PingController:
    @staticmethod
    @on_callback_query(filters.regex("^ping"))
    async def ping(_c, callback_query):
        await callback_query.answer("pong")
