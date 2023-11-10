from dataclasses import dataclass

from kink import inject
from pyrogram.types import CallbackQuery

from userlixo.modules.abstract import CallbackQueryHandler
from userlixo.modules.common.plugins import compose_list_plugins_message
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class ListPluginsCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        page = int(query.matches[0].group("page")) or 0

        is_inline = query.inline_message_id is not None

        text, keyboard = await compose_list_plugins_message(
            lang, page, append_back=True, use_deeplink=is_inline
        )

        await query.edit(text, reply_markup=keyboard)
