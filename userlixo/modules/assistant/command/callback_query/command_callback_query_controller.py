from dataclasses import dataclass

from hydrogram import filters

from userlixo.decorators import controller, on_callback_query

from .info_command_callback_query_handler import InfoCommandCallbackQueryHandler
from .list_commands_callback_query_handler import ListCommandsCallbackQueryHandler


@controller
@dataclass
class CommandCallbackQueryController:
    list_commands_handler: ListCommandsCallbackQueryHandler
    info_commands_handler: InfoCommandCallbackQueryHandler

    @on_callback_query(filters.regex(r"^list_commands (?P<page>\d+)"))
    async def list_commands(self, c, callback_query):
        await self.list_commands_handler.handle_callback_query(c, callback_query)

    @on_callback_query(filters.regex(r"^info_command (?P<cmd>.+) (?P<pg>\d+)"))
    async def info_command(self, c, callback_query):
        await self.info_commands_handler.handle_callback_query(c, callback_query)
