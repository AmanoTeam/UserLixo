from dataclasses import dataclass

from kink import inject

from userlixo.abstract import MessageHandler
from userlixo.common.settings import compose_settings_message
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class SettingsMessageHandler(MessageHandler):
    language_selector: LanguageSelector

    async def handle_message(self, _c, m):
        lang = self.language_selector.get_lang()

        text, keyboard = compose_settings_message(lang, append_back=False)

        await m.reply(text, reply_markup=keyboard)
