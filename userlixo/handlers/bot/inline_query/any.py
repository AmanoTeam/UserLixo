# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import os

from pyrogram import Client
from pyrogram.types import InlineQuery

from userlixo.config import langs


# Getting the language to use
@Client.on_inline_query(group=-2)
async def deflang(c: Client, iq: InlineQuery):
    iq._lang = langs.get_language(os.getenv("LANGUAGE"))
