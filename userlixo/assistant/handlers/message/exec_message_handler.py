from typing import BinaryIO

from kink import inject
from pyrogram.types import Message

from userlixo.assistant.handlers.abstract import MessageHandler
from userlixo.common.execs import execs
from userlixo.services.language_selector import LanguageSelector


@inject
class ExecMessageHandler(MessageHandler):
    def __init__(self, language_selector: LanguageSelector):
        self.get_lang = language_selector.get_lang

    async def handle_message(self, client, message: Message):
        lang = self.get_lang()
        code = message.matches[0].group("code")

        async def on_result(text: str):
            await message.reply(text, quote=True)

        async def on_error(text: str):
            await message.reply(text, quote=True)

        async def on_huge_result(io: BinaryIO):
            await message.reply_document(io, quote=True)

        async def on_no_result():
            await message.reply(lang.no_result, quote=True)

        await execs(code, client, message, on_result, on_error, on_huge_result, on_no_result)
