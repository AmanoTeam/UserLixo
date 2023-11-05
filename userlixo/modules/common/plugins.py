import os
import re

from langs import Langs
from pyrogram import Client, filters
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery, Message

from userlixo.config import bot, user
from userlixo.utils.plugins import get_plugin_info_from_zip


def compose_list_plugins_message(lang: Langs, append_back: bool = False):
    text = lang.list_plugins_select_type(
        user=("@" + user.me.username if user.me.username else user.me.first_name),
        bot=bot.me.username,
    )
    keyboard = ikb(
        [
            [
                (lang.user_plugins, "user_plugins 0"),
                (lang.bot_plugins, "bot_plugins 0"),
            ],
            [(lang.back, "start")] if append_back else [],
        ]
    )

    return text, keyboard


def compose_plugin_info_text(lang, info, **kwargs):
    lang.escape_html = False
    info_lines = {"status_line": "", "requirements_line": ""}
    for item in ["channel", "github", "contributors", "description"]:
        text = ""
        if item in info:
            text = getattr(lang, f"plugin_{item}_line")
            text = "\n" + text(**{item: info[item]})
        info_lines[item + "_line"] = text

    lang.escape_html = True
    if "requirements" in info:
        info_lines["requirements_line"] = "\n" + lang.plugin_requirements_line(
            requirements=info["requirements"]
        )

    text = lang.plugin_info
    text.escape_html = False
    return text(
        info=info,
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
        if not re.search("(py)$", msg.document.file_name):
            await msg.reply(lang.plugin_format_not_accepted, quote=True)
            continue
        if msg.document.file_size > (5 * 1024 * 1024):
            await msg.reply(lang.plugin_too_big, quote=True)
            continue
        break
    filename = await msg.download("cache/")
    filename = os.path.relpath(filename)

    plugin_info = get_plugin_info_from_zip(filename)

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
