# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2021 Amano Team

from pyrogram import Client, filters

from userlixo.handlers.bot.help import on_help_u


@Client.on_message(filters.su_cmd("help"))
async def on_help_m(c, m):
    await on_help_u(c, m)
