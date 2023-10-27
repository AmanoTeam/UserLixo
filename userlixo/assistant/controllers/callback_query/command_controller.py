from dataclasses import dataclass

from pyrogram import filters

from userlixo.assistant.handlers.callback_query.info_command_callback_query_handler import (
    InfoCommandCallbackQueryHandler,
)
from userlixo.assistant.handlers.callback_query.list_commands_callback_query_handler import (
    ListCommandsCallbackQueryHandler,
)
from userlixo.decorators import Controller, on_callback_query


@Controller()
@dataclass
class CommandController:
    list_commands_handler: ListCommandsCallbackQueryHandler
    info_commands_handler: InfoCommandCallbackQueryHandler

    @on_callback_query(filters.regex(r"^list_commands (?P<page>\d+)"))
    async def list_commands(self, c, callback_query):
        await self.list_commands_handler.handle_callback_query(c, callback_query)

    @on_callback_query(filters.regex(r"^info_command (?P<cmd>.+) (?P<pg>\d+)"))
    async def info_command(self, c, callback_query):
        await self.info_commands_handler.handle_callback_query(c, callback_query)
