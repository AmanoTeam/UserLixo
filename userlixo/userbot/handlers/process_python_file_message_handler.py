from dataclasses import dataclass

from kink import inject
from pyrogram import Client
from pyrogram.types import Message

from userlixo.abstract import MessageHandler
from userlixo.common.plugins import handle_add_plugin_request
from userlixo.services.language_selector import LanguageSelector


@inject
@dataclass
class ProcessPythonFileMessageHandler(MessageHandler):
    language_selector: LanguageSelector

    async def handle_message(self, client: Client, message: Message):
        lang = self.language_selector.get_lang()

        await handle_add_plugin_request(lang, client, message)
