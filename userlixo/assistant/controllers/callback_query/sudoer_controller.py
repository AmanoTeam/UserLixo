from pyrogram import filters

from userlixo.decorators import Controller, on_callback_query


@Controller()
class SudoerController:
    @staticmethod
    @on_callback_query(filters.regex("^setting_sudoers"))
    async def setting_sudoers(_c, callback_query):
        pass

    @staticmethod
    @on_callback_query(filters.regex(r"^remove_sudoer (?P<who>\w+)"))
    async def remove_sudoer(_c, callback_query):
        pass
