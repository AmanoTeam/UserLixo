from dataclasses import dataclass

from kink import inject
from pyrogram.enums import ChatType
from pyrogram.types import Message

from userlixo.modules.abstract import MessageHandler
from userlixo.modules.common.plugins import compose_list_plugins_message
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class ListPluginsMessageHandler(MessageHandler):
    language_selector: LanguageSelector

    async def handle_message(self, client, message: Message):
        lang = self.language_selector.get_lang()

        is_not_private = message.chat.type != ChatType.PRIVATE

        text, keyboard = await compose_list_plugins_message(
            lang, page_number=0, append_back=False, use_deeplink=is_not_private
        )
        await message.reply(text, reply_markup=keyboard, quote=True)
