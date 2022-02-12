# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from typing import Union

from pyrogram import Client, filters
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery, Message


@Client.on_callback_query(filters.sudoers & filters.regex("^settings"))
async def on_settings_cq(c: Client, cq: CallbackQuery):
    await on_settings_u(c, cq)


@Client.on_message(filters.sudoers & filters.regex("^/settings"))
async def on_settings_txt(c: Client, m: Message):
    await on_settings_u(c, m)


async def on_settings_u(c: Client, u: Union[Message, CallbackQuery]):
    lang = u._lang
    is_query = hasattr(u, "data")

    lines = [
        [(lang.language, "setting_language")],
        [(lang.sudoers, "setting_sudoers")],
        [(lang.env_vars, "setting_env")],
    ]
    if is_query:
        lines.append([(lang.back, "start")])
    keyb = ikb(lines)

    await (u.edit if is_query else u.reply)(lang.settings_text, keyb)
