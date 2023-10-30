from dataclasses import dataclass

from kink import inject
from pyrogram.types import CallbackQuery

from userlixo.modules.abstract import CallbackQueryHandler
from userlixo.modules.common.restart import (
    save_before_restart_message_info,
    self_restart_process,
)
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class RestartNowCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        await query.answer(lang.restarting_now_alert, show_alert=True)
        await query.message.remove_keyboard()

        chat_id = "inline"
        message_id = query.inline_message_id

        if query.message and query.message.chat:
            chat_id = query.message.chat.id
            message_id = query.message.id

        await save_before_restart_message_info(message_id, chat_id, "bot")
        self_restart_process()
