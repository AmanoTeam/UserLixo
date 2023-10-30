from dataclasses import dataclass

from kink import inject
from pyrogram.types import CallbackQuery

from userlixo.handlers.abstract import CallbackQueryHandler
from userlixo.handlers.common.plugins import handle_add_plugin_request
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class AddPluginCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        await query.message.delete()
        await handle_add_plugin_request(lang, _client, update=query)
