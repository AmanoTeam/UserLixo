# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import asyncio
import importlib
import inspect
import json
import math
import os
import re
import sys

from pyrogram import Client, filters
from pyromod.helpers import ikb

from userlixo.config import bot, plugins, user
from userlixo.database import Config
from userlixo.utils import (
    get_inactive_plugins,
    read_plugin_info,
    reload_plugins_requirements,
    write_plugin_info,
)


@Client.on_message(filters.sudoers & filters.document & filters.private & ~filters.me)
async def on_plugin_file(c, m):
    if m.document.file_name.endswith(".py"):
        await on_add_plugin_u(c, m)


@Client.on_callback_query(filters.sudoers & filters.regex("^add_plugin"))
async def on_add_plugin_cq(c, cq):
    await on_add_plugin_u(c, cq)


@Client.on_message(filters.sudoers & filters.regex("^/(start )?plugin[_ ]add"))
async def on_add_plugin_txt(c, m):
    await on_add_plugin_u(c, m)


async def on_add_plugin_u(c, u):
    is_query = hasattr(u, "data")
    if is_query:
        await u.message.delete()
    lang = u._lang

    loop_count = 0
    while True:
        loop_count += 1
        if not is_query and u.document:
            msg = u
            if loop_count > 1:
                break  # avoid infinite loop
        elif not is_query and u.reply_to_message and u.reply_to_message.document:
            msg = u.reply_to_message
            if loop_count > 1:
                break  # avoid infinite loop
        else:
            msg = await u.from_user.ask(lang.plugin_file_ask)
        if await filters.regex("/cancel")(c, msg):
            return await msg.reply(lang.command_cancelled)
        if not msg.document:
            await msg.reply(lang.plugin_waiting_file, quote=True)
            continue
        if not re.search("(py)$", msg.document.file_name):
            await msg.reply(lang.plugin_format_not_accepted, quote=True)
            continue
        if msg.document.file_size > (5 * 1024 * 1024):
            await msg.reply(lang.plugin_too_big, quote=True)
            continue
        break
    filename = await msg.download("cache/")
    filename = os.path.relpath(filename)
    plugin = read_plugin_info(filename)

    # Showing info
    text = write_plugin_info(plugins, lang, plugin, status_line="")
    lines = [
        [
            (lang.add, f"confirm_add_plugin {plugin['type']} {filename}"),
            (lang.cancel, "cancel_plugin"),
        ]
    ]
    keyb = ikb(lines)
    await msg.reply(text, keyb, disable_web_page_preview=True, quote=True)


@Client.on_callback_query(filters.sudoers & filters.regex("^cancel_plugin"))
async def oncancelplugin(c, cq):
    lang = cq._lang
    await cq.edit(lang.command_cancelled)


@Client.on_callback_query(
    filters.sudoers
    & filters.regex("^confirm_add_plugin (?P<plugin_type>user|bot) (?P<filename>.+)")
)
async def on_confirm_plugin(c, cq):
    lang = cq._lang
    module = None

    plugin_type = cq.matches[0]["plugin_type"]
    client = (user, bot)[plugin_type == "bot"]

    cache_filename = cq.matches[0]["filename"]
    basename = os.path.basename(cache_filename)
    new_filename = "userlixo/handlers/" + plugin_type + "/plugins/" + basename

    plugin = read_plugin_info(cache_filename)
    new_notation = re.sub("\.py$", "", os.path.relpath(new_filename)).replace("/", ".")

    requirements = plugin.get("requirements")
    if requirements:
        DGRAY = 'echo -e "\033[1;30m"'
        RESET = 'echo -e "\033[0m"'
        req_list = requirements.split()
        req_text = "".join(f" ├ <code>{r}</code>\n" for r in req_list[:-1])
        req_text += f" └ <code>{req_list[-1]}</code>"
        text = lang.installing_plugin_requirements
        text.escape_html = False
        await cq.edit(text(requirements=req_text))
        os.system(f"{DGRAY}; {sys.executable} -m pip install {requirements}; {RESET}")

    # Safely unload the plugin if existent
    if os.path.exists(new_filename):
        try:
            module = importlib.import_module(new_notation)
        except Exception as e:
            return await cq.edit(
                lang.plugin_could_not_load_existent(name=basename, e=e)
            )

        functions = [*filter(callable, module.__dict__.values())]
        functions = [*filter(lambda f: hasattr(f, "handlers"), functions)]

        for f in functions:
            for handler in f.handlers:
                client.remove_handler(*handler)

    os.renames(cache_filename, new_filename)
    plugin = read_plugin_info(new_filename)

    try:
        if module:
            importlib.reload(module)
        module = importlib.import_module(plugin["notation"])
    except Exception as e:
        os.remove(new_filename)
        await cq.edit(lang.plugin_could_not_load(e=e))
        raise e

    functions = [*filter(callable, module.__dict__.values())]
    functions = [*filter(lambda f: hasattr(f, "handlers"), functions)]

    # if not len(functions):
    #     os.remove(new_filename)
    #     return await cq.edit(lang.plugin_has_no_handlers)

    for f in functions:
        for handler in f.handlers:
            client.add_handler(*handler)

    if module:
        r = None
        functions = [*filter(callable, module.__dict__.values())]
        for f in functions:
            if hasattr(f, "__name__") and f.__name__ == "post_install_script":
                await cq.edit(lang.running_post_install_script)
                if inspect.iscoroutinefunction(f):
                    r = await f()
                else:
                    r = await asyncio.get_event_loop().run_in_executor(None, f)
                break

        if r is not None:
            unload = False
            if isinstance(r, (tuple, list)):
                if len(r) == 2:
                    if r[0] != 1:
                        await cq.edit(lang.plugin_could_not_load(e=r[1]))
                        unload = True
                else:
                    await cq.edit(
                        lang.plugin_could_not_load(
                            e="The return of post_install_script should be like this: (0, 'nodejs not found')"
                        )
                    )
                    unload = True

            else:
                await cq.edit(
                    lang.plugin_could_not_load(
                        e="The return of post_install_script should be a list or tuple"
                    )
                )
                unload = True

            if unload:
                functions = [*filter(lambda f: hasattr(f, "handlers"), functions)]

                for f in functions:
                    for handler in f.handlers:
                        client.remove_handler(*handler)
                os.remove(new_filename)
                return

    plugins[plugin_type][basename] = plugin
    reload_plugins_requirements(plugins)

    inactive = await get_inactive_plugins(plugins)

    if plugin["notation"] in inactive:
        inactive = [x for x in inactive if x != plugin["notation"]]
        await Config.get(key="INACTIVE_PLUGINS").update(value=json.dumps(inactive))

    # Discover which page is this plugin listed in
    quant_per_page = 4 * 2  # lines times columns
    page = math.ceil(len(plugins) / quant_per_page)

    keyb = ikb(
        [[(lang.see_plugin_info, f"info_plugin {basename} {plugin_type} {page}")]]
    )
    text = lang.plugin_added(name=basename)

    await cq.edit(text, keyb)
