from dataclasses import dataclass

from kink import inject
from pyrogram import Client
from pyrogram.types import Message

from userlixo.abstract import MessageHandler
from userlixo.common.commands import compose_list_commands_message
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class ListCommandsMessageHandler(MessageHandler):
    language_selector: LanguageSelector

    async def handle_message(self, _client: Client, message: Message):
        lang = self.language_selector.get_lang()

        text, keyboard = compose_list_commands_message(lang, page=0, append_back=False)
        await message.reply(text, reply_markup=keyboard, quote=True)
