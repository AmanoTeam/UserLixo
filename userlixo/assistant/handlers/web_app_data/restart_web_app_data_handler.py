from dataclasses import dataclass

from kink import inject
from pyrogram.types import Message

from userlixo.abstract.web_app_data_handler import WebAppDataHandler
from userlixo.common.restart import (
    compose_before_restart_message,
    save_before_restart_message_info,
    self_restart_process,
)
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class RestartWebAppDataHandler(WebAppDataHandler):
    language_selector: LanguageSelector

    async def handle_web_app_data(self, _c, m: Message):
        lang = self.language_selector.get_lang()

        text = compose_before_restart_message(lang)
        msg = await m.reply(text)

        await save_before_restart_message_info(msg.id, msg.chat.id, "bot")

        self_restart_process()
