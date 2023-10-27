from dataclasses import dataclass

from kink import inject
from pyrogram import Client
from pyrogram.types import Message

from userlixo.abstract import MessageHandler
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class AboutMessageHandler(MessageHandler):
    language_selector: LanguageSelector

    async def handle_message(self, _client: Client, message: Message):
        lang = self.language_selector.get_lang()

        text = lang.about_userlixo_text
        await message.reply(text, disable_web_page_preview=True)
