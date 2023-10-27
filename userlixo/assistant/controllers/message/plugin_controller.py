from dataclasses import dataclass

from pyrogram import filters, Client
from pyrogram.types import Message

from userlixo.assistant.handlers.message.add_plugin_message_handler import (
    AddPluginMessageHandler,
)
from userlixo.assistant.handlers.message.list_plugins_message_handler import (
    ListPluginsMessageHandler,
)
from userlixo.assistant.handlers.message.process_python_file_message_handler import (
    ProcessPythonFileMessageHandler,
)
from userlixo.decorators import Controller, on_message


@Controller()
@dataclass
class PluginController:
    list_plugins_handler: ListPluginsMessageHandler
    add_plugin_handler: AddPluginMessageHandler
    process_python_file_handler: ProcessPythonFileMessageHandler

    @on_message(filters.document & filters.private & ~filters.me)
    async def handle_plugin(self, client: Client, message: Message):
        if message.document.file_name.endswith(".py"):
            await self.process_python_file_handler.handle_message(client, message)

    @on_message(filters.regex("^/(start )?plugin[_ ]add"))
    async def add_plugin(self, client: Client, message):
        await self.add_plugin_handler.handle_message(client, message)

    @on_message(filters.regex("^/plugins"))
    async def plugins(self, client: Client, message: Message):
        await self.list_plugins_handler.handle_message(client, message)
