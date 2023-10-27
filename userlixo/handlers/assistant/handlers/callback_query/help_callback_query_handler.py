from dataclasses import dataclass

from kink import inject

from userlixo.handlers.abstract import CallbackQueryHandler
from userlixo.handlers.common.help import compose_help_message
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class HelpCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _c, m):
        lang = self.language_selector.get_lang()

        text, keyboard = compose_help_message(lang, append_back=True)
        await m.message.edit(text, reply_markup=keyboard)
