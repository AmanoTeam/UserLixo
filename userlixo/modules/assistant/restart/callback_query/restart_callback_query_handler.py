from dataclasses import dataclass

from kink import inject
from hydrogram.types import CallbackQuery

from userlixo.modules.abstract import CallbackQueryHandler
from userlixo.modules.common.restart import (
    compose_before_restart_message,
    save_before_restart_message_info,
    self_restart_process,
)
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class RestartCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _c, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        text = compose_before_restart_message(lang)
        await query.edit(text)

        chat_id = "inline"
        message_id = query.inline_message_id

        if query.message and query.message.chat:
            chat_id = query.message.chat.id
            message_id = query.message.id

        await save_before_restart_message_info(message_id, chat_id, "bot")

        self_restart_process()
