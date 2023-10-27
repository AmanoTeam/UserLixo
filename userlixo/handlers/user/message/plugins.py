# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import hashlib
import importlib
import json
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import Message
from userlixo.handlers.bot.list_plugins import on_list_plugins_u

from userlixo.config import bot, plugins, user
from userlixo.database import Config
from userlixo.handlers.bot.add_plugin import on_add_plugin_u
from userlixo.utils.plugins import get_inactive_plugins, read_plugin_info


@Client.on_message(filters.sudoers & filters.document & filters.private & ~filters.me)
async def on_plugin_file(c: Client, m: Message):
    if m.document.file_name.endswith(".py"):
        await on_add_plugin_u(c, m)


@Client.on_message(filters.su_cmd("plugins$"))
async def on_list_plugins_txt(c: Client, m: Message):
    await on_list_plugins_u(c, m)


@Client.on_message(filters.reply & filters.su_cmd(r"(plugin )?(?P<action>add|rm|\+|-)"))
async def on_plugin_action(c: Client, m: Message):
    lang = m._lang
    action = m.matches[0]["action"]
    if action in ["+", "add"]:
        if await filters.me(c, m):
            await m.delete()
        return await on_add_plugin_u(c, m)

    # remove plugin on .plugin rm
    act = m.edit if await filters.me(c, m) else m.reply
    msg = m.reply_to_message

    if not msg.document:
        return await act(lang.plugin_rm_not_document)
    if not msg.document.file_name.endswith(".py"):
        return await act(lang.plugin_rm_not_py)

    basename = msg.document.file_name
    cache_filename = await msg.download("cache/")
    plugin = read_plugin_info(cache_filename)
    if not plugin:
        Path(cache_filename).unlink()
        return await msg.reply(lang.plugin_info_block_not_found, quote=True)
    plugin_type = plugin["type"]

    if basename not in plugins[plugin_type]:
        return await act(lang.plugin_rm_not_added(name=basename))

    plugin = plugins[plugin_type][basename]

    # compare files via hash
    with Path(cache_filename).open() as remote_file, Path(plugin["filename"]).open() as local_file:
        local_data = local_file.read()
        local_hash = hashlib.md5(local_data.encode()).hexdigest()[:10]

        temp_data = remote_file.read()
        remote_hash = hashlib.md5(temp_data.encode()).hexdigest()[:10]
    Path(cache_filename).unlink()

    if local_hash != remote_hash:
        return await act(lang.plugin_rm_remote_local_are_diff(name=basename))

    inactive = await get_inactive_plugins(plugins)

    if not Path(plugin["filename"]).exists():
        del plugins[plugin_type][basename]
        return await act(lang.plugin_not_exists_on_server)

    if plugin["notation"] in inactive:
        inactive = [x for x in inactive if x != plugin["notation"]]
        await Config.get(key="INACTIVE_PLUGINS").update(value=json.dumps(inactive))

    try:
        module = importlib.import_module(plugin["notation"])
    except BaseException as e:
        Path(plugin["filename"]).unlink()
        return await act(lang.plugin_could_not_load(e=e))

    functions = [*filter(callable, module.__dict__.values())]
    functions = [*filter(lambda f: hasattr(f, "handler"), functions)]

    client = (user, bot)[plugin_type == "bot"]
    for f in functions:
        client.remove_handler(*f.handler)
    del plugins[plugin_type][basename]
    Path(plugin["filename"]).unlink()

    await act(lang.plugin_removed_text(name=basename))
    return None
