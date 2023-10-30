from dataclasses import dataclass

from kink import inject
from pyrogram.types import CallbackQuery

from userlixo.config import plugins
from userlixo.handlers.abstract import CallbackQueryHandler
from userlixo.handlers.assistant.common.plugins import (
    compose_info_plugin_message,
)
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class InfoPluginCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        plugin_basename = query.matches[0]["basename"]
        plugin_type = query.matches[0]["plugin_type"]
        page = int(query.matches[0]["page"])

        if plugin_basename not in plugins[plugin_type]:
            return await query.answer("UNKNOWN")

        text, keyboard = await compose_info_plugin_message(
            lang, plugin_type, plugin_basename, page
        )

        await query.edit(text, reply_markup=keyboard)
        return None
