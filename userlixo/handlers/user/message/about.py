# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from pyrogram import Client, filters
from pyrogram.types import Message


@Client.on_message(filters.su_cmd("about"))
async def on_about(c: Client, m: Message):
    lang = m._lang
    await m.reply(lang.about_userlixo_text, disable_web_page_preview=True)
