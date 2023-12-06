import re
from dataclasses import dataclass

from kink import inject
from pyrogram import filters
from pyrogram.helpers import force_reply, ikb
from pyrogram.types import Message

from userlixo.config import sudoers, user
from userlixo.database import Config
from userlixo.modules.abstract import MessageHandler
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class AddSudoerMessageHandler(MessageHandler):
    language_selector: LanguageSelector

    async def handle_message(self, _c, m: Message):
        lang = self.language_selector.get_lang()

        text = lang.add_sudoer_ask
        response = await m.chat.ask(text, filters.text, timeout=600, reply_markup=force_reply())

        if not re.match(r"@?\w+$", response.text):
            return await m.reply(lang.add_sudoer_not_match)

        sudoers_str: str = Config.get(Config.key == "SUDOERS_LIST").value
        sudoers_list = sudoers_str.split(" ")
        sudoers_list.append(response.text.lstrip("@"))
        sudoers[:] = [user.me.id, *sudoers_list]
        Config.update(value=" ".join(map(str, sudoers_list))).where(Config.key == "SUDOERS_LIST").execute()

        keyboard = ikb([[(lang.back, "setting_sudoers")]])
        await m.reply(lang.sudoer_added, keyboard)
        return None
