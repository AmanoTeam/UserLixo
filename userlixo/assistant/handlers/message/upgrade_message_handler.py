from dataclasses import dataclass

from kink import inject
from pyrogram.types import Message

from userlixo.assistant.handlers.abstract import MessageHandler
from userlixo.assistant.handlers.common.upgrade import (
    UpgradeLogicBuilder,
)
from userlixo.services.language_selector import LanguageSelector


@inject
@dataclass
class UpgradeMessageHandler(MessageHandler):
    language_selector: LanguageSelector

    async def handle_message(self, _c, m: Message):
        lang = self.language_selector.get_lang()

        async def reply_message(text):
            await m.reply(text)

        await (
            UpgradeLogicBuilder.set_lang(lang)
            .on_success(reply_message)
            .on_error(reply_message)
            .on_exception(reply_message)
        ).execute()
