from dataclasses import dataclass
from datetime import UTC, datetime

from hydrogram import Client
from hydrogram.enums import ChatAction
from hydrogram.types import Message
from kink import inject

from userlixo.modules.abstract import MessageHandler
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class PingMessageHandler(MessageHandler):
    language_selector: LanguageSelector

    @staticmethod
    async def handle_message(client: Client, message: Message):
        before = datetime.now(tz=UTC)
        await client.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        after = datetime.now(tz=UTC)
        diff_ms = (after - before).microseconds / 1000

        keyboard = [[("🏓", "ping")]]
        await message.reply(f"<b>Pong!</b> <code>{diff_ms}</code><code>ms</code>", keyboard)
