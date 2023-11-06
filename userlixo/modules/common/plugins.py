import os
import re

from langs import Langs
from pyrogram import Client, filters
from pyrogram.helpers import ikb
from pyrogram.nav import Pagination
from pyrogram.types import CallbackQuery, Message

from userlixo.config import bot, plugins
from userlixo.types.plugin_info import PluginInfo
from userlixo.utils.plugins import (
    InvalidPluginInfoValueError,
    get_inactive_plugins,
    get_plugin_info_from_zip,
)


async def compose_list_plugins_message(
    lang: Langs,
    page_number: int,
    show_add_plugin_button: bool = True,
    append_back: bool = False,
):
    inactive_plugins = await get_inactive_plugins(plugins)

    def item_title(plugin: PluginInfo, _pg):
        name = plugin.name
        status = "💤" if name in inactive_plugins else "❇️"

        return f"{status} {name}"

    def item_data(plugin: PluginInfo, page):
        name = plugin.name

        return f"info_plugin {name} {page}"

    layout = Pagination(
        [*plugins.values()],
        item_data=item_data,
        item_title=item_title,
        page_data=lambda page: f"list_plugins {page}",
    )

    lines = layout.create(page_number, lines=4, columns=2)

    # if the message is /plugins (sent to bot) or it's a callback query 'plugins'
    if show_add_plugin_button:
        lines.append([(lang.add_plugin, f"add_plugin {page_number}")])
    else:  # is command to user
        lines.append([(lang.add_plugin, f"t.me/{bot.me.username}?start=plugin_add", "url")])

    if append_back:
        lines.append([(lang.back, "settings")])
    keyboard = ikb(lines)
    return lang.plugins_text, keyboard


def compose_plugin_info_text(lang, info: PluginInfo, **kwargs):
    lang.escape_html = False
    info_lines = {"status_line": "", "requirements_line": ""}
    for item in ["channel", "github", "contributors", "description"]:
        text = ""
        if getattr(info, item, None):
            text = getattr(lang, f"plugin_{item}_line")
            text = "\n" + text(**{item: getattr(info, item)})
        info_lines[item + "_line"] = text

    lang.escape_html = True
    if info.requirements:
        info_lines["requirements_line"] = "\n" + lang.plugin_requirements_line(
            requirements="\n".join(info.requirements)
        )

    text = lang.plugin_info
    text.escape_html = False
    return text(
        info=info.__dict__,
        **{**info_lines, **kwargs},  # make kwargs override info_lines
    )


async def handle_add_plugin_request(lang: Langs, client: Client, update: Message | CallbackQuery):
    is_query = isinstance(update, CallbackQuery)
    loop_count = 0
    while True:
        loop_count += 1
        if not is_query and update.document:
            msg = update
            if loop_count > 1:
                break  # avoid infinite loop
        elif not is_query and update.reply_to_message and update.reply_to_message.document:
            msg = update.reply_to_message
            if loop_count > 1:
                break  # avoid infinite loop
        else:
            msg = await update.from_user.ask(lang.plugin_file_ask)
        if await filters.regex("/cancel")(client, msg):
            return await msg.reply(lang.command_cancelled)
        if not msg.document:
            await msg.reply(lang.plugin_waiting_file, quote=True)
            continue
        if not re.search("(zip)$", msg.document.file_name):
            await msg.reply(lang.plugin_format_not_accepted, quote=True)
            continue
        if msg.document.file_size > (5 * 1024 * 1024):
            await msg.reply(lang.plugin_too_big, quote=True)
            continue
        break
    filename = await msg.download("cache/")
    filename = os.path.relpath(filename)

    try:
        plugin_info = get_plugin_info_from_zip(filename)
    except InvalidPluginInfoValueError as e:
        return await msg.reply(lang.plugin_invalid_info_value_error(errors="\n".join(e.args[0])))

    if not plugin_info:
        return await msg.reply(lang.plugin_info_block_not_found)

    # Showing info
    text = compose_plugin_info_text(lang, plugin_info, status_line="")
    lines = [
        [
            (lang.add, f"confirm_add_plugin {filename}"),
            (lang.cancel, "cancel_plugin"),
        ]
    ]
    keyboard = ikb(lines)
    await msg.reply(text, reply_markup=keyboard)
    return None
