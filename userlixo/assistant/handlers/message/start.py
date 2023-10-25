from kink import inject
from pyrogram import Client
from pyrogram.types import Message

from userlixo.assistant.handlers.abstract import MessageHandler
from userlixo.assistant.handlers.common.start import compose_start_message
from userlixo.services.language_selector import LanguageSelector


@inject
class StartMessageHandler(MessageHandler):
    def __init__(self, language_selector: LanguageSelector):
        self.get_lang = language_selector.get_lang

    async def handle_message(self, _c: Client, m: Message):
        lang = self.get_lang()

        text, keyboard = compose_start_message(lang)
        await m.reply(text, reply_markup=keyboard, quote=True)
