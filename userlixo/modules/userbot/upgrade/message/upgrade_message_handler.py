from dataclasses import dataclass

from kink import inject
from pyrogram import Client
from pyrogram.types import Message

from userlixo.modules.abstract import MessageHandler
from userlixo.modules.common.restart import save_before_restart_message_info
from userlixo.modules.common.upgrade import UpgradeLogicBuilder
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class UpgradeMessageHandler(MessageHandler):
    language_selector: LanguageSelector

    async def handle_message(self, _client: Client, message: Message):
        lang = self.language_selector.get_lang()

        async def reply_message(text):
            await message.reply(text)

        async def before_upgrade(text):
            msg = await message.reply(text)

            chat_id = msg.chat.id
            message_id = msg.id

            await save_before_restart_message_info(message_id, chat_id, "user")

        await (
            UpgradeLogicBuilder.set_lang(lang)
            .on_success(before_upgrade)
            .on_error(reply_message)
            .on_exception(reply_message)
        ).execute()
