from dataclasses import dataclass

from kink import inject
from hydrogram.types import Message

from userlixo.modules.abstract.web_app_data_handler import WebAppDataHandler
from userlixo.modules.common.restart import save_before_restart_message_info
from userlixo.modules.common.upgrade import UpgradeLogicBuilder
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class UpgradeWebAppDataHandler(WebAppDataHandler):
    language_selector: LanguageSelector

    async def handle_web_app_data(self, _c, message: Message):
        lang = self.language_selector.get_lang()

        async def reply_message(text):
            await message.reply(text)

        async def before_upgrade(text):
            msg = await message.reply(text)

            chat_id = msg.chat.id
            message_id = msg.id

            await save_before_restart_message_info(message_id, chat_id, "bot")

        await (
            UpgradeLogicBuilder.set_lang(lang)
            .on_success(before_upgrade)
            .on_error(reply_message)
            .on_exception(reply_message)
        ).execute()
