from kink import inject

from userlixo.assistant.handlers.abstract import MessageHandler
from userlixo.assistant.handlers.common.settings import compose_settings_message
from userlixo.services.language_selector import LanguageSelector


@inject
class SettingsMessageHandler(MessageHandler):
    def __init__(self, language_selector: LanguageSelector):
        self.get_lang = language_selector.get_lang

    async def handle_message(self, _c, m):
        lang = self.get_lang()

        text, keyboard = compose_settings_message(lang, append_back=False)

        await m.reply(text, reply_markup=keyboard)
