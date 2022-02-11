# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from pyrogram import Client, filters

from userlixo.handlers.bot.settings import on_settings_u


@Client.on_message(filters.su_cmd("settings"))
async def on_settings_txt(c, m):
    await on_settings_u(c, m)
