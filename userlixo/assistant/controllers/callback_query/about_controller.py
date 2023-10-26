from pyrogram import filters

from userlixo.decorators import Controller, on_callback_query


@Controller()
class AboutController:
    @on_callback_query(filters.regex("^about_(?P<subject>userlixo|plugins|commands)"))
    async def about_userlixo(self, _c, callback_query):
        pass
