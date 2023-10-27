from dataclasses import dataclass

from kink import inject
from pyrogram import Client
from pyrogram.types import Message

from userlixo.abstract import MessageHandler
from userlixo.common.help import compose_help_message
from userlixo.services.language_selector import LanguageSelector


@inject
@dataclass
class HelpMessageHandler(MessageHandler):
    language_selector: LanguageSelector

    async def handle_message(self, _client: Client, message: Message):
        lang = self.language_selector.get_lang()

        text, keyboard = compose_help_message(lang)
        await message.reply(text, reply_markup=keyboard, quote=True)
