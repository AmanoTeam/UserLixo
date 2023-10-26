from dataclasses import dataclass

from kink import inject

from userlixo.assistant.handlers.abstract import CallbackQueryHandler
from userlixo.assistant.handlers.common.settings import compose_settings_message
from userlixo.services.language_selector import LanguageSelector


@inject
@dataclass
class SettingsCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _c, m):
        lang = self.language_selector.get_lang()

        text, keyboard = compose_settings_message(lang)

        await m.edit(text, reply_markup=keyboard)
