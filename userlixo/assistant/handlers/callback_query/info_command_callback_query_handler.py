from dataclasses import dataclass

from kink import inject
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery

from userlixo.abstract import CallbackQueryHandler
from userlixo.config import cmds
from userlixo.services.language_selector import LanguageSelector


@inject
@dataclass
class InfoCommandCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        cmd = query.matches[0]["cmd"]
        pg = int(query.matches[0]["pg"])

        if cmd not in cmds:
            return await query.answer(lang.unknown_command)

        info = lang.strings[lang.code].get(f"cmd_info_{cmd}", cmds[cmd])

        if len(info) < 100:
            return await query.answer("ℹ️ " + info, show_alert=True)

        keyboard = ikb([[(lang.back, f"list_commands {pg}")]])
        text = lang.command_info

        text.escape_html = False
        await query.message.edit(text(command=cmd, info=info), keyboard)
