# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from pyrogram import Client, filters
from pyrogram.types import Message

from userlixo.handlers.bot.restart import on_restart_u


@Client.on_message(filters.sudoers & filters.su_cmd("restart"))
async def on_restart(c: Client, m: Message):
    await on_restart_u(c, m)
