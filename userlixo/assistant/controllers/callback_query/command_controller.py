from pyrogram import filters

from userlixo.decorators import Controller, on_callback_query


@Controller()
class CommandController:
    @staticmethod
    @on_callback_query(filters.regex(r"^list_commands (?P<page>\d+)"))
    async def list_commands(c, callback_query):
        pass

    @staticmethod
    @on_callback_query(filters.regex(r"^info_command (?P<cmd>.+) (?P<pg>\d+)"))
    async def info_command(c, callback_query):
        pass
