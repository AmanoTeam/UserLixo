# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery


@Client.on_callback_query(filters.sudoers & filters.regex("ping"))
async def onping(c: Client, cq: CallbackQuery):
    before = datetime.now()
    await c.get_me()
    after = datetime.now()
    diff_ms = (after - before).microseconds / 1000

    await cq.answer(f"Pong! {diff_ms}ms", show_alert=True)
