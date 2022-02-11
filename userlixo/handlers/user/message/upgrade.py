# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from pyrogram import Client, filters

from userlixo.handlers.bot.upgrade import on_upgrade_u


@Client.on_message(filters.su_cmd("upgrade"))
async def on_upgrade_m(c, m):
    await on_upgrade_u(c, m)
