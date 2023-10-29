from dataclasses import dataclass

from kink import inject
from pyrogram.types import CallbackQuery

from userlixo.handlers.abstract import CallbackQueryHandler
from userlixo.handlers.common.restart import (
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
        msg = await query.edit(text)

        await save_before_restart_message_info(msg.id, msg.chat.id, "bot")

        self_restart_process()
