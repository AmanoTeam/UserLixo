from pyrogram import filters

from userlixo.decorators import Controller, on_callback_query


@Controller()
class LanguageController:
    @staticmethod
    @on_callback_query(filters.regex("^setting_language"))
    async def setting_language(_c, callback_query):
        pass

    @staticmethod
    @on_callback_query(filters.regex(r"^set_language (?P<code>\w+)"))
    async def set_language(_c, callback_query):
        pass
