from dataclasses import dataclass

from kink import inject
from pyrogram.types import CallbackQuery

from userlixo.modules.abstract import CallbackQueryHandler
from userlixo.modules.assistant.common.plugins import (
    compose_list_plugins_by_type_message,
)
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class ListPluginsByTypeCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        page = int(query.matches[0].group("page")) or 0

        text, keyboard = await compose_list_plugins_by_type_message(
            lang, page, show_add_plugin_button=False, append_back=True
        )

        await query.edit(text, reply_markup=keyboard)
