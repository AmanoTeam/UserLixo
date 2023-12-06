from dataclasses import dataclass

from kink import inject
from hydrogram import Client
from hydrogram.types import Message

from userlixo.modules.abstract import MessageHandler
from userlixo.modules.common.start import compose_start_message
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class StartMessageHandler(MessageHandler):
    language_selector: LanguageSelector

    async def handle_message(self, _client: Client, message: Message):
        lang = self.language_selector.get_lang()

        text, keyboard = compose_start_message(lang)
        await message.reply(text, reply_markup=keyboard, quote=True)
