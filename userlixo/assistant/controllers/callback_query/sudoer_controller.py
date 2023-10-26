from pyrogram import filters

from userlixo.decorators import Controller, on_callback_query


@Controller()
class SudoerController:
    @on_callback_query(filters.regex("^setting_sudoers"))
    async def setting_sudoers(self, _c, callback_query):
        pass

    @on_callback_query(filters.regex(r"^remove_sudoer (?P<who>\w+)"))
    async def remove_sudoer(self, _c, callback_query):
        pass
