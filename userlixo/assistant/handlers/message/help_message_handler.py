from dataclasses import dataclass

from kink import inject

from userlixo.abstract import MessageHandler
from userlixo.common.help import compose_help_message
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class HelpMessageHandler(MessageHandler):
    language_selector: LanguageSelector

    async def handle_message(self, _c, m):
        lang = self.language_selector.get_lang()

        text, keyboard = compose_help_message(lang)
        await m.reply(text, reply_markup=keyboard, quote=True)
