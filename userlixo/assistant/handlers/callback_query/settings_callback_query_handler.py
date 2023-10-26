from kink import inject

from userlixo.assistant.handlers.abstract import CallbackQueryHandler
from userlixo.assistant.handlers.common.settings import compose_settings_message
from userlixo.services.language_selector import LanguageSelector


@inject
class SettingsCallbackQueryHandler(CallbackQueryHandler):
    def __init__(self, language_selector: LanguageSelector):
        self.get_lang = language_selector.get_lang

    async def handle_callback_query(self, _c, m):
        lang = self.get_lang()

        text, keyboard = compose_settings_message(lang)

        await m.edit(text, reply_markup=keyboard)
