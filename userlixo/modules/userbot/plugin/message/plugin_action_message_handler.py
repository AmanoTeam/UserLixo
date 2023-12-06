from dataclasses import dataclass
from pathlib import Path

from kink import inject
from hydrogram import Client, filters
from hydrogram.types import Message

from userlixo.config import plugins
from userlixo.modules.abstract import MessageHandler
from userlixo.modules.common.plugins import handle_add_plugin_request
from userlixo.utils.plugins import (
    InvalidPluginInfoValueError,
    check_if_plugin_folder_exists,
    get_plugin_info_from_zip,
    unload_and_remove_plugin,
)
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class PluginActionMessageHandler(MessageHandler):
    language_selector: LanguageSelector

    async def handle_message(self, client: Client, message: Message):
        lang = self.language_selector.get_lang()

        action = message.matches[0]["action"]
        if action in ["+", "add"]:
            if await filters.me(client, message):
                await message.delete()
            return await handle_add_plugin_request(lang, client, message)

        # remove plugin on .plugin rm
        act = message.edit if await filters.me(client, message) else message.reply
        msg = message.reply_to_message

        if not msg.document:
            return await act(lang.plugin_rm_not_document)
        if not msg.document.file_name.endswith(".zip"):
            return await act(lang.plugin_rm_not_zip)

        cache_filename = await msg.download("cache/")
        try:
            plugin_info = get_plugin_info_from_zip(cache_filename)
        except InvalidPluginInfoValueError as e:
            return await act(lang.plugin_invalid_info_value_error(errors="\n".join(e.args)))

        if not plugin_info:
            Path(cache_filename).unlink()
            return await act(lang.plugin_info_block_not_found)

        plugin_name = plugin_info["name"]
        plugin_path = f"userlixo/plugins/{plugin_name}"

        if plugin_name not in plugins:
            return await act(lang.plugin_rm_not_added(name=plugin_name))

        if not check_if_plugin_folder_exists(plugin_name):
            del plugins[plugin_name]
            return await act(lang.plugin_not_exists_on_server)

        await unload_and_remove_plugin(plugin_path)
        await act(lang.plugin_removed_text(name=plugin_name))
        return None
