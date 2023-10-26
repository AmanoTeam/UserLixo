from dataclasses import dataclass

from kink import inject
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery

from userlixo.assistant.handlers.abstract import CallbackQueryHandler
from userlixo.assistant.handlers.common.upgrade import (
    UpgradeLogicBuilder,
)
from userlixo.services.language_selector import LanguageSelector


@inject
@dataclass
class UpgradeCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _c, cq: CallbackQuery):
        lang = self.language_selector.get_lang()

        back_keyboard = ikb([[(lang.back, "start")]])

        async def edit_message_with_keyboard(text):
            await cq.message.edit(text, reply_markup=back_keyboard)

        async def edit_message(text):
            await cq.message.edit(text)

        await (
            UpgradeLogicBuilder.set_lang(lang)
            .on_success(edit_message)
            .on_error(edit_message_with_keyboard)
            .on_exception(edit_message_with_keyboard)
        ).execute()
