from dataclasses import dataclass

from kink import inject
from pyrogram.types import CallbackQuery

from userlixo.handlers.abstract import CallbackQueryHandler
from userlixo.handlers.common.commands import compose_list_commands_message
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class ListCommandsCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        page = int(query.matches[0].group("page") or 0)

        text, keyboard = compose_list_commands_message(lang, page, append_back=True)
        await query.message.edit(text, reply_markup=keyboard)