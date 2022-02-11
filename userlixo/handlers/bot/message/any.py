# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import os

from pyrogram import Client, filters

from userlixo.config import langs


# Getting the language to use
@Client.on_message(group=-2)
async def deflang(c, m):
    m._lang = langs.get_language(os.getenv("LANGUAGE"))


@Client.on_message(filters.edited)
async def to_reject(c, m):
    m.stop_propagation()
