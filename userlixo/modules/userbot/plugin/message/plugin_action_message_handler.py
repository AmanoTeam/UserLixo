from dataclasses import dataclass
from pathlib import Path

from hydrogram import Client, filters
from hydrogram.types import Message
from kink import inject

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
        if action in {"+", "add"} and filters.me(client, message):
            await message.delete()
            await handle_add_plugin_request(lang, client, message)
            return

        # remove plugin on .plugin rm
        act = message.edit if filters.me(client, message) else message.reply
        msg = message.reply_to_message

        if not msg.document:
            await act(lang.plugin_rm_not_document)
        elif not msg.document.file_name.endswith(".zip"):
            await act(lang.plugin_rm_not_zip)
        else:
            cache_filename = await msg.download("cache/")
            try:
                plugin_info = get_plugin_info_from_zip(cache_filename)
            except InvalidPluginInfoValueError as e:
                await act(lang.plugin_invalid_info_value_error(errors="\n".join(e.args)))
            else:
                if not plugin_info:
                    Path(cache_filename).unlink()
                    await act(lang.plugin_info_block_not_found)
                else:
                    plugin_name = plugin_info["name"]
                    plugin_path = f"userlixo/plugins/{plugin_name}"

                    if plugin_name not in plugins:
                        await act(lang.plugin_rm_not_added(name=plugin_name))
                    elif not check_if_plugin_folder_exists(plugin_name):
                        del plugins[plugin_name]
                        await act(lang.plugin_not_exists_on_server)
                    else:
                        unload_and_remove_plugin(plugin_path)
                        await act(lang.plugin_removed_text(name=plugin_name))
