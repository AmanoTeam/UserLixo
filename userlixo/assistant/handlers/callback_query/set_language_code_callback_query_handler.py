import os
from dataclasses import dataclass

from kink import inject
from pyrogram.helpers import array_chunk, ikb
from pyrogram.types import CallbackQuery

from userlixo.abstract import CallbackQueryHandler
from userlixo.database import Config
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class SetLanguageCodeCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        match = query.matches[0]
        lang = lang.get_language(match["code"])
        await Config.get(key="LANGUAGE").update(value=lang.code)
        os.environ["LANGUAGE"] = lang.code
        buttons = []
        for code, obj in lang.strings.items():
            text, data = (
                (f"✅ {obj['NAME']}", "noop")
                if obj["LANGUAGE_CODE"] == lang.code
                else (obj["NAME"], f"set_language {obj['LANGUAGE_CODE']}")
            )
            buttons.append((text, data))

        lines = array_chunk(buttons, 2)
        lines.append([(lang.back, "settings")])

        keyboard = ikb(lines)
        await query.edit(lang.choose_language, keyboard, {"text": lang.language_chosen})
