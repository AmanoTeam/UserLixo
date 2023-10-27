from dataclasses import dataclass

from kink import inject
from pyrogram.types import CallbackQuery

from userlixo.abstract import CallbackQueryHandler
from userlixo.common.plugins import compose_list_plugins_message
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class ListPluginsCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        text, keyboard = compose_list_plugins_message(lang, append_back=True)
        await query.message.edit(text, reply_markup=keyboard)
