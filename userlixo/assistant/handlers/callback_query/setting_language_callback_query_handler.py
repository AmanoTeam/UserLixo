from dataclasses import dataclass

from kink import inject
from pyrogram.helpers import array_chunk, ikb
from pyrogram.types import CallbackQuery

from userlixo.abstract import CallbackQueryHandler
from userlixo.services.language_selector import LanguageSelector


@inject
@dataclass
class SettingLanguageCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

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
        await query.message.edit(lang.choose_language, keyboard)
