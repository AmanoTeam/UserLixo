from kink import inject
from pyrogram import Client
from pyrogram.types import CallbackQuery

from userlixo.assistant.handlers.abstract import CallbackQueryHandler
from userlixo.assistant.handlers.common.start import compose_start_message
from userlixo.services.language_selector import LanguageSelector


@inject
class StartCallbackQueryHandler(CallbackQueryHandler):
    def __init__(self, language_selector: LanguageSelector):
        self.get_lang = language_selector.get_lang

    async def handle_callback_query(self, _c: Client, cq: CallbackQuery):
        lang = self.get_lang()

        text, keyboard = compose_start_message(lang)
        await cq.edit_message_text(text, reply_markup=keyboard)
