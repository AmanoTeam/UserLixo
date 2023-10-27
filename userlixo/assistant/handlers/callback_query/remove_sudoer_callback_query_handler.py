import os
from dataclasses import dataclass

from kink import inject
from pyrogram.types import CallbackQuery

from userlixo.abstract import CallbackQueryHandler
from userlixo.assistant.handlers.common.sudoers import compose_list_sudoers_message
from userlixo.config import sudoers
from userlixo.database import Config
from userlixo.services.language_selector import LanguageSelector
from userlixo.utils import tryint


@inject
@dataclass
class RemoveSudoerCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        who = tryint(query.matches[0].group("who"))

        # Sanitize list
        sudoers[:] = [*map(tryint, sudoers)]
        removed = [x for x in sudoers if x != who]
        sudoers[:] = removed

        await Config.get(key="SUDOERS_LIST").update(
            value=" ".join([*map(str, sudoers)])
        )
        os.environ["SUDOERS_LIST"] = " ".join([*map(str, sudoers)])

        text, keyboard = await compose_list_sudoers_message(
            lang, _client, from_user_id=query.from_user.id
        )
        await query.message.edit(text, reply_markup=keyboard)
