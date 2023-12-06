from dataclasses import dataclass

from hydrogram import filters

from userlixo.decorators import controller, on_callback_query

from .remove_sudoer_callback_query_handler import RemoveSudoerCallbackQueryHandler
from .setting_sudoers_callback_query_handler import SettingSudoersCallbackQueryHandler


@controller
@dataclass
class SudoerCallbackQueryController:
    setting_sudoers_handler: SettingSudoersCallbackQueryHandler
    remove_sudoer_handler: RemoveSudoerCallbackQueryHandler

    @on_callback_query(filters.regex("^setting_sudoers"))
    async def setting_sudoers(self, _c, callback_query):
        await self.setting_sudoers_handler.handle_callback_query(_c, callback_query)

    @on_callback_query(filters.regex(r"^remove_sudoer (?P<who>\w+)"))
    async def remove_sudoer(self, _c, callback_query):
        await self.remove_sudoer_handler.handle_callback_query(_c, callback_query)
