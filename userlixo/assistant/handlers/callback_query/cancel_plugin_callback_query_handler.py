from dataclasses import dataclass

from kink import inject
from pyrogram.types import CallbackQuery

from userlixo.assistant.handlers.abstract import CallbackQueryHandler
from userlixo.services.language_selector import LanguageSelector


@inject
@dataclass
class CancelPluginCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        text = lang.command_cancelled
        await query.message.edit(text)
