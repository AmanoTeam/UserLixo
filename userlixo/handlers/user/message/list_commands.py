# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from pyrogram import Client, filters
from pyrogram.types import Message

from userlixo.handlers.bot.list_commands import on_list_commands_u


@Client.on_message(filters.su_cmd("(commands|cmds)"))
async def on_list_commands_txt(c: Client, m: Message):
    m.matches = [{"page": 0}]
    await on_list_commands_u(c, m)
