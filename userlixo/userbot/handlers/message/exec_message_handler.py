from dataclasses import dataclass
from typing import BinaryIO

from kink import inject
from pyrogram import Client
from pyrogram.types import Message

from userlixo.abstract import MessageHandler
from userlixo.common.execs import execs
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class ExecMessageHandler(MessageHandler):
    language_selector: LanguageSelector

    async def handle_message(self, client: Client, message: Message):
        lang = self.language_selector.get_lang()

        code = message.matches[0].group("code")

        async def on_result(text: str):
            await message.reply(text, quote=True)

        async def on_error(text: str):
            await message.reply(text, quote=True)

        async def on_huge_result(io: BinaryIO):
            await message.reply_document(io, quote=True)

        async def on_no_result():
            await message.reply(lang.no_result, quote=True)

        await execs(
            code, client, message, on_result, on_error, on_huge_result, on_no_result
        )
