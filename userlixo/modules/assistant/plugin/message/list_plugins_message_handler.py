from dataclasses import dataclass

from kink import inject
from pyrogram.types import Message

from userlixo.modules.abstract import MessageHandler
from userlixo.modules.common.plugins import compose_list_plugins_message
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class ListPluginsMessageHandler(MessageHandler):
    language_selector: LanguageSelector

    async def handle_message(self, _client, message: Message):
        lang = self.language_selector.get_lang()

        text, keyboard = await compose_list_plugins_message(
            lang, page_number=0, show_add_plugin_button=True, append_back=False
        )
        await message.reply(text, reply_markup=keyboard, quote=True)
