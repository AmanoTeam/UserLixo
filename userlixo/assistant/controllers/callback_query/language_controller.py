from dataclasses import dataclass

from pyrogram import filters

from userlixo.assistant.handlers.callback_query.set_language_code_callback_query_handler import (
    SetLanguageCodeCallbackQueryHandler,
)
from userlixo.assistant.handlers.callback_query.setting_language_callback_query_handler import (
    SettingLanguageCallbackQueryHandler,
)
from userlixo.decorators import Controller, on_callback_query


@Controller()
@dataclass
class LanguageController:
    setting_language_handler: SettingLanguageCallbackQueryHandler
    set_language_code_handler: SetLanguageCodeCallbackQueryHandler

    @on_callback_query(filters.regex("^setting_language"))
    async def setting_language(self, _c, callback_query):
        await self.setting_language_handler.handle_callback_query(_c, callback_query)

    @on_callback_query(filters.regex(r"^set_language (?P<code>\w+)"))
    async def set_language(self, _c, callback_query):
        await self.set_language_code_handler.handle_callback_query(_c, callback_query)
