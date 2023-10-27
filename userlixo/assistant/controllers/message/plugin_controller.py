from dataclasses import dataclass

from pyrogram import filters, Client
from pyrogram.types import Message

from userlixo.assistant.handlers.message.list_plugins_message_handler import (
    ListPluginsMessageHandler,
)
from userlixo.decorators import Controller, on_message


@Controller()
@dataclass
class PluginController:
    list_plugins_handler: ListPluginsMessageHandler

    @on_message(filters.document & filters.private & ~filters.me)
    def handle_plugin(self, client: Client, message):
        pass

    @on_message(filters.regex("^/(start )?plugin[_ ]add"))
    def add_plugin(self, client: Client, message):
        pass

    @on_message(filters.regex("^/plugins"))
    async def plugins(self, client: Client, message: Message):
        await self.list_plugins_handler.handle_message(client, message)
