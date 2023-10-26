from typing import BinaryIO

from kink import inject
from pyrogram.types import Message

from userlixo.assistant.handlers.abstract import MessageHandler
from userlixo.common.cmd import cmd
from userlixo.services.language_selector import LanguageSelector


@inject
class CmdMessageHandler(MessageHandler):
    def __init__(self, language_selector: LanguageSelector):
        self.get_lang = language_selector.get_lang

    async def handle_message(self, client, message: Message):
        lang = self.get_lang()
        code = message.matches[0].group("code")

        async def on_result(text: str):
            await message.reply(text, quote=True)

        async def on_huge_result(io: BinaryIO):
            await message.reply_document(io, quote=True)

        async def on_no_result():
            await message.reply(lang.executed_cmd, quote=True)

        await cmd(code, on_result, on_huge_result, on_no_result)
