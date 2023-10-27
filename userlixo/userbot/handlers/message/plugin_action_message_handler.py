import hashlib
import importlib
import json
import os
from dataclasses import dataclass

from kink import inject
from pyrogram import Client, filters
from pyrogram.types import Message

from userlixo.abstract import MessageHandler
from userlixo.common.plugins import handle_add_plugin_request
from userlixo.config import plugins, user, bot
from userlixo.database import Config
from userlixo.utils.plugins import read_plugin_info, get_inactive_plugins
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
        if not msg.document.file_name.endswith(".py"):
            return await act(lang.plugin_rm_not_py)

        basename = msg.document.file_name
        cache_filename = await msg.download("cache/")
        plugin = read_plugin_info(cache_filename)
        if not plugin:
            os.remove(cache_filename)
            return await msg.reply(lang.plugin_info_block_not_found, quote=True)
        plugin_type = plugin["type"]

        if basename not in plugins[plugin_type]:
            return await act(lang.plugin_rm_not_added(name=basename))

        plugin = plugins[plugin_type][basename]

        # compare files via hash
        with open(cache_filename) as remote_file, open(
            plugin["filename"]
        ) as local_file:
            local_data = local_file.read()
            local_hash = hashlib.md5(local_data.encode()).hexdigest()[:10]

            temp_data = remote_file.read()
            remote_hash = hashlib.md5(temp_data.encode()).hexdigest()[:10]
        os.remove(cache_filename)

        if local_hash != remote_hash:
            return await act(lang.plugin_rm_remote_local_are_diff(name=basename))

        inactive = await get_inactive_plugins(plugins)

        if not os.path.exists(plugin["filename"]):
            del plugins[plugin_type][basename]
            return await act(lang.plugin_not_exists_on_server)

        if plugin["notation"] in inactive:
            inactive = [x for x in inactive if x != plugin["notation"]]
            await Config.get(key="INACTIVE_PLUGINS").update(value=json.dumps(inactive))

        try:
            module = importlib.import_module(plugin["notation"])
        except BaseException as e:
            os.remove(plugin["filename"])
            return await act(lang.plugin_could_not_load(e=e))

        functions = [*filter(callable, module.__dict__.values())]
        functions = [*filter(lambda f: hasattr(f, "handler"), functions)]

        client = (user, bot)[plugin_type == "bot"]
        for f in functions:
            client.remove_handler(*f.handler)
        del plugins[plugin_type][basename]
        os.remove(plugin["filename"])

        await act(lang.plugin_removed_text(name=basename))
