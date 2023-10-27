from dataclasses import dataclass

from kink import inject
from pyrogram.types import CallbackQuery

from userlixo.assistant.handlers.abstract import CallbackQueryHandler
from userlixo.assistant.handlers.common.restart import (
    self_restart_process,
    save_before_restart_message_info,
)
from userlixo.services.language_selector import LanguageSelector


@inject
@dataclass
class RestartNowCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        await query.answer(lang.restarting_now_alert, show_alert=True)
        await query.message.remove_keyboard()

        message_id = query.message.id
        chat_id = query.message.chat.username or query.message.chat.id

        await save_before_restart_message_info(message_id, chat_id, "bot")
        self_restart_process()
