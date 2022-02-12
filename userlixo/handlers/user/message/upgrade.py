# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from pyrogram import Client, filters
from pyrogram.types import Message

from userlixo.handlers.bot.upgrade import on_upgrade_u


@Client.on_message(filters.su_cmd("upgrade"))
async def on_upgrade_m(c: Client, m: Message):
    await on_upgrade_u(c, m)
