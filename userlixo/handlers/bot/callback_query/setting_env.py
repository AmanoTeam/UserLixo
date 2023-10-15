# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import os
import sys
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.helpers import array_chunk, ikb
from pyrogram.types import CallbackQuery

from userlixo.config import bot
from userlixo.database import Config


@Client.on_callback_query(filters.sudoers & filters.regex("^setting_env"))
async def on_setting_env(c: Client, cq: CallbackQuery):
    if cq.message:
        cq.message.chat.stop_listening()
    lang = cq._lang
    buttons = []
    async for row in Config.all():
        btn = (f"👁‍🗨 {row.key}", f"view_env {row.key}")
        if cq.message and cq.message.from_user.id == bot.me.id:
            btn = (f"📝 {row.key}", f"edit_env {row.key}")
        buttons.append(btn)
    lines = array_chunk(buttons, 2)
    lines.append([(lang.back, "settings")])
    keyboard = ikb(lines)
    await cq.edit(lang.settings_env_text, keyboard)


@Client.on_callback_query(filters.sudoers & filters.regex("^edit_env (?P<key>.+)"))
async def on_edit(c: Client, cq: CallbackQuery):
    lang = cq._lang
    key = cq.matches[0]["key"]
    value = (await Config.get_or_none(key=key)).value

    text = lang.edit_env_text(key=key, value=value)
    keyboard = ikb([[(lang.back, "setting_env")]])
    last_msg = await cq.edit(text, keyboard)

    env_requires_restart = ["PREFIXES", "DATABASE_URL", "BOT_TOKEN"]
    try:
        while True:
            msg = await cq.from_user.listen(filters.text, None)
            await last_msg.remove_keyboard()
            await Config.get(key=key).update(value=msg.text)
            if key in env_requires_restart:
                text = lang.edit_env_text_restart(key=key, value=msg.text)
                keyboard = ikb(
                    [[(lang.restart_now, "restart_now")], [(lang.back, "setting_env")]]
                )
            else:
                text = lang.edit_env_text(key=key, value=msg.text)
                keyboard = ikb([[(lang.back, "setting_env")]])
            last_msg = await msg.reply_text(text, reply_markup=keyboard)
    except Exception as e:
        print(e)
        pass


@Client.on_callback_query(filters.sudoers & filters.regex("^view_env (?P<key>.+)"))
async def on_view(c: Client, cq: CallbackQuery):
    key = cq.matches[0]["key"]
    value = (await Config.get_or_none(key=key)).value
    await cq.answer(value, show_alert=True)


@Client.on_callback_query(filters.sudoers & filters.regex("^restart_now"))
async def onrestart(c: Client, cq: CallbackQuery):
    lang = cq._lang
    await cq.answer(lang.restarting_now_alert, show_alert=True)
    await cq.message.remove_keyboard()
    message_id = cq.message.id
    chat_id = cq.message.chat.username or cq.message.chat.id
    await Config.create(
        **{
            "key": "restarting_alert",
            "value": f"{message_id}|{chat_id}|{datetime.now().timestamp()}|restart_bot",
        }
    )
    args = [sys.executable, "-m", "userlixo"]
    if "--no-update" in sys.argv:
        args.append("--no-update")
    os.execv(sys.executable, args)
