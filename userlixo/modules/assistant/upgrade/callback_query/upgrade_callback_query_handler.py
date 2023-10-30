from dataclasses import dataclass

from kink import inject
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery

from userlixo.modules.abstract import CallbackQueryHandler
from userlixo.modules.common.restart import save_before_restart_message_info
from userlixo.modules.common.upgrade import (
    UpgradeLogicBuilder,
)
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class UpgradeCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _c, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        back_keyboard = ikb([[(lang.back, "start")]])

        async def edit_message_with_keyboard(text):
            await query.edit(text, reply_markup=back_keyboard)

        async def edit_message(text):
            await query.edit(text)

        async def before_upgrade(text):
            chat_id = "inline"
            message_id = query.inline_message_id

            if query.message and query.message.chat:
                chat_id = query.message.chat.id
                message_id = query.message.id

            await save_before_restart_message_info(message_id, chat_id, "bot")
            await edit_message(text)

        await (
            UpgradeLogicBuilder.set_lang(lang)
            .on_success(before_upgrade)
            .on_error(edit_message_with_keyboard)
            .on_exception(edit_message_with_keyboard)
        ).execute()
