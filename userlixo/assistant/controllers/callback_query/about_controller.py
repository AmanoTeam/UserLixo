from pyrogram import filters

from userlixo.decorators import Controller, on_callback_query


@Controller()
class AboutController:
    @staticmethod
    @on_callback_query(filters.regex("^about_(?P<subject>userlixo|plugins|commands)"))
    async def about_userlixo(_c, callback_query):
        pass
