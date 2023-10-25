from pyrogram import filters

from userlixo.decorators import Controller, on_callback_query


@Controller()
class EnvVarsController:
    @staticmethod
    @on_callback_query(filters.regex("^setting_env"))
    async def setting_env(c, callback_query):
        pass

    @staticmethod
    @on_callback_query(filters.regex("^edit_env (?P<key>.+)"))
    async def edit_env(c, callback_query):
        pass

    @staticmethod
    @on_callback_query(filters.regex("^view_env (?P<key>.+)"))
    async def view_env(c, callback_query):
        pass

    @staticmethod
    @on_callback_query(filters.regex("^restart_now"))
    async def restart_now(c, callback_query):
        pass
