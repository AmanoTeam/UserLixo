from dataclasses import dataclass

from kink import inject
from pyrogram.types import Message

from userlixo.modules.abstract.web_app_data_handler import WebAppDataHandler
from userlixo.modules.common.upgrade import UpgradeLogicBuilder
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class UpgradeWebAppDataHandler(WebAppDataHandler):
    language_selector: LanguageSelector

    async def handle_web_app_data(self, _c, m: Message):
        lang = self.language_selector.get_lang()

        async def reply_message(text):
            await m.reply(text)

        await (
            UpgradeLogicBuilder.set_lang(lang)
            .on_success(reply_message)
            .on_error(reply_message)
            .on_exception(reply_message)
        ).execute()
