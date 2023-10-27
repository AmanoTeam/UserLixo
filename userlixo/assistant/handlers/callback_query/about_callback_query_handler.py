import os
from dataclasses import dataclass

from kink import inject
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery

from userlixo.assistant.handlers.abstract import CallbackQueryHandler
from userlixo.config import cmds
from userlixo.services.language_selector import LanguageSelector


@inject
@dataclass
class AboutCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        subject = query.matches[0]["subject"]
        keyboard = ikb([[(lang.back, "help")]])
        text = {
            "userlixo": lang.about_userlixo_text,
            "plugins": lang.about_plugins_text,
            "commands": lang.about_commands_text,
        }
        text = text[subject]
        if subject == "commands":
            commands = [*cmds.keys()]
            total = len(commands)
            prefixes = os.getenv("PREFIXES")
            examples = []
            for n, p in enumerate([*prefixes]):
                if n > total - 1:  # if passed the end
                    break
                examples.append("<code>" + p + commands[n] + "</code>")
            examples = ", ".join(examples)
            commands_list = [*map(lambda x: f"<code>{x}</code>", commands)]

            text.escape_html = False
            text = text(
                total=total,
                commands=", ".join(commands_list[:-1]),
                last_command=commands_list[-1],
                prefixes=prefixes,
                examples=examples,
            )
        await query.edit(text, keyboard, disable_web_page_preview=True)
